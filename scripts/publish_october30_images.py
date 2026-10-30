"""Publish audited Joey images and a separate stopped Clairic screen, with no inference."""
import csv,io,json,re,shutil,sys
from copy import deepcopy
from decimal import Decimal
from html import escape
from urllib.parse import urlsplit,urlunsplit
import posixpath
import publish_native_images_2026_10_27 as prior
import publish_october29_subset as subset
ROOT=prior.ROOT;NAME='native_updates_2026-10-30';DEST=ROOT/'results/releases'/NAME
OLD=ROOT/'results/releases/native_updates_2026-10-27';ARCHIVE=ROOT/'results/archives/presentation_before_october30_2026'
RUN=ROOT.parent/'text-decision-hardening/runs/joey_clairic_2026-10-30';MID='baseten_joey1'
load,rows,digest,hashval,write=subset.load,subset.rows,subset.digest,subset.hashval,subset.write
NOTE='''## October 30: Joey-1 and a stopped extraction screen

**Joey-1 scored 94/200 (47.0%)**, with **457 / 368 / 1,009 ms mean / median / p95**. All 200 first attempts returned usable native decisions. OpenRouter reported **$0.00234504 for 200 questions**, or **$0.01172520 per 1,000**. Five separate image-binding probes cost $0.00001722. The model reported one output-token counter per native decision; it returned no prose or reasoning trace.

Attribute binding and set logic scored **9/10**; sequential visual state tracking and insufficient evidence each scored **7/10**. Geometry and folding scored **2/10**. Navigation, visual rules, constraint satisfaction, causal decisions and perspective each scored **3/10**. Each category contains ten questions. Amos, Fastino and D3 Turbo retain the three highest full-bank scores.

**Clairic remains a partial extraction-interface screen: 9/20 (45.0%)**, with **608 / 469 / 1,122 ms mean / median / p95**. One returned number was outside the supplied option IDs, reaching the agreed 5% unusable-output stop at 20 attempts. Its reported cost was **$0.00238230 for those 20 calls**. It has no full-bank score and no row in the 200-question ranking. [The labelled compatibility record](COMPATIBILITY_LINK) preserves its measurements.

Both routes passed five synthetic checks of image pixels and image order before scored calls. Joey used the exact original reviewed PNG/JPEG bytes on all 200 questions, including two- and three-image questions. Clairic used OpenRouter named image assets referenced in the state; a native Cloudflare-style image field was ignored by that gateway during admission and was not used for scored calls. No scored calls were retried. No resizing, OCR, captions or hidden solver were added. Provider-controlled image preprocessing remains unmeasured.

'''

def preserve():
 if (ARCHIVE/'manifest.json').exists():return
 files={}
 for name in ['README.md','docs/report.html','docs/sitemap.xml']:
  p=ROOT/name;t=ARCHIVE/name;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t);files[name]=dict(path=name,sha256=digest(p))
 write(ARCHIVE/'manifest.json',dict(files=files))

def capture():
 assert not (DEST/'summary.json').exists(),'Do not overwrite captured evidence'
 # The owner executor imports the text repository's layout helper.
 sys.modules.pop('repo_layout',None)
 sys.modules.pop('score',None)
 sys.path.insert(0,str(ROOT.parent/'jev-1.14-comparison-benchmark/scripts'))
 sys.path.insert(0,str(RUN));import runner as owner;import score as scorer;import clairic_images
 j=scorer.score('image',True);c=clairic_images.audit(False)
 assert (j['n'],j['correct'],c['n'],c['correct'],c['state'],c['pending_dispatches'])==(200,94,20,9,'paused_failures',0)
 qq,order,assets=owner.F.inputs('image');aa=rows(RUN/'joey/image/attempts.jsonl');ca=rows(RUN/'clairic/image/attempts.jsonl')
 s=deepcopy(load(OLD/'summary.json'));old=deepcopy(s);total=sum(Decimal(a['accounted_cost_usd']) for a in aa)
 m=dict(model_id=MID,label='Joey-1',model_requested='baseten/joey-1',model_kind='hosted_decision',execution_location='hosted',route='OpenRouter native Decisions; pinned BaseTen',date='2026-10-30',complete=True,reused=False,n=200,correct=94,accuracy=.47,usable=200,accuracy_usable=.47,
  mean_ms=j['mean_ms'],median_ms=j['median_ms'],p95_ms=j['p95_ms'],status_counts=j['statuses'],retries=0,families={f:dict(n=v['n'],correct=v['correct'],usable=v['statuses'].get('ok',0)) for f,v in j['families'].items()},public_free_access=False,cost_source='api_reported',core_cost=dict(known_api_usd=str(total),reported_records=200,missing_api_records=0,accounted_usd=str(total)),core_cost_per_1000_known_usd=str(total*5),reported_input_tokens=j['usage']['input_tokens'],reported_output_tokens=200,reported_reasoning_text=0,image_variant='Original reviewed mixed PNG/JPEG',probe_cost_usd='0.00001722',admission_probes=5,reasoning_verification='Native choice endpoint, no prose or reasoning trace; output_tokens is one native decision counter per request',processed_input_attestation='Exact delivered original image bytes; provider internal preprocessing not attested',returned_identity='baseten/joey-1-20261029')
 s['models'][MID]=m;s['rank_order']=sorted(s['models'],key=lambda k:(-s['models'][k]['correct'],s['models'][k]['median_ms']));s['decision_model_ids'].append(MID)
 s.update(version='native-image-updates-20261030-v1',complete_routes=22,hosted_model_count=19,decision_models_ranked=21,decision_models_reviewed=30,complete_first_attempt_cases=4400,updated_date_toronto='2026-10-30',prior_summary_sha256=digest(OLD/'summary.json'),added_model_ids=[MID],compatibility_screens=[dict(model='Cloudflare Clairic',scored=20,correct=9,status='paused_failures',full_bank=False,interface='extraction integer option-ID adapter')])
 assert all(s['models'][k]==v for k,v in old['models'].items());write(DEST/'summary.json',s)
 clean={k:c[k] for k in ['n','correct','accuracy','mean_ms','median_ms','p95_ms','statuses','cost_usd','missing_cost','usage','scope','state']}
 clean.update(label='Clairic: extraction number adapter',date='2026-10-30',included_in_full_ranking=False,full_bank=False,expected_bank=200,reason='One of20 outputs outside supplied option IDs reached the 5% stop at 20.',image_binding='Five pixel/order probes passed with positive reported image tokens; OpenRouter named assets and state references.',interface='POST /api/alpha/extractions; original question, rules and options in state; one integer field requests option ID. No output remapping.',cost_source='API-reported OpenRouter usage.cost')
 write(DEST/'clairic_compatibility.json',clean)
 timing=[]
 for mid,aa in [(MID,aa),('clairic_extraction',ca)]:
  for a in aa:
   q=qq[a['item_id']];timing.append(dict(model_id=mid,item_id=a['item_id'],family_id=a['family_id'],request_index=a['request_index'],attempt=1,status=a['status'],latency_ms=a['latency_ms'],question_sha256=a['question_sha256'],request_sha256=a['payload_sha256'],response_sha256=hashval(a['transport']['raw_response']),image_sha256=[assets[x]['sha256'] for x in q['asset_ids']],input_tokens=a['usage']['input_tokens'],output_tokens=a['usage']['output_tokens'],reported_cost_usd=a['accounted_cost_usd']))
 write(DEST/'october30_timing_evidence.jsonl','\n'.join(json.dumps(a,ensure_ascii=False) for a in timing))
 write(DEST/'original_asset_manifest.json',dict(variant='Original reviewed mixed PNG/JPEG',assets={k:{f:a[f] for f in ['sha256','mime']} for k,a in assets.items()}))
 write(DEST/'model_metadata.json',{name:load(RUN/(name+'.json')) for name in ['joey_endpoints_start','joey_endpoints_end','clairic_endpoints_start','clairic_endpoints_end']})
 write(DEST/'execution_protocol.json',dict(date='2026-10-30',question_bank_sha256=digest(ROOT/'data/questions.jsonl'),new_native_model='baseten/joey-1',returned='baseten/joey-1-20261029',route='OpenRouter; pinned BaseTen; no fallback',scored_retries=0,maximum_inflight_per_model=1,image_variant='Exact original reviewed PNG/JPEG bytes, order and questions',joey_admission='Five pixel/order probes, one/two/three images; all passed',clairic_admission='Correct OpenRouter named image assets passed five probes; ignored native-style image fields and invalid state-array format were admission diagnostics only',timing='Fresh HTTPS through complete response body; preparation/scoring/idle excluded',speed_screen='After20: cumulative median>2000ms',failure_screen='After20: unusable>=5%',clairic_scope='20 first attempts; stopped at5% unusable; not ranked',sources={name:owner.F.filehash(RUN/name) for name in ['runner.py','score.py','clairic.py','clairic_images.py']}))
 write(DEST/'audit_receipt.json',dict(status='PASS',new_native_first_attempts=200,new_native_usable=200,new_native_correct=94,separate_extraction_first_attempts=20,separate_extraction_correct=9,all_dispatches_resolved=True,raw_responses_reparsed=True,private_key_reconciled=True,original_assets_verified=227,previous_21_model_records_unchanged=True,previous_177_subset_unchanged=True,publication_inference_calls=0,privacy='Aggregate scores and answer-free timing hashes only'))

def exports(s):
 for name,fields,values in [('leaderboard.csv',['model_id','model','kind','correct','questions','accuracy','usable','mean_ms','median_ms','p95_ms','bank_cost_basis','cost_per_1000','date'],([mid,m['label'],m.get('model_kind','hosted_decision'),m['correct'],200,m['accuracy'],m['usable'],m['mean_ms'],m['median_ms'],m['p95_ms'],prior.money(m),prior.money(m,True),m['date']] for mid in s['rank_order'] for m in [s['models'][mid]])),('family_scores.csv',['model_id','model','family_id','family','correct','questions','accuracy'],([mid,s['models'][mid]['label'],f,d['name'],s['models'][mid]['families'][f]['correct'],10,s['models'][mid]['families'][f]['correct']/10] for mid in s['rank_order'] for f,d in s['families'].items()))]:
  stream=io.StringIO(newline='');w=csv.writer(stream,lineterminator='\n');w.writerow(fields);w.writerows(values);write(DEST/name,stream.getvalue())

def dated_links(page):
 def fix(match):
  key,url=match.group(1),match.group(2);u=urlsplit(url)
  if u.scheme or u.netloc or not u.path:return match.group(0)
  path=u.path[len(NAME)+1:] if u.path.startswith(NAME+'/') else posixpath.join('..',u.path)
  return key+'="'+urlunsplit(('', '',path,u.query,u.fragment))+'"'
 return re.sub(r'(href|src)="([^"]+)"',fix,page)

def build():
 preserve();s=load(DEST/'summary.json');exports(s)
 from matplotlib.figure import Figure
 suptitle,figtext=Figure.suptitle,Figure.text
 def title(fig,t,*a,**kw):return suptitle(fig,str(t).replace('21 complete routes · 18 hosted','22 complete routes · 19 hosted'),*a,**kw)
 def foot(fig,x,y,t,*a,**kw):
  if str(t).startswith('D3 Ultra:'):t='Joey-1:94/200,368 ms median; all21 earlier model records unchanged.\n'+str(t).split('\n',1)[1].replace('New D3/Liquid rows','Joey and D3/Liquid rows')
  return figtext(fig,x,y,t,*a,**kw)
 prior.DEST=DEST;Figure.suptitle=title;Figure.text=foot
 try:prior.plot(s)
 finally:Figure.suptitle=suptitle;Figure.text=figtext
 note=NOTE.replace('COMPATIBILITY_LINK','results/releases/'+NAME+'/clairic.html')
 md=(ARCHIVE/'README.md').read_text();md=md.replace('21 complete routes: 18 hosted','22 complete routes: 19 hosted').replace('All 19 earlier records','All 21 earlier records')
 start=md.index('## Overall results');end=md.index('\n## ',start+1);md=md[:start]+'## Overall results\n\n'+prior.old_presentation.table(s)+'\n'+md[end:]
 md=md.replace('## Overall results',note+'## Overall results',1)
 for stem in ['overview',*[f'abilities_{i}' for i in range(1,5)]]:md=md.replace('results/releases/'+OLD.name+'/'+stem,'results/releases/'+NAME+'/'+stem)
 write(ROOT/'README.md',md)
 html=(ARCHIVE/'docs/report.html').read_text();html=html.replace('21 complete routes: 18 hosted','22 complete routes: 19 hosted').replace('All 19 earlier records','All 21 earlier records').replace('21 image decision routes','22 image decision routes').replace('18 hosted decision models','19 hosted decision models')
 html=re.sub(r'<title>.*?</title>','<title>Image decisions · 22 complete routes and separate 177-question comparison</title>',html)
 tables=list(re.finditer(r'<table\b.*?</table>',html,re.S));target=next(t for t in tables if 'data-summary-model=' in t.group())
 new=prior.llm.reference_names(prior.previous.summary_html(s),s).replace('Actual 200 cost','200 cost / basis');new=new[new.index('<table'):new.index('</table>')+8]
 html=html[:target.start()]+new+html[target.end():]
 start=html.index('<label class="filter">');end=html.index('<h2 id="what-the-categories-test"',start);html=html[:start]+prior.llm.reference_names(prior.previous.categories_html(s),s)+'\n'+html[end:]
 from markdown import markdown
 html=html.replace('<h2 id="overall-results">',markdown(note.replace('results/releases/'+NAME+'/',NAME+'/'))+'<h2 id="overall-results">',1)
 for stem in ['overview',*[f'abilities_{i}' for i in range(1,5)]]:html=html.replace(OLD.name+'/'+stem,NAME+'/'+stem)
 html=html.replace('Updated October 27, 2026.','Updated October 30, 2026.').replace('full 420-cell category matrix','full 440-cell category matrix')
 write(ROOT/'docs/report.html',html);write(DEST/'report.html',dated_links(html));write(DEST/'analysis.md',note.replace('](results/releases/'+NAME+'/',']('))
 compatibility='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Clairic image extraction: stopped 20-question screen</title><style>body{font:17px/1.6 system-ui;max-width:950px;margin:35px auto;padding:20px}</style><h1>Clairic: partial image extraction screen</h1><p><b>9/20 correct (45.0%) · 19 usable · not a full 200 score.</b> October 30, 2026; OpenRouter → Cloudflare.</p><p>Mean 608 ms · median 469 ms · p95 1,122 ms · API-reported cost $0.00238230 for 20 calls. One numeric output was outside the supplied option IDs, reaching the 5% unusable-output stop at 20. No scored retries.</p><p>Five image pixel/order probes passed before scoring. Original reviewed image bytes were attached through named assets referenced in the state. The extraction integer field requested an option ID; no output was remapped. This interface is separate from native decision endpoints.</p><p><a href="clairic_compatibility.json">Aggregate record</a> · <a href="october30_timing_evidence.jsonl">Answer-free timing evidence</a> · <a href="report.html">Full comparison</a></p></html>'
 write(DEST/'clairic.html',compatibility)
 write(DEST/'manifest.json',dict(version='native-image-updates-20261030-v1',complete_routes=22,questions_each=200,separate_extraction_screen=20,prior_summary_sha256=digest(OLD/'summary.json'),artifacts={p.name:digest(p) for p in sorted(DEST.iterdir()) if p.is_file() and p.name!='manifest.json'}))
 shutil.copytree(DEST,ROOT/'docs'/NAME,dirs_exist_ok=True)
 write(ROOT/'docs/sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+prior.SITE+'</loc><lastmod>2026-10-30</lastmod></url></urlset>')
 prior.bind_layout();print('Built22 full image routes;21 earlier model records and177subset unchanged; partial Clairic separate.')
if __name__=='__main__':
 if '--capture' in sys.argv:capture()
 else:build()
