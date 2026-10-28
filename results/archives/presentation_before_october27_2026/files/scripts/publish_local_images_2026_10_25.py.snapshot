"""Offline publication of two completed local image routes; never runs inference."""
import argparse
from collections import Counter
from copy import deepcopy
import csv
from hashlib import sha256
from html import escape
import io
import json
from pathlib import Path
import shutil
import statistics
import subprocess

from benchmark import rows
from local_image_protocol import payload, wire
from local_image_publication_history import ARCHIVE
from repo_layout import ROOT, MANIFEST
from score import load_key

NAME = 'local_images_2026-10-25'
DEST = ROOT / 'results/releases' / NAME
OLD = ROOT / 'results/releases/fastino_2026-10-23'
CAPTURE = ROOT.parent / 'text-decision-hardening/runs/local_image_png_2026-10-25'
CAPABILITIES = CAPTURE.parent / 'local_image_capability_2026-10-25'
BASE_COMMIT = '1461432690efe359d761305776deeaa165668c9f'
KEY_HASH = 'f62348cb73594146497858473fb01c4f78bb06a0649a857329ca47197688fe7c'
LOCAL = {'local_h2o_lightning_4b': ('h2o-lightning:4b', 'H2O Lightning 4B'),
         'local_fovea_4b': ('fovea:4b', 'Fovea 4B')}
PURPLE, BLUE = '#7c3aed', '#16728c'
VARIANT = 'PNG-lossless-from-reviewed-decoded-RGB-v1'


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8')


def dump(path, value):
    write(path, json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False))


def archive_prior():
    """Preserve old sealed bytes, including files edited for this new release."""
    entries = {}
    for name, h in json.loads((OLD / 'release_checksums.json').read_text()).items():
        if name.startswith('results/releases/fastino_2026-10-23/'):
            continue
        target = ARCHIVE / (name + '.snapshot')
        if not target.exists():
            raw = subprocess.check_output(['git', 'show', BASE_COMMIT + ':' + name], cwd=ROOT)
            assert sha256(raw).hexdigest() == h, name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        assert digest(target) == h, name
        entries[name] = dict(path=target.relative_to(ROOT).as_posix(), sha256=h)
    value = dict(version='fastino-presentation-history-20261025', files=entries,
                 purpose='Exact sealed October23 presentation; old measurement files and seals unchanged')
    path = ARCHIVE / 'manifest.json'
    if path.exists():
        assert json.loads(path.read_text()) == value
    else:
        dump(path, value)


def load(key_path):
    assert digest(key_path) == KEY_HASH
    gold = load_key(key_path)
    seal = json.loads((CAPTURE / 'seal.json').read_text())
    for name, h in seal['files'].items():
        assert digest(CAPTURE / name) == h, name
    private = json.loads((CAPTURE / 'final_report.json').read_text())
    audit = json.loads((CAPTURE / 'audit_receipt.json').read_text())
    assert audit['status'] == 'PASS' and audit['first_attempts'] == audit['usable_first_attempts'] == 400
    variant = json.loads((CAPTURE / 'image_variant_manifest.json').read_text())
    questions = {q['candidate_id']: q for q in rows(ROOT / 'data/questions.jsonl')}
    assert digest(ROOT / 'data/questions.jsonl') == private['bank_sha256']
    assert set(questions) == set(gold) and len(gold) == 200
    manifest = json.loads((CAPTURE / 'manifest.json').read_text())
    old = json.loads((OLD / 'summary.json').read_text())
    result = deepcopy(old)
    timings, metadata = [], {}
    for mid, (model, label) in LOCAL.items():
        folder = CAPTURE / model.replace(':', '__')
        rr, dd = rows(folder / 'attempts.jsonl'), rows(folder / 'dispatches.jsonl')
        v = private['models'][model]
        assert v['state'] == 'complete' and len(rr) == len(dd) == v['attempted'] == 200
        assert [r['candidate_id'] for r in rr] == manifest['question_order']
        assert len({r['candidate_id'] for r in rr}) == 200
        assert all(r['status'] == 'ok' and r['attempt'] == 1 for r in rr)
        assert sum(r['choice'] == gold[r['candidate_id']] for r in rr) == v['correct']
        for r, d in zip(rr, dd):
            q = questions[r['candidate_id']]
            images = [Path(variant['assets'][a]['path']).read_bytes() for a in q['asset_ids']]
            assert sha256(wire(payload(model, q, images))).hexdigest() == r['payload_sha256'] == d['payload_sha256']
            timings.append(dict(model_id=mid, model_requested=model, request_index=r['request_index'],
                candidate_id=r['candidate_id'], family_id=r['family_id'], attempt=1, status=r['status'],
                latency_ms=r['latency_ms'], request_payload_sha256=r['payload_sha256'],
                image_sha256=r['image_sha256'], image_variant=VARIANT,
                output_tokens=r['response']['raw']['usage']['output_tokens'],
                state_truncated=r['response']['raw']['state_truncated']))
        xs = [r['latency_ms'] for r in rr]
        assert statistics.mean(xs) == v['mean_ms'] and statistics.median(xs) == v['median_ms']
        start = json.loads((folder / 'metadata_start.json').read_text())['raw']
        end = json.loads((folder / 'metadata_end.json').read_text())['raw']
        assert start['digest'] == end['digest']
        device = json.loads((folder / 'device_start.json').read_text())['raw']['models'][0]
        metadata[mid] = dict(model_requested=model, serving_digest=start['digest'], precision=start['details']['quantization_level'],
            device=device['device'], context_length=device['context_length'], runtime='Ollaya 0.17.0',
            hardware='NVIDIA RTX 2060', vram_gb=6, hardware_source='user_reported',
            immutable_upstream_weight_revision='Not reported by installed route', image_variant=VARIANT,
            screen_median_ms=statistics.median(xs[:20]), warmup_calls=v['warmup_calls'])
        families = {f: dict(n=c['attempted'], correct=c['correct'], usable=c['attempted']) for f,c in v['families'].items()}
        result['models'][mid] = dict(model_id=mid, label=label, execution_location='local',
            route='Local Ollaya /api/decide over LAN HTTP', complete=True, reused=False, date='2026-10-25',
            n=200, correct=v['correct'], accuracy=v['accuracy'], usable=200, accuracy_usable=v['accuracy'],
            mean_ms=v['mean_ms'], median_ms=v['median_ms'], p95_ms=v['p95_ms'], status_counts={'ok':200},
            retries=0, reported_output_tokens=0, reported_reasoning_text=0, families=families,
            public_free_access=False, core_cost_per_1000_known_usd=None,
            cost_source='local_hardware_electricity_unmeasured', **metadata[mid])
    result.update(version='local-images-20261025-v1', updated_date_toronto='2026-10-25',
        decision_models_ranked=17, decision_models_reviewed=26, new_complete_models=15,
        hosted_model_count=15, local_model_count=2, local_model_ids=list(LOCAL),
        prior_summary_sha256=digest(OLD/'summary.json'),
        input_variant_note='Hosted rows retain original mixed PNG/JPEG inputs. Local rows use PNG derivatives with verified identical decoded RGB pixels.',
        complete_first_attempt_cases=3400, local_first_attempt_cases=400,
        historical_cost_scope_note='Inherited new_scored_cost/probe_cost fields retain the October20 hosted aggregate scope. Later Fastino and local rows have their own cost qualifications; these fields are not totals for all 17 routes.',
        location_colors={'local':PURPLE,'hosted':BLUE})
    result['rank_order'] = sorted(result['models'], key=lambda mid:(-result['models'][mid]['correct'], result['models'][mid]['median_ms']))
    assert all(result['models'][mid] == m for mid,m in old['models'].items())
    return result, timings, metadata, variant, manifest


def is_local(m):
    return m.get('execution_location') == 'local'


def amount(m, per1000=False):
    if is_local(m):
        return 'Unmeasured local compute'
    from publish_fastino_images import amount as previous_amount
    return previous_amount(m, per1000)


def table(s):
    text=['| Decision model | Hosting / inputs | Correct / 200 | Accuracy | Usable | Mean | Median | p95 | Actual 200 cost | Cost / 1,000 | Test date |',
          '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |']
    for mid in s['rank_order']:
        m=s['models'][mid]
        setting='Local RTX 2060 6 GB · PNG' if is_local(m) else 'Hosted · original mixed images'
        text.append('| '+' | '.join([m['label'],setting,f"{m['correct']}/200",f"{m['accuracy']:.1%}",f"{m['usable']}/200"]+
            [f"{m[k]:.0f} ms" for k in ('mean_ms','median_ms','p95_ms')]+[amount(m),amount(m,True),m['date']+(' (reused)' if m['reused'] else '')])+' |')
    return '\n'.join(text)


def narrative(s):
    return '''The comparison now contains **17 complete decision routes: 15 hosted models and two local models**. Each completed route has 200 first attempts on the same questions and choices. Local models use a separately recorded PNG input variant. Earlier hosted measurements remain unchanged.

**H2O Lightning 4B scored 117/200 (58.5%) at 560/484/988 ms mean/median/p95. Fovea 4B scored 110/200 (55.0%) at 658/602/962 ms.** Both returned 200 usable typed choices, with no scored retries, on a user-reported NVIDIA RTX 2060 with 6 GB VRAM. This older GPU was chosen deliberately to examine a more accessible local setup.

Amos 1 Large remains the highest-scoring hosted route at **159/200 (79.5%)**, followed by Fastino GLiDE at **158/200 (79.0%)** and hosted d3-turbo at **155/200 (77.5%)**. The one-answer Amos/Fastino gap remains statistically unresolved. These results cover immediate fixed-choice decisions without tools or iterative reasoning.

## Local hosting: useful speed, lower accuracy

H2O answered seven more questions correctly than Fovea and had lower mean and median latency. Their p95 values were both close to one second; Fovea's was slightly lower. This two-model comparison does not establish a general model ordering.

The exact local routes were `h2o-lightning:4b` at **Q8_0** and `fovea:4b` at **NF4 with FP16 compute and FP32 readout**, served by Ollaya 0.17.0 on `cuda:0`. Both reported an 8,192-token context. Serving digests are captured in the metadata export; these routes did not report immutable upstream weight revisions.

H2O's strongest categories were **interface-state decisions and inspection against a reference, both 10/10**, followed by attribute/set filtering at 9/10. Spatial relationships, image/text consistency and recognizing insufficient evidence were 8/10. Its weakest categories were geometry/folding/fit at 1/10 and rotation/reflection at 3/10. Counting, connectivity, visual rules, constraint satisfaction and perspective/knowledge tracking were each 4/10.

Fovea scored **8/10 on attribute/set filtering, interface-state decisions and inspection against a reference**. Spatial relationships, matching across images and image/text consistency were 7/10. Flowcharts were 2/10 and perspective/knowledge tracking 3/10. Fovea exceeded H2O on counting (6 vs 4), rotation/reflection (5 vs 3), geometric fit (4 vs 1), visual rules (6 vs 4) and cross-image matching (7 vs 6). Each category has ten questions: one answer is ten percentage points.

The strongest practical candidate in this tested local shortlist is H2O, but its 58.5% accuracy is a material limitation. The hosted leader answered 42 more questions correctly; differences in weights, precision, image preprocessing, serving hardware and dates prevent attributing that gap to local hosting itself. Local execution provides control over deployment; it did not match the leading hosted accuracy in this run.

## What the PNG conversion changes

The local input variant is **PNG-lossless-from-reviewed-decoded-RGB-v1**. Exactly 47 original JPEG assets were decoded with **Pillow 12.3.0** and saved as PNG; all 180 original PNG assets retained their exact bytes. Independent checks confirmed identical decoded RGB pixels and dimensions for all 227 source files. No resizing, rotation, compositing, OCR, captions, sharpening or replacement download was used.

Questions, rules, option IDs, option order and image order stayed fixed. The local cohort also retained the original 200-question execution order. Older hosted measurements used the original mixed PNG/JPEG file bytes and were not repeated. The local PNG uploads are a distinct recorded format variant; their byte sizes and route timings must not be treated as a controlled hardware-only comparison.

The public image-variant manifest records both original and PNG hashes plus decoded RGB hashes. The answer-free reproduction tool can rebuild the 221 publicly available inputs with the captured Pillow version; six source-rights exclusions remain withheld. Derivative PNG files are generated on demand, keeping the public source repository small.

## Speed gate, loading and usability

Each local route first received two unscored admission/warmup probes: one converted single PNG and one three-image PNG input. Qualifying routes then received 20 scored questions. Continuation required a cumulative median at or below **2,000 ms** and fewer than **5% unusable outputs**, checked after every subsequent first attempt. There was no accuracy-only stop rule. Two further unscored warmups preceded continuation.

H2O's 20-question screen median was **493 ms**; Fovea's was **587 ms**. Both remained within the speed gate through all 200 questions. Cold loading and all warmups are recorded separately and excluded from scored timings. The reported mean/median/p95 include LAN upload and the complete response; local image encoding is excluded. Both routes reported `cuda:0`, unchanged serving digests and zero output tokens. These are observed runtime facts, not independent weight or architecture attestation.

## Admission failures are outside the complete ranking

Liquid d1 3B accepted the converted 1024 × 768 single-image PNG, then returned **HTTP 500 / INFERENCE_FAILED on the three-image admission probe**. The runner's response-body decoding error does not establish the underlying cause. It received no scored bank run and has no accuracy score here.

D3 Mini, Nano, Lite and Edge Q8_0 each failed the first small PNG admission: **185 input tokens exceeded physical batch size 128**. Liquid d1-omni 600M Q8_0 accepted tiny single PNGs, but larger and multiple inputs exceeded the same physical batch setting. These are deployment findings, not wrong answers or zero-accuracy results. No server configuration or weights were changed to rescue a run. Mapika Decider 2B vision accepted single PNGs but rejected multiple images and JPEGs; it was not selected for the full bank. Installed D3 Flash Artemis and Perplexity Flash mixed4 advertised text-only support.

The earlier exclusions remain: Respan Span-02 stopped after 21 questions at a 2,166 ms median, with 14 correct in that partial sample; ScaleDown's tested route rejected image parts. Neither is ranked as a 200-question zero.

## Cost and earlier hosted evidence

**Local hardware and electricity costs are unmeasured.** Local rows have no metered API tariff or monetary receipts; they are not priced at $0. Hosted costs, dates, tariffs and missing-charge qualifications retain their previously measured values. Cost / 1,000 normalizes an actual 200-question run; it does not mean 1,000 calls were made.

Fastino's earlier image result remains 158/200, with **719/359/1950 ms** mean/median/p95 and **~$0.00767264** for 200 questions, or **~$0.0383632 per 1,000**. The tilde marks reported token usage times the captured tariff, not monetary receipts. Perplexity Decider v1.2 remains 152/200 at $0.00431642 for 200; kettei-fat remains 147/200 at $0.00213102. Amos and d3 used free public access, which is not a permanent production tariff.

Fastino retained 10/10 on sequential state tracking, interfaces and reference inspection; navigation was 5/10. Amos scored 8/10 on perspective/knowledge tracking versus Fastino's 6/10. Jev 1.13 and 1.14 retain 142/200 and 141/200, each with five rejected images. No earlier failures, scores or timings were removed. Fastino's separate text lead does not make it the image leader.

## Limits and reproducibility

The bank has 20 categories with ten questions each, 187 grounded/reasoning questions and 13 perception controls. Choice counts vary, giving a **23.44% uniform-guessing baseline**. Related templates and shared source collections limit independence; these are selected tasks, not a general-intelligence ranking. Category scores and confidence intervals do not remove those limitations.

The frozen external answer key stayed outside inference. Offline checks reproduced both new totals from private first attempts and verified coverage, payload hashes, timings, image bindings and serving identity. Public local timing/status evidence contains no model choices, answer labels or per-item correctness. Reproducing accuracy requires the external frozen key and the original saved choices; public aggregates alone cannot independently recreate it. Six chart snapshots remain withheld pending source-terms review. The three older general LLM references remain archived outside the specialized ranking.
'''


def plot(s):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.colors import LinearSegmentedColormap
    import numpy as np
    import textwrap
    from plot_native_images import speed_color, cost_color
    models=[s['models'][mid] for mid in s['rank_order']]
    labels=[m['label'] for m in models]
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'local-images-20261025'}):
        def save(fig,stem):
            for ext in ('png','svg'):
                fig.savefig(DEST/(stem+'.'+ext),dpi=160,facecolor='white',metadata={'Date':None} if ext=='svg' else {})
            plt.close(fig)
        fig,axes=plt.subplots(1,3,figsize=(18,12),sharey=True,gridspec_kw={'width_ratios':[1.2,1.1,1.25]})
        y=np.arange(len(models));colors=[PURPLE if is_local(m) else BLUE for m in models]
        axes[0].barh(y,[m['accuracy']*100 for m in models],color=colors,height=.65)
        axes[0].set_yticks(y,labels);axes[0].invert_yaxis();axes[0].set_xlim(0,111)
        axes[0].axvline(s['random_uniform_baseline']*100,color='#6b7280',linestyle=':',linewidth=1)
        paid=[float(m['core_cost_per_1000_known_usd']) for m in models if not is_local(m) and not m['public_free_access']]
        xmax=max(paid)*1.75
        for i,m in enumerate(models):
            axes[0].text(m['accuracy']*100+1,i,f"{m['correct']}/200 · {m['accuracy']:.1%}",va='center',fontsize=9)
            axes[1].plot([m['median_ms'],m['p95_ms']],[i,i],color='#93a1ad',linewidth=2)
            axes[1].scatter(m['median_ms'],i,c=speed_color(m['median_ms']),s=55,edgecolor='#334155')
            axes[1].scatter(m['p95_ms'],i,c='#334155',marker='d',s=22)
            if is_local(m):
                axes[2].text(.015*xmax,i,'Local compute · unmeasured',color=PURPLE,va='center',fontsize=9)
            elif m['public_free_access']:
                axes[2].text(.015*xmax,i,'Free access · not a production tariff',va='center',fontsize=8.5)
            else:
                cost=float(m['core_cost_per_1000_known_usd']);axes[2].barh(i,cost,color=cost_color(cost),height=.65)
                axes[2].text(cost+.01*xmax,i,amount(m,True),va='center',fontsize=9)
        for tick,m in zip(axes[0].get_yticklabels(),models):
            tick.set_color(PURPLE if is_local(m) else BLUE)
            if is_local(m):tick.set_weight('bold')
        axes[1].set_xscale('log');axes[1].set_xlim(100,3500);axes[2].set_xlim(0,xmax)
        for ax,title in zip(axes,['Accuracy · 200 first attempts','Response time · median and p95','USD / 1,000 questions']):
            ax.set_title(title,fontweight='bold',pad=14);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
            for spine in ax.spines.values():spine.set_visible(False)
            ax.tick_params(axis='y',length=0)
        axes[0].set_xlabel('Accuracy (%) · dotted line: 23.44% guessing')
        axes[1].set_xlabel('Milliseconds, log scale · circle: median · diamond: p95')
        axes[2].set_xlabel('Normalizes actual 200-question costs')
        fig.suptitle('Image decisions · 15 hosted + 2 local routes · 200 questions each',fontsize=19,y=.98)
        fig.legend(handles=[Patch(color=BLUE,label='Hosted decision models'),Patch(color=PURPLE,label='Local · RTX 2060 · 6 GB · PNG')],loc='upper center',bbox_to_anchor=(.5,.955),ncol=2,frameon=False)
        fig.text(.025,.025,'Local runs: October 25, 2026, Ollaya 0.17.0; cold loading/warmups excluded; hardware/electricity unmeasured.\nThe older RTX 2060 6 GB was deliberately chosen as an accessible setup. Hosted measurements retain earlier dates and costs.\nLocal PNGs preserve reviewed decoded RGB pixels; older hosted inputs keep original PNG/JPEG bytes. Route timings are not controlled hardware comparisons.\nSpeed: green ≤500 ms, yellow ≤1 s, orange ≤2 s. Cost/1,000: green ≤$0.05, yellow ≤$0.15, orange ≤$0.50, red above. ~ tariff calculation; * missing charges.',fontsize=9)
        fig.subplots_adjust(left=.20,right=.98,top=.88,bottom=.16,wspace=.33);save(fig,'overview')
        cmap=LinearSegmentedColormap.from_list('accuracy',['#fff4d0','#d5ebce','#77c5c8','#338bac','#183f7a'])
        titles=['Objects, space and routes','Transformations, rules and state','Diagrams and documents','Comparison, perspective and uncertainty']
        for block in range(4):
            fids=list(s['families'])[block*5:block*5+5]
            values=np.array([[m['families'][f]['correct']/10 for f in fids] for m in models])
            fig,ax=plt.subplots(figsize=(13,11));im=ax.imshow(values,vmin=0,vmax=1,cmap=cmap,aspect='auto')
            ax.set_yticks(range(17),labels)
            for tick,m in zip(ax.get_yticklabels(),models):
                tick.set_color(PURPLE if is_local(m) else BLUE)
                if is_local(m):tick.set_weight('bold')
            ax.set_xticks(range(5),['\n'.join(textwrap.wrap(s['families'][f]['name'],21))+f'\n10 questions' for f in fids]);ax.tick_params(length=0,pad=8)
            for i in range(17):
                for j in range(5):ax.text(j,i,f'{round(values[i,j]*10)}/10',ha='center',va='center',color='white' if values[i,j]>=.7 else '#183044')
            for spine in ax.spines.values():spine.set_visible(False)
            fig.colorbar(im,ax=ax,pad=.025,fraction=.025).set_ticks([0,.25,.5,.75,1],labels=['0%','25%','50%','75%','100%'])
            fig.suptitle(titles[block],fontsize=19,y=.975)
            fig.text(.025,.025,'Purple names: local RTX 2060 6 GB with PNG inputs. Cell color always encodes accuracy on a fixed 0–100% scale.\nEvery cell is correct / 10. One answer changes a category by ten percentage points; local/hosted formats, routes and dates differ.',fontsize=10)
            fig.subplots_adjust(left=.25,right=.95,top=.91,bottom=.15);save(fig,'abilities_'+str(block+1))


def badge(m):
    return '<span class="local-badge">Local · RTX 2060 · 6 GB · PNG</span>' if is_local(m) else ''


def summary_html(s):
    result='<div class="table-scroll"><table class="summary"><thead><tr>'+''.join('<th>'+x+'</th>' for x in ['Model / hosting','Correct / 200','Accuracy','Usable','Mean','Median','p95','Actual 200 cost','Cost / 1,000','Test date'])+'</tr></thead><tbody>'
    for mid in s['rank_order']:
        m=s['models'][mid];kind='local-model' if is_local(m) else 'hosted-model'
        result+=f'<tr class="{kind}" data-summary-model="{mid}"><th scope="row">{escape(m["label"])}{badge(m)}</th><td>{m["correct"]}/200</td><td class="accuracy" data-ratio="{m["accuracy"]}">{m["accuracy"]:.1%}</td><td>{m["usable"]}/200</td>'
        for key in ('mean_ms','median_ms','p95_ms'):
            color='#d9eee2' if m[key]<=500 else '#fff1c9' if m[key]<=1000 else '#ffdfc2' if m[key]<=2000 else '#f4ced6'
            result+=f'<td style="background:{color}">{m[key]:.0f} ms</td>'
        for flag in (False,True):
            cost=m['core_cost_per_1000_known_usd']
            color='#edf1f5' if is_local(m) or m['public_free_access'] else '#d9eee2' if float(cost)<=.05 else '#fff1c9' if float(cost)<=.15 else '#ffdfc2' if float(cost)<=.5 else '#f4ced6'
            result+=f'<td style="background:{color}">{escape(amount(m,flag))}</td>'
        result+=f'<td>{m["date"]}{" (reused)" if m["reused"] else ""}</td></tr>'
    return result+'</tbody></table></div>'


def categories_html(s):
    out='<label class="filter">Find a model <input id="model-filter" placeholder="Type a model name…" autocomplete="off"></label>'
    for block in range(4):
        fs=list(s['families'])[block*5:block*5+5]
        out+='<div class="table-scroll"><table class="family-table"><thead><tr><th>Decision model</th>'+''.join('<th>'+escape(s['families'][f]['name'])+'<small>10 questions</small></th>' for f in fs)+'</tr></thead><tbody>'
        for mid in s['rank_order']:
            m=s['models'][mid]
            out+=f'<tr class="{"local-model" if is_local(m) else "hosted-model"}" data-model="{escape(m["label"],quote=True)}"><th scope="row">{escape(m["label"])}{badge(m)}</th>'
            out+=''.join(f'<td class="accuracy" data-model-id="{mid}" data-family="{f}" data-correct="{m["families"][f]["correct"]}" data-ratio="{m["families"][f]["correct"]/10}">{m["families"][f]["correct"]}/10</td>' for f in fs)+'</tr>'
        out+='</tbody></table></div>'
    return out


def bind_layout():
    m=json.loads(MANIFEST.read_text())
    paths=set(m['current_files']) | {p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*.py')} | {'documents/LOCAL_IMAGE_RUNS.md'}
    m['current_files']={name:digest(ROOT/name) for name in sorted(paths)}
    dump(MANIFEST,m)


def mirror():
    shutil.copytree(DEST,ROOT/'docs'/NAME,dirs_exist_ok=True)


def build(key_path):
    assert not (DEST/'manifest.json').exists(), 'Never overwrite a sealed release'
    archive_prior();s,timing,metadata,variant,execution=load(key_path)
    DEST.mkdir(parents=True,exist_ok=True)
    dump(DEST/'summary.json',s);dump(DEST/'local_model_metadata.json',metadata)
    write(DEST/'local_timing_evidence.jsonl','\n'.join(json.dumps(r,allow_nan=False) for r in timing))
    assets={a['asset_id']:a for a in rows(ROOT/'data/assets.jsonl')}
    public_variant={k:deepcopy(v) for k,v in variant.items() if k!='assets'}
    public_variant['assets']={aid:{**{k:v for k,v in a.items() if k!='path'},'original_public_path':('data/'+assets[aid]['path'] if assets[aid]['path'] else None)} for aid,a in variant['assets'].items()}
    dump(DEST/'image_variant_manifest.json',public_variant)
    dump(DEST/'execution_protocol.json',{k:v for k,v in execution.items() if k not in ('source_sha256','created_at')})
    dump(DEST/'execution_source_hashes.json',{Path(k).name:v for k,v in execution['source_sha256'].items()})
    blocked=[dict(model='d1:3b-vision',stage='PNG admission',scored_attempts=0,reason='Three-image PNG returned HTTP 500 / INFERENCE_FAILED; runner response-body decoding error; cause unknown'),
        *[dict(model='d3:'+size+'-gguf-q8_0',stage='small PNG admission',scored_attempts=0,reason='185 input tokens exceeded physical batch size 128') for size in ('mini','nano','lite','edge')],
        dict(model='d1-omni:600m-gguf-q8_0',stage='capability probes',scored_attempts=0,reason='Tiny single PNG accepted; larger/multiple inputs exceeded physical batch size 128'),
        dict(model='decider:2b-vision',stage='capability probes; not selected',scored_attempts=0,reason='Single PNG accepted; multiple images and JPEGs rejected')]
    dump(DEST/'local_admission_findings.json',blocked)
    with io.StringIO() as buf:
        writer=csv.writer(buf,lineterminator='\n');writer.writerow(['model_id','model','hosting','correct','questions','accuracy','usable','mean_ms','median_ms','p95_ms','actual_200_cost','cost_per_1000','input_variant','date'])
        for mid in s['rank_order']:
            m=s['models'][mid];writer.writerow([mid,m['label'],'local' if is_local(m) else 'hosted',m['correct'],200,m['accuracy'],m['usable'],m['mean_ms'],m['median_ms'],m['p95_ms'],amount(m),amount(m,True),VARIANT if is_local(m) else 'original_mixed_png_jpeg',m['date']])
        write(DEST/'leaderboard.csv',buf.getvalue())
    with io.StringIO() as buf:
        writer=csv.writer(buf,lineterminator='\n');writer.writerow(['model_id','model','family_id','family','correct','questions','accuracy'])
        for mid in s['rank_order']:
            for f,v in s['families'].items():
                c=s['models'][mid]['families'][f]['correct'];writer.writerow([mid,s['models'][mid]['label'],f,v['name'],c,10,c/10])
        write(DEST/'family_scores.csv',buf.getvalue())
    notes=narrative(s);write(DEST/'analysis.md',notes);plot(s)
    intro,details=notes.split('## Local hosting:',1)
    legend='**Hosting colours:** purple `#7c3aed` = local RTX 2060 6 GB; blue `#16728c` = hosted decisions. Accuracy cells keep the fixed 0–100% scale. Speed bands: ≤500 ms, ≤1 s, ≤2 s, above. Cost/1,000 bands: ≤$0.05, ≤$0.15, ≤$0.50, above.'
    charts='\n\n'.join(f'![Named category scores, part {i}](results/releases/{NAME}/abilities_{i}.png)' for i in range(1,5))
    definitions='\n'.join(f"- **[{f} {v['name']}](data/questions/{f}.md)**: {v['description']}" for f,v in s['families'].items())
    links=f'[Aggregate results](results/releases/{NAME}/summary.json) · [Category CSV](results/releases/{NAME}/family_scores.csv) · [Local timing evidence](results/releases/{NAME}/local_timing_evidence.jsonl) · [Input hashes](results/releases/{NAME}/image_variant_manifest.json) · [Audit](results/releases/{NAME}/audit_receipt.json) · [Method](documents/LOCAL_IMAGE_RUNS.md)'
    report='# Image-grounded System 1 decision benchmark\n\n'+intro.strip()+f'\n\n[Open the colour-coded report](https://etsabary.github.io/visual-decision-benchmark/report.html)\n\n![Accuracy, speed and cost](results/releases/{NAME}/overview.png)\n\n'+legend+'\n\n## Overall results\n\n'+table(s)+'\n\n## Local hosting:'+details+'\n\n## Results by named category\n\n'+charts+'\n\n## What the categories test\n\n'+definitions+'\n\n'+links+'\n\n[Questions and sources](data/questions/README.md) · [Image gallery](docs/gallery.html) · [Attribution](documents/THIRD_PARTY_NOTICES.md) · [Separate text benchmark](https://etsabary.github.io/system-1-decision-benchmark/report.html)\n'
    write(ROOT/'README.md',report)
    import markdown
    site_md=report.replace(f'results/releases/{NAME}/',NAME+'/').replace('(data/questions/','(questions/').replace('(docs/gallery.html)','(gallery.html)')
    site_md=site_md.replace('(documents/LOCAL_IMAGE_RUNS.md)','(LOCAL_IMAGE_RUNS.md)').replace('(documents/THIRD_PARTY_NOTICES.md)','(THIRD_PARTY_NOTICES.md)')
    content=markdown.markdown(site_md,extensions=['tables','fenced_code','toc'])
    start=content.index('<table>');end=content.index('</table>',start)+len('</table>')
    content=content[:start]+summary_html(s)+content[end:]
    start=content.index('<p><img alt="Named category scores, part 1"');end=content.index('<h2 id="what-the-categories-test"',start)
    content=content[:start]+categories_html(s)+content[end:]
    css='''*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,sans-serif;color:#182f43;background:#f4f7fa}main{max-width:1500px;margin:auto;padding:30px}nav{position:sticky;top:0;background:#fff;border-bottom:1px solid #ccd5de;padding:12px 24px;display:flex;gap:20px;flex-wrap:wrap;z-index:3}a{color:#126482}h1{font-size:34px;line-height:1.2}h2{margin-top:36px;scroll-margin-top:100px}main>p,main>ul{max-width:1100px}img{max-width:100%;height:auto;background:#fff}table{border-collapse:collapse;width:100%;font-size:14px;background:#fff}th,td{padding:10px 12px;border:1px solid #d2dce4;text-align:right;vertical-align:middle}th:first-child{text-align:left}thead{background:#e7eef4}small{display:block;font-weight:400}.table-scroll{overflow:auto;max-width:100%;margin:20px 0 28px}.summary{min-width:1450px}.family-table{min-width:1050px}.family-table th:first-child{min-width:235px}.local-model th:first-child{color:#7c3aed;border-left:5px solid #7c3aed;background:#f5f0ff}.hosted-model th:first-child{color:#16728c;border-left:5px solid #16728c}.local-badge{display:block;font-size:11px;font-weight:500;background:#ede9fe;color:#5b21b6;border:1px solid #c4b5fd;border-radius:4px;padding:3px 5px;margin-top:5px;white-space:normal}.filter{display:block;margin:20px 0}.filter input{font:inherit;padding:8px 12px;max-width:100%;margin-left:10px}footer{padding:30px;color:#516577}.legend{display:flex;flex-wrap:wrap;gap:22px;margin:20px 0}.swatch{display:inline-block;width:14px;height:14px;margin-right:7px}.local-note{border-left:5px solid #7c3aed;background:#f5f0ff;padding:18px;margin:20px 0}@media(max-width:600px){main{padding:16px}h1{font-size:27px}nav{font-size:13px;padding:10px;gap:12px}.filter input{display:block;margin:8px 0;width:100%}}'''
    js='''document.querySelectorAll('.accuracy[data-ratio]').forEach(c=>{const p=Number(c.dataset.ratio);const stops=[[255,244,208],[213,235,206],[119,197,200],[51,139,172],[24,63,122]];const n=Math.min(3,Math.floor(p*4));const t=p*4-n;c.style.background=`rgb(${stops[n].map((x,i)=>Math.round(x+(stops[n+1][i]-x)*t)).join(',')})`;c.style.color=p>=.7?'white':'#183044'});document.getElementById('model-filter').addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('[data-model]').forEach(r=>r.hidden=!r.dataset.model.toLowerCase().includes(q))});'''
    legend_html='<div class="legend"><span><i class="swatch" style="background:#16728c"></i>Hosted decisions</span><span><i class="swatch" style="background:#7c3aed"></i>Local · RTX 2060 · 6 GB · PNG</span></div>'
    content=content.replace('<h2 id="overall-results">',legend_html+'<h2 id="overall-results">')
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Image decisions · 15 hosted + 2 local routes</title><style>'+css+'</style></head><body><nav><a href="#">Overview</a><a href="#overall-results">Scores, speed &amp; cost</a><a href="#local-hosting-useful-speed-lower-accuracy">Local analysis</a><a href="#results-by-named-category">Named categories</a><a href="gallery.html">Questions &amp; images</a><a href="https://github.com/etsabary/visual-decision-benchmark">GitHub evidence</a></nav><main>'+content+'</main><footer>Updated October 25, 2026. Earlier records retain their original measurements. Local input format and hardware are labelled.</footer><script>'+js+'</script></body></html>'
    write(ROOT/'docs/report.html',page);write(DEST/'report.html',page)
    guide='# Local image run protocol\n\n'+notes+'\n\n## Reproduce public PNG inputs\n\nInstall `Pillow==12.3.0`, then run from the repository root:\n\n```sh\npython scripts/local_image_protocol.py --variant-manifest results/releases/'+NAME+'/image_variant_manifest.json --output /tmp/visual-benchmark-png\n```\n\nThis reproduces the public 221 image hashes, including 47 JPEG-to-PNG derivatives; six withheld source images cannot be reconstructed. The gallery continues to show original public source snapshots. No inference occurs.\n'
    write(ROOT/'documents/LOCAL_IMAGE_RUNS.md',guide)
    write(ROOT/'documents/native_image_analysis.md',notes)
    current=(ROOT/'documents/METHODOLOGY.md').read_text()
    if not current.startswith('# Current local-image addition'):
        write(ROOT/'documents/METHODOLOGY.md','# Current local-image addition — October 25, 2026\n\nThe current report adds two local routes using a separately recorded PNG variant. See [local image run protocol](LOCAL_IMAGE_RUNS.md) for conversion, admission, stopping, hardware, timing and privacy rules. The 15 earlier hosted records retain their original mixed-format inputs and measurements. The methodology below describes the original October15 cohort.\n\n'+current)
    release=(ROOT/'documents/RELEASE_NOTES.md').read_text()
    if not release.startswith('# Local image addition'):
        write(ROOT/'documents/RELEASE_NOTES.md','# Local image addition — October 25, 2026\n\n- Added H2O Lightning 4B (117/200, 58.5%) and Fovea 4B (110/200, 55.0%) on a deliberately chosen RTX 2060 6 GB, with mean/median/p95 and unmeasured local operating cost.\n- Local names, accuracy bars and badges use purple #7c3aed; hosted models use blue #16728c. Accuracy/speed/cost scales stay fixed.\n- Recorded the PNG variant with identical decoded RGB pixels; preserved all 15 earlier hosted model records and dated seals. No inference was repeated for publication.\n- Added answer-free local timing, input hashes, metadata, admission findings, 340 named category cells, public PNG reproduction and offline validation. Private model-choice ledgers, keys and LAN addresses remain excluded.\n\n'+release)
    write(ROOT/'results/README.md','# Dated image results\n\n- [Current: 15 hosted + two local routes](releases/'+NAME+'/summary.json), with [analysis](releases/'+NAME+'/analysis.md), [category scores](releases/'+NAME+'/family_scores.csv), [answer-free local timings](releases/'+NAME+'/local_timing_evidence.jsonl) and [audit](releases/'+NAME+'/audit_receipt.json).\n- [Prior 15 hosted models](releases/fastino_2026-10-23/summary.json): unchanged.\n- [Earlier 14-model release](releases/native_images_2026-10-20/summary.json): unchanged.\n- [Original October15 results](original_2026-10-15/summary.json).\n\nHistorical presentation snapshots under archives/ preserve prior seals. Local PNG rows keep their input-variant qualification; admission failures stay outside complete rankings.\n')
    dump(DEST/'audit_receipt.json',dict(status='VERIFIED_LOCAL_IMAGE_400_FIRST_ATTEMPTS',complete_local_models=2,scored_attempts=400,usable=400,
        correct={mid:s['models'][mid]['correct'] for mid in LOCAL},prior_15_records_unchanged=True,private_seal_sha256=digest(CAPTURE/'seal.json'),
        key_sha256=KEY_HASH,question_sha256=digest(ROOT/'data/questions.jsonl'),decoded_rgb_verified_assets=227,jpeg_conversions=47,original_png_bytes_unchanged=180,
        scored_retries=0,unscored_png_admission_warmups=10,initial_capability_probes=34,publication_inference_calls=0,
        original_private_variant_manifest_sha256=digest(CAPTURE/'image_variant_manifest.json'),
        privacy='No local choices, probabilities, answer labels, per-item correctness, credentials, LAN address or private paths exported.',
        correctness_reproducibility='Offline private frozen-key verification; public aggregates do not independently establish correctness.'))
    mirror();bind_layout()
    print('Built unsealed publication: 17 complete routes, 340 category cells, no inference.')


def seal():
    assert not (DEST/'manifest.json').exists(), 'Never overwrite sealed evidence'
    dump(DEST/'manifest.json',dict(version='local-images-20261025-v1',ranked_models=17,hosted_models=15,local_models=2,questions_each=200,
        bank_sha256=digest(ROOT/'data/questions.jsonl'),prior_summary_sha256=digest(OLD/'summary.json'),
        artifacts={p.relative_to(DEST).as_posix():digest(p) for p in sorted(DEST.rglob('*')) if p.is_file()}))
    mirror();bind_layout()
    paths={ROOT/name for name in json.loads(MANIFEST.read_text())['current_files']}
    paths.add(MANIFEST)
    paths.update(p for p in DEST.rglob('*') if p.is_file())
    checks={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)}
    dump(DEST/'release_checksums.json',checks);mirror()
    print('Sealed local image release and exact docs mirror.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--answer-key',type=Path)
    parser.add_argument('--seal',action='store_true')
    args=parser.parse_args()
    if args.seal:seal()
    else:
        assert args.answer_key, 'Explicit external key required for offline scoring'
        build(args.answer_key)
