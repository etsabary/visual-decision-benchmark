"""Publish the audited October27 image additions offline; never sends model calls."""
import argparse,csv,io,json,re,shutil
from pathlib import Path
from html import escape
from hashlib import sha256
from decimal import Decimal
import publish_celeris_images_2026_10_26 as old_presentation
import october27_image_evidence as evidence
from repo_layout import ROOT,MANIFEST
NAME='native_updates_2026-10-27'
DEST=ROOT/'results/releases'/NAME
OLD=ROOT/'results/releases/celeris_2026-10-26'
SITE='https://etsabary.github.io/visual-decision-benchmark/report.html'
llm,previous=old_presentation.llm,old_presentation.previous
PURPLE,BLUE,YELLOW=llm.PURPLE,llm.BLUE,llm.YELLOW
digest,write,dump=llm.digest,llm.write,llm.dump
money=old_presentation.money
FIELDS=evidence.FIELDS

def narrative(s):
    intro='''The comparison contains **21 complete routes: 18 hosted decision models, two local models and GPT-6 Sol as a non-reasoning LLM reference**. Each complete route covers the same 200 first attempts across 20 categories. All 19 earlier records and three partial LLM speed stops are preserved.

**D3 Ultra scored 148/200 (74.0%); Liquid d1.1 scored 144/200 (72.0%).** Both returned 200 usable native decisions and passed the two-second cumulative-median gate. Amos remains highest at 159/200 (79.5%), followed by Fastino GLiDE at 158 (79.0%) and the earlier D3 Turbo at 155 (77.5%). Sol retains 147 (73.5%). One overall answer is half a percentage point; these observed gaps do not establish a universal model ranking.

## October 27 findings

### D3 Ultra improves on text and loses seven image answers

D3 Ultra measured **451 / 361 / 752 ms mean / median / p95**, compared with the earlier Turbo image median of 431 ms. Its image score fell from 155/200 to 148/200, while its text score rose from 1,106/1,342 (82.4%) to 1,124 (83.8%). A newer model does not improve every tested operation.

Navigation and planning fell from **7/10 to 3/10**; connectivity and reachability from **7/10 to 5/10**. Document reconciliation—comparing records across documents—improved from **6/10 to 8/10**, and spatial relationships from **8/10 to 9/10**. Visual rule application scored 5/10; constraint satisfaction 4/10. Each category contains ten questions, so a one-answer difference is ten percentage points.

### Liquid d1.1 gains nine image answers, with a longer median

Liquid d1.1 measured **487 / 425 / 915 ms mean / median / p95**. It scored nine more than the older d1 run's 135/200 (67.5%), whose median was 240 ms. Liquid d1-ultra retains 149/200 (74.5%). Its text run also improved: 1,044/1,342 (77.8%) versus the older d1's 965 (71.9%).

Causal and counterfactual image decisions rose from **4/10 to 7/10**. Sequential visual state tracking and insufficient-evidence decisions each rose from **8/10 to 10/10**. Visual rule application fell from **4/10 to 2/10**, and attribute binding/set logic from **10/10 to 9/10**. The full 420-cell category matrix shows where each model differs.

### Image inputs, identity and cost

The new runs used the **exact original reviewed PNG/JPEG bytes** from the earlier native-provider D3/Liquid image runs. The same 200 questions, rules, option IDs/text, image order and request order were retained. No resizing, replacement downloads, OCR or captions. Celeris, Sol and the two local rows retain their separately documented lossless PNG variant; all earlier inputs and measurements are unchanged.

D3 explicitly requested and returned `vllm-sr/d3-ultra`. The current service aliases its old Turbo name to Ultra, so the October 20 Turbo record remains a separately dated historical measurement. OpenRouter was pinned to Liquid, requested `liquid/d1.1`, and returned `liquid/d1.1-20261027` throughout. Start/end selected identity, provider and tariff remained unchanged. Provider-controlled image preprocessing and immutable weights were not independently attested.

D3 used **free public access**, without monetary receipts or a permanent production-price guarantee. Liquid reported **$0.00604404 for 200 questions**, or **$0.03022020 per 1,000**. Five separate admission probes added **$0.00001032**. Cost per 1,000 rescales the actual 200-question run; it does not mean 1,000 scored calls per model.

Five synthetic probes per route checked red/blue recognition, reversed pair order and a three-image request. All passed. Every scored output was a usable native choice with zero reported output tokens and no explanation. No scored retries. One fresh HTTPS call per provider ran at a time; the independent D3/Liquid providers ran concurrently. The timer includes connection, upload and full response; image/base64/JSON preparation and idle waits are excluded. All cumulative medians after the first 20 stayed below 2,000 ms.

The [new timing/usage evidence](Oct27_TIMING), [model metadata](Oct27_METADATA) and [execution protocol](Oct27_PROTOCOL) are answer-free. Scores were reconciled offline with the existing revision-bound private key. Public exports can verify coverage, timing and arithmetic, but cannot independently reproduce private-key correctness.

'''
    tail='## Why Sol'+(OLD/'analysis.md').read_text().split('## Why Sol',1)[1]
    return intro+tail.replace('380-cell category ranking','420-cell category ranking')

def bind_layout():
    m=json.loads(MANIFEST.read_text())
    paths=set(m['current_files'])|{p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*.py')}|{'documents/OCTOBER27_UPDATES.md','docs/sitemap.xml'}
    m['current_files']={name:digest(ROOT/name) for name in sorted(paths)};dump(MANIFEST,m)

def mirror():shutil.copytree(DEST,ROOT/'docs'/NAME,dirs_exist_ok=True)

def build(key_path):
    assert not (DEST/'manifest.json').exists(),'Never overwrite sealed dated evidence'
    s,timing,metadata,protocol,assets=evidence.load(key_path);DEST.mkdir(parents=True,exist_ok=True)
    generated={'summary.json','leaderboard.csv','family_scores.csv','analysis.md','report.html','manifest.json','release_checksums.json','audit_receipt.json'}
    for p in OLD.iterdir():
        if p.is_file() and p.name not in generated and p.suffix not in ('.png','.svg'):shutil.copyfile(p,DEST/p.name)
    dump(DEST/'summary.json',s);dump(DEST/'october27_model_metadata.json',metadata);dump(DEST/'october27_execution_protocol.json',protocol)
    dump(DEST/'october27_original_asset_manifest.json',dict(variant='Original reviewed mixed PNG/JPEG',assets=assets))
    write(DEST/'october27_timing_evidence.jsonl','\n'.join(json.dumps(r,ensure_ascii=False,allow_nan=False) for r in timing))
    for filename,fields,values in (
        ('leaderboard.csv',['model_id','model','kind','correct','questions','accuracy','usable','mean_ms','median_ms','p95_ms','bank_cost_basis','cost_per_1000','date'],
          ([mid,m['label'],m.get('model_kind','hosted_decision'),m['correct'],200,m['accuracy'],m['usable'],m['mean_ms'],m['median_ms'],m['p95_ms'],money(m),money(m,True),m['date']] for mid in s['rank_order'] for m in [s['models'][mid]])),
        ('family_scores.csv',['model_id','model','family_id','family','correct','questions','accuracy'],
          ([mid,s['models'][mid]['label'],f,definition['name'],s['models'][mid]['families'][f]['correct'],10,s['models'][mid]['families'][f]['correct']/10] for mid in s['rank_order'] for f,definition in s['families'].items()))):
        stream=io.StringIO(newline='');w=csv.writer(stream,lineterminator='\n');w.writerow(fields);w.writerows(values);write(DEST/filename,stream.getvalue())
    notes=narrative(s)
    for token,file in [('Oct27_TIMING','october27_timing_evidence.jsonl'),('Oct27_METADATA','october27_model_metadata.json'),('Oct27_PROTOCOL','october27_execution_protocol.json')]:notes=notes.replace(token,'results/releases/'+NAME+'/'+file)
    write(DEST/'analysis.md',notes.replace('](results/releases/'+NAME+'/',']('));plot(s)
    opening,detail=notes.split('## October 27 findings',1)
    legend='**Colour key:** blue `#16728c` = hosted decisions; purple `#7c3aed` = local RTX 2060 6 GB; pale yellow with transparency = LLM reference with reasoning off. Accuracy cells and speed/cost bands retain their fixed scales.'
    charts='\n\n'.join(f'![Named category scores, part {i}](results/releases/{NAME}/abilities_{i}.png)' for i in range(1,5))
    defs='\n'.join(f"- **[{f} {v['name']}](data/questions/{f}.md)**: {v['description']}" for f,v in s['families'].items())
    report='# Image-grounded System 1 decision benchmark\n\n'+opening.strip()+'\n\n[Open the colour-coded report]('+SITE+')'+f'\n\n![Accuracy, speed and cost](results/releases/{NAME}/overview.png)\n\n'+legend+'\n\n## Overall results\n\n'+old_presentation.table(s)+'\n\n## October 27 findings'+detail+'\n\n## Results by named category\n\n'+charts+'\n\n## What the categories test\n\n'+defs+f'\n\n[Aggregate results](results/releases/{NAME}/summary.json) · [Category CSV](results/releases/{NAME}/family_scores.csv) · [New timing/usage](results/releases/{NAME}/october27_timing_evidence.jsonl) · [Audit](results/releases/{NAME}/audit_receipt.json) · [New method](documents/OCTOBER27_UPDATES.md)\n\n[Questions and sources](data/questions/README.md) · [Gallery](docs/gallery.html) · [Attribution](documents/THIRD_PARTY_NOTICES.md) · [Local method](documents/LOCAL_IMAGE_RUNS.md)\n'
    write(ROOT/'README.md',report)
    import markdown
    md=report.replace(f'results/releases/{NAME}/',NAME+'/').replace('(data/questions/','(questions/').replace('(docs/gallery.html)','(gallery.html)')
    for file in ('LLM_IMAGE_REFERENCES.md','LOCAL_IMAGE_RUNS.md','THIRD_PARTY_NOTICES.md','OCTOBER27_UPDATES.md'):md=md.replace('(documents/'+file+')','('+file+')')
    content=markdown.markdown(md,extensions=['tables','fenced_code','toc'])
    first=content.index('<table>');end=content.index('</table>',first)+len('</table>')
    content=content[:first]+llm.reference_names(previous.summary_html(s),s).replace('Actual 200 cost','200 cost / basis')+content[end:]
    first=content.index('<p><img alt="Named category scores, part 1"');end=content.index('<h2 id="what-the-categories-test"',first)
    content=content[:first]+llm.reference_names(previous.categories_html(s),s)+content[end:]
    heading=content.index('<h2 id="llm-speed-stops"');first=content.index('<table>',heading);end=content.index('</table>',first)+len('</table>')
    partial=content[first:end]
    for m in s['llm_speed_stops']:partial=partial.replace('<tr>\n<td>'+escape(m['label'])+'</td>','<tr data-speed-stop="'+m['model_id']+'">\n<td>'+escape(m['label'])+'</td>')
    content=content[:first]+'<div class="table-scroll speed-stops">'+partial+'</div>'+content[end:]
    old_html=(OLD/'report.html').read_text();css=re.search(r'<style>(.*?)</style>',old_html,re.S).group(1);js=re.search(r'<script>(.*?)</script>',old_html,re.S).group(1)
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Compare 21 image decision routes on 200 questions: 18 hosted decision models, two local models and Sol without reasoning. D3 Ultra and Liquid d1.1 results, latency, cost and 20 category profiles."><link rel="canonical" href="'+SITE+'"><title>Image decisions · 21 complete routes · D3 Ultra and Liquid d1.1</title><style>'+css+'</style></head><body><nav><a href="#">Overview</a><a href="#overall-results">Scores, speed &amp; cost</a><a href="#october-27-findings">October 27 findings</a><a href="#llm-speed-stops">Speed stops</a><a href="#results-by-named-category">Categories</a><a href="gallery.html">Questions &amp; images</a><a href="https://github.com/etsabary/visual-decision-benchmark">GitHub evidence</a></nav><main>'+content+'</main><footer>Updated October 27, 2026. All 19 earlier records unchanged. Partial speed stops remain outside the complete ranking.</footer><script>'+js+'</script></body></html>'
    write(ROOT/'docs/report.html',page)
    dated=page.replace(NAME+'/','')
    for href in ('gallery.html','LLM_IMAGE_REFERENCES.md','LOCAL_IMAGE_RUNS.md','THIRD_PARTY_NOTICES.md','OCTOBER27_UPDATES.md'):dated=dated.replace('href="'+href+'"','href="../'+href+'"')
    write(DEST/'report.html',dated.replace('href="questions/','href="../questions/'))
    write(ROOT/'documents/OCTOBER27_UPDATES.md','# D3 Ultra and Liquid d1.1 image runs\n\n'+notes.replace('](results/releases/'+NAME+'/','](../results/releases/'+NAME+'/'))
    write(ROOT/'documents/native_image_analysis.md',notes.replace('](results/releases/'+NAME+'/','](../results/releases/'+NAME+'/'))
    for name,title,text in [('METHODOLOGY.md','October 27 native image update','D3 Ultra and Liquid d1.1 add 400 first attempts using exact original reviewed PNG/JPEG bytes, no retries. All 19 earlier records and three LLM speed stops remain unchanged. See [new protocol](OCTOBER27_UPDATES.md).'),('RELEASE_NOTES.md','October 27 image publication','Added D3 Ultra 148/200 (74.0%),361ms median; Liquid d1.1 144/200 (72.0%),425 ms median. 21 complete routes, 420 category cells; preserved19 previous model records and all exclusions.')]:
        p=ROOT/'documents'/name
        if not p.read_text().startswith('# '+title):write(p,'# '+title+'\n\n'+text+'\n\n'+p.read_text())
    write(ROOT/'results/README.md','# Dated image results\n\n- [Current: 21 complete routes](releases/'+NAME+'/summary.json):18 hosted decisions, two local and Sol reference. [New timing/usage](releases/'+NAME+'/october27_timing_evidence.jsonl).\n- [Previous19 routes](releases/celeris_2026-10-26/summary.json), [18 routes](releases/llm_reference_2026-10-25/summary.json), [17 routes](releases/local_images_2026-10-25/summary.json): preserved.\n\nAll dated evidence remains sealed. New D3/Liquid routes use original reviewed files; previous PNG variants retain their exact provenance.\n')
    dump(DEST/'audit_receipt.json',dict(status='VERIFIED_21_ROUTES',complete_routes=21,new_models=2,prior_19_records_unchanged=True,
        question_sha256=digest(ROOT/'data/questions.jsonl'),key_sha256=evidence.KEY_HASH,private_seal_sha256=digest(evidence.CAPTURE/'seal.json'),
        scored_first_attempts=400,new_usable=400,new_correct={'d3_ultra':148,'liquid11_decision':144},admission_probes=10,retries=0,
        payloads_rebuilt=400,original_image_hashes_verified=227,publication_inference_calls=0,
        privacy='Answer-free timing hashes and aggregate scores; no keys, model choices, per-item correctness, credentials or LAN addresses',
        scoring_limit='Owner reconciled frozen private key offline; public exports reproduce timing, coverage and arithmetic'))
    write(ROOT/'docs/sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+SITE+'</loc><lastmod>2026-10-27</lastmod></url></urlset>')
    mirror();bind_layout();print('Built21 image routes, 420 category cells;19 earlier records unchanged; no inference')

def seal():
    assert not (DEST/'manifest.json').exists(),'Never overwrite sealed evidence'
    dump(DEST/'manifest.json',dict(version='native-image-updates-20261027-v1',complete_routes=21,questions_each=200,
        complete_llm_references=1,speed_stopped_llm_references=3,question_sha256=digest(ROOT/'data/questions.jsonl'),
        prior_summary_sha256=digest(OLD/'summary.json'),artifacts={p.relative_to(DEST).as_posix():digest(p) for p in sorted(DEST.rglob('*')) if p.is_file()}))
    mirror();bind_layout();paths={ROOT/name for name in json.loads(MANIFEST.read_text())['current_files']};paths.add(MANIFEST);paths.update(p for p in DEST.rglob('*') if p.is_file())
    dump(DEST/'release_checksums.json',{p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)});mirror();print('Sealed October27 image release and exact mirror')


def plot(s):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Patch
    import numpy as np
    import textwrap
    from plot_native_images import speed_color,cost_color
    ids=s['rank_order'];models=[s['models'][mid] for mid in ids];labels=[m['label'] for m in models];y=np.arange(len(ids))
    colors=[YELLOW if mid=='reference_sol' else PURPLE if previous.is_local(m) else BLUE for mid,m in zip(ids,models)]
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'native-images-20261027'}):
        def save(fig,stem):
            for ext in ('png','svg'):fig.savefig(DEST/(stem+'.'+ext),dpi=160,facecolor='white',metadata={'Date':None} if ext=='svg' else {})
            svg=DEST/(stem+'.svg');write(svg,'\n'.join(line.rstrip() for line in svg.read_text().splitlines()));plt.close(fig)
        fig,axes=plt.subplots(1,3,figsize=(18,13.5),sharey=True,gridspec_kw={'width_ratios':[1.2,1.1,1.25]})
        axes[0].barh(y,[m['accuracy']*100 for m in models],color=colors,height=.65)
        axes[0].set_yticks(y,labels);axes[0].invert_yaxis();axes[0].set_xlim(0,112)
        axes[0].axvline(s['random_uniform_baseline']*100,color='#8b98a5',linestyle=':',linewidth=1)
        for i,(mid,m) in enumerate(zip(ids,models)):
            axes[0].text(m['accuracy']*100+1,i,f"{m['correct']}/200 · {m['accuracy']:.1%}",va='center',fontsize=9)
            axes[1].plot([m['median_ms'],m['p95_ms']],[i,i],color='#93a1ad',linewidth=2)
            axes[1].scatter(m['median_ms'],i,c=speed_color(m['median_ms']),s=50,edgecolor='#334155');axes[1].scatter(m['p95_ms'],i,c='#334155',marker='d',s=22)
            if previous.is_local(m):axes[2].text(.03,i,'Local compute · unmeasured',transform=axes[2].get_yaxis_transform(),color=PURPLE,va='center',fontsize=9)
            elif m['public_free_access']:axes[2].text(.03,i,'Free access†',transform=axes[2].get_yaxis_transform(),va='center',fontsize=9)
            else:
                v=float(m['core_cost_per_1000_known_usd']);axes[2].scatter(v,i,c=cost_color(v),s=50,edgecolor='#334155');axes[2].annotate(money(m,True),(v,i),xytext=(8,0),textcoords='offset points',va='center',fontsize=9)
        for tick,mid,m in zip(axes[0].get_yticklabels(),ids,models):
            tick.set_color('#8d6c0a' if mid=='reference_sol' else PURPLE if previous.is_local(m) else BLUE)
            if mid=='reference_sol' or previous.is_local(m):tick.set_weight('bold')
        axes[1].set_xscale('log');axes[1].set_xlim(100,5000);axes[2].set_xscale('log');axes[2].set_xlim(.005,12)
        for a,title in zip(axes,['Accuracy · 200 first attempts','Response time · median and p95','USD / 1,000 questions']):
            a.set_title(title,fontweight='bold',pad=14);a.grid(axis='x',alpha=.15);a.set_axisbelow(True);a.tick_params(axis='y',length=0)
            for spine in a.spines.values():spine.set_visible(False)
        axes[0].set_xlabel('Accuracy (%) · dotted line: 23.44% guessing');axes[1].set_xlabel('ms, log scale · circle median · diamond p95');axes[2].set_xlabel('USD, log scale · rescales actual 200-question cost')
        fig.suptitle('21 complete routes · 18 hosted decisions + 2 local + Sol reasoning-off reference',fontsize=18,y=.98)
        handles=[Patch(color=BLUE,label='Hosted decisions'),Patch(color=PURPLE,label='Local RTX 2060 6 GB'),Patch(color=YELLOW,label='LLM reference, reasoning off')]
        fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.955),ncol=3,frameon=False)
        fig.text(.025,.025,'D3 Ultra: 148/200,361 ms median; Liquid d1.1: 144/200,425 ms median. All 19 earlier records unchanged.\nSonnet 5.5, Opus 5 and Qwen3.8-Max stopped after 20 above the two-second median cutoff; partial results are outside this figure.\nNew D3/Liquid rows reuse exact original PNG/JPEG bytes; Celeris/Sol/local retain their recorded PNG variant. Dates, routes and hardware differ.\nPurple locals use the deliberately chosen older RTX 2060 6 GB; hardware/electricity unmeasured. † Free access is not a production tariff; ~ tariff calculation; * missing charges.',fontsize=9)
        fig.subplots_adjust(left=.21,right=.98,top=.88,bottom=.16,wspace=.34);save(fig,'overview')
        cmap=LinearSegmentedColormap.from_list('accuracy',['#fff4d0','#d5ebce','#77c5c8','#338bac','#183f7a'])
        titles=['Objects, space and routes','Transformations, rules and state','Diagrams and documents','Comparison, perspective and uncertainty']
        for block in range(4):
            fs=list(s['families'])[block*5:block*5+5];values=np.array([[m['families'][f]['correct']/10 for f in fs] for m in models])
            fig,a=plt.subplots(figsize=(13.5,11.5));im=a.imshow(values,vmin=0,vmax=1,cmap=cmap,aspect='auto');a.set_yticks(range(len(models)),labels)
            for tick,mid,m in zip(a.get_yticklabels(),ids,models):
                tick.set_color('#8d6c0a' if mid=='reference_sol' else PURPLE if previous.is_local(m) else BLUE)
                if mid=='reference_sol' or previous.is_local(m):tick.set_weight('bold')
            a.set_xticks(range(5),['\n'.join(textwrap.wrap(s['families'][f]['name'],21))+'\n10 questions' for f in fs]);a.tick_params(length=0,pad=8)
            for i in range(len(models)):
                for j in range(5):a.text(j,i,f'{round(values[i,j]*10)}/10',ha='center',va='center',color='white' if values[i,j]>=.7 else '#183044')
            for spine in a.spines.values():spine.set_visible(False)
            fig.colorbar(im,ax=a,pad=.025,fraction=.025).set_ticks([0,.25,.5,.75,1],labels=['0%','25%','50%','75%','100%'])
            fig.suptitle(titles[block],fontsize=19,y=.975);fig.text(.025,.025,'Purple names: local RTX 2060. Amber name: Sol reasoning-off LLM reference. Cells always encode accuracy on a fixed 0–100% scale.\nOnly complete 200-question routes; each cell is correct / 10. One answer changes a category by ten percentage points.',fontsize=10)
            fig.subplots_adjust(left=.29,right=.95,top=.91,bottom=.15);save(fig,'abilities_'+str(block+1))



if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--answer-key',type=Path);ap.add_argument('--seal',action='store_true');a=ap.parse_args()
    if a.seal:seal()
    else:
        assert a.answer_key,'Explicit external frozen key required';build(a.answer_key)
