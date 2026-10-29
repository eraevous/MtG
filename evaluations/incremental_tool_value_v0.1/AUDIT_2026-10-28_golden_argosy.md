# Appended audit: Golden Argosy (2026-10-28)

This note is appended; the scores and transcripts above are unchanged, as Kate asked.

- **Finding (Kate, confirmed by Claude):** both arms of H08 called Golden Argosy Brigid's only board wipe. Both copied `context --deck` → `roles.single_source_roles.wipe = "Golden Argosy"`. That value came from a false positive in the KB wipe regex: "exile each creature that crewed it" is a crew flicker, not a wipe.
- **For scoring:** both H08 answers carry a shared factual-error annotation for their deck-role assessment. The P/Q comparison is unaffected. The error counts against the shared evidence layer, not against `explore` or `hypothesis`.
- **Lesson:** two agents agreeing is not independent confirmation when both read the same wrong upstream datum.
- **Fix:** KB release r20261028 (kb patch 3) and `sole_detected_candidates` in place of `single_source_roles`. See decision D-0007 (proposed).
- **Future regression (Kate):** an agent should not protect a supposedly unique deck function because an unreviewed classifier found one provider. It should check the card first.
