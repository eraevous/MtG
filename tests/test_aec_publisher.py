"""Exercise the writer with a fake GitHub API; never invoke upstream code."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class PublisherTests(unittest.TestCase):
    def test_writer_reconstructs_only_pin(self):
        script = r'''
const assert=require('node:assert/strict');
const publish=require('./.github/scripts/aec-publish.cjs');
const base='a'.repeat(40), candidate='b'.repeat(40);
process.env.BASE=base; process.env.CANDIDATE=candidate; process.env.CHECK_RESULT='success';
const calls=[];
const pin={repo:'https://github.com/eraevous/Telosmith',commit:'c'.repeat(40),date:'2026-01-01'};
const github={rest:{git:{
 getRef:async x=>{if(x.ref==='heads/main') return {data:{object:{sha:base}}}; throw {status:404}},
 createRef:async x=>calls.push(['ref',x])},repos:{
 getContent:async()=>({data:{sha:'blob',content:Buffer.from(JSON.stringify(pin)).toString('base64')}}),
 getCommit:async()=>({data:{sha:candidate,commit:{committer:{date:'2026-11-10T00:00:00Z'}}}}),
 createOrUpdateFileContents:async x=>calls.push(['file',x])},pulls:{create:async x=>calls.push(['pr',x])},
 actions:{createWorkflowDispatch:async x=>calls.push(['dispatch',x])}}};
(async()=>{
 await publish({github,context:{repo:{owner:'eraevous',repo:'MtG'},runId:1},core:{notice(){}}});
 assert.deepEqual(calls.map(c=>c[0]),['ref','file','pr','dispatch']);
 const file=calls[1][1]; assert.equal(file.path,'tools/aec_upstream.json');
 const data=JSON.parse(Buffer.from(file.content,'base64')); assert.equal(data.commit,candidate);
 assert.equal(calls[2][1].draft,true);
 calls.length=0; process.env.CANDIDATE='bad\n$(touch /tmp/no)';
 await assert.rejects(()=>publish({github,context:{repo:{}},core:{}}),/Invalid planned/);
 assert.equal(calls.length,0);
 process.env.CANDIDATE=candidate; process.env.BASE='d'.repeat(40);
 await assert.rejects(()=>publish({github,context:{repo:{}},core:{}}),/Main moved/);
 assert.equal(calls.length,0);
})().catch(e=>{console.error(e);process.exit(1)});
'''
        subprocess.run(['node', '-e', script], cwd=ROOT, check=True)

    def test_workflow_boundaries(self):
        workflow=(ROOT/'.github/workflows/aec-upstream.yml').read_text()
        check=workflow.split('  check:',1)[1].split('  publish:',1)[0]
        writer=workflow.split('  publish:',1)[1]
        self.assertNotIn(': write',check)
        self.assertIn('--network none',check)
        self.assertIn('--read-only',check)
        self.assertIn('persist-credentials: false',check)
        self.assertNotIn('download-artifact',writer)
        self.assertNotIn('needs.check.outputs',writer)
        self.assertNotIn('GH_TOKEN',workflow)
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('permissions:\n  contents: read',ci)
        self.assertIn('persist-credentials: false',ci)
