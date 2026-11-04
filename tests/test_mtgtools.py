"""Tests for the mtg tool surface. Grading rules run everywhere; verb tests need the KB database (data/README.md)
and are skipped when it is absent, as in CI until the release databases are published (C-006)."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mtgtools.claims import claim, grade  # noqa: E402

DB = ROOT / 'kb' / 'mtg_cards_v0.2.sqlite'


class Grading(unittest.TestCase):
    def test_grade_is_per_kind(self):
        self.assertEqual(grade('mechanics', 'semantic_reviewed'), 'decision_grade')
        for s in ('ready_for_review', 'blocked', 'quarantined', 'candidate'):
            self.assertEqual(grade('mechanics', s), 'exploratory')
        self.assertEqual(grade('rules_text', 'oracle'), 'decision_grade')
        self.assertEqual(grade('rules_text', 'sheet_text'), 'exploratory')
        self.assertEqual(grade('inventory', 'collection_snapshot'), 'decision_grade')

    def test_performance_and_preference_are_never_decision_grade(self):
        for s in ('evaluator_model', 'semantic_reviewed', 'oracle', 'collection_snapshot'):
            self.assertEqual(grade('performance', s), 'exploratory')
            self.assertEqual(grade('preference', s), 'not_system_gradable')

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            claim('x', 'vibes', 'oracle')


class Qualifiers(unittest.TestCase):
    """Qualifier matching on hand-built contracts, so it runs in CI without the KB database."""
    VOCAB = {'legendary', 'creature', 'enchantment', 'saga', 'artifact', 'artificer', 'human', 'wizard', 'land', 'aura'}

    def k(self, card, faces, feeds=(), hooks=(), subject='others', filt=None, self_phrase=False, targets=()):
        return {'contract_id': card + '.op', 'card': card, 'faces': list(faces), 'feeds': list(feeds), 'hooks': list(hooks),
                'hook_subject': subject, 'targets': list(targets), 'state': 'blocked',
                'triggers': {h: {'filter': filt, 'self': self_phrase, 'parsed': True} for h in hooks}}

    def setUp(self):
        from mtgtools import verbs
        self.v = verbs
        self.terra_return = self.k('Terra', ['legendary creature — human wizard', 'legendary enchantment creature — saga wizard'],
                                   feeds=['card.return_to_battlefield'])
        self.terra_copy = self.k('Terra', self.terra_return['faces'], feeds=['token.create'],
                                 targets=['target nonlegendary enchantment you control'])

    def q(self, p, eff, o, hook='battlefield.enter'):
        return self.v._qualify(p, eff, o, hook, self.VOCAB)

    def test_object_type_filter(self):
        era = self.k('Era', ['enchantment'], hooks=['battlefield.enter'], filt='artifact or artificer')
        module = self.k('Module', ['artifact'], hooks=['battlefield.enter'], filt='creature')
        self.assertEqual(self.q(self.terra_return, 'card.return_to_battlefield', era)[0], 'incompatible')
        self.assertEqual(self.q(self.terra_return, 'card.return_to_battlefield', module)[0], 'compatible')

    def test_counter_type_is_never_assumed(self):
        chapter = self.k('Terra', [], hooks=['counter.put'], subject=None)
        energy = self.k('Nissa', ['legendary creature'], feeds=['counter.put'])
        self.assertEqual(self.q(energy, 'counter.put', chapter, 'counter.put')[0], 'unresolved')

    def test_counter_kinds_decide_counter_links(self):
        # C-016: Hapatra hears -1/-1 counters; Leonardo puts +1/+1; Twitching Doll puts nest; proliferate depends on the board
        hapatra = dict(self.k('Hapatra', ['legendary creature'], hooks=['counter.put']), counters=[{'role': 'listen_put', 'kind': '-1/-1', 'holder': 'permanent'}])
        anyc = dict(self.k('Patron', ['creature'], hooks=['counter.put']), counters=[{'role': 'listen_put', 'kind': 'any', 'holder': 'permanent'}])
        leo = dict(self.k('Leonardo', ['legendary creature'], feeds=['counter.put']), counters=[{'role': 'put', 'kind': '+1/+1', 'holder': 'permanent'}])
        clasp = dict(self.k('Clasp', ['artifact'], feeds=['counter.put']), counters=[{'role': 'put', 'kind': '-1/-1', 'holder': 'permanent'}])
        sage = dict(self.k('Sage', ['creature'], feeds=['counter.put']), counters=[{'role': 'proliferate', 'kind': 'present_kinds', 'holder': 'permanent_or_player'}])
        q = lambda p, o: self.q(p, 'counter.put', o, 'counter.put')[0]
        self.assertEqual(q(leo, hapatra), 'incompatible')
        self.assertEqual(q(clasp, hapatra), 'compatible')
        self.assertEqual(q(leo, anyc), 'compatible')
        self.assertEqual(q(sage, hapatra), 'unresolved')

    def test_self_enter_needs_a_copy_or_return_of_that_card(self):
        light = self.k('Light', ['enchantment'], hooks=['battlefield.enter'], subject='self')
        talent = self.k('Talent', ['enchantment — class'], hooks=['battlefield.enter'], self_phrase=True)
        golem = self.k('Golem', ['artifact creature'], hooks=['battlefield.enter'], subject='self')
        self.assertEqual(self.q(self.terra_copy, 'token.create', light)[1], 'reentry_of_target')
        self.assertEqual(self.q(self.terra_copy, 'token.create', talent)[1], 'reentry_of_target')
        self.assertEqual(self.q(self.terra_copy, 'token.create', golem)[0], 'incompatible')   # not an enchantment
        self.assertEqual(self.q(self.terra_return, 'card.return_to_battlefield', light)[0], 'incompatible')

    def test_a_target_disjunction_is_not_read_as_a_conjunction(self):
        copier = self.k('Copier', ['enchantment'], feeds=['token.create'], targets=['target artifact or enchantment you control'])
        artifact = self.k('Relic', ['artifact'], hooks=['battlefield.enter'], subject='self')
        land = self.k('Field', ['land'], hooks=['battlefield.enter'], subject='self')
        self.assertEqual(self.q(copier, 'token.create', artifact)[0], 'unresolved')     # was rejected as "artifact enchantment"
        self.assertEqual(self.q(copier, 'token.create', land)[0], 'unresolved')         # a miss on a disjunction is not a rejection

    def test_a_card_can_feed_its_own_watcher_of_other_objects(self):
        maker = self.k('Maker', ['creature'], feeds=['token.create'])
        watcher = dict(self.k('Maker', ['creature'], hooks=['battlefield.enter'], filt='creature'), contract_id='Maker.op2')
        links = self.v._links([maker, watcher])
        self.assertTrue(any(l['same_card'] and l['observer_contract'] == 'Maker.op2' for l in links))

    def test_same_card_reentry_on_a_two_faced_card_stays_unresolved(self):
        etb = self.k('Terra', self.terra_return['faces'], hooks=['battlefield.enter'], subject='self')
        self.assertEqual(self.q(self.terra_return, 'card.return_to_battlefield', etb)[:2], ('unresolved', 'same_card'))


    def test_a_sacrifice_cost_feeds_a_dies_trigger(self):
        # 2026-11-01 practical-question run: Viscera Seer's "Sacrifice a creature:" is a cost, so query_index.feeds omits it
        seer = dict(self.k('Seer', ['creature'], feeds=['permanent.sacrifice']), paid={'permanent.sacrifice': 'creature'},
                    text='Sacrifice a creature: Scry 1.')
        artist = self.k('Artist', ['creature'], hooks=['permanent.dies'], subject='self', filt='creature')
        artist['triggers']['permanent.dies'].update(others=True)        # "this creature or another creature dies"
        self.assertEqual(self.q(seer, 'permanent.sacrifice', artist, 'permanent.dies')[:2], ('compatible', 'paid_object'))
        altar = dict(seer, paid={'permanent.sacrifice': 'artifact'})
        self.assertEqual(self.q(altar, 'permanent.sacrifice', artist, 'permanent.dies')[0], 'unresolved')   # artifact creatures exist

    def test_this_or_another_is_not_self_only(self):
        artist = self.k('Artist', ['creature'], hooks=['permanent.dies'], subject='self', filt='creature')
        self.assertTrue(self.v._self_obs(artist, 'permanent.dies'))
        artist['triggers']['permanent.dies'].update(others=True)
        self.assertFalse(self.v._self_obs(artist, 'permanent.dies'))

    def test_a_player_target_never_acts_on_a_card(self):
        drain = self.k('Artist', ['creature'], targets=['target player'])
        seer = self.k('Seer', ['creature'])
        self.assertFalse(self.v._fits_target(drain, seer, self.VOCAB))

    def test_a_legendary_card_named_by_its_short_name_is_self(self):
        # "When Sharuum enters" on Sharuum the Hegemon was read as watching every permanent enter
        self.assertIn('sharuum ', self.v._own_names('Sharuum the Hegemon', 'Legendary Artifact Creature — Sphinx'))
        self.assertIn('jet ', self.v._own_names('Jet, Freedom Fighter', 'Legendary Creature — Human Rebel'))
        self.assertNotIn('blood ', self.v._own_names('Blood Artist', 'Creature — Vampire'))

class Ontology(unittest.TestCase):
    """The DIO lookup and the grounding label run everywhere: an agent without the KB can still consult the ontology."""
    def run_cli(self, *args):
        from mtgtools.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(list(args))
        return code, json.loads(buf.getvalue())

    def test_dio_needs_no_database(self):
        code, out = self.run_cli('--db', str(ROOT / 'no_such.sqlite'), 'dio', 'persistence')
        self.assertEqual(code, 0)
        self.assertEqual(out['grounding']['level'], 'doctrine')
        self.assertEqual(out['claims'], [])
        heads = [s['heading'] for s in out['data']['sections']]
        self.assertTrue(any('6.4 The persistence table' in h for h in heads), heads)

    def test_dio_section_number_finds_that_section_first(self):
        _, out = self.run_cli('dio', '7', '--limit', '1')
        self.assertIn('7. CONNECTIONS', out['data']['sections'][0]['heading'])

    def test_dio_reads_the_addendum_numbered_headings(self):
        _, out = self.run_cli('dio', 'feedstock')
        self.assertTrue(any(s['source'].startswith('DIO v3.1.1 addendum') for s in out['data']['sections']))

    def test_missing_kb_is_labelled_and_points_to_the_bootstrap(self):
        code, out = self.run_cli('--db', str(ROOT / 'no_such.sqlite'), 'card', 'Sol Ring')
        self.assertEqual(code, 2)
        self.assertEqual(out['grounding']['level'], 'doctrine_only')
        self.assertIn('tools/kb_bootstrap.py install', out['error'])


@unittest.skipUnless(DB.exists(), 'KB database not present (data/README.md)')
class Verbs(unittest.TestCase):
    def run_cli(self, *args):
        from mtgtools.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(['--db', str(DB), *args])
        return code, json.loads(buf.getvalue())

    def test_envelope_names_its_collection(self):
        code, out = self.run_cli('context')
        self.assertEqual(code, 0)
        pinned = json.loads((ROOT / 'tools' / 'kb_release.json').read_text(encoding='utf-8'))['release']
        self.assertEqual(out['collection']['release'], pinned)
        self.assertEqual(out['grounding']['level'], 'kb_grounded')
        self.assertEqual(out['collection']['release'], 'mtg-kb-v0.2.1-r20261104')
        self.assertTrue(all({'kind', 'support', 'grade'} <= set(c) for c in out['claims']))

    def test_card_separates_oracle_text_from_contract_readings(self):
        code, out = self.run_cli('card', 'Terra, Magical Adept')
        self.assertEqual(code, 0)
        kinds = {c['kind']: c for c in out['claims']}
        self.assertEqual(kinds['rules_text']['grade'], 'decision_grade')
        mech = [c for c in out['claims'] if c['kind'] == 'mechanics']
        self.assertTrue(mech and all(c['grade'] == 'exploratory' for c in mech))   # nothing is reviewed in r20261104

    def test_explore_works_without_a_seed_and_marks_discovery(self):
        code, out = self.run_cli('explore', '--ci', 'RG', '--limit', '5')
        self.assertEqual(code, 0)
        self.assertEqual(out['data']['mode'], 'divergent')
        self.assertTrue(out['claims'])
        self.assertTrue(all(c['discovery'] == 'unrequested' for c in out['claims']))

    def test_divergent_chains_start_at_the_seed(self):
        code, out = self.run_cli('explore', 'Terra, Magical Adept', '--mode', 'divergent', '--limit', '10')
        self.assertEqual(code, 0)
        for ch in out['data']['chains']:
            self.assertTrue(ch['first']['producer'].startswith('Terra, Magical Adept'))
            self.assertEqual(ch['first']['observer'], ch['second']['producer'])
            self.assertNotEqual((ch['first']['produces'], ch['first']['hook']), (ch['second']['produces'], ch['second']['hook']))

    def test_explore_without_pool_is_an_error_not_a_guess(self):
        code, out = self.run_cli('explore')
        self.assertEqual(code, 2)
        self.assertIn('error', out)

    def test_hypothesis_reports_unverified_links(self):
        code, out = self.run_cli('hypothesis', 'Cauldron of Essence', 'Knightfisher')
        self.assertEqual(code, 0)
        self.assertTrue(out['data']['links'] or out['data']['loops'])
        self.assertTrue(out['data']['unverified_contracts'])
        self.assertTrue(out['data']['would_settle_it'])

    def run_check(self, items):
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(items, f)
        code, out = self.run_cli('check', f.name)
        self.assertEqual(code, 0)
        return out['claims']

    def test_check_grades_each_claim_by_kind(self):
        claims = self.run_check([{'text': 'owned', 'kind': 'inventory', 'cards': ['Cauldron of Essence']},
                                 {'text': 'faster', 'kind': 'performance'},
                                 {'text': 'likes it', 'kind': 'preference', 'deck': 'NoSuchDeck'}])
        self.assertEqual([c['evidence_grade'] for c in claims], ['decision_grade', 'exploratory', 'not_system_gradable'])
        # no assertion given: the source is good, but the claim itself is not checked, so it is not decision grade
        self.assertEqual([c['verdict'] for c in claims], ['NOT_CHECKED'] * 3)
        self.assertEqual(claims[0]['grade'], 'exploratory')

    # --- regressions from the Terra runs (Kate, 2026-10-27): the questions are no longer held out ---

    def test_check_never_turns_a_good_source_into_a_true_claim(self):
        claims = self.run_check([
            {'text': 'Leaves from the Vine is available for Steph', 'kind': 'inventory', 'cards': ['Leaves from the Vine']},
            {'text': 'a free copy exists', 'kind': 'inventory', 'cards': ['Leaves from the Vine'], 'assert': {'free_min': 1}},
            {'text': 'nonlegendary only', 'kind': 'rules_text', 'cards': ['Terra, Magical Adept'],
             'assert': {'text_contains': 'nonlegendary enchantment'}}])
        self.assertEqual(claims[0]['evidence_grade'], 'decision_grade')
        self.assertEqual((claims[0]['verdict'], claims[0]['grade']), ('NOT_CHECKED', 'exploratory'))
        self.assertEqual(claims[1]['verdict'], 'CONTRADICTED')          # owned 1, free 0
        self.assertEqual(claims[2]['verdict'], 'SUPPORTED')

    def test_a_true_assertion_does_not_verify_a_false_sentence(self):
        c = self.run_check([{'text': 'Leaves from the Vine has a free copy for Steph', 'kind': 'inventory',
                             'cards': ['Leaves from the Vine'], 'assert': {'owned_min': 1}}])[0]
        self.assertEqual((c['verdict'], c['verdict_on'], c['text_judged']), ('SUPPORTED', 'assertion', False))

    def hyp(self, a, b):
        code, out = self.run_cli('hypothesis', a, b)
        self.assertEqual(code, 0)
        return out['data']

    def test_copy_of_a_self_enter_enchantment_triggers_on_the_copy(self):
        d = self.hyp('Terra, Magical Adept', 'Banishing Light')
        enters = [l for l in d['links'] if l['observer'] == 'Banishing Light' and l['basis'] == 'copy_enters']
        self.assertTrue(enters)
        self.assertEqual(enters[0]['qualifiers'], 'compatible')        # C-024: the contract records the token copies its target
        self.assertTrue(any(x['actor'].startswith('Terra') and x['acts_on'] == 'Banishing Light' for x in d['acts_on']))

    def test_terra_cycle_is_a_same_card_link(self):
        d = self.hyp('Terra, Magical Adept', 'Banishing Light')
        same = [l for l in d['same_card_links'] if l['produces'] == 'card.return_to_battlefield']
        self.assertTrue(same and all(l['observer'].startswith('Terra') for l in same))

    def test_type_qualifier_rejects_era_of_innovation(self):
        d = self.hyp('Terra, Magical Adept', 'Era of Innovation')
        self.assertFalse([l for l in d['links'] if l['produces'] == 'card.return_to_battlefield'])
        self.assertTrue(any('artifact or artificer' in l['qualifier_note'] for l in d['rejected_links']))

    def test_energy_loops_are_contested_and_do_not_hide_the_card(self):
        d = self.hyp('Terra, Magical Adept', 'Decoction Module')
        self.assertFalse(d['loops'])                                   # no contract records Decoction Module putting counters
        self.assertEqual({l['kb_check'] for l in d['loops_contested']}, {'unsupported_by_contracts'})
        self.assertTrue(d['loops_contested'])
        bounce = [x for x in d['acts_on'] if x['actor'] == 'Decoction Module']
        self.assertTrue(bounce and 'card.return_to_hand' in bounce[0]['produces'])

    def test_a_finality_counter_ends_a_loop_after_one_pass(self):
        d = self.hyp('Cirith Ungol Patrol', 'Wolfbat')
        self.assertFalse(d['loops'])
        self.assertEqual({l['kb_check'] for l in d['loops_contested']}, {'once_only'})

    def test_sacrifice_outlet_links_to_aristocrat(self):
        d = self.hyp('Viscera Seer', 'Blood Artist')
        self.assertTrue(any(l['produces'] == 'permanent.sacrifice' and l['hook'] == 'permanent.dies' and l['qualifiers'] == 'compatible'
                            for l in d['links']))
        self.assertFalse(d['acts_on'])                                 # Blood Artist targets a player, not Viscera Seer

    def test_unsupported_theme_names_the_supported_ones(self):
        code, out = self.run_cli('explore', 'saga')
        self.assertEqual(code, 2)
        self.assertIn('self_mill', out['error'])

    def test_card_reports_availability_under_the_policy(self):
        code, out = self.run_cli('card', 'Leaves from the Vine')
        self.assertEqual(code, 0)
        av = out['data']['availability']
        self.assertEqual(av['usable_without_asking'], 0)
        self.assertIn('Necrobloom', av['in_other_built_decks'])

    def test_role_summary_reports_detected_candidates_not_verified_roles(self):
        # Golden Argosy was the sole "wipe" in both arms of the 2026-10-28 paired run (Kate's audit)
        code, out = self.run_cli('context', '--deck', 'Brigid')
        self.assertEqual(code, 0)
        roles = out['data']['roles']
        self.assertNotIn('single_source_roles', roles)
        self.assertNotIn('Golden Argosy', [v['card'] for v in roles['sole_detected_candidates'].values()])
        caveat = [c for c in out['claims'] if 'sole detected candidate' in c['text']]
        self.assertEqual(len(caveat), 1)
        self.assertEqual(caveat[0]['grade'], 'exploratory')

    # Zach's blind ChatGPT Merfolk test, 2026-10-31: a search for the word missed the type's generic support
    def test_typal_census_finds_members_support_and_protected_copies(self):
        code, out = self.run_cli('typal', 'Merfolk')
        self.assertEqual(code, 0)
        d = out['data']
        self.assertEqual(d['counts']['members'], 35)
        self.assertEqual(d['members_by_color_identity'], {'U': 21, 'W': 7, 'WU': 4, 'UB': 2, 'UG': 1})
        self.assertEqual(sum(m['free'] for m in d['members']), 75)
        self.assertIn('kindred', {m['kind'] for m in d['members'] if m['card'] == 'Wanderwine Farewell'})
        found = {x['card'] for g in ('every_type', 'type_support', 'names_the_type') for x in d[g]}
        for name in ('Harmonized Crescendo', 'Gathering Stone', 'Kindred Judgment', 'Kindred Summons', 'Distant Melody',
                     "Urza's Incubator", 'Omni-Changeling', 'Seahunter'):
            self.assertIn(name, found)
        for name in ('Distant Melody', "Urza's Incubator", 'Secluded Courtyard', 'Unclaimed Territory'):
            self.assertIn(name, d['held_in_protected_decks'])
        self.assertEqual({s['commander'] for s in d['commander_candidates']},
                         {'Emperor Mihail II', 'Orysa, Tide Choreographer', 'Tatyova, Steward of Tides', 'Vohar, Vodalian Desecrator'})
        self.assertEqual(d['identities_without_type_commander'], ['W', 'WU'])
        self.assertIn('Gathering Stone', d['tag_gaps'])           # the Sheet Roles tags miss it: a data-layer gap
        for k, v in d['counts'].items():                         # the counts agree with the lists they summarise
            self.assertEqual(v, len(d[k]))
        lexical = [c for c in out['claims'] if c['support'] == 'lexical_match']
        self.assertTrue(lexical and all(c['grade'] == 'exploratory' for c in lexical))

    def test_typal_rejects_a_word_no_type_line_has(self):
        code, out = self.run_cli('typal', 'Merfolkk')
        self.assertEqual(code, 2)

    # Zach's blind ChatGPT decommission test, 2026-10-31 (Auntie Ool / Blight Curse into TMNT)
    def test_deck_resolves_by_commander_name(self):
        code, out = self.run_cli('context', '--deck', 'Auntie Ool')
        self.assertEqual(code, 0)
        self.assertEqual(out['data']['deck'], 'Blight Curse')

    def test_release_separates_what_disassembly_actually_unlocks(self):
        code, out = self.run_cli('release', 'Auntie Ool', '--to', 'TMNT')
        self.assertEqual(code, 0)
        d = out['data']
        self.assertEqual((d['donor'], d['receiver']), ('Blight Curse', 'TMNT'))
        self.assertEqual(d['counts'], {'already_in_receiver': 12, 'outside_receiver_identity': 0, 'free_copy_elsewhere': 10,
                                       'unlocked_by_decommission': 60})
        self.assertEqual(sum(d['counts'].values()) + 0, 82)
        names = lambda g: {x['card'] for x in d[g]}
        self.assertIn('Devoted Druid', names('already_in_receiver'))
        self.assertIn('Nesting Grounds', names('free_copy_elsewhere'))
        self.assertIn("Puca's Covenant", names('unlocked_by_decommission'))
        self.assertTrue(all('check' in x for x in d['unlocked_by_decommission'] if x['card'] == 'Everlasting Torment'))
        # only Current deck rows count: TMNT's bench and Oops' proposed borrowing are not allocations
        code, ctx = self.run_cli('context', '--deck', 'TMNT')
        self.assertEqual(len(ctx['data']['cards']), 92)


if __name__ == '__main__':
    unittest.main()


@unittest.skipUnless(DB.exists(), 'KB database not installed (python3 tools/kb_bootstrap.py install)')
class Find(unittest.TestCase):
    """Kate's acceptance cases for find (2026-11-01): retrieval with evidence classes, never a completeness claim."""
    def run_cli(self, *args):
        from mtgtools.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(['--db', str(DB), 'find', *args])
        return code, json.loads(buf.getvalue())

    def test_sacrifice_outlets_label_one_shot_spells(self):
        _, out = self.run_cli('--role', 'sacrifice', '--ci', 'B', '--free')
        per = {x['card']: x for x in out['data']['performs']}
        self.assertTrue(per['Viscera Seer']['shape']['repeatable'])
        self.assertEqual(per['Bone Splinters']['shape']['kind'], 'one-shot spell')

    def test_payoffs_are_listed_apart_from_outlets(self):
        _, out = self.run_cli('--role', 'sacrifice', '--free', '--limit', '1000')
        performs = {x['card'] for x in out['data']['performs']}
        supports = {x['card'] for x in out['data']['supports']}
        self.assertIn('Viscera Seer', performs)
        self.assertNotIn('Viscera Seer', supports)

    def test_ci_means_commander_color_identity(self):
        _, out = self.run_cli('--role', 'protection', '--ci', 'WUB', '--free', '--limit', '500')
        self.assertTrue(all(set(x['color_identity']) <= set('WUBC') for x in out['data']['performs']))

    def test_conditional_wipe_is_flagged(self):
        _, out = self.run_cli('--role', 'wipe', '--limit', '500')
        amalia = next(x for x in out['data']['performs'] if x['card'] == 'Amalia Benavides Aguirre')
        self.assertTrue(amalia['shape']['conditional'])

    def test_protected_only_card_is_never_free(self):
        _, out = self.run_cli('--role', 'ramp', '--free', '--limit', '1000')
        self.assertNotIn('Sol Ring', {x['card'] for x in out['data']['performs']})   # every copy is in a deck

    def test_every_answer_is_nonexhaustive_and_dates_both_sources(self):
        _, out = self.run_cli('--role', 'tutor', '--ci', 'C', '--free')
        self.assertTrue(any('Nonexhaustive' in l for l in out['data']['limitations']))
        f = out['data']['freshness']
        self.assertTrue(f['kb_release'] and f['inventory_snapshot_modified_utc'])

    def test_unknown_role_lists_the_known_ones(self):
        code, out = self.run_cli('--role', 'vibes')
        self.assertEqual(code, 2)
        self.assertIn('sacrifice', out['error'])

    def test_missing_card_is_not_assumed_acquired(self):
        from mtgtools.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(['--db', str(DB), 'card', 'Cyclonic Rift'])
        self.assertIn('not owned', json.loads(buf.getvalue())['error'])


@unittest.skipUnless(DB.exists(), 'KB database not installed (python3 tools/kb_bootstrap.py install)')
class AsOf(unittest.TestCase):
    """tools/asof_kb.py: a past collection for replaying historical questions (Kate's preflight, 2026-11-04)."""
    @classmethod
    def setUpClass(cls):
        import tempfile
        sys.path.insert(0, str(ROOT / 'tools'))
        import asof_kb
        cls.tmp = tempfile.TemporaryDirectory()
        d = Path(cls.tmp.name)
        (d / 'inv.csv').write_text('name,qty\nViscera Seer,1\nBlood Artist,2\nSol Ring,1\nNo Such Card,1\n', encoding='utf-8')
        (d / 'Test.csv').write_text('name,qty,status\nBlood Artist,1,\nViscera Seer,1,proposed\n', encoding='utf-8')
        cls.man = asof_kb.build('2026-10-06', d / 'inv.csv', [d / 'Test.csv'], None, d / 'db')
        cls.db = d / 'db' / DB.name

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_cli(self, *args):
        from mtgtools.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(['--db', str(self.db), *args])
        return json.loads(buf.getvalue())

    def test_only_cards_owned_on_the_date_exist(self):
        self.assertIn('card not found', self.run_cli('card', 'Sharuum the Hegemon')['error'])
        self.assertEqual(self.man['counts']['owned_names'], 3)
        self.assertEqual(self.man['gaps']['fixture_names_not_in_kb'], {'No Such Card': 1})

    def test_planned_rows_do_not_hold_copies(self):
        a = self.run_cli('card', 'Viscera Seer')['data']
        self.assertEqual(a['custody'], {'owned': 1, 'assigned': 0, 'free': 1, 'locations': []})
        self.assertEqual(a['availability']['planned_only'], {'Test': 'proposed'})
        b = self.run_cli('card', 'Blood Artist')['data']['custody']
        self.assertEqual((b['owned'], b['assigned'], b['free']), (2, 1, 1))

    def test_todays_policy_is_not_applied(self):
        texts = [c['text'] for c in self.run_cli('context')['claims']]
        self.assertTrue(any('No collection policy is recorded' in t for t in texts))
        self.assertFalse(any('TMNT' in t for t in texts))

    def test_grounding_names_the_date(self):
        g = self.run_cli('context')['grounding']
        self.assertEqual(g['as_of'], '2026-10-06')
        self.assertEqual(g['level'], 'kb_grounded')

    def test_compare_refuses_todays_workbook(self):
        out = self.run_cli('compare', 'Test', 'Sol Ring=Blood Artist')
        self.assertIn('as-of collection', out.get('error', ''))

    def test_no_later_state_outside_card_keyed_tables(self):
        # source_sheet_rows held every sheet of the later workbook (Collection, Plans, Photo Intake ...): no card_name column,
        # so the prune missed it. It, the stored doctrine copies and the live-sheet pointers must not survive into the copy.
        import sqlite3
        c = sqlite3.connect(f'file:{self.db}?mode=ro', uri=True)
        try:
            for t in ('source_sheet_rows', 'reference_documents'):
                self.assertEqual(c.execute(f'select count(*) from {t}').fetchone()[0], 0, t)
            for k, v in c.execute("select key, value from meta where key in ('canonical_sheet_id', 'canonical_url')"):
                self.assertTrue(v.startswith('redacted:asof-'), k)
            orphan = c.execute('select count(*) from compile_losses where contract_id not in '
                               '(select contract_id from operation_contracts)').fetchone()[0]
            self.assertEqual(orphan, 0)
        finally:
            c.close()
        self.assertIn('source_sheet_rows', self.man['counts']['later_state_cleared'])
