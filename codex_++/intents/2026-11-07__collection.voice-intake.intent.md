# Intent: voice intake, 2026-11-07

**User authorization:** "The intake process for MTG should not be taking this long ... the speech to text has numbers, set symbols, and names ... a tool for voice intake that is also ... does it better would be lovely. This can go into production."

**Run slice:** a no-dependency CLI from speech-to-text to a 75-ID Scryfall batch, with conservative ambiguity review and CSV/JSON staging. Do not modify ownership or existing import procedures. No automatic merge; normal review remains.

**Five-question Drift/dissent check (new module):**
1. Risk: duplicating Scryfall logic / authority or assuming an uncertain spoken name represents an owned card.
2. Evidence: existing collection/mtgcollection.py already batches /cards/collection, while there is no transcript-to-review command; user reports five-minute intake bottleneck.
3. Alternative: add another command to existing collection module. Distinct parser/review contract and non-mutating boundary warrant a small separate adapter initially.
4. Failure if wrong: duplicate code and incorrectly identified physical cards. Naming identity is not proof of ownership.
5. Evidence required: one HTTP batch for 60 IDs in tests, fuzzy/mismatch gated, API 429 respectful, docs and review; time a real 60-card voice session before claiming performance improvement.

No new KB contract, semantics interpretation, allocation changes or governance change.
