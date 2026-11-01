"""DF021 synthetic, no cloud/network spend. New hackathon code only."""
import copy
import unittest
from unittest.mock import patch
import df021_planner
import indie_core

class DF021PlannerTests(unittest.TestCase):
    def test_original_obligations(self):
        p=df021_planner.plan()
        self.assertEqual(p["open_obligations"],["QTY_MISMATCH","TECHNICAL_GAP"])
        self.assertIsNone(p["operational_plan"])
        self.assertFalse(p["execute_request_authorized"])
        self.assertTrue(p["human_review_required"])
    def test_counterfactual_cascade(self):
        a=df021_planner.plan()
        b=df021_planner.plan(invoice_quantity=28)
        self.assertEqual(b["open_obligations"],["TECHNICAL_GAP","VALUE_MISMATCH"])
        self.assertEqual(a["source_anchor_sha256"],b["source_anchor_sha256"])
        self.assertEqual(b["changes"]["opened_obligations"],["VALUE_MISMATCH"])
        self.assertEqual(b["changes"]["resolved_checks"],["invoice_vs_packing"])
        self.assertEqual(b["changes"]["opened_checks"],["invoice_value_arithmetic"])
        self.assertTrue(b["source_documents_unchanged"])
    def test_profile_flip(self):
        x=df021_planner.plan()
        self.assertEqual(x["ranking_stability"],"SENSITIVE_TO_ASSUMPTIONS")
        self.assertNotEqual(*x["rank_winner_by_profile"].values())
        y=df021_planner.plan(profile="supplier_and_factory_are_faster")
        self.assertEqual(y["requests"][0]["request_id"],
                         x["rank_winner_by_profile"]["supplier_and_factory_are_faster"])
        self.assertNotEqual(x["requests"][0]["request_id"],y["requests"][0]["request_id"])
    def test_rank_order_is_deterministic(self):
        for profile in df021_planner.ALLOWED_PROFILES:
            for qty in (None,28):
                a=df021_planner.plan(invoice_quantity=qty,profile=profile)
                b=df021_planner.plan(invoice_quantity=qty,profile=profile)
                self.assertEqual(a,b)
                self.assertEqual(a["result_sha256"],b["result_sha256"])
                scores=[r["scores_by_profile"][profile]["fictional_efficiency"]
                        for r in a["requests"]]
                self.assertEqual(scores,sorted(scores,reverse=True))
    def test_reject_invalid_profile_and_hypotheses(self):
        for profile in ("",None,[],{}, "hack", "__class__"):
            with self.subTest(profile=profile),self.assertRaises(df021_planner.PlannerRefusal):
                df021_planner.plan(profile=profile)
        for qty in (0,True,1,29,31.0,10000,"28",None if False else 32):
            with self.subTest(qty=qty),self.assertRaises(df021_planner.PlannerRefusal):
                df021_planner.plan(invoice_quantity=qty)
    def test_request_never_evidence_or_approval(self):
        for qty in (None,28):
            for profile in df021_planner.ALLOWED_PROFILES:
                x=df021_planner.plan(invoice_quantity=qty,profile=profile)
                self.assertFalse(x["model_inference_performed"])
                self.assertTrue(x["historical_muse_result_is_not_for_this_scenario"])
                self.assertTrue(x["potential_coverage_not_verified_resolution"])
                self.assertTrue(all(r["does_not_resolve"] for r in x["requests"]))
                self.assertTrue(all(r["source"]=="FICTIONAL_REQUEST_NOT_ACQUIRED"
                                    for r in x["requests"]))
    def test_spotlight_exact_source(self):
        x=df021_planner.spotlight()
        self.assertEqual(x["quote"],"QUANTITY: 31 PCS")
        self.assertEqual(x["source_line"],3)
        self.assertEqual(x["pdf_url"],"/api/pdf/invoice.pdf")
        self.assertEqual(x["text_lines"][x["source_line"]-1],x["quote"])
        self.assertFalse(x["model_generated_bbox"])
        self.assertEqual(x["pdf_region_status"],"NOT_MODEL_LOCALIZED")
        self.assertFalse(x["issuer_authenticated"])
    def test_spotlight_refuses_source_tampering(self):
        original=indie_core.DOCS["invoice.txt"]
        with patch.dict(indie_core.DOCS,{"invoice.txt":original.replace(
                "QUANTITY: 31 PCS","QUANTITY: 31 PCS"+chr(10)+"QUANTITY: 31 PCS")}):
            with self.assertRaises(indie_core.EngineRefusal):
                df021_planner.spotlight()
    def test_no_unearned_coverage(self):
        for qty in (None,28):
            x=df021_planner.plan(invoice_quantity=qty)
            needed=set(x["open_obligations"])
            for r in x["requests"]:
                self.assertTrue(set(r["may_address"])<=needed)
                self.assertTrue(r["may_address"])
                for s in r["scores_by_profile"].values():
                    self.assertGreater(s["fictional_efficiency"],0)
                    self.assertEqual(s["weighted_coverage"],
                        sum(df021_planner.WEIGHTS[o] for o in r["may_address"]))
    def test_isolated_branch_nonmutation(self):
        original=copy.deepcopy(indie_core.DOCS)
        for q in (None,28):
            df021_planner.plan(invoice_quantity=q)
        self.assertEqual(indie_core.DOCS,original)

if __name__=="__main__": unittest.main()
