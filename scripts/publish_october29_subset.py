"""Publish the matched 177 single-image subset; never run inference or alter the full 200 ranking."""
from collections import Counter
import csv,hashlib,io,json,math,re,shutil,statistics,sys
from copy import deepcopy
from pathlib import Path
from html import escape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from markdown import markdown
ROOT=Path(__file__).resolve().parents[1];H=ROOT.parent/'text-decision-hardening'
LOCAL=H/'runs/startlux_lan_2026-10-29';HOST=H/'runs/turion_triospark_2026-10-29'
NAME='single_image_subset_2026-10-29';DEST=ROOT/'results/releases'/NAME;FULL=ROOT/'results/releases/native_updates_2026-10-27'
IDS=['trio_spark14','local_startlux_instant4b','local_startlux_autothink4b'];AUTO=IDS[2]
PURPLE='#7c3aed';GOLD='#d97706';BLUE='#16728c'
def load(p):return json.loads(Path(p).read_text())
def rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hashval(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text((v.rstrip() if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2))+'\n')
def quant(t):
 t=sorted(t);pos=(len(t)-1)*.95;lo=math.floor(pos);hi=math.ceil(pos)
 return dict(mean_ms=statistics.mean(t),median_ms=statistics.median(t),p95_ms=t[lo]+(t[hi]-t[lo])*(pos-lo))
def capture():
 assert not (DEST/'manifest.json').exists(),'Never overwrite a sealed release'
 qs={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')};subset={i:q for i,q in qs.items() if len(q['asset_ids'])==1};assert len(qs)==200 and len(subset)==177
 key=ROOT.parent/'jev-1.14-comparison-benchmark/runs/visual_benchmark_curation_PRIVATE/coordinator/frozen_2026-10-15_v1/answers_PRIVATE.jsonl'
 gold={r['candidate_id']:str(r['correct_option_id']) for r in rows(key)}
 assets={a['asset_id']:a['sha256'] for a in rows(ROOT/'data/assets.jsonl')}
 definitions=load(FULL/'summary.json')['families'];newaudit=load(LOCAL/'images/final_report.json');trio=load(HOST/'trio_image_audit.json');records=[];models={}
 for mid,model,label in [(IDS[0],'trio-spark-v1.3','Trio-Spark v1.4'),(IDS[1],'startlux:4b-v1.1-instant','StartLux v1.1 4B Instant'),(AUTO,'startlux:4b-v1.1-autothink','StartLux v1.1 4B AutoThink')]:
  local=mid!=IDS[0];src=LOCAL/'images'/model.replace(':','__')
  aa=rows(src/'attempts.jsonl') if local else rows(HOST/'trio_image_single_screen.jsonl')
  assert len(aa)==len({a['id'] for a in aa})==177 and {a['id'] for a in aa}==set(subset)
  if local:
   dd=rows(src/'dispatches.jsonl');assert len(dd)==177
   for a,d in zip(aa,dd):assert a['id']==d['id'] and a['request_sha256']==d['request_sha256']
  byid={a['id']:a for a in aa};valid=0
  for index,a in enumerate(aa,1):
   q=subset[a['id']];im=[assets[aid] for aid in q['asset_ids']];assert (a['image_sha256'] if local else [a['image_hash']])==im
   assert a['choice'] in {str(o['id']) for o in q['options']} and (a['status']=='ok' if local else a['valid'] and a['status']==200)
   valid+=1;raw=a['transport']['raw'] if local else None
   records.append(dict(model_id=mid,item_id=a['id'],family_id=q['family_id'],index=index,attempt=1,status='ok',latency_ms=a['latency_ms'] if local else a['ms'],input_tokens=a['usage']['input_tokens'],output_tokens=a['usage']['output_tokens'],image_sha256=im[0],request_sha256=a.get('request_sha256'),response_sha256=hashval(raw) if raw else None))
  fam={fid:dict(n=sum(subset[i]['family_id']==fid for i in byid),correct=sum(subset[i]['family_id']==fid and a['choice']==gold[i] for i,a in byid.items())) for fid in definitions}
  correct=sum(a['choice']==gold[i] for i,a in byid.items());expected=newaudit[model] if local else trio;assert correct==expected['correct']
  if local:assert fam==expected['families'] and expected['audit']['status']=='PASS'
  ts=quant([a['latency_ms'] if local else a['ms'] for a in aa]);m=dict(label=label,n=177,correct=correct,accuracy=correct/177,usable=177,**ts,families=fam,date='2026-10-29',location='local' if local else 'hosted',mode='adaptive' if mid==AUTO else 'immediate',model_requested=model,reported_output_tokens=sum(a['usage']['output_tokens'] for a in aa),reported_generation_calls=sum(a['usage']['output_tokens']>0 for a in aa),cost_basis='Hardware/electricity unmeasured' if local else 'Usage × tariff estimate, not a monetary receipt',known_api_cost_usd=None,estimated_tariff_usd=None if local else sum(a['usage']['input_tokens'] for a in aa)*.042/1e6)
  models[mid]=m
 # Prior reference choices already published in this dated evidence. Recompute
 # ONLY the same subset; no new inference or changes to original200 scores.
 previous=rows(ROOT/'results/releases/fastino_2026-10-23/attempts.jsonl');baseline=load(FULL/'summary.json')['models']
 for mid,want in [('amos_large',138),('fastino_glide',136),('d3_turbo',132),('jev113',124)]:
  aa=[a for a in previous if a['model_id']==mid and a['attempt']==1 and a['candidate_id'] in subset];assert len(aa)==len({a['candidate_id'] for a in aa})==177
  c=sum(a['status']=='ok' and str(a['choice'])==gold[a['candidate_id']] for a in aa);assert c==want
  fam={fid:dict(n=sum(a['family_id']==fid for a in aa),correct=sum(a['family_id']==fid and a['status']=='ok' and str(a['choice'])==gold[a['candidate_id']] for a in aa)) for fid in definitions}
  ts=quant([a['latency_ms'] for a in aa]);models[mid]=dict(label=baseline[mid]['label'],n=177,correct=c,accuracy=c/177,usable=sum(a['status']=='ok' for a in aa),**ts,families=fam,date=baseline[mid]['date'],location='hosted',mode='immediate',reference_recomputed=True,cost_basis='See unchanged full 200 record; subset cost not re-accounted')
  for index,a in enumerate(aa,1):records.append(dict(model_id=mid,item_id=a['candidate_id'],family_id=a['family_id'],index=index,attempt=1,status=a['status'],latency_ms=a['latency_ms'],input_tokens=a.get('usage',{}).get('input_tokens'),output_tokens=a.get('reported_output_tokens',0),image_sha256=a['image_sha256'][0],request_sha256=a.get('request_payload_sha256'),response_sha256=None))
 out=dict(version='matched-single-image-177-october29-v1',full_bank_questions=200,subset_questions=177,excluded_multi_image_questions=23,new_model_ids=IDS,adaptive_model_ids=[AUTO],scope='Three new routes and four selected prior native references on identical 177 single-image questions; separate from full 200 ranking',date='2026-10-29',models=models,rank_order=sorted(models,key=lambda k:(-models[k]['correct'],k)),families=definitions,question_bank_sha256=digest(ROOT/'data/questions.jsonl'),full200_statistics_sha256=digest(FULL/'summary.json'),paired_startlux=load(LOCAL/'images/comparison.json'),turion_image_binding='Failed four red/blue probes on tested endpoint; no benchmark score',pixel_policy='Original reviewed mixed PNG/JPEG bytes submitted unchanged. Internal preprocessing provider-controlled; StartLux advertises262144 processed pixels and one image.',local_setup=dict(runtime='Ollaya0.17.0',precision='Q8_0',observed_device='cuda:0',gpu_model='Not reported by API',network='Direct wired LAN; sequential models and requests',native_autothink_budget=512,thought_text_exposed=False,speed_exception='AutoThink only; explicitly authorized adaptive research run'))
 write(DEST/'summary.json',out)
 buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records);write(DEST/'timing_evidence.csv',buf.getvalue())
 write(DEST/'subset_items.json',dict(included=[dict(item_id=i,family_id=q['family_id'],image_sha256=assets[q['asset_ids'][0]]) for i,q in sorted(subset.items())],excluded=[dict(item_id=i,family_id=q['family_id'],image_count=len(q['asset_ids'])) for i,q in sorted(qs.items()) if i not in subset]))
 write(DEST/'audit_receipt.json',dict(status='PASS',new_model_attempts=531,reference_records_reused=708,subset_questions=177,excluded_questions=23,scored_retries=0,all_new_responses_usable=True,all_dispatches_resolved=True,original_asset_hashes_verified=True,private_key_binding_sha256=digest(key),full200_statistics_unchanged=True,privacy='Aggregates and answer-free hashes/timings; no new choices, probabilities, keys or per-item correctness'))

ANALYSIS='''## October 29: image decisions on the same 177 questions

**Trio-Spark and the two StartLux routes support one image per request.** They completed the 177 single-image questions in the frozen bank. The other 23 questions require multiple images, which these interfaces reject. This comparison covers a subset; the full 200-question scores and ranking above remain unchanged.

Trio-Spark scored **106/177 (59.9%)**, StartLux Instant **101/177 (57.1%)**, and StartLux AutoThink **108/177 (61.0%)**. Each returned 177 usable first decisions. On these identical items, the earlier Amos run scored **138/177 (78.0%)**, Fastino GLiDE **136 (76.8%)**, D3 Turbo **132 (74.6%)** and Jev 1.13 **124 (70.1%)**, recomputed from existing records. These four are selected reference routes; the subset chart is not a ranking of every previously tested model.

## AutoThink adds seven answers and a much longer response time

AutoThink's purple fill connects it to the local CUDA measurements. A gold frame and ✦ badge identify its adaptive generation. It scored seven answers above Instant, with **7.12 s mean, 8.36 s median and 13.73 s p95**. Instant measured **391 / 387 / 461 ms**. AutoThink generated on **99/177 calls (55.9%)** in this image subset, so the fast path was used less often than in text. Its full image run was explicitly allowed to exceed the normal two-second screen for research.

AutoThink uniquely answered 20 images correctly, Instant uniquely answered 13, both answered 88 correctly and both missed 56. Relative to Instant, AutoThink improved document reconciliation **6/10 → 8/10** and navigation/planning **3/10 → 5/10**; spatial relationships fell **9/10 → 7/10**. Each score refers to this subset's category counts. The two released variants have different weights and prompt attention, so this does not isolate the effect of a reasoning toggle.

It reported 45,679 output tokens; 68 calls reported exactly the native 512-token budget. The API did not reveal the thoughts or an explicit budget-exhaustion flag. The [StartLux implementation](https://github.com/StartLuxLabs/StartLux-Decision) describes a confidence gate for immediate decisions or extra generation; the exact local gate was not exposed.

## Trio's hosted subset and the image-input limits

Trio's image mean / median / p95 were **1,143 / 1,072 / 1,673 ms**. Its 56,718 reported input tokens imply approximately **$0.00238216** at the listed tariff. This is an estimate from tokens × tariff, rather than an API monetary receipt. The v1.3 alias served the October 28 v1.4 release in text; the image endpoint did not return a dated version field, so that image identity is qualified by the alias and provider release notice.

Turion accepted image-bearing requests but chose “none” on all four solid-red/blue binding probes. It did not demonstrate pixel binding on the tested endpoint and was not assigned an image score.

## Subset coverage, local setup and interpretation

The original reviewed PNG/JPEG bytes and dimensions were submitted unchanged. Both StartLux models and Trio passed red/blue binding checks; their two-image requests were rejected. Provider-controlled internal preprocessing still applies. The local server advertises one image and 262,144 processed pixels, and accepted a 768×768 test fixture.

Local tests ran sequentially through Ollaya 0.17.0, CUDA and Q8_0 on direct wired LAN. The API did not identify the precise GPU, so the new badges say Local · CUDA · Q8. They share the earlier RTX 2060 purple to identify local execution; the provenance remains explicit. Warm-ups and loading are separate. Hardware and electricity costs were not measured. All records are first attempts with no scored retries.

Question counts differ within this subset: 17 categories retain all 10 items, sequential state tracking has six, inspection against a reference has none, and matching across images has one. A one-item category cannot establish a broad skill. The table shows counts and marks empty categories as unavailable. The full 200-question category distribution is unchanged.
'''
CSS='''body{font:16px/1.6 system-ui;margin:0;background:#f4f7fa;color:#182f43}main{max-width:1400px;margin:auto;padding:30px}a{color:#126482}h1{line-height:1.25}table{border-collapse:collapse;width:100%;background:white}th,td{padding:12px;border:1px solid #cbd5e1;text-align:right;white-space:nowrap}th:first-child{text-align:left}thead{background:#e7eef4}.scroll{overflow:auto;margin:24px 0;max-height:900px}.local th:first-child{background:#f5f0ff;color:#5b21b6;border-left:5px solid #7c3aed}.adaptive td{border-top:3px solid #d97706;border-bottom:3px solid #d97706}.adaptive th:first-child{background:#f5f0ff;color:#5b21b6;border:4px solid #d97706;border-left:6px solid #7c3aed}.subset-note{padding:22px;background:#edf6f8;border-left:5px solid #16728c;margin:24px 0}.adaptive-note{padding:22px;background:#f5f0ff;border:3px solid #d97706;border-radius:12px;margin:25px 0}.badge{display:block;font-size:12px;padding:3px 6px;border:1px solid #c4b5fd;background:#ede9fe;color:#5b21b6;border-radius:4px;margin-top:7px;white-space:normal}.adaptive .badge{border:2px solid #d97706}img{max-width:100%;height:auto}.category-matrix th:first-child{position:sticky;left:0;min-width:240px;background:#f0f5f8;z-index:2}.category-matrix td strong,.category-matrix td span{display:block}.category-matrix thead th{white-space:normal;min-width:170px;vertical-align:bottom;position:sticky;top:0;z-index:3;background:#e7eef4}.category-matrix thead th:first-child{z-index:4}.category-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:15px}.category-card{background:white;border:1px solid #cbd5e1;border-top:4px solid #16728c;padding:18px;border-radius:6px}.summary th:first-child{min-width:245px}nav{margin:22px 0}small{font-size:12px}section{scroll-margin-top:70px}
'''
def plot(s):
 ids=s['rank_order'];fig,axes=plt.subplots(1,2,figsize=(13,6.7),sharey=True,gridspec_kw={'width_ratios':[1,1]});yy=range(len(ids));colors=[PURPLE if m in IDS[1:] else BLUE for m in ids];bars=axes[0].barh(yy,[100*s['models'][m]['accuracy'] for m in ids],color=colors);axes[0].set_yticks(list(yy),[s['models'][m]['label']+(' [sometimes thinks]' if m==AUTO else '') for m in ids]);axes[0].invert_yaxis();axes[0].set_xlim(0,100)
 for y,mid,bar in zip(yy,ids,bars):
  m=s['models'][mid];axes[0].text(100*m['accuracy']+1,y,f"{m['correct']}/177 · {m['accuracy']:.1%}",va='center',fontsize=9);axes[1].plot([m['median_ms'],m['p95_ms']],[y,y],color='#94a3b8');axes[1].scatter(m['median_ms'],y,color=colors[y],s=45);axes[1].scatter(m['p95_ms'],y,color='#35424d',marker='d',s=18)
  if mid==AUTO:
   bar.set_edgecolor(GOLD);bar.set_linewidth(5);bar.set_hatch('..');axes[1].scatter(m['mean_ms'],y,marker='*',color=GOLD,s=90)
   for ax in axes:ax.axhspan(y-.46,y+.46,facecolor='none',edgecolor=GOLD,lw=3.5)
 for ax in axes:ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
 axes[0].set_title('Accuracy on identical single-image questions');axes[0].set_xlabel('Correct first decisions (%)');axes[1].set_xscale('log');axes[1].set_title('Response time: median to p95');axes[1].set_xlabel('Client response (ms, log scale)');fig.suptitle('177-question subset · 3 new routes + 4 selected prior references',fontsize=15)
 fig.legend(handles=[Patch(facecolor=BLUE,label='Hosted decision'),Patch(facecolor=PURPLE,label='Local CUDA'),Patch(facecolor=PURPLE,edgecolor=GOLD,hatch='..',label='Local adaptive · sometimes thinks')],ncol=3,loc='upper center',bbox_to_anchor=(.56,.92),frameon=False)
 fig.text(.025,.025,'23 multi-image questions excluded because the new interfaces support one image. Earlier reference records recomputed, not rerun.\nPurple local CUDA; gold frame marks AutoThink, completed under a research speed exception. Gold star: mean.\nThese subset scores do not replace the separate full 200 ranking. Original dates and routes retained.',fontsize=9);fig.subplots_adjust(left=.27,right=.98,top=.80,bottom=.22,wspace=.3)
 for ext in ['png','svg']:fig.savefig(DEST/('subset_comparison.'+ext),dpi=160,metadata={'Date':None} if ext=='svg' else {})
 plt.close(fig)
def heat(v):
 import matplotlib.colors as colors
 cmap=matplotlib.colormaps['YlGnBu'];return colors.to_hex(cmap(v)), '#ffffff' if v>=.55 else '#172638'
def badge(mid):return '<span class="badge">✦ Local · CUDA · Q8 · sometimes thinks</span>' if mid==AUTO else '<span class="badge">Local · CUDA · Q8</span>' if mid==IDS[1] else ''
def content(s):
 result='<div class="subset-note"><b>177 single-image questions, not the full 200 ranking.</b> Three new routes cannot accept the 23 multi-image questions. Four selected older routes are recomputed on the exact same 177 items. No original 200 scores are changed.</div><p><a href="single_image_subset_2026-10-29/report.html">Open the subset report and all named category scores</a> · <a href="https://etsabary.github.io/system-1-decision-benchmark/report.html#adaptive">Full text AutoThink analysis</a></p><a href="single_image_subset_2026-10-29/subset_comparison.svg"><img src="single_image_subset_2026-10-29/subset_comparison.png" alt="177 matched image questions; local StartLux purple and AutoThink framed gold"></a><div class="scroll"><table class="summary"><thead><tr><th>Model</th><th>Correct /177</th><th>Accuracy</th><th>Mean</th><th>Median</th><th>p95</th><th>Test date</th></tr></thead><tbody>'
 for mid in s['rank_order']:
  m=s['models'][mid];cls='adaptive' if mid==AUTO else 'local' if mid in IDS[1:] else 'hosted'
  result+=f'<tr class="{cls}" data-subset-model="{mid}"><th scope="row">{escape(m["label"])}{badge(mid)}</th><td>{m["correct"]}/177</td><td>{m["accuracy"]:.1%}</td><td>{m["mean_ms"]:,.0f} ms</td><td>{m["median_ms"]:,.0f} ms</td><td>{m["p95_ms"]:,.0f} ms</td><td>{escape(m["date"])}</td></tr>'
 result+='</tbody></table></div><div class="adaptive-note"><b>✦ AutoThink: seven more correct than Instant, with an 8.36-second median.</b><p>The purple fill identifies local CUDA execution; the gold frame marks adaptive generation. It reported generation on 99/177 image calls (55.9%). The native budget was512 tokens. This completed under the explicit research exception to the normal speed screen.</p></div>'+markdown(ANALYSIS)
 return result

def categories(s):
 ids=s['rank_order'];parts=['<section id="subset-categories"><h2>Named category scores within the subset</h2><p>Same177 questions in every row; selected references only. Each cell shows correct / tested and accuracy. The fixed 0–100% heatmap encodes accuracy. Unavailable means no items from this category occur in the subset.</p>']
 fams=list(s['families'])
 for start in range(0,20,5):
  fids=fams[start:start+5];parts.append('<div class="scroll category-matrix"><table><thead><tr><th>Model</th>'+''.join('<th>'+escape(s['families'][f]['name'])+f'<small> · {s["models"][ids[0]]["families"][f]["n"]} questions</small></th>' for f in fids)+'</tr></thead><tbody>')
  for mid in ids:
   m=s['models'][mid];parts.append(f'<tr class="{"adaptive" if mid==AUTO else "local" if mid in IDS[1:] else "hosted"}"><th>{escape(m["label"])}{badge(mid)}</th>')
   for f in fids:
    v=m['families'][f];n=v['n'];bg,fg=heat(v['correct']/n) if n else ('#edf1f5','#526577');value=f'<strong>{v["correct"]}/{n}</strong><span>{v["correct"]/n:.1%}</span>' if n else 'Unavailable'
    parts.append(f'<td data-subset-cell="{mid}" data-family="{f}" data-correct="{v["correct"]}" data-n="{n}" style="background:{bg};color:{fg}">{value}</td>')
   parts.append('</tr>')
  parts.append('</tbody></table></div>')
 parts.append('<div class="category-cards">')
 for fid,f in s['families'].items():parts.append('<article class="category-card"><h3>'+escape(f['name'])+'</h3><p>'+escape(f['description'])+'</p><p>'+str(s['models'][ids[0]]['families'][fid]['n'])+' questions in this subset; 10 in the full bank.</p></article>')
 parts.append('</div></section>');return ''.join(parts)
def build():
 s=load(DEST/'summary.json');plot(s)
 # Preserve the exact pre-addition overview for public visual comparison.
 archive=ROOT/'results/archives/presentation_before_october29_2026'
 if not (archive/'manifest.json').exists():
  files={}
  for name in ['README.md','docs/report.html','docs/sitemap.xml']:
   p=ROOT/name;target=archive/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);files[name]=dict(path=name,sha256=digest(p))
  write(archive/'manifest.json',dict(files=files))
 result=content(s)
 # A dedicated page uses local relative URLs; the live report embeds the exact
 # same subset section, while preserving the full 200 table and category cells.
 page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>177 single-image decisions · October 29 · StartLux and Trio</title><style>'+CSS+'</style></head><body><main><h1>Single-image decision comparison · 177 questions</h1><nav><a href="https://etsabary.github.io/visual-decision-benchmark/report.html">Full200 image benchmark</a> · <a href="#subset-categories">Named subset categories</a></nav>'+result.replace(NAME+'/','')+categories(s)+'<p><a href="summary.json">Subset aggregates</a> · <a href="timing_evidence.csv">Answer-free timing evidence</a> · <a href="subset_items.json">Included/excluded question IDs</a> · <a href="audit_receipt.json">Audit</a></p></main></body></html>'
 write(DEST/'report.html',page);write(DEST/'analysis.md',ANALYSIS)
 stream=io.StringIO(newline='');w=csv.writer(stream,lineterminator='\n');w.writerow(['model_id','model','correct','questions','accuracy','mean_ms','median_ms','p95_ms','date','mode','cost_basis'])
 for mid in s['rank_order']:
  m=s['models'][mid];w.writerow([mid,m['label'],m['correct'],177,m['accuracy'],m['mean_ms'],m['median_ms'],m['p95_ms'],m['date'],m['mode'],m['cost_basis']])
 write(DEST/'leaderboard.csv',stream.getvalue())
 stream=io.StringIO(newline='');w=csv.writer(stream,lineterminator='\n');w.writerow(['model_id','family_id','category','correct','questions','accuracy'])
 for mid in s['rank_order']:
  for fid,f in s['models'][mid]['families'].items():w.writerow([mid,fid,s['families'][fid]['name'],f['correct'],f['n'],f['correct']/f['n'] if f['n'] else ''])
 write(DEST/'category_scores.csv',stream.getvalue())
 for p in DEST.glob('*.svg'):write(p,'\n'.join(x.rstrip() for x in p.read_text().splitlines()))
 write(DEST/'manifest.json',dict(version='subset177-october29-v1',full200_statistics_sha256=digest(FULL/'summary.json'),artifacts={p.name:digest(p) for p in sorted(DEST.iterdir()) if p.is_file() and p.name!='manifest.json'}));shutil.copytree(DEST,ROOT/'docs'/NAME,dirs_exist_ok=True)
 base=(archive/'docs/report.html').read_text();base=base.replace('</head>','<style>'+CSS+'</style></head>');base=base.replace('= local RTX 2060 6 GB;', '= local CUDA (earlier runs: RTX 2060 6 GB); gold frame = adaptive AutoThink;');base=base.replace('<a href="#october-27-findings">','<a href="#single-image-subset">New 177-item comparison</a><a href="#october-27-findings">');section='<section id="single-image-subset"><h2>New: Trio-Spark and local StartLux on 177 single-image questions</h2>'+result+'</section>'
 # Add after the existing introductory figure, before the unchanged200 table.
 anchor='<h2 id="overall-results">';assert anchor in base;base=base.replace(anchor,section+anchor,1)
 base=re.sub(r'<title>.*?</title>','<title>Image decisions · full 200 ranking and 177-question adaptive comparison</title>',base)
 write(ROOT/'docs/report.html',base)
 readme=(archive/'README.md').read_text();sectionmd='## New:177 single-image questions · October 29\n\nThe new Trio-Spark and local StartLux interfaces support one image per request. They completed the same 177 single-image questions; 23 multi-image questions are unsupported. **These scores form a separate matched subset and do not replace the full 200 ranking.**\n\n| Model | Correct /177 | Accuracy | Mean | Median | p95 |\n| --- | ---: | ---: | ---: | ---: | ---: |\n'
 for mid in s['rank_order']:
  m=s['models'][mid];sectionmd+=f"| {m['label']}{' ✦ adaptive' if mid==AUTO else ''} | {m['correct']}/177 | {m['accuracy']:.1%} | {m['mean_ms']:,.0f} ms | {m['median_ms']:,.0f} ms | {m['p95_ms']:,.0f} ms |\n"
 sectionmd+='\nThe four earlier hosted references were recomputed from existing first attempts. **AutoThink shares local purple, with a gold frame and ✦ badge for its sometimes-thinking behavior.** It reported generation on 99/177 image calls; its speed exception is explicit.\n\n![177-question subset; AutoThink purple with gold frame](results/releases/'+NAME+'/subset_comparison.png)\n\n[Full subset report and named categories](https://etsabary.github.io/visual-decision-benchmark/'+NAME+'/report.html) · [Subset analysis](results/releases/'+NAME+'/analysis.md) · [Evidence](results/releases/'+NAME+'/timing_evidence.csv) · [Question coverage](results/releases/'+NAME+'/subset_items.json).\n\nTurion did not pass image-binding probes on the tested endpoint and has no image score. Trio’s image tariff estimate is approximately $0.00238216, rather than a monetary receipt. Local compute costs are unmeasured.\n\n'
 readme=readme.replace('## Overall results',sectionmd+'## Overall results',1);readme=readme.replace('= local RTX 2060 6 GB;', '= local CUDA (earlier runs: RTX 2060 6 GB); gold frame = adaptive AutoThink;');write(ROOT/'README.md',readme)
 write(ROOT/'docs/sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://etsabary.github.io/visual-decision-benchmark/report.html</loc><lastmod>2026-10-29</lastmod></url><url><loc>https://etsabary.github.io/visual-decision-benchmark/'+NAME+'/report.html</loc><lastmod>2026-10-29</lastmod></url></urlset>')
 bind_layout();print('Built separate177-image comparison; full 200 ranking and all earlier values retained.')
def bind_layout():
 path=ROOT/'scripts/layout_manifest.json';m=load(path);names=set(m['current_files'])|{p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*.py')};m['current_files']={n:digest(ROOT/n) for n in sorted(names)};write(path,m)
if __name__=='__main__':
 if '--capture' in sys.argv:capture()
 build()
