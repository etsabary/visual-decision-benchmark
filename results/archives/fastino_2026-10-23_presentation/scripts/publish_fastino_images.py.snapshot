"""Publish the completed GLiDE image capture offline; no inference or credentials.

Scores the saved choices against an explicitly supplied frozen external key,
exports aggregates and sanitized responses, and preserves the prior release.
"""
from repo_layout import repo_file, frozen_file
import argparse
import ast
from collections import Counter
from copy import deepcopy
import csv
from decimal import Decimal
from hashlib import sha256
from html import escape
import io
import json
import math
from pathlib import Path
import re
import shutil
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import analyze_native_images as old_analysis
import benchmark as bank
import plot_native_images as plots
from score import load_key

NAME='fastino_2026-10-23'
DEST=repo_file('results/releases', root=ROOT)/NAME
OLD=repo_file('native_images_2026-10-20', root=ROOT)
TEXT=ROOT.parent/'jev-1.14-comparison-benchmark'
CAPTURE=TEXT/'runs/fastino_glide_2026-10-23'
PRIVATE=CAPTURE/'analysis/94a8a3cda795c060/statistics.json'
MID='fastino_glide'
SOURCES=['https://docs.fastino.ai/inference/systemone','https://docs.fastino.ai/concepts/models']


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.rstrip()+'\n',encoding='utf-8')
def dump(path,value):write(path,json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False))
def lines(path,values):write(path,'\n'.join(json.dumps(v,ensure_ascii=False,allow_nan=False) for v in values))


def archive_prior():
    seal=json.loads((OLD/'checksums.json').read_text())
    folder=repo_file('results/archives/native_images_2026-10-20_presentation', root=ROOT)
    entries={}
    for name,h in seal['files'].items():
        path=Path(name)
        if (len(path.parts)==1 and path.suffix in ('.py','.md','.html','.cff','.txt')) or path.parts[0]=='.github':
            target=folder/(name+'.snapshot')
            if target.exists():assert digest(target)==h,name
            else:
                assert digest(repo_file(name, root=ROOT))==h,name
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo_file(name, root=ROOT),target)
            entries[name]=dict(path=target.relative_to(ROOT).as_posix(),sha256=h)
    target=folder/'manifest.json'
    value=dict(version='native-image-history-20261023',files=entries,purpose='Exact October20 presentation/source bytes; dated data and seals are not rewritten.')
    if target.exists():assert json.loads(target.read_text())==value
    else:dump(target,value)


def load(key_path):
    assert digest(key_path)==old_analysis.KEY_HASH,'Image key is not the frozen reference'
    key=load_key(key_path)
    questions={q['candidate_id']:q for q in bank.rows(repo_file('data/questions.jsonl', root=ROOT))}
    private=json.loads(PRIVATE.read_text());v=private['groups']['image']
    out=CAPTURE/'image';seal=json.loads((out/'completion.json').read_text())
    assert seal['status']=='COMPLETE' and seal['n']==200
    for name,h in seal['files_sha256'].items():assert digest(out/name)==h,name
    raw=bank.rows(out/'attempts.jsonl')
    assert len(raw)==len({r['candidate_id'] for r in raw})==200
    assert set(r['candidate_id'] for r in raw)==set(key)==set(questions)
    assert all(r['attempt']==1 and r['status']=='ok' and r['model_returned']=='glide_v2' for r in raw)
    assert sum(r['choice']==key[r['candidate_id']] for r in raw)==v['correct']==158
    assert v['median_ms']==statistics.median(r['latency_ms'] for r in raw)
    assert v['p95_ms']==old_analysis.percentile([r['latency_ms'] for r in raw],.95)
    assert Decimal(v['cost']['exact_decimal'])==sum((Decimal(r['usage']['input_tokens'])*Decimal('.00000004') for r in raw),Decimal(0))
    baseline=json.loads((OLD/'summary.json').read_text());combined=deepcopy(baseline)
    model={k:deepcopy(v[k]) for k in ('n','correct','accuracy','usable','accuracy_usable','wilson95','mean_ms','median_ms','p95_ms',
        'status_counts','retries','core_cost','first_cost','probabilities_invalid','eventual_correct','eventual_usable','window',
        'identities','reported_output_tokens','reported_reasoning_text','families','subsets','confidence')}
    model.update(model_id=MID,label='Fastino GLiDE',model_requested='fastino/GLiDE',route='api.fastino.ai/v1/systemone',
        date='2026-10-23',reused=False,public_free_access=False,complete=True,
        core_cost_per_1000_known_usd=str(Decimal(v['cost']['exact_decimal'])*5),
        cost_source='usage_times_published_tariff',usage_based_core_cost_usd=v['cost']['exact_decimal'],
        monetary_receipts=0,version_note=private['version_note'])
    combined['models'][MID]=model
    combined['rank_order']=sorted(combined['models'],key=lambda k:(-combined['models'][k]['correct'],combined['models'][k]['median_ms']))
    combined.update(version='native-images-fastino-20261023',decision_models_reviewed=17,decision_models_ranked=15,
        new_complete_models=13,updated_date_toronto='2026-10-23',prior_summary_sha256=digest(OLD/'summary.json'))
    assert all(combined['models'][mid]==m for mid,m in baseline['models'].items())
    previous=bank.rows(OLD/'attempts.jsonl');original=bank.rows(repo_file('data/attempts.jsonl', root=ROOT))
    for mid,m in baseline['models'].items():
        rr=[r for r in (original if m['reused'] else previous) if r['model_requested']==m['model_requested'] and r['attempt']==1]
        assert len(rr)==200 and sum(r['status']=='ok' and r['choice']==key[r['candidate_id']] for r in rr)==m['correct']
    amos={r['candidate_id']:r['choice']==key[r['candidate_id']] for r in previous if r['model_id']=='amos_large' and r['attempt']==1}
    fastino={r['candidate_id']:r['choice']==key[r['candidate_id']] for r in raw}
    x=sum(amos[i] and not fastino[i] for i in key);y=sum(fastino[i] and not amos[i] for i in key);n=x+y
    combined['leader_pairwise'][MID]=dict(leader_only=x,other_only=y,both_correct=sum(amos[i] and fastino[i] for i in key),
        neither_correct=sum(not amos[i] and not fastino[i] for i in key),
        unadjusted_exact_mcnemar_p=min(1,2*sum(math.comb(n,i) for i in range(min(x,y)+1))/2**n) if n else 1)
    return combined,raw,key


def amount(s,per1000=False):
    if s['public_free_access']:return 'Free access†'
    calculated=s.get('cost_source')=='usage_times_published_tariff'
    value=Decimal(s['core_cost_per_1000_known_usd'] if per1000 else s['usage_based_core_cost_usd'] if calculated else s['core_cost']['known_api_usd'])
    return ('~' if calculated else '')+f'${value:.6f}'+('*' if not calculated and s['core_cost']['missing_api_records'] else '')


def table(s):
    text=['| Decision model | Correct / 200 | Accuracy | Usable | Mean | Median | p95 | Actual 200 cost | Cost / 1,000 | Test date |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for mid in s['rank_order']:
        m=s['models'][mid]
        text.append(f"| {m['label']} | {m['correct']}/200 | {m['accuracy']:.1%} | {m['usable']}/200 | {m['mean_ms']/1000:.3f} s | {m['median_ms']/1000:.3f} s | {m['p95_ms']/1000:.3f} s | {amount(m)} | {amount(m,True)} | {m['date']}{' (reused)' if m['reused'] else ''} |")
    return '\n'.join(text)


def analysis(s):
    p=s['leader_pairwise'][MID]
    return f"""Fastino GLiDE joins the image comparison at **158/200 (79.0%)**, second to **Amos 1 Large at 159/200 (79.5%)**. GLiDE leads the separate text benchmark at **1154/1342 (86.0%)**; it is not first in both banks. Its image mean / median / p95 was **719/359/1950 ms**, and all 200 first attempts returned usable typed choices without retries.

The comparison contains **15 specialized decision models**, all tested on the same 200 image questions. Fastino was measured October 23, 2026. The earlier 14 model records, image bytes, questions and options are unchanged.

<!-- DETAILS -->

## Fastino and Amos: one answer apart, different profiles

Amos answered {p['leader_only']} questions correctly that Fastino missed; Fastino answered {p['other_only']} that Amos missed. The one-answer overall gap is not statistically resolved: the unadjusted paired exact p-value is {p['unadjusted_exact_mcnemar_p']:.3f}. This selected bank includes related task types, so item-level tests do not establish a universal ordering or remove source and category dependence.

Fastino scored **10/10 on sequential state tracking, interface-state decisions and inspection against a reference**. Sequential questions ask what remains after the pictured actions; interface questions ask which action or state follows from a screenshot. It scored 9/10 on attribute/set filtering, spatial relationships, flowcharts, charts, cross-image matching, image/text consistency and recognizing insufficient evidence.

Navigation and planning was **5/10**. Connectivity, rotation/reflection, geometric fit, visual rules and perspective/knowledge tracking were each **6/10**. Amos scored 8/10 on perspective and knowledge tracking, versus Fastino’s 6/10. A strong combined total does not imply equal performance on every visual operation. Each category has ten questions: one answer is ten percentage points, and 10/10 is not a reliability certificate.

## Cost and the two-second rule

Fastino’s complete 200-question cost is **~$0.00767264**, or **~$0.0383632 per 1000 questions**. The tilde marks a calculation from reported input-token usage at the captured **$0.04 per million input tokens, $0 output** tariff, not API monetary receipts. The two separate image admission probes add **~$0.00010484**. Costs per 1000 normalize an actual 200-question run; no extra 1000 calls were made.

Perplexity Decider v1.2 remains a lower-priced metered option at $0.00431642 for 200, with 152 correct answers; kettei-fat costs $0.00213102 and scored 147. Amos and d3 used currently free public access, not guaranteed production tariffs of zero. Fastino is neither the cheapest nor the shortest-median image route.

The predeclared cutoff is a **cumulative median above two seconds after at least 20 cases**, not a p95 cutoff. Fastino’s 359 ms median passed throughout; its p95 was 1950 ms. The first-attempt timings include fresh HTTPS connection, image upload and the complete response. Local encoding, queues and deliberate waits are excluded. The serial image stream overlapped its two-request text stream, with at most three Fastino requests globally. Dates, hardware, load and provider image processing remain confounds.

## Version and actual image support

The native request model is `fastino/GLiDE`; all scored responses identify `glide_v2`. The authenticated catalog described **one-pass GLiDE v2.2**. This is a hosted alias, not an immutable-weight attestation, and the run must not be labelled v1.2. The catalog image flag was false while Fastino’s documentation described image parts. Single-image and three-image probes succeeded, followed by the complete unchanged 200-question image bank. No OCR, captions or replacement images were used.

All scored responses returned valid probabilities, zero reported output tokens and `not-stored` retention headers for `store:false` requests. These are observed API facts, not independent inspection of hidden computation.

## Other models retain category-specific strengths

d3-turbo scored 155/200, including 10/10 on charts, state tracking, interfaces, reference inspection, image matching and image/text consistency. Perplexity scored 152, with 9/10 on causal questions and 10/10 on charts, but 4/10 on connectivity and constraint satisfaction. Cloudflare Clef’s constraint-satisfaction score was 7/10, above Amos’s 6/10 and matching Fastino’s 7/10. Luna Decisions retains the strongest observed rotation/reflection score at 8/10. Model choice can depend on the operation, not just the overall row.

Jev 1.13 and 1.14 remain 142/200 and 141/200, each with five rejected images in their tested routes. Their old failures and timings have not been removed or rerun. The three older general LLMs remain archived references, not the current specialized-model ranking.

## Exclusions are not zero accuracy scores

Respan Span-02’s existing image stream stopped after 21 questions when its median reached 2.166 seconds. Its 14/21 partial score is not a 200-question accuracy estimate. ScaleDown’s pinned route rejected image parts despite catalog support. Those two routes remain outside the complete ranking. Their exclusion is not a claim about their text performance, and the old image statement that Span leads the text bank is superseded by the current text report.
"""


def plot(s):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import numpy as np
    import textwrap
    order=s['rank_order'];models=[s['models'][m] for m in order];y=np.arange(len(models))
    labels=[m['label'] for m in models]
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'fastino-images-20261023'}):
        def save(fig,name):
            for ext in ('png','svg'):fig.savefig(DEST/(name+'.'+ext),dpi=175,bbox_inches='tight',facecolor='white',metadata={'Date':None} if ext=='svg' else {})
            svg=DEST/(name+'.svg');write(svg,'\n'.join(line.rstrip() for line in svg.read_text().splitlines()))
            plt.close(fig)
        fig,ax=plt.subplots(1,3,figsize=(16,8.7),sharey=True,gridspec_kw={'width_ratios':[1.2,1,1.3]})
        ax[0].barh(y,[100*m['accuracy'] for m in models],color='#2176ae',height=.65)
        ax[0].set_yticks(y,labels);ax[0].invert_yaxis();ax[0].set_xlim(0,108)
        ax[0].set_title('Accuracy · all 200 questions',loc='left')
        ax[1].barh(y,[m['median_ms'] for m in models],color=[plots.speed_color(m['median_ms']) for m in models],height=.65)
        ax[1].set_xlim(0,max(m['median_ms'] for m in models)*1.45);ax[1].set_title('Median complete response · ms',loc='left')
        paid=[float(m['core_cost_per_1000_known_usd']) for m in models if not m['public_free_access']];xmax=max(paid)*1.6
        for i,m in enumerate(models):
            ax[0].text(100*m['accuracy']+1,i,f"{m['correct']}/200 · {m['accuracy']:.1%}",va='center',fontsize=9)
            ax[1].text(m['median_ms']+8,i,f"{m['median_ms']:.0f}",va='center',fontsize=9)
            if m['public_free_access']:ax[2].text(.01*xmax,i,'Free access · not a metered $0 price',va='center',fontsize=8.5)
            else:
                v=float(m['core_cost_per_1000_known_usd']);ax[2].barh(i,v,color=plots.cost_color(v),height=.65)
                ax[2].text(v+.012*xmax,i,amount(m,True),va='center',fontsize=9)
        ax[2].set_xlim(0,xmax);ax[2].set_title('Cost / 1,000 questions · USD',loc='left')
        for a in ax:
            for spine in ('top','right','left'):a.spines[spine].set_visible(False)
            a.tick_params(axis='y',length=0);a.grid(axis='x',alpha=.13);a.set_axisbelow(True)
        fig.suptitle('Image-grounded decisions · 15 specialized models · 200 questions each',x=.05,y=1.01,ha='left',fontsize=19,fontweight='bold')
        fig.text(.05,.01,'Fastino: October 23, 2026; earlier October 15/20 measurements unchanged. ~ = usage-based tariff calculation, not monetary receipt.\nCost / 1,000 normalizes actual 200-question totals; * = missing error charges. Free access is not a production-price guarantee.\nSpeed: green ≤500 ms, yellow ≤1 s, orange ≤2 s. Cost per 1,000: green ≤$0.05, yellow ≤$0.15, orange ≤$0.50, red above.\nSpan partial and ScaleDown rejection remain excluded. Different routes, dates and hardware remain confounds.',fontsize=9)
        fig.tight_layout(rect=(0,.13,1,.97),w_pad=3);save(fig,'overview')
        cmap=LinearSegmentedColormap.from_list('accuracy',['#fff4d0','#d5ebce','#77c5c8','#338bac','#183f7a'])
        titles=['Objects, space and routes','Transformations, rules and state','Diagrams and documents','Comparison, perspective and uncertainty']
        for block in range(4):
            fs=list(s['families'])[block*5:block*5+5];values=np.array([[m['families'][f]['correct']/10 for f in fs] for m in models])
            fig,a=plt.subplots(figsize=(12.5,8));im=a.imshow(values,vmin=0,vmax=1,cmap=cmap,aspect='auto')
            a.set_yticks(range(15),labels);a.set_xticks(range(5),['\n'.join(textwrap.wrap(s['families'][f]['name'],24))+f'\n({f}, n=10)' for f in fs]);a.tick_params(length=0,pad=8)
            for i in range(15):
                for j in range(5):a.text(j,i,f'{round(values[i,j]*10)}/10',ha='center',va='center',fontsize=11,color='white' if values[i,j]>=.7 else '#183044')
            for spine in a.spines.values():spine.set_visible(False)
            bar=fig.colorbar(im,ax=a,pad=.025,fraction=.025);bar.set_ticks([0,.25,.5,.75,1],labels=['0%','25%','50%','75%','100%'])
            fig.suptitle(titles[block],x=.05,y=1.01,ha='left',fontsize=18,fontweight='bold')
            fig.text(.05,-.02,'Same overall-score order; every cell is correct / 10. One answer is ten percentage points, not a reliability guarantee.',fontsize=9)
            fig.tight_layout();save(fig,'abilities_'+str(block+1))


def css_js():
    tree=ast.parse((repo_file('publish_native_images.py', root=ROOT)).read_text());values={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ('css','js'):values[target.id]=node.value.value
    return values['css'],values['js']


def build(key_path):
    import markdown
    archive_prior();assert not (DEST/'manifest.json').exists(),'Never overwrite a sealed release'
    s,raw,key=load(key_path);DEST.mkdir(parents=True,exist_ok=True)
    dump(DEST/'summary.json',s)
    fields=set(old_analysis.PUBLIC_FIELDS)|{'usage','response_headers'}
    sanitized=[{k:v for k,v in r.items() if k in fields} for r in raw]
    old_rows=bank.rows(OLD/'attempts.jsonl');lines(DEST/'attempts.jsonl',old_rows+sanitized)
    probes=bank.rows(OLD/'compatibility_probes.jsonl')
    for index in (1,2):
        value=json.loads((CAPTURE/'image'/f'probe_{index}_attempt_1.json').read_text())
        row={**value['response'],**value['parsed'], 'model_id':MID,'model_requested':'fastino/GLiDE'}
        probes.append({k:v for k,v in row.items() if k in fields}|{'probe_index':index,'payload_sha256':value['payload_sha256']})
    lines(DEST/'compatibility_probes.jsonl',probes)
    wrappers=json.loads((OLD/'model_manifests.json').read_text())
    wrappers[MID]=dict(manifest=json.loads((CAPTURE/'image/manifest.json').read_text()),
        software=json.loads((CAPTURE/'image/software.json').read_text()),
        metadata=json.loads((CAPTURE/'image/model_metadata.json').read_text()),
        completion=json.loads((CAPTURE/'image/completion.json').read_text()))
    dump(DEST/'model_manifests.json',wrappers)
    # Public source snapshots reproduce the executed pre-layout revision, without keys.
    for name,h in wrappers[MID]['software'].items():
        source=CAPTURE/'image/software_capture'/(name+'.snapshot');assert digest(source)==h
        target=DEST/'captured_software'/(name+'.snapshot');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    caps=json.loads((OLD/'image_capabilities.json').read_text())
    caps.setdefault('models',{})[MID]=dict(image_input=True,source=SOURCES,checked='2026-10-23',
        evidence='Single and three-image probes plus 200 unchanged scored image cases; catalog flag false is preserved in metadata',model_requested='fastino/GLiDE',returned='glide_v2')
    dump(DEST/'image_capabilities.json',caps)
    narrative=analysis(s);write(DEST/'analysis.md',narrative)
    plot(s)
    intro,details=narrative.split('<!-- DETAILS -->',1)
    methods='''Every ranked model has the same **200 questions**, original choices and reviewed image bytes. Accuracy includes all first attempts; invalid answers and provider errors remain unsuccessful. No wrong-choice or formatting retries. At most one transient recovery was permitted; Fastino needed none. The median cutoff is above two seconds after at least 20 questions.

**Cost / 1,000 is a normalization of each actual 200-question run**, not another 1000 calls. ~ means usage times captured tariff, not API monetary receipts; * means an incomplete sum with missing error charges; † means free public access, not a permanent production price of zero. Probes and stopped runs are separate from ranked core totals.

Speed colours: green ≤0.5 s, yellow ≤1 s, orange ≤2 s, red above. Cost colours per 1000: green ≤$0.05, yellow ≤$0.15, orange ≤$0.50, red above. Accuracy uses one fixed 0–100% scale across categories. Dates and routes differ; none of the older measurements was rerun.'''
    charts='\n\n'.join(f'![Named category scores, part {i}](results/releases/{NAME}/abilities_{i}.png)' for i in range(1,5))
    definitions='\n'.join(f"- **[{fid} {v['name']}](questions/{fid}.md)**: {v['description']}" for fid,v in s['families'].items())
    limits=f'''The bank has 20 categories × 10 questions, 227 compressed source files and {s['random_uniform_baseline']:.2%} uniform-random baseline (choice counts vary). There are 187 reasoning/grounded-decision questions and 13 perception controls. No image was recompressed for this update. 221 files are publicly redistributable; six Our World in Data charts remain withheld pending source-terms review. All scored models used the same private reviewed snapshots, not replacement downloads.

The frozen supplied key was kept outside inference execution. Offline re-scoring reproduced all 14 prior specialized totals and Fastino’s new total. This is consistency against the existing key, not an independent new audit of every answer. Public validators reconcile hashes, payloads where assets are available, categories, timing and exact-decimal costs; private-key correctness cannot be independently reproduced from aggregate exports alone.

[Questions and source images](questions/README.md) · [Image gallery](gallery.html) · [Attribution](THIRD_PARTY_NOTICES.md) · [Aggregate results](results/releases/{NAME}/summary.json) · [Category CSV](results/releases/{NAME}/family_scores.csv) · [Sanitized route evidence](results/releases/{NAME}/attempts.jsonl) · [Audit](results/releases/{NAME}/audit_receipt.json).

Older general LLM runs are preserved in [original results](results/summary.json), outside the current specialized ranking. The [separate text benchmark](https://etsabary.github.io/system-1-decision-benchmark/report.html) has 1342 text questions; the two bank scores must not be combined.

Implementation is in scripts/, supporting documents in documents/, bank and image assets in data/, and dated evidence in results/. Public report and gallery URLs remain stable. Offline checks: `python3 scripts/validate_fastino_images.py`, `python3 scripts/validate_native_images.py`, and the focused tests in scripts/.'''
    report='# Image-grounded System 1 decision benchmark\n\n'+intro.strip()+'\n\n[Open the colour-coded report](https://etsabary.github.io/visual-decision-benchmark/report.html)\n\n'+f'![Accuracy, speed and cost](results/releases/{NAME}/overview.png)\n\n## Overall results\n\n'+table(s)+'\n\n## Method and reading the costs\n\n'+methods+'\n\n'+details.strip()+'\n\n## Results by named category\n\nEvery category has ten questions; one answer is ten percentage points.\n\n'+charts+'\n\n## What the categories test\n\n'+definitions+'\n\n## Bank and limitations\n\n'+limits
    write(repo_file('README.md', root=ROOT),report)
    buffer=io.StringIO();writer=csv.writer(buffer,lineterminator='\n');writer.writerow(['model_id','model','family_id','family','correct','questions','accuracy'])
    for mid in s['rank_order']:
        for fid,v in s['families'].items():writer.writerow([mid,s['models'][mid]['label'],fid,v['name'],s['models'][mid]['families'][fid]['correct'],10,s['models'][mid]['families'][fid]['correct']/10])
    write(DEST/'family_scores.csv',buffer.getvalue())
    buffer=io.StringIO();writer=csv.writer(buffer,lineterminator='\n');writer.writerow(['model_id','model','correct','questions','accuracy','usable','mean_ms','median_ms','p95_ms','actual_200_cost','cost_per_1000','cost_basis','test_date'])
    for mid in s['rank_order']:
        m=s['models'][mid];writer.writerow([mid,m['label'],m['correct'],200,m['accuracy'],m['usable'],m['mean_ms'],m['median_ms'],m['p95_ms'],amount(m),amount(m,True),m.get('cost_source','free_access' if m['public_free_access'] else 'api_reported'),m['date']])
    write(DEST/'leaderboard.csv',buffer.getvalue())
    # Preserve familiar CSS and filtering, replacing only the data-bearing content.
    css,js=css_js();site_md=report.replace('results/releases/'+NAME+'/',NAME+'/')
    content=markdown.markdown(site_md,extensions=['tables','fenced_code'])
    matrix='<label class="filter">Find a model <input id="model-filter" placeholder="Type a model name…" autocomplete="off"></label>'
    for block in range(4):
        fs=list(s['families'])[block*5:block*5+5]
        heads=''.join('<th>'+escape(s['families'][f]['name'])+'<small>'+f+' · n=10</small></th>' for f in fs)
        rr=''
        for mid in s['rank_order']:
            m=s['models'][mid];cells=''.join(f'<td class="accuracy" data-model-id="{mid}" data-family="{f}" data-correct="{m["families"][f]["correct"]}" data-ratio="{m["families"][f]["correct"]/10}">{m["families"][f]["correct"]}/10</td>' for f in fs)
            rr+=f'<tr data-model="{escape(m["label"],quote=True)}"><th scope="row">{escape(m["label"])}</th>{cells}</tr>'
        matrix+='<div class="table-scroll"><table class="family-table"><thead><tr><th>Decision model</th>'+heads+'</tr></thead><tbody>'+rr+'</tbody></table></div>'
    start=content.index('<p><img alt="Named category scores, part 1"');end=content.index('<h2>What the categories test</h2>',start)
    content=content[:start]+matrix+content[end:]
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Image decisions · 15 models · Fastino update</title><style>'+css+'</style></head><body><nav><a href="#">Overview</a><a href="#overall-results">Scores, speed &amp; cost</a><a href="#results-by-named-category">Named categories</a><a href="gallery.html">Questions &amp; images</a><a href="https://github.com/etsabary/visual-decision-benchmark">GitHub evidence</a></nav><main>'+content+'<footer>Updated October 23, 2026. Earlier records and dated seals remain unchanged.</footer></main><script>'+js+'</script></body></html>'
    write(repo_file('report.html', root=ROOT),page)
    write(repo_file('index.html', root=ROOT),'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=report.html"><title>Image decision benchmark</title><a href="report.html">Open the image benchmark</a>')
    dump(DEST/'audit_receipt.json',dict(status='VERIFIED_COMPLETE_FASTINO_IMAGE_200',n=200,correct=158,prior_14_records_unchanged=True,
        bank_sha256=digest(repo_file('data/questions.jsonl', root=ROOT)),key_sha256=old_analysis.KEY_HASH,private_aggregate_sha256=digest(PRIVATE),
        capture_files_sha256=json.loads((CAPTURE/'image/completion.json').read_text())['files_sha256'],
        usage_core_usd='0.00767264',probe_usage_usd='0.00010484',reported_monetary_receipts=0,
        note='No per-item correct labels, answer key, raw account state or credentials exported.'))
    artifacts={p.relative_to(DEST).as_posix():digest(p) for p in DEST.rglob('*') if p.is_file()}
    dump(DEST/'manifest.json',dict(version='fastino-images-20261023-v1',ranked_models=15,questions_each=200,
        bank_sha256=digest(repo_file('data/questions.jsonl', root=ROOT)),prior_summary_sha256=digest(OLD/'summary.json'),artifacts=artifacts))
    print('Built image publication: 15 complete models; 300 named category cells; Fastino second; no inference.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-only',action='store_true')
    parser.add_argument('--answer-key',type=Path)
    args=parser.parse_args()
    if args.archive_only:archive_prior()
    else:
        assert args.answer_key,'External frozen key required for offline consistency check'
        build(args.answer_key)
