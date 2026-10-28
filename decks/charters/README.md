# Deck charters

One JSON file per deck, `decks/charters/<deck>.json`, holding what the *person* wants from that deck. The tools read it (`mtg context --deck <deck>`, `mtg check` for preference claims) and never write it. Preferences belong to the deck's owner, so Zach's tastes are not applied to Steph's decks or the other way round.

```json
{
  "deck": "Terra",
  "owner": "steph",
  "version": "1",
  "intent": "What the deck is meant to do, in the owner's words.",
  "likes": ["…"],
  "avoid": ["…"],
  "constraints": {"collection": "whose cards", "budget": null, "tutors": "allowed | limited | none"},
  "criteria_version": "decisions/criteria/<name>.md, if a criteria version applies"
}
```

Changing a charter is a design decision: append a `criteria_revision` event to `decisions/decision_events.jsonl`.
