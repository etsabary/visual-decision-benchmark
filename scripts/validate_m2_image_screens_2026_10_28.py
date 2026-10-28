"""Verify partial Apple M2 image screens without private answer keys."""
import csv,json,math,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'results/releases/local_m2_screens_2026-10-28'
def validate():
 screens=json.loads((DEST/'screens.json').read_text());rows=list(csv.DictReader((DEST/'timing.csv').open()));assert len(screens)==2 and len(rows)==40
 for s in screens:
  r=[x for x in rows if x['model']==s['model']];assert len(r)==20 and len({x['item_id'] for x in r})==20 and s['state']=='stopped_slow' and s['usable']==20 and all(x['status']=='ok' for x in r)
  t=sorted(float(x['latency_ms']) for x in r);pos=19*.95;lo=int(pos);hi=math.ceil(pos)
  for a,b in [(s['mean_ms'],statistics.mean(t)),(s['median_ms'],statistics.median(t)),(s['p95_ms'],t[lo]+(t[hi]-t[lo])*(pos-lo))]:assert math.isclose(a,b,rel_tol=1e-12)
  assert s['median_ms']>2000
 assert [s['correct'] for s in screens]==[9,13] and json.loads((DEST/'audit_receipt.json').read_text())['full_bank_results'] is False
 for p in [ROOT/'README.md',ROOT/'docs/report.html']:
  t=p.read_text();assert all(x in t for x in ['Apple M2','9/20','13/20','4,709 ms','3,323 ms'])
 print('PASS: two 20-question M2 image speed screens; timing verified and excluded from 200-question rankings.')
if __name__=='__main__':validate()
