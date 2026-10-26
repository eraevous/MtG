"""Closed word classes for the Oracle grammar, built from Scryfall catalogs.

The catalogs are copied into data/catalogs/ so a rebuild does not depend on the network.
Everything here is surface vocabulary. Meaning lives in concepts.py and the DIO.
"""
import json
import re
from pathlib import Path

CAT = Path(__file__).parent / 'data' / 'catalogs'


def _cat(name):
    return [v for v in json.load(open(CAT / f'cat_{name}.json'))['data'] if v]


KEYWORD_ABILITIES = sorted({k.lower() for k in _cat('keyword-abilities')}, key=len, reverse=True)
KEYWORD_ACTIONS = sorted({k.lower() for k in _cat('keyword-actions')}, key=len, reverse=True)
ABILITY_WORDS = {k.lower() for k in _cat('ability-words')}

CARD_TYPES = {t.lower() for t in _cat('card-types')} | {'tribal'}
SUPERTYPES = {t.lower() for t in _cat('supertypes')}
SUBTYPES = set()
for c in ('creature-types', 'land-types', 'artifact-types', 'enchantment-types', 'spell-types',
          'planeswalker-types', 'battle-types'):
    SUBTYPES |= {t.lower() for t in _cat(c)}

IRREGULAR_PLURALS = {'elf': 'elves', 'dwarf': 'dwarves', 'wolf': 'wolves', 'werewolf': 'werewolves',
                     'ox': 'oxen', 'mouse': 'mice', 'fish': 'fish', 'sheep': 'sheep', 'octopus': 'octopuses',
                     'thief': 'thieves', 'leaf': 'leaves', 'cyclops': 'cyclopes', 'sphinx': 'sphinxes',
                     'fungus': 'fungi', 'homunculus': 'homunculi', 'djinn': 'djinn', 'efreet': 'efreet',
                     'mercenary': 'mercenaries', 'samurai': 'samurai', 'ninja': 'ninja', 'kor': 'kor',
                     'moonfolk': 'moonfolk', 'kithkin': 'kithkin', 'merfolk': 'merfolk', 'phyrexian': 'phyrexians',
                     'aetherborn': 'aetherborn', 'saproling': 'saprolings', 'gnome': 'gnomes'}


def plural(w):
    if w in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[w]
    if re.search(r'[^aeiou]y$', w):
        return w[:-1] + 'ies'
    if re.search(r'(s|x|ch|sh|z)$', w):
        return w + 'es'
    return w + 's'


GENERIC_HEADS = {'permanent', 'card', 'spell', 'token', 'object', 'source', 'ability', 'creature', 'land',
                 'artifact', 'enchantment', 'planeswalker', 'battle', 'instant', 'sorcery', 'nonland', 'copy',
                 'mana ability', 'activated ability', 'triggered ability', 'spell or ability',
                 'permanent card', 'creature card', 'land card'}

TYPE_WORDS = CARD_TYPES | SUPERTYPES | SUBTYPES
HEAD_SINGULAR = (CARD_TYPES | SUBTYPES | {'permanent', 'card', 'spell', 'token', 'object', 'source', 'ability',
                                          'copy', 'commander', 'face', 'nontoken', 'player', 'opponent',
                                          'attacker', 'blocker', 'land', 'aura', 'equipment', 'vehicle'})
HEAD_WORDS = HEAD_SINGULAR | {plural(w) for w in HEAD_SINGULAR} | {'abilities', 'copies', 'others'}

COLORS = ['white', 'blue', 'black', 'red', 'green', 'colorless', 'multicolored', 'monocolored']

# Adjectives that can precede an object head.
PREMODS = set(COLORS) | SUPERTYPES | {
    'token', 'nontoken', 'tapped', 'untapped', 'attacking', 'blocking', 'blocked', 'unblocked', 'enchanted',
    'equipped', 'face-down', 'face-up', 'modified', 'historic', 'outlaw', 'party', 'activated', 'triggered',
    'mana', 'exiled', 'chosen', 'sacrificed', 'destroyed', 'nonbasic', 'noncombat', 'combat', 'other',
    'colored', 'double-faced', 'transformed', 'suspected', 'saddled', 'goaded', 'creature', 'artifact',
    'enchantment', 'land', 'planeswalker', 'instant', 'sorcery', 'battle', 'kindred', 'tribal',
    'monocolored', 'multicolored', 'basic', 'legendary', 'snow', 'commander', 'nonlegendary', 'noncommander',
    'single', 'top', 'revealed', 'defending', 'additional', 'new', 'random', 'permanent'}

NUMBER_WORDS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
                'twelve', 'thirteen', 'fourteen', 'fifteen', 'twenty', 'x', 'that many', 'half']

# Effect verbs: base form -> its third-person form(s). Used to lemmatize and to decide where a
# coordinated clause starts a second action ("draw a card and lose 1 life").
VERBS = {
    'add': ['adds'], 'attach': ['attaches'], 'attack': ['attacks'], 'become': ['becomes'], 'block': ['blocks'],
    'cast': ['casts'], 'change': ['changes'], 'choose': ['chooses'], 'control': ['controls'],
    'copy': ['copies'], 'cost': ['costs'], 'counter': ['counters'], 'create': ['creates'], 'deal': ['deals'],
    'destroy': ['destroys'], 'die': ['dies'], 'discard': ['discards'], 'distribute': ['distributes'],
    'double': ['doubles'], 'draw': ['draws'], 'enter': ['enters'], 'exchange': ['exchanges'],
    'exile': ['exiles'], 'explore': ['explores'], 'fight': ['fights'], 'flip': ['flips'], 'gain': ['gains'],
    'get': ['gets'], 'have': ['has'], 'investigate': ['investigates'], 'leave': ['leaves'],
    'look': ['looks'], 'lose': ['loses'], 'mill': ['mills'], 'move': ['moves'], 'pay': ['pays'],
    'phase': ['phases'], 'play': ['plays'], 'prevent': ['prevents'], 'proliferate': ['proliferates'],
    'put': ['puts'], 'regenerate': ['regenerates'], 'remove': ['removes'], 'return': ['returns'],
    'reveal': ['reveals'], 'sacrifice': ['sacrifices'], 'scry': ['scries'], 'search': ['searches'],
    'shuffle': ['shuffles'], 'skip': ['skips'], 'spend': ['spends'], 'surveil': ['surveils'],
    'tap': ['taps'], 'take': ['takes'], 'transform': ['transforms'], 'untap': ['untaps'],
    'connive': ['connives'], 'amass': ['amasses'], 'populate': ['populates'], 'manifest': ['manifests'],
    'goad': ['goads'], 'venture': ['ventures'], 'learn': ['learns'], 'adapt': ['adapts'],
    'bolster': ['bolsters'], 'support': ['supports'], 'detain': ['detains'], 'monstrosity': [],
    'incubate': ['incubates'], 'discover': ['discovers'], 'forage': ['forages'], 'endure': ['endures'],
    'earthbend': ['earthbends'], 'waterbend': ['waterbends'], 'airbend': ['airbends'], 'firebend': [],
    'blight': ['blights'], 'suspect': ['suspects'], 'cloak': ['cloaks'], 'collect': ['collects'],
    'vote': ['votes'], 'roll': ['rolls'], 'open': ['opens'], 'harness': ['harnesses'], 'exert': ['exerts'],
    'assemble': ['assembles'], 'behold': ['beholds'], 'conjure': ['conjures'], 'seek': ['seeks'],
    'heal': ['heals'], 'plot': ['plots'], 'meld': ['melds'], 'convert': ['converts'],
    'win': ['wins'], 'lose the game': [], 'turn': ['turns'], 'can': [], 'may': [], 'separate': ['separates'],
    'switch': ['switches'], 'redirect': ['redirects'], 'unattach': ['unattaches'], 'reorder': [],
    'note': ['notes'], 'name': ['names'], 'guess': ['guesses'], 'flip a coin': [], 'repeat': ['repeats'],
    'remain': ['remains'], 'deal damage': [], 'trigger': ['triggers'], 'resolve': ['resolves'],
    'assign': ['assigns'], 'divide': ['divides'], 'perpetually': [], 'time travel': [], 'train': ['trains'],
    'craft': ['crafts'], 'saddle': ['saddles'], 'crew': ['crews'], 'station': ['stations'],
}
LEMMA = {}
for base, forms in VERBS.items():
    LEMMA[base] = base
    for f in forms:
        LEMMA[f] = base
ACTION_VERB_START = sorted(set(LEMMA) - {'can', 'may', 'control', 'have', 'enter', 'die', 'leave', 'remain',
                                         'cost', 'perpetually', 'resolve', 'trigger'}, key=len, reverse=True)

ZONE_PHRASES = [
    r"(?:the )?top of (?:your|its owner's|their owners'|that player's|target player's|each player's|a player's|his or her) library",
    r"(?:the )?bottom of (?:your|its owner's|their owners'|that player's|target player's|each player's) library",
    r"(?:your|its owner's|their owners'|that player's|target player's|target opponent's|each player's|each opponent's|an opponent's|a player's|defending player's|its controller's|his or her|their) (?:graveyards?|hands?|librar(?:y|ies))",
    r"(?:a|any|each|all|target) (?:graveyards?|librar(?:y|ies))",
    r"anywhere",
    r"your library and/or graveyard", r"your graveyard and/or hand", r"your hand or graveyard",
    r"your graveyard or hand", r"among them", r"among the revealed cards", r"among those cards",
]
