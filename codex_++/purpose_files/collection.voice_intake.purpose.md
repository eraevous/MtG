# Module: collection.voice_intake

> Resolve dictated card identities through Scryfall efficiently and conservatively, returning reviewable staging artifacts without altering ownership.

@ai-path: collection.voice_intake
@ai-source-file: collection/voice_intake.py
@ai-role: adapter
@ai-intent: "Identify card printings from transcribed speech-to-text without mutating an inventory."
@ai-version: 0.1.0
@schema-version: 0.3
@ai-generated: true
@ai-verified: false
@ai-risk-pii: low (dictation may describe privately held cards; no user data is committed)
@ai-dependencies: ext:Scryfall API
@ai-used-by: optional collection import after owner review
@ai-contracts: P-01, P-05
@ai-semantic-role: candidate-source

## Contract
- In: transcribed text; explicit names, set codes and collector numbers; Scryfall's card-collection batch endpoint, with bounded optional fuzzy suggestions.
- Out: source-linked per-line JSON review and a CSV containing **only exact accepted** Scryfall identities.
- One request per ≤75 unique exact identifiers, not one lookup per card.
- Spoken-name disagreement with a specific printing **requires review**; a fuzzy suggestion cannot become confirmed by automation.
- No mutation of canonical inventory Sheet, collection SQLite, KB or deck allocations.
- Standard library only; no card mechanics claims; no alternate ontology or rules source.

## Rationale and acceptance
Zach authorized a production-bound voice intake tool (2026-11-07), observing that 60 spoken set/number/name combinations should not require five minutes of sequential card lookup. The repo already has Scryfall batching via collection/mtgcollection.py; this is a thin transcript intake and review interface, not a new card-data authority. A mock transport test must show 60 explicit set/number pairs → one batch request. Real phone/transcript latency remains to be measured.
