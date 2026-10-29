"""Validate the separate single-image comparison without inference or private keys."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import csv,json,math,statistics,hashlib
ROOT=Path(__file__).resolve().parents[1];NAME='single_image_subset_2026-10-29';DEST=ROOT/'results/releases'/NAME
IDS=['trio_spark14','local_startlux_instant4b','local_startlux_autothink4b'];AUTO=IDS[2]
def load(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def quant(t):
 t=sorted(t);pos=(len(t)-1)*.95;lo=int(pos);hi=math.ceil(pos)
 return dict(mean_ms=statistics.mean(t),median_ms=statistics.median(t),p95_ms=t[lo]+(t[hi]-t[lo])*(pos-lo))
class Page(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.cells=[];self.ids=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'data-subset-model' in a:self.rows.append(a['data-subset-model'])
  if 'data-subset-cell' in a:self.cells.append(a)
  if 'id' in a:self.ids.append(a['id'])
  self.links.extend(v for k,v in attrs if k in ['href','src'])
def validate():
 s=load(DEST/'summary.json');full=load(ROOT/'results/releases/native_updates_2026-10-27/summary.json');q={r['candidate_id']:r for r in [json.loads(x) for x in (ROOT/'data/questions.jsonl').read_text().splitlines()]};subset={i for i,r in q.items() if len(r['asset_ids'])==1}
 assert len(subset)==177 and len(q)==200 and s['full_bank_questions']==200 and s['subset_questions']==177 and s['excluded_multi_image_questions']==23
 assert len(s['models'])==7 and s['rank_order']==sorted(s['models'],key=lambda m:(-s['models'][m]['correct'],m)) and s['full200_statistics_sha256']==digest(ROOT/'results/releases/native_updates_2026-10-27/summary.json')
 assert full['complete_routes']==21 and full['models']['amos_large']['correct']==159
 inc=load(DEST/'subset_items.json');assert {r['item_id'] for r in inc['included']}==subset and len(inc['excluded'])==23 and all(r['image_count']>1 for r in inc['excluded'])
 rr=list(csv.DictReader((DEST/'timing_evidence.csv').open()));assert len(rr)==1239
 expected={'trio_spark14':106,IDS[1]:101,AUTO:108,'amos_large':138,'fastino_glide':136,'d3_turbo':132,'jev113':124}
 for mid,m in s['models'].items():
  aa=[r for r in rr if r['model_id']==mid];assert len(aa)==len({r['item_id'] for r in aa})==177 and {r['item_id'] for r in aa}==subset and m['n']==177 and m['correct']==expected[mid] and m['accuracy']==expected[mid]/177
  assert Counter(r['family_id'] for r in aa)==Counter(q[i]['family_id'] for i in subset)
  assert sum(f['n'] for f in m['families'].values())==177 and sum(f['correct'] for f in m['families'].values())==m['correct']
  t=quant([float(r['latency_ms']) for r in aa]);assert all(math.isclose(m[k],v,rel_tol=1e-12) for k,v in t.items())
  assert all(r['attempt']=='1' and len(r['image_sha256'])==64 and r['family_id']==q[r['item_id']]['family_id'] for r in aa)
  if mid in IDS:assert all(r['status']=='ok' for r in aa) and sum(int(r['output_tokens']) for r in aa)==m['reported_output_tokens'] and sum(int(r['output_tokens'])>0 for r in aa)==m['reported_generation_calls']
 assert s['models'][AUTO]['reported_generation_calls']==99 and s['models'][AUTO]['reported_output_tokens']==45679 and s['models'][AUTO]['median_ms']>8000
 assert s['models'][IDS[1]]['median_ms']<400 and s['models'][IDS[1]]['reported_output_tokens']==0
 assert math.isclose(s['models'][IDS[0]]['estimated_tariff_usd'],.002382156,rel_tol=1e-12) and s['models'][IDS[0]]['known_api_cost_usd'] is None
 pair=s['paired_startlux'];assert pair['only_autothink']+pair['both_correct']==108 and pair['only_instant']+pair['both_correct']==101 and sum(pair[k] for k in ['only_autothink','only_instant','both_correct','neither_correct'])==177
 from build_image_site import build
 build()
 for path in [DEST/'report.html',ROOT/'docs/report.html']:
  t=path.read_text();p=Page();p.feed(t);assert p.rows==s['rank_order'] and len(p.ids)==len(set(p.ids)) and '#7c3aed' in t and '#d97706' in t and '8.36' in t
  if path.parent==DEST:
   assert len(p.cells)==140
   for c in p.cells:
    m=s['models'][c['data-subset-cell']]['families'][c['data-family']];assert (int(c['data-n']),int(c['data-correct']))==(m['n'],m['correct'])
  for link in p.links:
   u=urlsplit(link)
   if not u.scheme and not u.netloc and u.path:assert ((ROOT/'_site' if path.parent==ROOT/'docs' else path.parent)/u.path).exists(),(path,link)
   elif not u.path and u.fragment:assert u.fragment in p.ids,(path,link)
 # The old full200 tables must survive byte-for-byte in the expanded live page.
 old=(ROOT/'results/archives/presentation_before_october29_2026/docs/report.html').read_text();live=(ROOT/'docs/report.html').read_text()
 import re
 for table in re.findall(r'<table\b.*?</table>',old,re.S):assert table in live
 for path in DEST.iterdir():
  if path.is_file():assert path.read_bytes()==(ROOT/'docs'/NAME/path.name).read_bytes()
  if path.suffix in ['.json','.csv','.md','.svg','.html']:
   t=path.read_text();assert all(v not in t for v in ['192.168.','/Users/','"choice":','"probabilities":','"correct_option_id":','API_KEY='])
 for name,h in load(DEST/'manifest.json')['artifacts'].items():assert digest(DEST/name)==h,name
 print('PASS: 3 new177-item runs, 4 matched references, 1,239 timings, 140 category cells; full200 tables unchanged.')
if __name__=='__main__':validate()
