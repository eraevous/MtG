"""The concept side of the bipartite registry, and the rules that propose frame -> concept edges.

Concept kinds are kept apart on purpose:
  operation        something an ability does (result.produces/... in a DIO §5 operation). Its event_intent is
                   the hook the operation *tries* to produce. Whether that event is confirmed (destroy -> dies)
                   is a rules question and is not asserted here.
  event            something a trigger observes (requirement_group class=trigger). Always a confirmed event.
  state_predicate  something that is true (requirement_group class=state/history, §5.6 comparison).
  cost             a cost component (§5.3) with its rules.cost.family and on_payment events.
  modifier         amplifier, duration, timing window, capacity, restriction, choice.
  process          sequencing between parts: if you do, then, otherwise, reflexive trigger, modes, instead.
  keyword_macro    a printed keyword that expands to one versioned rules definition (A7).

dio_status says how firm the DIO side is:
  ontology_defined   the hook/relation/domain exists in DIO v3.1.1 or Registry v0.1
  addendum_pending   depends on one of the A1-A7 decisions being ratified in the separate addendum work
  language_layer     a label used only by this registry to group frames; it points at existing DIO structure
                     and is not a new DIO primitive

Every edge is created with status 'proposed'. Only review.py promotes an edge.
"""
import re
from lexicon import KEYWORD_ABILITIES, KEYWORD_ACTIONS

CONCEPTS_VERSION = 'concepts-0.2.1'

OBJ = r'(?:<obj\.[a-z_]+>|<self>|<ref>)'
PL = r'<player\.[a-z_]+>'
ANY = r'(?:<obj\.[a-z_]+>|<self>|<ref>|<player\.[a-z_]+>)'


def P(s):
    return s.replace('ANY', ANY).replace('PL', PL)


# concept_id: (semantic_type, dio_ref, dio_status, label, event_intent)
C = {}


def concept(cid, st, dio, status, label, intent=None):
    C[cid] = (st, dio, status, label, intent)


# ---- events (observed, confirmed)
for cid, hook, status, label in [
    ('ev.battlefield.enter', 'battlefield.enter (+ type facets: creature/artifact/land.enters_battlefield)', 'ontology_defined', 'an object enters the battlefield'),
    ('ev.permanent.dies', 'permanent.dies', 'ontology_defined', 'a permanent dies'),
    ('ev.battlefield.leave', 'battlefield.leave', 'ontology_defined', 'a permanent leaves the battlefield'),
    ('ev.zone.change', 'zone.enter/zone.leave with source/destination qualifiers', 'ontology_defined', 'a card is put into a zone from a zone'),
    ('ev.attacker.declared', 'attacker.declared', 'ontology_defined', 'a creature attacks / a player attacks'),
    ('ev.blocker.declared', 'blocker.declared', 'ontology_defined', 'a creature blocks'),
    ('ev.creature.blocked', 'creature.blocked', 'ontology_defined', 'a creature becomes blocked'),
    ('ev.combat.damage', 'combat.damage', 'ontology_defined', 'combat damage is dealt'),
    ('ev.damage.deal', 'damage.deal', 'ontology_defined', 'damage is dealt (any kind)'),
    ('ev.spell.cast', 'spell.cast', 'ontology_defined', 'a spell is cast'),
    ('ev.ability.activated', 'ability.activated', 'ontology_defined', 'an ability is activated'),
    ('ev.life.gain', 'life.gain', 'ontology_defined', 'a player gains life'),
    ('ev.life.lose', 'life.lose', 'ontology_defined', 'a player loses life'),
    ('ev.card.draw', 'card.draw', 'ontology_defined', 'a player draws a card'),
    ('ev.card.discard', 'card.discard', 'ontology_defined', 'a player discards a card'),
    ('ev.card.mill', 'card.mill', 'ontology_defined', 'cards are milled'),
    ('ev.permanent.sacrifice', 'permanent.sacrifice (actor qualifier, A2)', 'ontology_defined', 'a player sacrifices a permanent'),
    ('ev.permanent.tap', 'permanent.tap', 'ontology_defined', 'a permanent becomes tapped'),
    ('ev.permanent.untap', 'permanent.untap', 'ontology_defined', 'a permanent becomes untapped'),
    ('ev.permanent.tapped_for_mana', 'permanent.tapped_for_mana (A1 facet)', 'addendum_pending', 'a permanent is tapped for mana'),
    ('ev.counter.put', 'counter.put', 'ontology_defined', 'counters are put on an object or player'),
    ('ev.counter.remove', 'counter.remove', 'ontology_defined', 'counters are removed'),
    ('ev.token.create', 'token.create', 'ontology_defined', 'a token is created'),
    ('ev.object.becomes_target', 'object.becomes_target', 'ontology_defined', 'an object becomes the target of a spell or ability'),
    ('ev.permanent.transform', 'permanent.transform', 'ontology_defined', 'a permanent transforms'),
    ('ev.permanent.turn_face_up', 'permanent.turn_face_up', 'ontology_defined', 'a permanent is turned face up'),
    ('ev.land.play', 'land.play', 'ontology_defined', 'a player plays a land'),
    ('ev.card.search', 'card.search', 'ontology_defined', 'a player searches a library'),
    ('ev.library.shuffle', 'library.shuffle', 'ontology_defined', 'a library is shuffled'),
    ('ev.spell.countered', 'spell.countered', 'ontology_defined', 'a spell is countered'),
    ('ev.permanent.attach', 'permanent.attach', 'ontology_defined', 'something becomes attached'),
    ('ev.control.change', 'control.change', 'ontology_defined', 'control of a permanent changes'),
    ('ev.turn.step.begin', 'turn.step.begin {which, whose_turn} (A6)', 'addendum_pending', 'beginning of a step'),
    ('ev.turn.phase.begin', 'turn.phase.begin {which, whose_turn} (A6)', 'addendum_pending', 'beginning of a phase'),
    ('ev.saga.chapter', 'counter.put [lore] + threshold.crossed (chapter ability)', 'ontology_defined', 'a Saga chapter triggers'),
    ('ev.card.exile', 'exile.enter', 'ontology_defined', 'a card is exiled'),
    ('ev.cast_self', 'spell.cast [subject: this]', 'ontology_defined', 'you cast this card'),
    ('ev.spell.copied', 'spell.copied (does not imply spell.cast)', 'ontology_defined', 'a spell is copied'),
    ('ev.card.return_to_hand', 'card.return_to_hand', 'ontology_defined', 'a card returns to hand'),
    ('ev.keyword_action', 'keyword action performed (scry/surveil/explore/... via macro, A7)', 'addendum_pending', 'a keyword action is performed'),
    ('ev.designation', 'designation.gain/lose (monarch, initiative, ring, day/night)', 'ontology_defined', 'a designation changes'),
    ('ev.combat.begin', 'combat.begin / combat.end', 'ontology_defined', 'combat begins or ends'),
]:
    concept(cid, 'event', 'requirement_group[class=trigger].alternatives: ' + hook, status, label)

# ---- operations (what an ability does). intent = the hook it attempts to produce
for cid, hook, rel, status, label in [
    ('op.card.draw', 'card.draw', 'PRODUCES', 'ontology_defined', 'draw cards'),
    ('op.card.discard', 'card.discard', 'PRODUCES', 'ontology_defined', 'discard cards'),
    ('op.card.mill', 'card.mill', 'PRODUCES', 'ontology_defined', 'mill cards'),
    ('op.card.search', 'card.search', 'PRODUCES', 'ontology_defined', 'search a library'),
    ('op.library.shuffle', 'library.shuffle', 'PRODUCES', 'ontology_defined', 'shuffle a library'),
    ('op.card.reveal', 'card.reveal', 'PRODUCES', 'ontology_defined', 'reveal cards'),
    ('op.card.look', 'card.look', 'PRODUCES', 'ontology_defined', 'look at hidden cards'),
    ('op.library.arrange', 'card.look + library order (put on top/bottom, rest in random order)', 'TRANSFORMS', 'ontology_defined', 'arrange library cards'),
    ('op.token.create', 'token.create (-> token.enters_battlefield)', 'PRODUCES', 'ontology_defined', 'create tokens'),
    ('op.life.gain', 'life.gain', 'PRODUCES', 'ontology_defined', 'gain life'),
    ('op.life.lose', 'life.lose', 'PRODUCES', 'ontology_defined', 'lose life'),
    ('op.mana.add', 'mana.add {amount, types, alternatives, restrictions, source} (A4)', 'PRODUCES', 'ontology_defined', 'add mana'),
    ('op.damage.deal', 'damage.deal (combat.damage / noncombat.damage)', 'PRODUCES', 'ontology_defined', 'deal damage'),
    ('op.counter.put', 'counter.put', 'PRODUCES', 'ontology_defined', 'put counters'),
    ('op.counter.remove', 'counter.remove', 'CONSUMES', 'ontology_defined', 'remove counters'),
    ('op.counter.move', 'counter.move', 'TRANSFORMS', 'ontology_defined', 'move counters'),
    ('op.permanent.destroy', 'permanent.destroy (intent; permanent.dies only if not replaced/indestructible)', 'PRODUCES', 'ontology_defined', 'destroy permanents'),
    ('op.permanent.sacrifice', 'permanent.sacrifice (actor = instructed player, A2)', 'PRODUCES', 'ontology_defined', 'sacrifice permanents (as an effect)'),
    ('op.zone.exile', 'exile.enter (+ battlefield.leave / graveyard.leave by source zone)', 'TRANSFORMS', 'ontology_defined', 'exile objects'),
    ('op.zone.return', 'card.return_to_hand / card.return_to_battlefield (by destination)', 'TRANSFORMS', 'ontology_defined', 'return objects to a zone'),
    ('op.zone.put', 'zone.enter/zone.leave (destination-qualified)', 'TRANSFORMS', 'ontology_defined', 'put objects into a zone'),
    ('op.spell.counter', 'spell.countered', 'PREVENTS', 'ontology_defined', 'counter spells or abilities'),
    ('op.permanent.tap', 'permanent.tap [as: effect]', 'PRODUCES', 'ontology_defined', 'tap permanents (as an effect)'),
    ('op.permanent.untap', 'permanent.untap', 'PRODUCES', 'ontology_defined', 'untap permanents'),
    ('op.pt.modify', 'characteristics.change [axis: power_toughness] (layer 7)', 'MODIFIES', 'ontology_defined', 'change power/toughness'),
    ('op.pt.set', 'characteristics.change [axis: power_toughness, operation: set] (CDA or layer 7b)', 'MODIFIES', 'ontology_defined', 'set power/toughness'),
    ('op.ability.grant', 'characteristics.change [axis: ability, operation: add]', 'MODIFIES', 'ontology_defined', 'grant abilities or keywords'),
    ('op.ability.remove', 'characteristics.change [axis: ability, operation: remove]', 'MODIFIES', 'ontology_defined', 'remove abilities'),
    ('op.type.change', 'characteristics.change [axis: type/subtype/color]', 'MODIFIES', 'ontology_defined', 'change types or colors'),
    ('op.control.change', 'control.change', 'TRANSFORMS', 'ontology_defined', 'gain control'),
    ('op.permanent.transform', 'permanent.transform', 'TRANSFORMS', 'ontology_defined', 'transform'),
    ('op.permanent.attach', 'permanent.attach', 'PRODUCES', 'ontology_defined', 'attach'),
    ('op.copy', 'spell.copied / object.becomes_copy / token copy', 'PRODUCES', 'ontology_defined', 'copy a spell, ability or permanent'),
    ('op.permission.cast', 'permission.cast (cost.method may be without_paying_mana_cost)', 'PERMITS', 'ontology_defined', 'cast a card (from a zone / for free)'),
    ('op.permission.play', 'permission.play / permission.cast from zone', 'PERMITS', 'ontology_defined', 'may play cards from a zone'),
    ('op.restrict', 'PREVENTS: cannot_attack/cannot_block/cannot_cast/... (rules_gate.prohibition_kind)', 'PREVENTS', 'ontology_defined', 'restrict an action'),
    ('op.evasion', "PREVENTS blocker.declared for the subject (can't be blocked [except by])", 'PREVENTS', 'ontology_defined', 'evasion'),
    ('op.untap.prevent', 'PREVENTS permanent.untap in untap step', 'PREVENTS', 'ontology_defined', "doesn't untap"),
    ('op.damage.prevent', 'PREVENTS damage.deal (prevention shield)', 'PREVENTS', 'ontology_defined', 'prevent damage'),
    ('op.regenerate', 'replacement shield: permanent.destroy -> tap + remove from combat', 'PREVENTS', 'ontology_defined', 'regenerate'),
    ('op.cost.modify', 'cost.modifiers {reductions, increases}', 'MODIFIES', 'ontology_defined', 'make spells/abilities cost more or less'),
    ('op.fight', 'damage.deal x2 (each deals damage equal to its power to the other)', 'PRODUCES', 'ontology_defined', 'fight'),
    ('op.retarget', 'choice: change targets of a spell/ability', 'MODIFIES', 'ontology_defined', 'choose new targets'),
    ('op.choice.value', 'choice {legal_set: color/type/name/number/player} remembered as state.chosen_value', 'PRODUCES', 'ontology_defined', 'choose a value'),
    ('op.turn.extra', 'extra turn / additional combat or phase (turn structure)', 'PRODUCES', 'language_layer', 'extra turns and phases'),
    ('op.game.win_lose', 'game result (win/lose the game)', 'PRODUCES', 'language_layer', 'win or lose the game'),
    ('op.entry.tapped', 'replacement: battlefield.enter -> enters tapped (entered tapped != became tapped)', 'PREVENTS', 'ontology_defined', 'enters tapped'),
    ('op.entry.with_counters', 'replacement: battlefield.enter with counters', 'MODIFIES', 'ontology_defined', 'enters with counters'),
    ('op.entry.choice', 'choice [choice_time: entry] (As ~ enters ...)', 'PRODUCES', 'ontology_defined', 'as-enters choice'),
    ('op.player.counter', 'counter.put [subject: player] (poison, energy, experience, rad ...)', 'PRODUCES', 'ontology_defined', 'give a player counters'),
    ('op.trigger.extra', 'MODIFIES trigger_multiplier', 'MODIFIES', 'ontology_defined', 'abilities trigger an additional time'),
    ('op.hand_size', 'MODIFIES maximum hand size', 'MODIFIES', 'language_layer', 'maximum hand size'),
    ('op.land.extra', 'PERMITS additional land.play', 'PERMITS', 'ontology_defined', 'play additional lands'),
    ('op.timing.permit', 'PERMITS timing exception (as though it had flash)', 'PERMITS', 'ontology_defined', 'cast at instant speed'),
    ('op.attack.require', 'requirement: attacks/blocks each combat if able', 'MODIFIES', 'language_layer', 'must attack/block'),
    ('op.phase.out', 'permanent.phase_out', 'PRODUCES', 'ontology_defined', 'phase out'),
    ('op.goad', 'goad (designation + attack requirement), keyword action', 'MODIFIES', 'addendum_pending', 'goad'),
    ('op.designation', "designation.gain (monarch, initiative, city's blessing, ring-bearer ...)", 'PRODUCES', 'ontology_defined', 'gain a designation'),
    ('op.exchange', 'exchange control / life totals / zones', 'TRANSFORMS', 'language_layer', 'exchange'),
    ('op.random', 'random selection / coin flip / die roll (grammar.random.selector)', 'PRODUCES', 'language_layer', 'random outcome'),
    ('op.pay', 'optional payment inside an effect (§5.3 cost paid on resolution)', 'CONSUMES', 'ontology_defined', 'pay a cost during resolution'),
    ('op.mana.retain', 'mana pool persistence / spend-as-though', 'MODIFIES', 'language_layer', 'mana rules modification'),
]:
    concept(cid, 'operation', 'result.' + rel.lower() + ': ' + hook, status, label, intent=hook.split(' ')[0])

KWA_USED = ('scry', 'surveil', 'investigate', 'proliferate', 'populate', 'explore', 'connive', 'amass',
            'venture into the dungeon', 'learn', 'manifest', 'manifest dread', 'incubate', 'discover', 'forage',
            'endure', 'earthbend', 'waterbend', 'airbend', 'blight', 'suspect', 'cloak', 'collect evidence',
            'adapt', 'bolster', 'support', 'detain', 'monstrosity', 'time travel', 'plot', 'seek', 'heal',
            'conjure', 'exert', 'behold', 'clash', 'vote', 'open an attraction', 'assemble', 'fateseal',
            'harness', 'double', 'triple', 'convert', 'meld', 'set in motion', 'abandon', 'planeswalk',
            'face a dilemma', 'roll to visit your attractions', 'assimilate', 'incorporate')
for ka in KEYWORD_ACTIONS:
    if ka in KWA_USED:
        concept('kwa.' + ka.replace(' ', '_'), 'keyword_macro',
                'keyword action -> versioned rules expansion (A7); e.g. scry = card.look + library order',
                'addendum_pending', 'keyword action: ' + ka)
for kw in KEYWORD_ABILITIES:
    concept('kw.' + kw.replace(' ', '_'), 'keyword_macro', 'keyword ability -> versioned rules expansion (A7)',
            'addendum_pending', 'keyword ability: ' + kw)
concept('kw.landwalk', 'keyword_macro', 'keyword ability -> versioned rules expansion (A7)', 'addendum_pending', 'landwalk')
concept('kw.landcycling', 'keyword_macro', 'keyword ability -> versioned rules expansion (A7)', 'addendum_pending', 'typecycling')

# ---- costs
for cid, fam, onpay, status, label in [
    ('cost.mana', 'mana', 'mana.spend', 'ontology_defined', 'mana cost (typed pips, A4)'),
    ('cost.tap_self', 'tap', 'permanent.tap [subject: this]', 'ontology_defined', '{T}'),
    ('cost.untap_self', 'untap', 'permanent.untap [subject: this]', 'ontology_defined', '{Q}'),
    ('cost.tap_other', 'tap', 'permanent.tap [subject: other, must_come_from_other_unit]', 'ontology_defined', 'tap untapped permanents you control'),
    ('cost.sacrifice_self', 'sacrifice', 'permanent.sacrifice [subject: this] -> permanent.dies if creature', 'ontology_defined', 'sacrifice this'),
    ('cost.sacrifice_other', 'sacrifice', 'permanent.sacrifice [subject: other]', 'ontology_defined', 'sacrifice another permanent'),
    ('cost.discard', 'discard', 'card.discard', 'ontology_defined', 'discard'),
    ('cost.life', 'pay_life', 'life.pay', 'ontology_defined', 'pay life'),
    ('cost.exile', 'exile', 'exile.enter', 'ontology_defined', 'exile cards/permanents as a cost'),
    ('cost.counter_remove', 'remove_counter (A5)', 'counter.remove', 'addendum_pending', 'remove counters'),
    ('cost.loyalty', 'loyalty (A5)', 'counter.put/remove [loyalty]', 'addendum_pending', 'loyalty ability cost'),
    ('cost.energy', 'energy (A5)', 'counter.remove [energy, player]', 'addendum_pending', 'pay energy'),
    ('cost.return_to_hand', 'return_to_hand', 'card.return_to_hand', 'ontology_defined', 'return a permanent to hand'),
    ('cost.reveal', 'reveal', 'card.reveal', 'ontology_defined', 'reveal a card'),
    ('cost.keyword', 'keyword cost (collect evidence, blight, behold, exert, forage, waterbend ... A5/A7)', 'per macro', 'addendum_pending', 'keyword-defined cost'),
    ('cost.mill', 'mill', 'card.mill', 'language_layer', 'mill as a cost'),
    ('cost.additional', 'cost.additional (still owed under any method)', '-', 'ontology_defined', 'additional cost header'),
]:
    concept(cid, 'cost', 'cost.components[family=' + fam + ']; on_payment: ' + onpay, status, label)

# ---- state predicates
for cid, dio, status, label in [
    ('st.control', 'state: you control <filter> [comparison count >= n] (§5.6)', 'ontology_defined', 'you control something / n or more'),
    ('st.zone_count', 'state: count of <filter> in <zone> compared to n (§5.6)', 'ontology_defined', 'n or more cards in a zone'),
    ('st.object_status', 'state: object is tapped/attacking/blocking/equipped/... (§4.1 status qualifiers)', 'ontology_defined', 'object status'),
    ('st.object_characteristic', 'state: object has type/color/power/mana value ... (§5.6)', 'ontology_defined', 'object characteristic test'),
    ('st.history', 'historical_condition: event happened this turn/game (died, attacked, gained life, cast ...)', 'ontology_defined', 'something happened earlier'),
    ('st.cast_option', 'historical_condition: cost option paid (kicked, bargained, gift promised, mana spent ...)', 'ontology_defined', 'how the spell was cast'),
    ('st.comparison', 'comparison between players/sets (more than, greatest, highest ...) §5.6', 'ontology_defined', 'comparison'),
    ('st.designation', "state: designation held (monarch, initiative, day/night, city's blessing)", 'ontology_defined', 'designation held'),
    ('st.random_outcome', 'result of a random selector (won the flip, rolled n)', 'language_layer', 'random outcome'),
    ('st.target_check', 'information: what the spell/ability targets', 'ontology_defined', 'target test'),
    ('st.player_resource', 'state: life total / hand size / counters on player compared to n', 'ontology_defined', 'player resource level'),
    ('st.if_able', 'requirement modality: if able', 'language_layer', 'if able'),
    ('st.unless_payment', 'choice [opponent_agency]: unless <player> pays <cost>', 'ontology_defined', 'unless someone pays'),
    ('st.zone_location', 'state: object is in a zone', 'ontology_defined', 'object location'),
    ('st.did_action', "process outcome: if <player> does/doesn't", 'ontology_defined', 'if a player did it'),
]:
    concept(cid, 'state_predicate', 'requirement_group[class=state|history]: ' + dio, status, label)

# ---- modifiers
for cid, dio, status, label in [
    ('amp.count', 'amplifier: for each / equal to the number of <filter> (MODIFIES quantity)', 'ontology_defined', 'scales with a count'),
    ('amp.stat', 'amplifier: equal to power/toughness/mana value of a reference (§5.6)', 'ontology_defined', 'scales with a stat'),
    ('amp.counters', 'amplifier: for each counter on <object>', 'ontology_defined', 'scales with counters'),
    ('amp.player', 'amplifier: per player / life gained / devotion / damage dealt', 'ontology_defined', 'scales with a player quantity'),
    ('amp.other', 'amplifier: other measured quantity', 'ontology_defined', 'scales with another quantity'),
    ('time.until_eot', 'timing.expiry: until end of turn', 'ontology_defined', 'until end of turn'),
    ('time.this_turn', 'timing.expiry: this turn', 'ontology_defined', 'this turn'),
    ('time.until_next_turn', 'timing.expiry: until your next turn', 'ontology_defined', 'until your next turn'),
    ('time.while', 'timing.expiry: for as long as <state> / until <object> leaves (linked)', 'ontology_defined', 'for as long as'),
    ('time.window', 'timing.window {phase, step, turn_scope}', 'ontology_defined', 'timing window'),
    ('time.delayed_trigger', 'timing.delay: delayed trigger created now', 'ontology_defined', 'delayed trigger'),
    ('time.sorcery_speed', 'timing.speed = sorcery', 'ontology_defined', 'activate only as a sorcery'),
    ('time.turn_scope', 'timing.turn_scope = your_turn / step window', 'ontology_defined', 'only during your turn/step'),
    ('cap.once_each_turn', 'capacity {uses: 1, renews: each_turn}', 'ontology_defined', 'once each turn'),
    ('cap.limited', 'capacity {uses: n, renews: never/each_turn}', 'ontology_defined', 'limited uses'),
    ('gate.activate_if', 'requirement_group[class=state, checkpoint=initiation] on activation', 'ontology_defined', 'activate only if'),
    ('rest.uncounterable', 'PREVENTS spell.countered for this spell', 'ontology_defined', "can't be countered"),
    ('rest.mana_spend', 'mana_restrictions on produced mana (A4)', 'addendum_pending', 'spend this mana only'),
    ('rest.no_regen', 'PREVENTS regeneration replacement', 'ontology_defined', "can't be regenerated"),
    ('rest.still_type', "characteristic retained (it's still a land)", 'ontology_defined', "it's still a <type>"),
    ('rest.activator', 'rules_gate.initiation_authority (any player may activate)', 'ontology_defined', 'who may activate'),
    ('choice.modal', 'choice {legal_set: modes, cardinality} + branch_outputs', 'ontology_defined', 'choose one/two/...'),
]:
    concept(cid, 'modifier', dio, status, label)

for cid, dio, status, label in [
    ('proc.if_you_do', 'process: branch conditioned on the previous optional action/payment', 'ontology_defined', 'if you do / if they do'),
    ('proc.if_not', 'process: branch when the previous action did not happen', 'ontology_defined', "if you don't / otherwise"),
    ('proc.then', 'process: ordered step', 'ontology_defined', 'then'),
    ('proc.reflexive', 'process: reflexive trigger (when you do)', 'ontology_defined', 'when you do'),
    ('proc.instead', 'process/replacement: branch substitutes the previous result (instead)', 'ontology_defined', 'instead'),
    ('proc.replacement', 'operation[kind=replacement].result.rewrites: proposed -> resulting event', 'ontology_defined', 'replacement effect (if ... would ..., instead)'),
]:
    concept(cid, 'process', dio, status, label)
concept('kw.start_your_engines', 'keyword_macro', 'keyword ability -> versioned rules expansion (A7): speed designation', 'addendum_pending', 'start your engines!')
concept('kwa.prepare', 'keyword_macro', 'keyword action -> versioned rules expansion (A7): prepared designation / prepare face', 'addendum_pending', 'prepared')
concept('st.counter_threshold', 'state_predicate', 'requirement_group[class=state]: threshold.reached {object, counter_kind, n} (station striations, level bands)', 'ontology_defined', 'has N or more counters')
concept('choice.target', 'modifier', 'choice {choice_time: initiation, legal_set: targets} + requirement_group[class=eligibility] (§5.5)', 'ontology_defined', 'choose a target')
concept('struct.level', 'structure', 'leveler/class level band (state.kind=counter thresholds)', 'language_layer', 'level band')

# ------------------------------------------------------------------ rules
# R(rule_id, roles, pattern, (concept, relation), ...)
E = ('effect', 'static')
T = ('trigger_event',)
RULES = []


def R(rid, roles, pat, *edges):
    RULES.append((rid, roles, re.compile(P(pat)), edges))


Z = r'<zone>'
O = r'<obj\.[a-z_]+>'
PP = r'<player\.[a-z_]+_poss>'

# events --------------------------------------------------------------
TW = r'(?:when|whenever|at) '
R('ev.enter', T, TW + r'(?:ANY(?: or ANY)* )?enter(?: the battlefield)?(?: under ' + PP + r' control)?(?: tapped| attacking)?(?: from ' + Z + r')?', ('ev.battlefield.enter', 'OBSERVES'))
R('ev.die', T, TW + r'(?:ANY(?: or ANY)* )?die', ('ev.permanent.dies', 'OBSERVES'))
R('ev.leave', T, TW + r'(?:ANY(?: or ANY)* )?leave the battlefield', ('ev.battlefield.leave', 'OBSERVES'))
R('ev.zone', T, TW + r'(?:ANY(?: or ANY)* )?(?:is|are) put into ' + Z + r'(?: from ' + Z + r')?(?: from anywhere)?', ('ev.zone.change', 'OBSERVES'))
R('ev.attack', T, TW + r'(?:ANY(?: or ANY)* )?attack(?: ANY| alone)?(?: while (?:saddled|<self> is (?:saddled|tapped)))?', ('ev.attacker.declared', 'OBSERVES'))
R('ev.block', T, TW + r'(?:ANY )?block(?: ANY)?', ('ev.blocker.declared', 'OBSERVES'))
R('ev.blocked', T, TW + r'(?:ANY )?become blocked(?: by ANY)?', ('ev.creature.blocked', 'OBSERVES'))
R('ev.combat_damage', T, TW + r'(?:ANY(?: or ANY)* )?deal combat damage(?: to ANY(?: or ANY)*)?', ('ev.combat.damage', 'OBSERVES'))
R('ev.damage', T, TW + r'(?:ANY(?: or ANY)* )?(?:deal (?:noncombat )?damage(?: to ANY(?: or ANY)*)?|is dealt damage|(?:is|are) dealt (?:combat |noncombat )?damage)', ('ev.damage.deal', 'OBSERVES'))
R('ev.cast', T, TW + r'(?:ANY )?cast (?:a |an )?(?:<color> )?ANY(?: (?:or|and) (?:<color> )?ANY)*(?: (?:that targets ANY|with mana value <n> or greater|from ' + Z + r'|during ' + PP + r' turn|that has <kw>))*', ('ev.spell.cast', 'OBSERVES'))
R('ev.cast_nth', T, TW + r'(?:ANY )?cast (?:' + PP + r'|their) (?:first|second|third|next) ' + O + r'(?: (?:each|this|during (?:each|' + PP + r')) (?:turn|opponent\'s turn))?', ('ev.spell.cast', 'OBSERVES'))
R('ev.activate', T, TW + r'(?:ANY )?activate (?:ANY|an ability)(?: of ANY)?(?: that isn\'t a mana ability)?', ('ev.ability.activated', 'OBSERVES'))
R('ev.lifegain', T, TW + r'(?:ANY )?gain life(?: for the first time each turn)?', ('ev.life.gain', 'OBSERVES'))
R('ev.lifeloss', T, TW + r'(?:ANY )?lose life(?: for the first time each turn| during ' + PP + r' turn)?', ('ev.life.lose', 'OBSERVES'))
R('ev.draw', T, TW + r'(?:ANY )?draw (?:(?:' + PP + r'|<ref>|their) (?:first|second|third) ' + O + r'|ANY)(?: each turn)?(?: except the first one <player\.you> draw in each of ' + PP + r' draw steps)?', ('ev.card.draw', 'OBSERVES'))
R('ev.discard', T, TW + r'(?:ANY )?discard ANY', ('ev.card.discard', 'OBSERVES'))
R('ev.mill', T, TW + r'(?:ANY )?mill ANY', ('ev.card.mill', 'OBSERVES'))
R('ev.sacrifice', T, TW + r'(?:ANY )?sacrifice ANY', ('ev.permanent.sacrifice', 'OBSERVES'))
R('ev.tapped', T, TW + r'(?:ANY )?become tapped', ('ev.permanent.tap', 'OBSERVES'))
R('ev.untapped', T, TW + r'(?:ANY )?become untapped|' + TW + r'(?:ANY )?untap ANY(?: during ' + PP + r' untap step)?', ('ev.permanent.untap', 'OBSERVES'))
R('ev.tap_for_mana', T, TW + r'(?:ANY )?tap ANY for mana', ('ev.permanent.tapped_for_mana', 'OBSERVES'))
R('ev.tap', T, TW + r'(?:PL )?tap (?:an untapped )?ANY', ('ev.permanent.tap', 'OBSERVES'))
R('ev.counters', T, TW + r'(?:<n> or more |one or more )?<counter> (?:is|are) put on ANY|' + TW + r'(?:ANY )?put (?:<n> or more |one or more )?<counter> on ANY', ('ev.counter.put', 'OBSERVES'))
R('ev.counters_removed', T, TW + r'(?:<n> or more |one or more |the last )?<counter> (?:is|are) removed from ANY', ('ev.counter.remove', 'OBSERVES'))
R('ev.token', T, TW + r'(?:ANY )?create ANY', ('ev.token.create', 'OBSERVES'))
R('ev.target', T, TW + r'(?:ANY )?become the target of (?:ANY|a spell or ability)(?: <player\.[a-z_]+> control| an opponent control)?(?: for the first time each turn)?', ('ev.object.becomes_target', 'OBSERVES'))
R('ev.transform', T, TW + r'(?:ANY )?transform(?: into ANY)?', ('ev.permanent.transform', 'OBSERVES'))
R('ev.faceup', T, TW + r'(?:ANY )?(?:is|are) turned (?:' + O + r'|face) up', ('ev.permanent.turn_face_up', 'OBSERVES'))
R('ev.landplay', T, TW + r'(?:PL )?play ANY', ('ev.land.play', 'OBSERVES'))
R('ev.search', T, TW + r'(?:PL )?search ' + Z, ('ev.card.search', 'OBSERVES'))
R('ev.shuffle', T, TW + r'(?:PL )?shuffle ' + Z, ('ev.library.shuffle', 'OBSERVES'))
R('ev.countered', T, TW + r'(?:ANY )?(?:is )?countered', ('ev.spell.countered', 'OBSERVES'))
R('ev.attach', T, TW + r'(?:ANY )?become attached to ANY|' + TW + r'(?:ANY )?attach ANY|' + TW + r'(?:ANY )?become equipped', ('ev.permanent.attach', 'OBSERVES'))
R('ev.control', T, TW + r'(?:PL )?gain control of ANY', ('ev.control.change', 'OBSERVES'))
R('ev.exiled', T, TW + r'(?:ANY )?(?:is|are) exiled|' + TW + r'(?:PL )?exile ANY', ('ev.card.exile', 'OBSERVES'))
R('ev.returned', T, TW + r'(?:ANY )?(?:is|are) returned to ' + Z + r'|' + TW + r'(?:PL )?return ANY to ' + Z, ('ev.card.return_to_hand', 'OBSERVES'))
R('ev.copy', T, TW + r'(?:ANY )?copy (?:a |an )?(?:<color> )?ANY', ('ev.spell.copied', 'OBSERVES'))
R('ev.cast_self', T, TW + r'(?:PL )?cast <self>', ('ev.cast_self', 'OBSERVES'))
R('ev.step', T, r'at the beginning of (?:the |each |' + PP + r' |each ' + PP + r' |that turn\'s |the next |<player\.[a-z_]+> |each of ' + PP + r' )?(?:upkeep|draw step|end step|combat(?: on (?:' + PP + r'|each|each opponent\'s|each ' + PP + r') turn)?|end of combat|declare blockers step|turn|cleanup step)(?: of each turn)?(?: on ' + PP + r' turn)?', ('ev.turn.step.begin', 'OBSERVES'))
R('ev.phase', T, r'at the beginning of (?:the |each |' + PP + r' |each ' + PP + r' |that turn\'s |the next |each of ' + PP + r' )?(?:(?:first |second |precombat |postcombat |next )?main phase|second main phase)(?: of each turn)?(?: on ' + PP + r' turn)?', ('ev.turn.phase.begin', 'OBSERVES'))
R('ev.end_of_combat', T, r'at end of combat', ('ev.combat.begin', 'OBSERVES'))
R('ev.chapter', T, r'chapter <n>', ('ev.saga.chapter', 'OBSERVES'))
R('ev.kwaction', T, TW + r'(?:ANY )?(?:scry|surveil|explore|investigate|connive|proliferate|venture into the dungeon|cycle|exert|discover|forage|expend <n>|commit a crime|crew|saddle|station|airbend|earthbend|waterbend|firebend|plot|manifest|cloak|clash|vote|cycle or discard ANY)(?: ANY| <n>)?', ('ev.keyword_action', 'OBSERVES'))
R('ev.designation', T, TW + r'(?:ANY )?become (?:the monarch|day|night|the ring-bearer)|' + TW + r'(?:PL )?(?:take the initiative|tempt|complete a dungeon)|' + TW + r'it becomes (?:day|night)', ('ev.designation', 'OBSERVES'))
R('ev.combat_begin', T, r'when(?:ever)? combat begins?', ('ev.combat.begin', 'OBSERVES'))

# operations -----------------------------------------------------------
S = r'(?:ANY )?'
R('op.draw', E, S + r'draw (?:ANY|<n> ' + O + r'|<n> additional ' + O + r'|an additional ' + O + r'|that many ' + O + r'|cards equal to [^,]+|up to <n> ' + O + r')', ('op.card.draw', 'PRODUCES'))
R('op.discard', E, S + r'discard (?:ANY|' + PP + r' hand|' + Z + r'|<n> ' + O + r'|that many ' + O + r')(?: at random)?', ('op.card.discard', 'PRODUCES'))
R('op.mill', E, S + r'mill (?:ANY|<n> ' + O + r'|that many ' + O + r')', ('op.card.mill', 'PRODUCES'))
R('op.search', E, S + r'search ' + Z + r'(?: and(?:/or)? ' + Z + r')? for (?:ANY|up to <n> ' + O + r')(?: with different names)?', ('op.card.search', 'PRODUCES'))
R('op.shuffle', E, S + r'shuffle(?: ' + Z + r'| ANY into ' + Z + r'| ANY and ANY into ' + Z + r')?', ('op.library.shuffle', 'PRODUCES'))
R('op.reveal', E, S + r'reveal (?:<obj\.[a-z_]+> of ' + Z + r'|ANY from ' + Z + r'|' + Z + r'|<obj\.bare> from ' + Z + r' until ANY reveal ANY|ANY|' + PP + r' hand|the top ' + O + r' of ' + Z + r'|cards from the top of ' + Z + r' until [^,]+)', ('op.card.reveal', 'PRODUCES'))
R('op.look', E, S + r'look at (?:<obj\.[a-z_]+> of ' + Z + r'(?: any time)?|ANY|the top ' + O + r' of ' + Z + r'|' + PP + r' hand)', ('op.card.look', 'PRODUCES'))
R('op.arrange', E, r'put (?:the rest|ANY|<n> of <ref>|the other) (?:on|into) ' + Z + r' in (?:a random|any) order|put (?:the rest|the other) (?:on|into) ' + Z + r'|put ANY back in any order', ('op.library.arrange', 'TRANSFORMS'))
R('op.token', E, S + r'create (?:(?:a|<n>) [a-z\'-]+ <obj\.bare>|<obj\.q> (?:named [a-z\' ,-]+|of <obj\.[a-z_]+>)|ANY|<n> ' + O + r'|that many ' + O + r'|a number of ' + O + r')(?: with <granted_ability>| with <kw>(?: and <kw>)*| that(?:\'s| is| are)(?: tapped and)? attacking(?: that player| that opponent| <player\.[a-z_]+>)?| tapped(?: and attacking)?| that\'s a copy of ANY| that are copies of ANY)*(?:, except [^,]+)?', ('op.token.create', 'PRODUCES'))
R('op.lifegain', E, S + r'gain (?:<n> |that much |x )?life', ('op.life.gain', 'PRODUCES'))
R('op.lifeloss', E, S + r'lose (?:<n> |that much |half (?:their|' + PP + r') )?life', ('op.life.lose', 'PRODUCES'))
R('op.mana', E, S + r'add (?:<mana>(?:(?: ,)? (?:or|and/or) <mana>| , <mana>)*|<n> mana of any (?:one |<n> )?(?:color|type)(?: in ' + O + r' \'s color identity)?(?: that a land an opponent controls could produce| among [^,]+)?|<n> mana in any combination of (?:colors|<mana>(?: and/or <mana>)*)|an amount of <mana> equal to [^,]+|<mana> for each [^,]+|<n> mana of the chosen color|that much <mana>|<n> <mana>|<n> mana of (?:any|one) color)', ('op.mana.add', 'PRODUCES'))
R('op.damage', E, S + r'deal (?:<n> |that much |x |excess )?damage(?: to (?:ANY|each of up to <n> targets|any number of targets|<n> targets|each of <n> targets)(?:(?:,| and| or|, and) ANY)*)?(?: divided as <player\.you> choose among (?:any number of|one, two, or three) targets)?', ('op.damage.deal', 'PRODUCES'))
R('op.pt', E, S + r'get <pt>', ('op.pt.modify', 'MODIFIES'))
R('op.pt_set', E, r"(?:ANY 's )?(?:base )?power(?: and toughness)? (?:is|are)(?: each)?(?: <pt>| <n>)?|(?:ANY )?have base power and toughness <pt>|ANY 's toughness is", ('op.pt.set', 'MODIFIES'))
R('op.kwgrant', E, S + r'(?:gain|have)(?: <kw>)+(?:(?:,| and|, and| or) <kw>)*', ('op.ability.grant', 'MODIFIES'))
R('op.grant_ability', E, S + r'(?:gain|have) <granted_ability>(?: and <granted_ability>)*', ('op.ability.grant', 'MODIFIES'))
R('op.pt_kw', E, S + r'get <pt> and (?:gain|have) (?:<kw>|<granted_ability>)(?:(?:,| and|, and) (?:<kw>|<granted_ability>))*', ('op.pt.modify', 'MODIFIES'), ('op.ability.grant', 'MODIFIES'))
R('op.lose_abilities', E, S + r'lose (?:all abilities|<kw>(?: and <kw>)*)', ('op.ability.remove', 'MODIFIES'))
R('op.counter_put', E, S + r'put (?:<n> |a number of |that many |x )?(?:additional )?<counter> on (?:ANY|each of up to <n> target ' + O + r'|each of ANY)(?:(?:,| and| or) ANY)*', ('op.counter.put', 'PRODUCES'))
R('op.player_counter', E, S + r'get (?:<n> |that many )?(?:<counter>|<energy>)', ('op.player.counter', 'PRODUCES'))
R('op.counter_remove', E, S + r'remove (?:<n> |all |a |up to <n> |any number of )?<counter> from ANY', ('op.counter.remove', 'CONSUMES'))
R('op.counter_move', E, S + r'move (?:<n> |all |any number of )?<counter> from ANY onto ANY', ('op.counter.move', 'TRANSFORMS'))
R('op.destroy', E, S + r'destroy (?:ANY|up to <n> target ' + O + r')(?:(?:,| and| or|, and) ANY)*', ('op.permanent.destroy', 'PRODUCES'))
R('op.sacrifice', E, S + r'sacrifice (?:ANY|<n> ' + O + r'|that many ' + O + r'|half the ' + O + r' (?:they|<player\.[a-z_]+>) control)(?: of (?:their|<ref>|' + PP + r') choice)?(?:(?:,| and| or) ANY)*', ('op.permanent.sacrifice', 'PRODUCES'))
R('op.exile', E, S + r'exile (?:<obj\.[a-z_]+> of ' + Z + r'|<obj\.bare> from ' + Z + r' until ANY exile ANY|ANY|' + Z + r'|the top ' + O + r' of ' + Z + r'|up to <n> target ' + O + r')(?:(?:,| and| or) ANY)*(?: from ' + Z + r')?(?: (?:face down|with <n> <counter> on <ref>))?(?: until ANY leave the battlefield)?', ('op.zone.exile', 'TRANSFORMS'))
R('op.return', E, S + r'return (?:ANY|up to <n> target ' + O + r'|<n> ' + O + r')(?:(?: and| or|,) ANY)*(?: (?:exiled|milled) <ref>)?(?: from ' + Z + r')? to ' + Z + r'(?: (?:tapped|under ' + PP + r' control|attached to ANY|with (?:<n> )?<counter> on <ref>|transformed|face down))*', ('op.zone.return', 'TRANSFORMS'))
R('op.put_zone', E, S + r'put (?:ANY|<n>|the rest|<n> of <ref>|the other|up to <n> ' + O + r')(?: from among <ref>)?(?: from ' + Z + r')? (?:into|onto|on) ' + Z + r'(?: (?:tapped|under ' + PP + r' control|attacking|face down|transformed|with <n> <counter> on <ref>|second from the top|third from the top))*(?: and the (?:other|rest) (?:into|on) ' + Z + r'(?: in a random order)?)?', ('op.zone.put', 'TRANSFORMS'))
R('op.counterspell', E, S + r'counter (?:ANY|up to <n> target ' + O + r')', ('op.spell.counter', 'PREVENTS'))
R('op.tap_or_untap', E, S + r'tap or untap (?:ANY|up to <n> target ' + O + r')', ('op.permanent.tap', 'PRODUCES'), ('op.permanent.untap', 'PRODUCES'))
R('op.tap', E, S + r'tap (?:ANY|up to <n> target ' + O + r'|<n> target ' + O + r')(?:(?:,| and| or) ANY)*', ('op.permanent.tap', 'PRODUCES'))
R('op.untap', E, S + r'untap (?:ANY|up to <n> ' + O + r'|<n> target ' + O + r')(?:(?:,| and| or) ANY)*', ('op.permanent.untap', 'PRODUCES'))
R('op.control', E, S + r'(?:gain|exchange) control of ANY(?: and ANY)?', ('op.control.change', 'TRANSFORMS'))
R('op.transform', E, S + r'transform (?:ANY|up to <n> target ' + O + r')|turn ANY face (?:up|down)', ('op.permanent.transform', 'TRANSFORMS'))
R('op.attach', E, S + r'attach (?:ANY )?to ANY|' + S + r'attach ANY to ANY|unattach ANY', ('op.permanent.attach', 'PRODUCES'))
R('op.copy', E, S + r'copy ANY(?: <n> times)?|create a copy of ANY|choose new targets for the cop(?:y|ies)|ANY become a copy of ANY(?:, except [^,]+)?|(?:ANY )?enter as a copy of (?:ANY|any ' + O + r' on the battlefield)', ('op.copy', 'PRODUCES'))
R('op.cast_free', E, S + r'cast (?:ANY|' + O + r' from among <ref>)(?: from ' + Z + r')?(?: without paying (?:its|their|<ref>) mana costs?)?', ('op.permission.cast', 'PERMITS'))
# "play" also covers lands (CR 305.1), so it is a play permission, not a cast permission
R('op.play_free', E, S + r'play ANY(?: from ' + Z + r')?(?: without paying (?:its|<ref>) mana cost)?', ('op.permission.play', 'PERMITS'))
R('op.play_zone', E, S + r'(?:play|cast) (?:ANY|lands|' + O + r')(?: and cast ' + O + r')? from (?:' + Z + r'|among the exiled cards)', ('op.permission.play', 'PERMITS'))
R('op.restrict', E, r"(?:ANY )?(?:can't|cannot|don't|doesn't) (?:attack or block|block or be blocked|attack|block|be the target|be countered|cast|activate|gain life|be enchanted|search|draw|transform|untap|lose life|be sacrificed|be destroyed|play|be regenerated)(?: (?:ANY|you|alone|more than one " + O + r" each turn|during " + PP + r" turn|unless [^,]+|of " + O + r"|abilities|except by <n> or more " + O + r"|by ANY|spells|" + O + r" of ANY|cards))*(?: or ANY)?", ('op.restrict', 'PREVENTS'))
R('op.evasion', E, r"(?:ANY )?can't be blocked(?: (?:except by (?:ANY|<n> or more " + O + r")|by (?:ANY|more than one " + O + r")))*|(?:ANY )?can block only ANY", ('op.evasion', 'PREVENTS'))
R('op.no_untap', E, r"(?:ANY )?(?:doesn't|don't) untap during (?:" + PP + r"|its controller's|their controllers') (?:next )?untap step", ('op.untap.prevent', 'PREVENTS'))
R('op.prevent', E, r'prevent (?:all |the next <n> |<n> of that |that |all but <n> of that )?(?:combat )?damage(?: that would be dealt (?:to|by) ANY)?(?: dealt (?:to|by) ANY)?', ('op.damage.prevent', 'PREVENTS'))
R('op.regenerate', E, r'regenerate ANY', ('op.regenerate', 'PREVENTS'))
R('op.cost', E, r'(?:ANY )?cost (?:<mana>|<n>|x) (?:less|more)(?: to (?:cast|activate|equip))?|activated abilities of ANY cost <mana> (?:less|more) to activate', ('op.cost.modify', 'MODIFIES'))
R('op.fight', E, S + r'fight (?:ANY|each other)|ANY and ANY fight', ('op.fight', 'PRODUCES'))
R('op.retarget', E, r'(?:ANY )?(?:choose new targets for ANY|change the target of ANY)(?: to ANY)?', ('op.retarget', 'MODIFIES'))
R('st.counter_threshold', ('condition',), r'as long as ANY (?:has|have) <n> or more <counter> on (?:ANY|<ref>)', ('st.counter_threshold', 'OBSERVES'))
R('cost.also_return', ('condition',), r'if <player\.you> also return <obj\.[a-z_]+> (?:you control )?to (?:hand|<zone>)', ('cost.return_to_hand', 'CONSUMES'))
R('time.declare_blockers', ('condition', 'timing', 'duration'), r'during the declare <obj\.bare> step', ('time.window', 'MODIFIES'))
R('op.alt_cost', E, r'cast <self> for <mana>', ('op.permission.cast', 'PERMITS'))
R('choice.target', E, S + r'choose (?:<obj\.target>|<player\.target>|<obj\.upto>)', ('choice.target', 'STRUCTURE'))
R('op.choose_value', E, S + r'(?:choose|name|secretly choose) (?:(?:a|<n>) (?:color|card type|creature type|nonland card name|card name|number|land type|player|basic land type)(?: other than <color>)?|(?:ANY|<n>|<n> of <ref>) from (?:ANY|among <ref>)|' + O + r' type|an opponent|<player\.[a-z_]+>|<color>|ANY)', ('op.choice.value', 'PRODUCES'))
R('op.extra_turn', E, S + r'take an extra turn after this one|there is an additional (?:combat|beginning|main) phase(?: after this phase)?(?: followed by an additional main phase)?', ('op.turn.extra', 'PRODUCES'))
R('op.game', E, S + r'(?:win|lose) the game', ('op.game.win_lose', 'PRODUCES'))
R('op.enter_tapped', E, r'(?:ANY )?enter tapped(?: and attacking)?', ('op.entry.tapped', 'PREVENTS'))
R('op.enter_counters', E, r'(?:ANY )?enter with (?:<n> |an additional |x |a number of |that many )?(?:additional )?<counter> on ANY', ('op.entry.with_counters', 'MODIFIES'))
R('op.as_enters', E, r'as ANY enter', ('op.entry.choice', 'PRODUCES'))
R('op.trigger_extra', E, r'(?:ANY )?trigger an additional time', ('op.trigger.extra', 'MODIFIES'))
R('op.hand_size', E, r"(?:ANY )?have no maximum hand size|(?:ANY 's )?maximum hand size is (?:reduced by <n>|increased by <n>|<n>)", ('op.hand_size', 'MODIFIES'))
R('op.land_extra', E, r'(?:ANY )?play (?:an|<n>) additional (?:' + O + r'|lands?) (?:on each of (?:' + PP + r') turns|this turn)', ('op.land.extra', 'PERMITS'))
R('op.flash', E, r'(?:ANY )?cast (?:ANY|spells) as though (?:it|they|<ref>) had flash', ('op.timing.permit', 'PERMITS'))
R('op.must_attack', E, r'(?:ANY )?(?:attack|block) each (?:combat|turn)|ANY must be blocked|(?:ANY )?must attack', ('op.attack.require', 'MODIFIES'))
R('op.phase', E, r'ANY phase out', ('op.phase.out', 'PRODUCES'))
R('op.goad', E, r'goad ANY', ('op.goad', 'MODIFIES'))
R('op.designation', E, S + r"become the monarch|" + S + r"take the initiative|the ring tempts <player\.[a-z_]+>|" + S + r"get the city's blessing|it becomes (?:day|night)", ('op.designation', 'PRODUCES'))
R('op.exchange', E, r"exchange (?:control of|life totals|ANY)[^,]*|switch ANY 's power and toughness", ('op.exchange', 'TRANSFORMS'))
R('op.random', E, S + r'(?:flip a coin|roll (?:a |<n> )?(?:six-sided |twenty-sided )?(?:die|dice)|roll a d<n>)|choose ANY at random', ('op.random', 'PRODUCES'))
R('op.pay', E, S + r'pay (?:<mana>|<n> life|<energy>|<n> <energy>|any amount of (?:mana|<energy>|life)|x|that much life)(?: (?:or|and) (?:<mana>|<n> life))?', ('op.pay', 'CONSUMES'))
R('op.type', E, r"(?:ANY )?(?:is|are|become) (?:a|an|<pt>|<color>|all colors|colorless|every creature type|the chosen type|" + O + r")(?: (?:<pt>|<color>|" + O + r"|artifact|creature|in addition to (?:its|their|<ref>) other (?:types|colors|creature types)|with <kw>|with base power and toughness <pt>|that's still " + O + r"))*", ('op.type.change', 'MODIFIES'))
R('op.mana_retain', E, r"(?:<player\.[a-z_]+> )?(?:don't|doesn't) lose (?:this|unspent) mana[^,]*|(?:ANY )?spend mana as though it were mana of any (?:color|type)[^,]*", ('op.mana.retain', 'MODIFIES'))
for ka in sorted(KWA_USED, key=len, reverse=True):
    R('kwa.' + ka.replace(' ', '_'), E, S + re.escape(ka) + r'(?: (?:<n>|ANY|x|<mana>|<n> ' + O + r'|<n> <counter>|<obj\.bare> <n>))?', ('kwa.' + ka.replace(' ', '_'), 'EXPANDS_TO'))

# costs ----------------------------------------------------------------
CO = ('cost',)
R('cost.mana', CO, r'<mana>|pay <mana>', ('cost.mana', 'CONSUMES'))
R('cost.tap', CO, r'<tap_symbol>', ('cost.tap_self', 'CONSUMES'))
R('cost.untap', CO, r'<untap_symbol>', ('cost.untap_self', 'CONSUMES'))
R('cost.tap_other', CO, r'tap (?:<n> )?(?:untapped )?(?:' + O + r'|<ref>)', ('cost.tap_other', 'CONSUMES'))
R('cost.sac_self', CO, r'sacrifice <self>', ('cost.sacrifice_self', 'CONSUMES'))
R('cost.sac_other', CO, r'sacrifice (?:<n> )?(?:a )?(?:<color> )?' + O + r'(?: or ' + O + r')?', ('cost.sacrifice_other', 'CONSUMES'))
R('cost.discard', CO, r'discard (?:' + O + r'|<self>|<n> ' + O + r'|' + Z + r')(?: at random)?', ('cost.discard', 'CONSUMES'))
R('cost.life', CO, r'pay (?:<n>|x) life', ('cost.life', 'CONSUMES'))
R('cost.exile', CO, r'exile (?:<self>|' + O + r'|<n> ' + O + r'|the top ' + O + r' of ' + Z + r')(?: from ' + Z + r')?(?: and ' + O + r' from ' + Z + r')?', ('cost.exile', 'CONSUMES'))
R('cost.counter_remove', CO, r'remove (?:<n> |a |all |x |any number of |one or more )?<counter> from (?:<self>|' + O + r'|among [^,]+)', ('cost.counter_remove', 'CONSUMES'))
R('cost.loyalty', CO, r'loyalty (?:\+ |- )?(?:<n>|x)', ('cost.loyalty', 'CONSUMES'))
R('cost.energy', CO, r'pay (?:<n> |any amount of )?<energy>', ('cost.energy', 'CONSUMES'))
R('cost.return', CO, r'return (?:<self>|' + O + r') to ' + Z, ('cost.return_to_hand', 'CONSUMES'))
R('cost.reveal', CO, r'reveal (?:' + O + r'|<self>)(?: from ' + Z + r')?', ('cost.reveal', 'CONSUMES'))
R('cost.mill', CO, r'mill (?:' + O + r'|<n> ' + O + r')', ('cost.mill', 'CONSUMES'))
R('cost.keyword', CO, r'(?:[a-z]+ <mana>|collect evidence <n>|blight <n>|behold (?:' + O + r'|<n> ' + O + r')|exert <self>|forage|(?:waterbend|earthbend|airbend|firebend) <mana>)', ('cost.keyword', 'CONSUMES'))
R('cost.header', ('cost_header',), r'as an additional cost to cast (?:this spell|<self>)', ('cost.additional', 'STRUCTURE'))

# conditions -------------------------------------------------------------
CK = ('condition',)
R('st.control', CK, r"(?:if|as long as|unless) (?:PL )?(?:don't )?control (?:<n> or more |no |at least <n> |exactly <n> |<n> or fewer |another )?(?:ANY)(?:(?:,| and| or) ANY)*", ('st.control', 'OBSERVES'))
R('st.zone_count', CK, r'(?:if|as long as) there (?:are|is) (?:<n> or more|no|<n> or fewer) (?:' + O + r'|<counter>)(?: types among ' + O + r')? (?:in|on) (?:' + Z + r'|ANY)', ('st.zone_count', 'OBSERVES'))
R('st.status', CK, r"(?:if|as long as|while) ANY (?:is|isn't|are|aren't|was|were) (?:tapped|untapped|attacking|blocking|blocked|unblocked|equipped|enchanted|paired with ANY|monstrous|renowned|suspected|saddled|face down|attacking or blocking|still on the battlefield)", ('st.object_status', 'OBSERVES'))
R('st.characteristic', CK, r"(?:if|as long as) ANY (?:is|are|isn't|aren't|was|wasn't|has|have) (?:ANY|<color>|a <color> " + O + r"|<n> or more <counter> on ANY|<kw>)|if ANY 's (?:ANY|<color>)|if ANY have <n> or more <counter> on <ref>|(?:if|as long as) ANY 's (?:power|toughness|mana value) is [^,]+", ('st.object_characteristic', 'OBSERVES'))
R('st.history', CK, r"if (?:ANY|no " + O + r") (?:attacked|gained|lost|cast|died|has died|entered|dealt damage|had|played|sacrificed|drew|discarded|descended|committed a crime|created|left the battlefield|was dealt damage|attacked with|was put into)[^,]*(?:this turn|last turn|this game)|if (?:" + O + r"|<n> or more " + O + r") (?:were|was) cast last turn|if no " + O + r" were cast last turn|if ANY 've [^,]+ this (?:turn|game)", ('st.history', 'OBSERVES'))
R('st.cast_option', CK, r"if (?:<self>|<ref>|ANY) was (?:kicked(?: twice| with its [^,]+)?|bargained|cast from " + Z + r"|foretold|evoked)|if the (?:<kw>|gift) was promised|if <mana> was spent to cast ANY|if <n> or more mana was spent to cast ANY|if ANY 's (?:additional|spree|surge|madness|blitz|prowl|evoke|dash|warp) cost was paid|if ANY 've cast ANY(?: this turn)?", ('st.cast_option', 'OBSERVES'))
R('st.comparison', CK, r"if ANY (?:control|have) (?:more|fewer|the most|the greatest|at least as many|less) [^,]+|if ANY(?: 's)? (?:life total|power|toughness) is (?:greater|less|higher|lower) than [^,]+", ('st.comparison', 'OBSERVES'))
R('st.designation', CK, r"if ANY (?:'re|is|are) the (?:monarch|ring-bearer)|if ANY have the (?:city's blessing|initiative)|if it's (?:day|night)|as long as ANY 're the monarch", ('st.designation', 'OBSERVES'))
R('st.random', CK, r'if (?:PL )?(?:win|lose|won|lost) the (?:flip|clash|vote)|if (?:PL )?win', ('st.random_outcome', 'OBSERVES'))
R('st.target', CK, r'if ANY targets (?:only )?ANY|if ANY has a single target', ('st.target_check', 'OBSERVES'))
R('st.resource', CK, r"if ANY have (?:<n> or (?:more|less|fewer) |no |at least <n> |exactly <n> )?(?:life|" + O + r" in (?:hand|" + Z + r")|<counter>)|if ANY(?: 's)? life total is [^,]+|if ANY have <n> or (?:more|less) life|if ANY have no " + O + r" in hand", ('st.player_resource', 'OBSERVES'))
R('st.if_able', CK, r'if able', ('st.if_able', 'MODIFIES'))
R('st.unless_pay', CK, r'unless ANY (?:pay|discard|sacrifice|exile|tap|return|reveal) [^,]+', ('st.unless_payment', 'OBSERVES'))
R('st.zone_loc', CK, r'(?:if|as long as|while) ANY is (?:in|on) (?:' + Z + r'|the battlefield)|if <self> is in ' + PP + r' opening hand', ('st.zone_location', 'OBSERVES'))
R('st.did', CK, r"if (?:ANY|no one|a player) (?:do|does|did|doesn't|don't|can't|cannot|didn't)(?: [a-z ]+)?|if (?:PL )?search " + Z + r" <ref>|if ANY die <ref>|if (?:PL )?(?:cast|sacrificed|discarded|exiled|revealed) ANY <ref>", ('st.did_action', 'OBSERVES'))

# modifiers --------------------------------------------------------------
AM = ('amplifier',)
R('amp.counters', AM, r'(?:for each|equal to the number of|where <n> is the number of) <counter> (?:on|removed) ANY(?: <ref>)?', ('amp.counters', 'MODIFIES'))
R('amp.stat', AM, r"(?:equal to|where <n> is) (?:ANY 's|<ref>|ANY) (?:power|toughness|mana value|mana cost|loyalty|base power)(?: (?:rather than|plus|minus) [^,]+)?(?: to ANY)?|(?:equal to|where <n> is) the (?:greatest|highest|total) (?:power|toughness|mana value) (?:among|of) [^,]+|(?:where <n> is|equal to) the mana value of ANY|equal to <n> plus ANY 's mana value", ('amp.stat', 'MODIFIES'))
R('amp.player', AM, r"(?:equal to|where <n> is) (?:" + PP + r" (?:devotion to [^,]+|life total|hand size)|the (?:amount of )?life (?:<player\.[a-z_]+> )?(?:gained|lost) (?:this turn|<ref>)|the amount of (?:damage|life|mana) [^,]+)|for <player\.each>", ('amp.player', 'MODIFIES'))
R('amp.count', AM, r'(?:for|where <n> is|equal to) (?:the number of |each )?(?:' + O + r'|<player\.[a-z_]+>|' + O + r' types? among ' + O + r'|color among ' + O + r')(?: (?:in|on|among) (?:' + Z + r'|the battlefield|ANY))?(?: (?:that (?:died|entered|attacked) this turn|<ref>|beyond the first))?(?: to ANY)?|for each of ANY|where <n> is the number of [^,]+|equal to the number of [^,]+|for each target beyond the first', ('amp.count', 'MODIFIES'))
R('amp.other', AM, r'(?:equal to|where <n> is|for each) [^,]+', ('amp.other', 'MODIFIES'))
DU = ('duration',)
R('time.eot', DU, r'until end of turn', ('time.until_eot', 'MODIFIES'))
R('time.this_turn', DU, r'this turn', ('time.this_turn', 'MODIFIES'))
R('time.next_turn', DU, r'until ' + PP + r' next turn|until the end of ' + PP + r' next turn', ('time.until_next_turn', 'MODIFIES'))
R('time.while', DU, r'for as long as [^,]+|until ANY leave the battlefield|until [^,]+ leave the battlefield', ('time.while', 'MODIFIES'))
R('time.window_turn', ('timing',), r"during (?:" + PP + r"|each|an opponent's|each opponent's) (?:turn|upkeep|combat|end step)|each (?:turn|combat)|after this (?:main )?phase", ('time.window', 'MODIFIES'))
R('time.window', ('timing',), r'.+', ('time.window', 'MODIFIES'))
R('time.delayed_step', ('delayed_trigger',), r"at (?:the beginning of (?:the next|" + PP + r" next|the next turn's) (?:end step|upkeep|combat)|end of combat)", ('time.delayed_trigger', 'MODIFIES'))
R('time.delayed', ('delayed_trigger',), r'.+', ('time.delayed_trigger', 'MODIFIES'))
RS = ('restriction',)
R('time.sorcery', RS, r'(?:activate|station|crew|saddle) only as <obj\.q>|activate only any time you could cast a sorcery', ('time.sorcery_speed', 'MODIFIES'))
R('cap.once', RS, r'(?:<self> trigger only once each turn|activate only once each turn|do this only once each turn|once each turn)', ('cap.once_each_turn', 'MODIFIES'))
R('cap.limited', RS, r'(?:activate|<self> trigger) (?:only once|no more than (?:twice|<n> times) each turn)', ('cap.limited', 'MODIFIES'))
R('time.turn_scope', RS, r"activate only during (?:" + PP + r" (?:turn|upkeep|end step)|combat|an opponent's turn)(?:, before [^,]+)?|activate only (?:before|after) [^,]+|cast <self> only during [^,]+", ('time.turn_scope', 'MODIFIES'))
R('gate.activate_if', RS, r'activate only if .+|cast <self> only if .+', ('gate.activate_if', 'OBSERVES'))
R('rest.uncounter', RS, r"<self> can't be countered", ('rest.uncounterable', 'PREVENTS'))
R('rest.mana_spend_cast', RS, r'spend this mana only (?:to|on) (?:cast|activate) (?:ANY|<obj\.[a-z_]+> spells?)(?: from ' + Z + r')?(?: or (?:to )?(?:activate|cast) (?:ANY|abilities)(?: of ANY)?)?', ('rest.mana_spend', 'MODIFIES'))
R('rest.mana_spend', RS, r'spend this mana only .+', ('rest.mana_spend', 'MODIFIES'))
R('rest.no_regen', RS, r"(?:ANY )?can't be regenerated", ('rest.no_regen', 'PREVENTS'))
R('rest.still', RS, r"(?:ANY )?'s still .+", ('rest.still_type', 'MODIFIES'))
R('rest.activator', RS, r'(?:<player\.[a-z_]+> )?activate <self>(?: but only .+)?|only ' + PP + r' may activate <self>', ('rest.activator', 'MODIFIES'))
LI = ('link',)
R('proc.if_you_do', LI, r'if (?:ANY|you|they|that player) (?:do|does)', ('proc.if_you_do', 'STRUCTURE'))
R('proc.if_not', LI, r"if (?:ANY|you|they|that player|no one) (?:don't|doesn't|can't|does)|otherwise", ('proc.if_not', 'STRUCTURE'))
R('proc.then', LI, r'then|also', ('proc.then', 'STRUCTURE'))
R('proc.reflexive', LI, r'when(?:ever)? (?:ANY|you) do', ('proc.reflexive', 'STRUCTURE'))
R('proc.instead', ('replacement_marker',), r'instead', ('proc.instead', 'STRUCTURE'))
R('proc.modal_n', ('mode_header',), r"choose (?:<n>|<n> or both|<n> or more|any number|up to <n>|<n> or <n>|<n> —)(?: (?:that hasn't been chosen|of them|at random|instead|—))*(?: (?:or both|or more))?", ('choice.modal', 'STRUCTURE'))
R('proc.modal', ('mode_header',), r'choose .+', ('choice.modal', 'STRUCTURE'))
RP = ('replacement',)
R('rep.die_exile', RP, r"if ANY(?: dealt damage(?: by ANY)?(?: <ref>)?(?: this turn)?)? would (?:die|be put into " + Z + r"(?: from " + Z + r")?|leave the battlefield)(?: this turn)?, exile (?:ANY|<ref>) instead(?: of putting <ref> " + Z + r" else)?", ('proc.replacement', 'STRUCTURE'), ('op.zone.exile', 'TRANSFORMS'))
R('rep.counters_plus', RP, r'if (?:<n> or more|<n> or) <counter> would be put on ANY(?: [^,]+)?, (?:<n> plus <n>|twice <n>|that many plus <n>|<n> plus <n> of each of those kinds)(?: of each of those kinds)? <counter> (?:are|is) put on ANY instead', ('proc.replacement', 'STRUCTURE'), ('op.counter.put', 'MODIFIES'))
R('rep.tokens_plus', RP, r'if (?:an effect would create |ANY would create )?(?:ANY|<obj\.oneormore>)(?: would be created)? under ' + PP + r' control, (?:twice <n> of ANY are created|ANY (?:plus ANY )?are created|<ref> create twice <n> of ANY) instead|if ANY would create ANY, (?:instead )?create ANY(?: plus ANY)?(?: instead)?', ('proc.replacement', 'STRUCTURE'), ('op.token.create', 'MODIFIES'))
R('rep.prevent', RP, r'if (?:ANY would deal damage to ANY(?: or ANY)?|damage would be dealt to ANY), prevent (?:<n> of |all but <n> of )?that damage', ('proc.replacement', 'STRUCTURE'), ('op.damage.prevent', 'PREVENTS'))
R('rep.damage_plus', RP, r'if ANY would deal (?:noncombat |combat )?damage to ANY(?: or ANY)?, <ref> deal (?:double that damage|that much damage plus <n>)(?: to ANY)? instead', ('proc.replacement', 'STRUCTURE'), ('op.damage.deal', 'MODIFIES'))
R('rep.life_plus', RP, r'if ANY would gain life, (?:ANY )?(?:gain (?:twice that much life|that much life plus <n>)|lose that much life) instead', ('proc.replacement', 'STRUCTURE'), ('op.life.gain', 'MODIFIES'))
R('rep.draw', RP, r'if ANY would draw ANY(?: [^,]+)?, (?:instead )?(?:ANY )?[a-z]+ [^,]+ instead', ('proc.replacement', 'STRUCTURE'), ('op.card.draw', 'MODIFIES'))
R('proc.replacement', RP, r'if .+ would .+', ('proc.replacement', 'STRUCTURE'))
R('struct.level', ('structure',), r'<structure>', ('struct.level', 'STRUCTURE'))
R('struct.level_up', E, r'level <n>', ('struct.level', 'STRUCTURE'))
R('kw.engines', E, r'start ' + PP + r' engines!', ('kw.start_your_engines', 'EXPANDS_TO'))
R('kwa.prepare', E, r'(?:ANY )?(?:enter|become) prepared', ('kwa.prepare', 'EXPANDS_TO'))

CONNECTORS = re.compile(r'(?:\band/or\b|\band\b|\bor\b|\bthen\b|\bmay\b|,)')
# Roles whose rule is a whole-part catch (the part is structurally recognised but its inner content is not
# decomposed further yet). These count as 'partial', never 'complete'.
CATCH_ALL = {'time.window', 'time.delayed', 'proc.replacement', 'amp.other', 'gate.activate_if', 'rest.mana_spend',
             'rest.still', 'proc.modal', 'rep.draw'}

# Replacement rules compose into ONE operation of kind replacement whose result rewrites a proposed event into a
# resulting one (DIO §5.4). 'proposed' is the event the replacement watches for; 'resulting' is the concept whose
# edge carries the new event; mode says how: substitute (a different event happens), modify (same event, other
# magnitude), prevent (the event does not happen).
REWRITES = {
    'rep.die_exile': ('ev.permanent.dies', 'op.zone.exile', 'substitute'),
    'rep.counters_plus': ('ev.counter.put', 'op.counter.put', 'modify'),
    'rep.tokens_plus': ('ev.token.create', 'op.token.create', 'modify'),
    'rep.prevent': ('ev.damage.deal', 'op.damage.prevent', 'prevent'),
    'rep.damage_plus': ('ev.damage.deal', 'op.damage.deal', 'modify'),
    'rep.life_plus': ('ev.life.gain', 'op.life.gain', 'modify'),
    'rep.draw': ('ev.card.draw', None, 'substitute'),
}

def keyword_concept(frame_text):
    k = frame_text[len('keyword '):]
    for kw in KEYWORD_ABILITIES:
        if k == kw or k.startswith(kw + ' '):
            return 'kw.' + kw.replace(' ', '_')
    if re.match(r'[a-z]+walk\b', k):
        return 'kw.landwalk'
    if re.match(r'[a-z]+cycling\b', k):
        return 'kw.landcycling'
    return None


SLOT_TOK = re.compile(r'<[a-z_.]+>')
TRIGGER_WORD = re.compile(r'^(?:when|whenever|at) ')
EVENT_VERBS = ('enter', 'attack', 'block', 'die', 'leave', 'become', 'is', 'are', 'deal', 'cast', 'copy', 'create',
               'sacrifice', 'transform', 'gain', 'lose', 'draw', 'discard', 'mill', 'tap', 'untap', 'put', 'exile',
               'return', 'search', 'activate', 'cycle', 'play', 'explore', 'scry', 'surveil', 'attach', 'counter')
TRANSITIVE = {'cast', 'copy', 'create', 'sacrifice', 'gain', 'lose', 'draw', 'discard', 'mill', 'tap', 'untap',
              'exile', 'return', 'search', 'activate', 'cycle', 'play', 'attach', 'counter', 'deal', 'put'}
_COORD = re.compile(r' or (?=(?:' + '|'.join(EVENT_VERBS) + r')\b)')
_FIRST_VERB = re.compile(r'\b(?:' + '|'.join(EVENT_VERBS) + r')\b')


def slot_positions(frame_text):
    return [m.start() for m in SLOT_TOK.finditer(frame_text)]


def coordinate(frame_text):
    """Split a coordinated trigger ("whenever <self> enter or attack", "whenever you cast or copy <obj.q>") into
    alternatives that share the subject. Returns [(alt_text, [slot indices of frame_text])] or None.

    "This or another" (coordinated subjects) is already one alternative group via 'ANY or ANY'; this handles
    coordinated verbs, which DIO §5.1 also treats as alternatives inside one trigger requirement group."""
    tw = TRIGGER_WORD.match(frame_text)
    if not tw:
        return None
    cuts = [m for m in _COORD.finditer(frame_text) if m.start() > tw.end()]
    if not cuts:
        return None
    pos = slot_positions(frame_text)
    verb = _FIRST_VERB.search(frame_text, tw.end())
    if not verb or verb.start() > cuts[0].start():
        return None
    subj_end = verb.start()
    subj = frame_text[tw.end():subj_end]
    subj_slots = [i for i, p in enumerate(pos) if tw.end() <= p < subj_end]
    bounds = [subj_end] + [c.end() for c in cuts]
    ends = [c.start() for c in cuts] + [len(frame_text)]
    alts = []
    for k, (b0, e0) in enumerate(zip(bounds, ends)):
        vp = frame_text[b0:e0]
        slots = [i for i, p in enumerate(pos) if b0 <= p < e0]
        alts.append([vp, slots])
    # a bare verb shares the object of the last alternative when that verb is transitive:
    # "cast or copy <obj.q>", "gain or lose life"; never "die or is put into <zone>"
    last_vp, last_slots = alts[-1]
    verb2, _, tail = last_vp.partition(' ')
    if tail and verb2 in TRANSITIVE:
        for alt in alts[:-1]:
            if ' ' not in alt[0]:
                alt[0] = alt[0] + ' ' + tail
                alt[1] = list(last_slots)
    return [(frame_text[:tw.end()] + subj + vp, subj_slots + slots) for vp, slots in alts]


def _match(role, frame_text):
    if role == 'keyword':
        cid = keyword_concept(frame_text)
        return ([(cid, 'EXPANDS_TO', 'kw.macro', {})] if cid else []), ('complete' if cid else 'none')
    lookup = 'effect' if role in ('static',) else role
    cands = []
    for order, (rid, roles, rx, ed) in enumerate(RULES):
        if lookup not in roles and role not in roles:
            continue
        for m in rx.finditer(frame_text):
            if m.end() == m.start():
                continue
            if m.start() > 0 and frame_text[m.start() - 1] not in ' ,':
                continue
            if m.end() < len(frame_text) and frame_text[m.end()] not in ' ,':
                continue
            cands.append((-(m.end() - m.start()), order, m.start(), m.end(), rid, ed))
    cands.sort()
    edges, spans, catch_only = [], [], True
    pos = slot_positions(frame_text)
    for _, _, st_, en, rid, ed in cands:
        if any(st_ < e and s_ < en for s_, e in spans):
            continue
        spans.append((st_, en))
        if rid not in CATCH_ALL:
            catch_only = False
        slots = [i for i, p in enumerate(pos) if st_ <= p < en]
        rw = REWRITES.get(rid)
        for cid, rel in ed:
            meta = {'span': [st_, en], 'slots': slots}
            if rw:
                meta['composite'] = {'kind': 'replacement', 'rule': rid, 'proposed': rw[0], 'resulting': rw[1],
                                     'mode': rw[2], 'member': 'structure' if cid == 'proc.replacement' else 'resulting'}
            edges.append((cid, rel, rid, meta))
    if not edges:
        return [], 'none'
    covered = [False] * len(frame_text)
    for s_, e in spans:
        for i in range(s_, e):
            covered[i] = True
    left = ''.join(ch if not covered[i] else ' ' for i, ch in enumerate(frame_text))
    left = CONNECTORS.sub(' ', left).strip()
    seen, uniq = set(), []
    for e in edges:
        if (e[0], e[1]) not in seen:
            seen.add((e[0], e[1]))
            uniq.append(e)
    complete = not left and not catch_only
    return uniq, ('complete' if complete else 'partial')


def match_frame(role, frame_text):
    """Return (edges, completeness). Each edge is (concept_id, relation, rule_id, meta).

    complete means the rules consumed every word of the frame except connectors (span accounting).
    partial means at least one concept was found but some words are unaccounted for, or the only match
    is a whole-part catch rule.

    meta carries the span the rule matched, the indices of the frame's slots inside it, and how the edge composes
    with its siblings: {'group': 'trigger', 'alt': i} for alternatives of one trigger requirement group, or
    {'composite': {...}} for the members of one replacement operation.
    """
    if role == 'trigger_event':
        alts = coordinate(frame_text)
        if alts:
            out, comps = [], []
            for k, (alt, slots) in enumerate(alts):
                ed, c = _match(role, alt)
                comps.append(c)
                for cid, rel, rid, meta in ed:
                    out.append((cid, rel, rid, {'group': 'trigger', 'alt': k, 'alt_text': alt, 'slots': slots}))
            if out and all(c == 'complete' for c in comps):
                return out, 'complete'
            if out:
                return out, 'partial'
    edges, comp = _match(role, frame_text)
    if role == 'trigger_event':
        k = 0
        for cid, rel, rid, meta in edges:
            if concept_type(cid) == 'event':
                meta.update({'group': 'trigger', 'alt': k})
                k += 1
    return edges, comp


def concept_type(cid):
    return C[cid][0] if cid in C else ('keyword_macro' if cid.startswith(('kw.', 'kwa.')) else None)


def install(db):
    import json
    db.executemany('INSERT OR REPLACE INTO concept VALUES(?,?,?,?,?,?,?)',
                   [(cid, st, dio, status, label, intent, None) for cid, (st, dio, status, label, intent) in C.items()])
    db.execute('ALTER TABLE frame ADD COLUMN completeness TEXT')
    rows, comp = [], []
    for fid, role, ft in db.execute('SELECT frame_id, role, frame_text FROM frame').fetchall():
        edges, c = match_frame(role, ft)
        comp.append((c, fid))
        for cid, rel, rid, meta in edges:
            rows.append((fid, cid, rel, json.dumps(meta, sort_keys=True), rid, 'proposed'))
    db.executemany('INSERT OR IGNORE INTO frame_concept_edge VALUES(?,?,?,?,?,?)', rows)
    db.executemany('UPDATE frame SET completeness=? WHERE frame_id=?', comp)
