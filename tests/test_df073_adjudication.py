"""DF069 fabricated attacks integrated into DF072; no archived model outputs."""
from pathlib import Path
import copy, json, unittest
import df069_adjudication as core
ROOT=Path(__file__).resolve().parents[1]
CASES=json.loads((ROOT/'fixtures/df069_synthetic_attacks.json').read_bytes())['cases']
class DF073Adjudication(unittest.TestCase):
    def test_thirty_independent_expected_verdicts_and_evidence_boundaries(self):
        self.assertEqual(len(CASES),30)
        for row in CASES:
            with self.subTest(case=row['id']):
                request=copy.deepcopy(row['request'])
                before=core.canonical(request)
                try:
                    result=core.adjudicate(request)
                except core.EvidenceRejected:
                    self.assertEqual(row['expected']['gate'],'REJECTED_INPUT')
                else:
                    expected=row['expected']; actual=result['adjudication']
                    self.assertEqual(actual['status'],expected['gate'])
                    self.assertEqual(actual['difference'],expected['difference'])
                    self.assertEqual(len(result['excluded_noncomparable']),expected['excluded'])
                    self.assertFalse(actual['physical_shortage_confirmed'])
                    self.assertFalse(result['legal_entitlement_determined'])
                    self.assertFalse(result['actual_missing_goods_identified'])
                    self.assertEqual(result['external_calls'],0)
                    for key in ('privacy_outbound_allowed','data_export_approved','human_source_final_approved','automatic_customs_action_authorized'):
                        self.assertFalse(result['review'][key])
                    nodes={n['id'] for n in result['evidence_graph']}
                    self.assertTrue(all(set(n['depends_on'])<=nodes for n in result['evidence_graph']))
                    projected=json.dumps(core.public_projection(result))
                    self.assertTrue(all(doc['source_sha256'] not in projected for doc in request['documents']))
                self.assertEqual(core.canonical(request),before)
    def test_import_is_the_frozen_competition_engine(self):
        import hashlib
        self.assertEqual(hashlib.sha256((ROOT/'integration/df069_adjudication.py').read_bytes()).hexdigest(),
                         '6dc5e8f2031999d9d9aa715450050156ae05c77ce185bd0d85784d180fb48ca3')
    def test_browser_lab_reproduces_all_engine_results(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('df073_builder',ROOT/'scripts/df073_build_adjudication.py')
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertEqual((ROOT/'docs/adjudication-data.json').read_bytes(),module.content())
if __name__=='__main__': unittest.main()
