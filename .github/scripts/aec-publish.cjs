// Runs only from the trusted workflow revision, never from the candidate checkout.
module.exports = async ({github, context, core}) => {
  const {owner, repo} = context.repo;
  const {CANDIDATE: candidate, BASE: base, CHECK_RESULT: result} = process.env;
  const sha = /^[a-f0-9]{40}$/;
  if (!sha.test(candidate || '') || !sha.test(base || '')) throw Error('Invalid planned revision');
  if (!['success', 'failure', 'cancelled'].includes(result)) throw Error('Unexpected check state');
  const ref = await github.rest.git.getRef({owner, repo, ref: 'heads/main'});
  if (ref.data.object.sha !== base) throw Error('Main moved; rerun against the new base');
  const run = `https://github.com/${owner}/${repo}/actions/runs/${context.runId}`;
  // Deliberately do not consume logs, artifacts, patches or outputs from candidate execution.
  const body = `Candidate Telosmith commit: ${candidate}\nMtG base: ${base}\n\nIsolated candidate job: ${result}. [Inspect the run](${run}).\n\nCandidate code controls its own results. A successful job is compatibility evidence only, not a security review or approval. Independent review is required before adopting this pin. No candidate-generated files or text were imported.`;
  if (result !== 'success') {
    const title = `AEC upstream ${candidate} fails isolated checks`;
    const issues = await github.paginate(github.rest.issues.listForRepo, {owner, repo, state:'open', creator:'github-actions[bot]', per_page:100});
    const existing = issues.find(i => !i.pull_request && i.title === title);
    if (existing) await github.rest.issues.createComment({owner, repo, issue_number:existing.number, body});
    else await github.rest.issues.create({owner, repo, title, body});
    return;
  }
  const path = 'tools/aec_upstream.json';
  const original = await github.rest.repos.getContent({owner, repo, path, ref:base});
  const pin = JSON.parse(Buffer.from(original.data.content, 'base64').toString('utf8'));
  if (pin.repo !== 'https://github.com/eraevous/Telosmith' || !sha.test(pin.commit)) throw Error('Unexpected upstream configuration');
  if (pin.commit === candidate) return;
  const commit = await github.rest.repos.getCommit({owner:'eraevous', repo:'Telosmith', ref:candidate});
  if (commit.data.sha !== candidate) throw Error('Candidate mismatch');
  const date = commit.data.commit.committer.date.slice(0,10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw Error('Invalid commit date');
  const updated = {...pin, commit:candidate, date, history:[...(pin.history || []), {commit:pin.commit, date:pin.date || null}]};
  delete updated.aec_version;
  const branch = `aec/upstream-${candidate}`;
  // Never overwrite an existing branch (including a partially completed prior attempt).
  try { await github.rest.git.getRef({owner, repo, ref:`heads/${branch}`}); core.notice('Candidate branch already exists; inspect existing work before retry'); return; }
  catch (e) { if (e.status !== 404) throw e; }
  await github.rest.git.createRef({owner, repo, ref:`refs/heads/${branch}`, sha:base});
  await github.rest.repos.createOrUpdateFileContents({owner, repo, path, branch, sha:original.data.sha,
    message:`Propose AEC upstream pin ${candidate}`, content:Buffer.from(JSON.stringify(updated,null,2)+'\n').toString('base64')});
  await github.rest.pulls.create({owner, repo, base:'main', head:branch, draft:true, title:`Propose AEC upstream pin ${candidate.slice(0,7)}`, body});
  await github.rest.actions.createWorkflowDispatch({owner, repo, workflow_id:'ci.yml', ref:branch});
};
