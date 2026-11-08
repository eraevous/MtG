# Intent: repair voice-intake review boundaries, 2026-11-08

Repair of the four independently reproduced safety defects documented in PR #36's review (https://github.com/eraevous/MtG/pull/36#pullrequestreview-5814662395), against main 5ba076c403e62dc800c9efaf21646da11c19e993. This restores the existing conservative staging contract, not a new subsystem or inventory workflow. Prepared locally, then authorized by the owner for publication as a draft PR; no merge or inventory edits.

- Retain a spoken set without a collector number in the request and require review on any resolved-set disagreement.
- Preserve both interpretations of an implicit leading number word in the same batch. Prefer the complete exact name at quantity one; mark dual exact matches for review. When neither matches, fuzzy lookup uses the complete name and retains the alternate quantity in JSON. Explicit quantity phrases remain unchanged.
- Reuse the existing collection name matcher rather than defining competing face/name semantics.
- Propagate a distinct HTTP-429 exception through fuzzy lookup so the CLI aborts before writing outputs.

No ownership, allocation, KB, DIO or design-authority change. Synthetic fixtures only; live Scryfall identifier behavior and timing remain unverified.
