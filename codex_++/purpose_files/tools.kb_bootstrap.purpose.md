# Module: tools.kb_bootstrap
> Reports whether this checkout can ground card work in the KB (kb_grounded / kb_unpinned / doctrine_only) and installs the pinned KB release databases into kb/, verified against kb/MANIFEST.sha256.

@ai-path: tools.kb_bootstrap
@ai-source-file: tools/kb_bootstrap.py
@ai-role: governance
@ai-intent: "Make a missing or mismatched KB visible and fixable, so agents stop falling back to their own reading of Oracle text without saying so."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: none
@ai-dependencies: none
@ai-contracts: P-01, P-03

### Inputs and outputs
| Direction | What |
|---|---|
| In | tools/kb_release.json (release, zip name and sha256, download URL, search dirs), kb/MANIFEST.sha256, a release zip (local, found, or downloaded) |
| Out | Status (text or JSON, exit 0/3/4 by level); kb/mtg_cards_v0.2.sqlite and kb/mtg_cards.sqlite |

### Risks, invariants and known gaps
- Never edits a database (CHARTER: rebuild, never hand-edit). It only replaces a file with the released one, after the hash matches.
- A zip with the pinned name must match the pinned sha256. Any other zip is accepted only if its databases match kb/MANIFEST.sha256.
- The download URL works only once the zip is published as a GitHub release asset (C-006). Until then it finds the zip in data/ or the Claude project files.
- Every KB release must update tools/kb_release.json. tests/test_kb_bootstrap.py checks it names the release kb/SOURCE_MANIFEST.json describes.
