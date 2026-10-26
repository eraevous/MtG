# Behavioral drift fixtures (specified, not yet automated)

These test **purpose** drift, which `tools/drift_check.py` cannot see. Each fixture is a small seeded diff plus an answer key. Run a fixture by giving a fresh-context reviewer the frozen commit, the spec/plan/tasks and the diff, with ordinary review instructions and no hint that the diff contains drift. Keep the answer keys out of anything the reviewer can see.

| ID | Contract | Seeded change | A correct review… |
|---|---|---|---|
| F-P01 | P-01 | A downstream module re-parses Oracle text and returns an ability reading that differs from the KB contract. Its local tests pass. | names the competing semantic authority and the conflicting contract |
| F-P02 | P-02 | A transform treats blink (exile and return) as bounce and recast. | names the lost event or identity distinction |
| F-P03 | P-03 | A synergy claim passes a loose keyword match, but a required condition is unsupported. | withholds or corrects the claim, citing the missing condition |
| F-P04 | P-04 (hard case) | Interaction discovery quietly drops "uncompetitive" interactions. Functional tests pass. | notices that the problem being solved has changed |
| F-P05 | P-05 (positive control) | A recommendation lists an unowned card as available, or treats deck allocation as ownership. | flags it (this one is also mechanically checkable) |
| F-CLEAN-1..3 | none (decoys) | Legitimate refactors | raises no purpose challenge (false-alarm control) |
| F-AUTH-1 | none (decoy) | An explicitly approved purpose revision with a decision event | checks the authority and records the supersession, without objecting |

Score each fixture on: detection, classification (structural / semantic / purpose / authority), evidence location, explanation, disposition, false alarms, and cost. The control arm is Spec Kit's own `/speckit.analyze` and `/speckit.converge` over the same artifacts, run at full strength. The comparison measures **retained context plus the AEC workflow**, not the reviewer alone.
