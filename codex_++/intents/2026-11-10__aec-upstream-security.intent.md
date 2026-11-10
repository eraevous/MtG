# Isolate unreviewed upstream execution

Zach authorized preparing the MtG workflow security draft fix on 2026-11-10.
Preserve weekly/manual compatibility testing and pin proposal/failure reporting, while
preventing candidate Telosmith code from sharing a write token or writable filesystem
with publication. Planning resolves immutable revisions without executing candidate code.
Checks run in a read-only, network-disabled container on a separate read-only job.
Publication uses trusted-base code and reconstructs one pin file through GitHub's API;
it imports no candidate files, logs, patches, or outputs. The job conclusion is an
untrusted compatibility signal, never security approval. Proposed bumps are drafts.
CI dispatch remains available but CI now explicitly has only contents:read and no
persisted checkout credentials. No merge or settings change is authorized here.

Tradeoff: detailed candidate diagnostics remain in the linked run, not copied into
privileged-generated PR/issue text. No dependency was added to Python project code.
The workflow requires Docker on hosted Ubuntu and the official Python image. Containers
reduce exposure but do not establish proof against kernel/container escapes. Trusted
workflow/action supply chains remain trusted. Partial publication failures must be
inspected rather than overwriting an existing candidate branch automatically.
