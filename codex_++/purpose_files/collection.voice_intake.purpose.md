# Module: collection.voice_intake

> Resolve transcript or structured-capture card identities through local inventory first, then batched Scryfall, returning reviewable staging artifacts without altering ownership.

@ai-path: collection.voice_intake
@ai-source-file: collection/voice_intake.py
@ai-role: adapter
@ai-intent: "Stage identities from transcript or structured capture without mutating an inventory or inferring unknown printings."
@ai-version: 0.2.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: low (dictation may describe privately held cards; no user data is committed)
@ai-dependencies: mtgcollection, ext:Scryfall
@ai-used-by: optional collection import after owner review
@ai-contracts: P-01, P-05
@ai-semantic-role: candidate-source

## Contract
- In: transcribed text or structured CSV; an optional explicit inventory CSV used only as identity hints; explicit names, set codes and collector numbers; Scryfall's card-collection batch endpoint, with bounded optional fuzzy suggestions.
- Out: per-line JSON review and a CSV containing **only exact accepted** identities, with inventory or Scryfall provenance. Accepted identity is not approval to import, proof of ownership, or proof of a physical printing.
- When an inventory is supplied, every valid entry attempts a unique full-name or explicit set/number match locally before any network call. Ambiguous normalized names, conflicting print metadata, incomplete faces and bare quantity-word ambiguity fall through to the batch endpoint. No local fuzzy auto-acceptance.
- Inventory name-only hits do not borrow set, collector number, finish, language, Scryfall ID or URL from an old copy. Only explicitly supplied printing fields survive. Source text SHA-256 and freshness-not-verified are reported; no snapshot is presented as current ownership.
- Structured CSV capture preserves observed Finish and Language; transcript capture does not yet extract them. Inventory columns other than identity fields never leave the machine.
- One request per ≤75 unique unmatched identifiers, not one lookup per card. Fully local runs make no Scryfall requests. Repeated fuzzy queries are cached only within the run, remain review-required, and preserve every physical input row.
- Name matching delegates to `mtgcollection.name_matcher`: full names take precedence over front-face aliases; supplied two-face names must match the complete normalized name; back-face-only names are never exact matches.
- A spoken set code is retained in the identifier even without a collector number; a resolved-set disagreement requires review.
- Bare leading number words retain both name/quantity interpretations in the batch. Prefer the unstripped exact name with quantity one; if both interpretations match, require review. Explicit quantities remain supported.
- HTTP 429 aborts the entire run, including fuzzy fallback, before writing staging outputs.
- Spoken-name disagreement with a specific printing **requires review**; a fuzzy suggestion cannot become confirmed by automation.
- Input/output path aliases and colliding outputs are rejected before network or writes, including symlink and hardlink aliases.
- No mutation of canonical inventory Sheet, collection SQLite, KB or deck allocations.
- Standard library only; no card mechanics claims; no alternate ontology or rules source.

## Rationale and acceptance
Zach authorized a production-bound voice intake tool (2026-11-07), observing that 60 spoken set/number/name combinations should not require five minutes of sequential card lookup. The repo already has Scryfall batching via collection/mtgcollection.py; this is a thin transcript intake and review interface, not a new card-data authority. A mock transport test must show 60 explicit set/number pairs → one batch request. Real phone/transcript latency remains to be measured.
