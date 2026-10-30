"""Offline coverage, cost, presentation and preservation checks for October30."""
import csv,math,re,statistics
from collections import Counter
from decimal import Decimal
from urllib.parse import urlsplit
from validate_llm_image_reference_2026_10_25 import Page,percentile
# Public validation intentionally has only standard-library dependencies.
import hashlib,json
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];NAME='native_updates_2026-10-30'
def load(p):return json.loads(Path(p).read_text())
def rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
b=SimpleNamespace(ROOT=ROOT,NAME=NAME,DEST=ROOT/'results/releases'/NAME,OLD=ROOT/'results/releases/native_updates_2026-10-27',ARCHIVE=ROOT/'results/archives/presentation_before_october30_2026',MID='baseten_joey1',load=load,rows=rows,digest=digest)

def historical(path):
 rel=path.relative_to(b.ROOT).as_posix();manifest=b.load(b.ARCHIVE/'manifest.json')
 if rel not in manifest['files']:return path
 saved=b.ARCHIVE/rel;assert b.digest(saved)==manifest['files'][rel]['sha256'];return saved

def validate():
 s=b.load(b.DEST/'summary.json');old=b.load(b.OLD/'summary.json');c=b.load(b.DEST/'clairic_compatibility.json')
 assert (len(s['models']),s['complete_routes'],s['hosted_model_count'],s['complete_first_attempt_cases'])==(22,22,19,4400)
 assert all(s['models'][k]==v for k,v in old['models'].items()) and set(s['models'])-set(old['models'])=={b.MID}
 assert s['llm_speed_stops']==old['llm_speed_stops'] and s['exclusions']==old['exclusions']
 assert s['rank_order']==sorted(s['models'],key=lambda k:(-s['models'][k]['correct'],s['models'][k]['median_ms']))
 assert s['rank_order'][:3]==old['rank_order'][:3] and len(s['decision_model_ids'])==21
 qq={q['candidate_id']:q for q in b.rows(b.ROOT/'data/questions.jsonl')};assets={a['asset_id']:a['sha256'] for a in b.rows(b.ROOT/'data/assets.jsonl')}
 rows=b.rows(b.DEST/'october30_timing_evidence.jsonl');assert len(rows)==220
 for mid,n,expected,cost in [(b.MID,200,94,Decimal('.00234504')),('clairic_extraction',20,9,Decimal('.00238230'))]:
  a=[r for r in rows if r['model_id']==mid];m=s['models'][mid] if mid==b.MID else c
  assert len(a)==len({r['item_id'] for r in a})==n and [r['request_index'] for r in a]==list(range(1,n+1))
  assert Counter(r['family_id'] for r in a)==({f:10 for f in s['families']} if n==200 else Counter(qq[r['item_id']]['family_id'] for r in a))
  for r in a:
   assert r['attempt']==1 and r['family_id']==qq[r['item_id']]['family_id'] and r['image_sha256']==[assets[i] for i in qq[r['item_id']]['asset_ids']]
   assert len(r['request_sha256'])==len(r['response_sha256'])==len(r['question_sha256'])==64
  assert m['correct']==expected and m['n']==n
  assert math.isclose(m['mean_ms'],statistics.mean(r['latency_ms'] for r in a),rel_tol=1e-12) and m['median_ms']==statistics.median(r['latency_ms'] for r in a)
  assert math.isclose(m['p95_ms'],percentile([r['latency_ms'] for r in a]),rel_tol=1e-12)
  assert sum(Decimal(r['reported_cost_usd']) for r in a)==cost
 assert c['included_in_full_ranking'] is False and c['full_bank'] is False and c['statuses']=={'ok':19,'invalid_answer':1}
 m=s['models'][b.MID];assert sum(v['correct'] for v in m['families'].values())==94 and all(v['n']==v['usable']==10 for v in m['families'].values())
 assert m['reported_output_tokens']==200 and m['admission_probes']==5 and m['retries']==0
 assert len(list(csv.DictReader((b.DEST/'family_scores.csv').open())))==440
 from build_image_site import build
 build()
 for path,base in [(b.ROOT/'docs/report.html',b.ROOT/'_site'),(b.DEST/'report.html',b.ROOT/'_site'/b.NAME)]:
  text=path.read_text();p=Page();p.feed(text);assert p.rows==s['rank_order'] and len(p.cells)==440
  assert all(t in text for t in ['22 complete routes','Joey-1','94/200','Clairic','9/20','177','✦','#d97706','#7c3aed'])
  for cell in p.cells:assert int(cell['data-correct'])==s['models'][cell['data-model-id']]['families'][cell['data-family']]['correct']
  for link in p.links:
   u=urlsplit(link)
   if not u.scheme and not u.netloc and u.path:assert (base/u.path).exists(),(path,link)
   elif not u.path and u.fragment:assert u.fragment in p.ids,(path,link)
 # The separate177 subset tables survive exactly; only the complete200 table changes.
 oldhtml=historical(b.ROOT/'docs/report.html').read_text();live=(b.ROOT/'docs/report.html').read_text()
 for table in re.findall(r'<table\b.*?</table>',oldhtml,re.S):
  if 'data-subset-model=' in table:assert table in live
 for path in b.DEST.iterdir():
  if path.is_file():assert path.read_bytes()==(b.ROOT/'docs'/b.NAME/path.name).read_bytes()
  if path.suffix in ['.json','.jsonl','.csv','.md','.svg','.html']:
   text=path.read_text();assert all(x not in text for x in ['/Users/','192.168.','"choice":','"probabilities":','"correct_option_id":','API_KEY='])
 for name,h in b.load(b.DEST/'manifest.json')['artifacts'].items():assert b.digest(b.DEST/name)==h,name
 print('PASS:22 full image routes;21 prior records unchanged;220 new timings;440 category cells;177subset preserved; Clairic partial.')
 return s
if __name__=='__main__':validate()
