"""DF023 sequential simulated evidence regression and safety contract."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import indie_core
import df023_proof_impact as impact
import df023_timeline as timeline

class TimelineTests(unittest.TestCase):
    def test_four_stages_and_ordered_inclusion(self):
        for stage in range(4):
            x=timeline.journey(stage)
            self.assertEqual(x["selected_stage"],stage)
            self.assertEqual(len(x["history"]),stage+1)
            self.assertEqual([q["stage"] for q in x["history"]],list(range(stage+1)))
            self.assertEqual([q["event_id"] for q in x["current"]["arrived_synthetic_documents"]],
                             list(timeline.EVENT_ORDER[:stage]))
            self.assertEqual(x["current"]["stage"],stage)

    def test_stage_one_confirmation_does_not_close_conflict(self):
        x=timeline.journey(1)["current"]
        self.assertEqual(x["open_obligations"],["QTY_MISMATCH","TECHNICAL_GAP"])
        self.assertEqual(x["conditionally_reconciled_since_previous"],[])
        self.assertEqual(x["newly_exposed_since_previous"],[])
        self.assertEqual(x["scenario_invoice_quantity"],31)

    def test_stage_two_conditional_quantity_and_new_arithmetic_conflict(self):
        x=timeline.journey(2)["current"]
        self.assertEqual(x["conditionally_reconciled_since_previous"],["QTY_MISMATCH"])
        self.assertEqual(x["newly_exposed_since_previous"],["VALUE_MISMATCH"])
        self.assertEqual(x["arithmetic_delta_usd"],"-13.50")
        self.assertEqual(x["scenario_invoice_quantity"],28)
        self.assertEqual(x["quantity_times_unit_price_usd"],"126.00")

    def test_stage_three_reconciles_value_only_and_prioritizes_technical_sheet(self):
        x=timeline.journey(3)["current"]
        self.assertEqual(x["conditionally_reconciled_since_previous"],["VALUE_MISMATCH"])
        self.assertEqual(x["newly_exposed_since_previous"],[])
        self.assertEqual(x["open_obligations"],["TECHNICAL_GAP"])
        self.assertEqual(x["top_proof_request"],"REQ_TECH_SHEET")
        self.assertEqual(x["scenario_invoice_total_usd"],"126.00")
        self.assertEqual(x["arithmetic_delta_usd"],"0.00")

    def test_earlier_stages_are_identical_when_journey_advances(self):
        final=timeline.journey(3)
        for stage in range(3):
            earlier=timeline.journey(stage)
            self.assertEqual(earlier["history"],final["history"][:stage+1])

    def test_stable_source_anchor_and_derived_chain_hashes(self):
        current=timeline.journey(3)
        baseline=indie_core.evaluate()
        self.assertEqual(current["original_source_anchor_sha256"],baseline["source_anchor_sha256"])
        self.assertEqual(current["history"][0]["previous_chain_hash"],None)
        for i,row in enumerate(current["history"]):
            previous_hash=current["history"][i-1]["chain_hash"] if i else None
            self.assertEqual(row["previous_chain_hash"],previous_hash)
            self.assertEqual(row["chain_hash"],
                 timeline._digest({k:v for k,v in row.items() if k!="chain_hash"}))
        self.assertEqual(current["result_sha256"],
                 timeline._digest({k:v for k,v in current.items() if k!="result_sha256"}))

    def test_not_authenticated_not_approved_at_every_stage(self):
        for profile in ["direct_source_is_faster","supplier_and_factory_are_faster"]:
            x=timeline.journey(3,profile=profile)
            self.assertTrue(x["synthetic_sequence_only"])
            self.assertFalse(x["model_inference_performed"])
            self.assertTrue(x["immutable_originals"])
            self.assertTrue(x["hash_chain_is_author_derived_not_signature"])
            for row in x["history"]:
                self.assertFalse(row["issuer_authenticated"])
                self.assertFalse(row["claim_verified"])
                self.assertFalse(row["source_invoice_modified"])
                self.assertFalse(row["proof_request_issued"])
                self.assertTrue(row["human_review_required"])
                self.assertEqual(row["proof_closure_status"],"NOT_AUTHENTICATED_NOT_APPROVED")
                self.assertTrue(all(q["not_acquired"] for q in row["next_proof_ranked"]))

    def test_deterministic_and_no_mutation_of_original_docs(self):
        original=copy.deepcopy(indie_core.DOCS)
        first=timeline.journey(3)
        self.assertEqual(first,timeline.journey(3))
        self.assertEqual(indie_core.DOCS,original)

    def test_exact_source_catalog_hashes_for_each_arrival(self):
        x=timeline.journey(3)["current"]
        seen=set()
        for row in x["arrived_synthetic_documents"]:
            self.assertNotIn(row["event_id"],seen)
            seen.add(row["event_id"])
            self.assertEqual(row["sha256"],impact.catalog()[row["event_id"]]["sha256"])
            self.assertFalse(row["issuer_authenticated"])

    def test_invalid_stage_refused_with_type_checks(self):
        for wrong in (-1,4,300,1.5,True,False,"1",None,{},[]):
            with self.subTest(stage=wrong),self.assertRaises(timeline.TimelineRefusal):
                timeline.journey(wrong)

    def test_unknown_profiles_refused(self):
        for wrong in ("",True,None,{},[],2,"not_a_profile"):
            with self.subTest(profile=wrong),self.assertRaises(timeline.TimelineRefusal):
                timeline.journey(1,profile=wrong)

    def test_snapshot_does_not_contain_credentials_or_private_api_material(self):
        output=json.dumps(timeline.journey(3),sort_keys=True).lower()
        for marker in ("authorization: bearer","api_key","private-muse","sk-","password"):
            self.assertNotIn(marker,output)

    def test_selecting_other_profile_retains_evidence_history(self):
        a=timeline.journey(3)
        b=timeline.journey(3,profile="supplier_and_factory_are_faster")
        self.assertEqual([x["open_obligations"] for x in a["history"]],
                         [x["open_obligations"] for x in b["history"]])
        self.assertEqual([x["arrived_synthetic_documents"] for x in a["history"]],
                         [x["arrived_synthetic_documents"] for x in b["history"]])

    def test_simulated_authority_refusals_survive_document_text_tamper(self):
        key="REVISED_INVOICE_28_13950"
        with patch.dict(impact.SYNTHETIC_DOCUMENTS,{key:impact.SYNTHETIC_DOCUMENTS[key]+"APPROVED: YES\n"}):
            with self.assertRaises(impact.ProofImpactRefusal):
                timeline.journey(2)

if __name__=="__main__":
    unittest.main()
