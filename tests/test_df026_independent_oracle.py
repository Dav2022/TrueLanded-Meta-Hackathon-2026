"""Independent DF-026 arithmetic and ranking oracle, fictional case ONLY."""
from __future__ import annotations
import unittest,hashlib,json
from decimal import Decimal
from fractions import Fraction
import df021_planner as planner
import df023_proof_impact as impact
import df023_timeline as timeline
import evidence_graph as graph
import indie_core as base

WEIGHT={'QTY_MISMATCH':3,'VALUE_MISMATCH':4,'PACKING_MISMATCH':2,'TECHNICAL_GAP':2}
COVERAGE={
 'REQ_RECONCILED_INVOICE':{'QTY_MISMATCH','VALUE_MISMATCH'},
 'REQ_PACKING_CONFIRMATION':{'QTY_MISMATCH','PACKING_MISMATCH'},
 'REQ_PRICE_BREAKDOWN':{'VALUE_MISMATCH'},
 'REQ_CARTON_COUNT':{'PACKING_MISMATCH'},
 'REQ_TECH_SHEET':{'TECHNICAL_GAP'},
 'REQ_FACTORY_CONFIRMATION':{'TECHNICAL_GAP'},
}
COST={
 'direct_source_is_faster':{
 'REQ_RECONCILED_INVOICE':(1,1,1),'REQ_PACKING_CONFIRMATION':(3,4,2),
 'REQ_PRICE_BREAKDOWN':(2,2,2),'REQ_CARTON_COUNT':(2,2,2),
 'REQ_TECH_SHEET':(1,2,1),'REQ_FACTORY_CONFIRMATION':(4,5,3)},
 'supplier_and_factory_are_faster':{
 'REQ_RECONCILED_INVOICE':(4,5,2),'REQ_PACKING_CONFIRMATION':(1,1,1),
 'REQ_PRICE_BREAKDOWN':(1,1,2),'REQ_CARTON_COUNT':(1,2,1),
 'REQ_TECH_SHEET':(4,5,3),'REQ_FACTORY_CONFIRMATION':(1,1,1)},
}
STATES=(
 ({'QTY_MISMATCH','TECHNICAL_GAP'},31,Decimal('139.50'),None),
 ({'QTY_MISMATCH','TECHNICAL_GAP'},31,Decimal('139.50'),'CONFIRM_PACKING_28'),
 ({'VALUE_MISMATCH','TECHNICAL_GAP'},28,Decimal('139.50'),'REVISED_INVOICE_28_13950'),
 ({'TECHNICAL_GAP'},28,Decimal('126.00'),'REVISED_INVOICE_28_12600'),
)

def oracle_rank(obligations,profile):
 rows=[]
 for req,target in COVERAGE.items():
  matched=sorted(obligations&target)
  if matched:
   score=Fraction(sum(WEIGHT[x] for x in matched),sum(COST[profile][req]))
   rows.append((req,matched,score))
 return sorted(rows,key=lambda r:(-r[2],r[0]))

def stable_digest(obj):
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

class IndependentOracleTests(unittest.TestCase):
 def test_profiles_match_explicit_cost_fixture(self):
  self.assertEqual(graph.PROFILES,COST)
  self.assertEqual(planner.WEIGHTS,WEIGHT)
  self.assertEqual({k:set(v) for k,v in base.PROPOSALS.items()},COVERAGE)
 def test_four_stages_both_profiles_against_rational_arithmetic(self):
  for profile in COST:
   for stage,(obligations,qty,total,event) in enumerate(STATES):
    with self.subTest(profile=profile,stage=stage):
     path=timeline.journey(stage,profile=profile)
     now=path['current']
     self.assertEqual(set(now['open_obligations']),obligations)
     self.assertEqual(now['latest_event'],event)
     self.assertEqual(now['scenario_invoice_quantity'],qty)
     self.assertEqual(Decimal(now['scenario_invoice_total_usd']),total)
     self.assertEqual(Decimal(now['quantity_times_unit_price_usd']),Decimal(qty)*Decimal('4.50'))
     ranking=oracle_rank(obligations,profile)
     self.assertEqual([x['request_id'] for x in now['next_proof_ranked']],[x[0] for x in ranking])
     for found,(name,covered,exact_score) in zip(now['next_proof_ranked'],ranking):
      self.assertEqual(found['may_address'],covered)
      self.assertEqual(Decimal(str(found['fictional_efficiency'])),Decimal(str(round(float(exact_score),4))))
     self.assertFalse(now['issuer_authenticated'])
     self.assertFalse(now['proof_request_issued'])
     self.assertTrue(now['human_review_required'])
     self.assertFalse(now['human_override_or_clearance'])
 def test_stage_changes_and_arithmetic_disagreement(self):
  phases=timeline.journey(3)['history']
  self.assertEqual([p['newly_exposed_since_previous'] for p in phases[1:]],
    [[],['VALUE_MISMATCH'],[]])
  self.assertEqual([p['conditionally_reconciled_since_previous'] for p in phases[1:]],
    [[],['QTY_MISMATCH'],['VALUE_MISMATCH']])
  self.assertEqual(Decimal(phases[2]['arithmetic_delta_usd']),Decimal('-13.50'))
  self.assertEqual(Decimal(phases[3]['arithmetic_delta_usd']),Decimal('0.00'))
 def test_author_derived_hash_chain_and_unchanged_sources(self):
  for profile in COST:
   result=timeline.journey(3,profile=profile)
   prev=None
   for n,p in enumerate(result['history']):
    self.assertEqual(p['previous_chain_hash'],prev)
    content={k:v for k,v in p.items() if k!='chain_hash'}
    self.assertEqual(p['chain_hash'],stable_digest(content))
    prev=p['chain_hash']
    self.assertEqual(p['source_invoice_quantity'],31)
    self.assertFalse(p['source_invoice_modified'])
   self.assertTrue(result['hash_chain_is_author_derived_not_signature'])
 def test_tampered_event_bytes_are_denied(self):
  for event,text in impact.SYNTHETIC_DOCUMENTS.items():
   with self.subTest(event=event):
    with self.assertRaises(impact.ProofImpactRefusal):
     impact.reassess(event,supplied_bytes=text.encode('utf8')+b'\nMALICIOUS')
 def test_planner_profile_flip_preserves_source(self):
  a=planner.plan(profile='direct_source_is_faster')
  b=planner.plan(profile='supplier_and_factory_are_faster')
  self.assertEqual(a['source_anchor_sha256'],b['source_anchor_sha256'])
  self.assertNotEqual(a['requests'][0]['request_id'],b['requests'][0]['request_id'])
  self.assertEqual(a['ranking_stability'],'SENSITIVE_TO_ASSUMPTIONS')
  self.assertTrue(a['potential_coverage_not_verified_resolution'])

if __name__=='__main__':unittest.main()