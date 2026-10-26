"""Offline addition of Sol and three preserved speed stops; no model calls."""
import argparse
from copy import deepcopy
import csv
from decimal import Decimal
from hashlib import sha256
from html import escape
import io
import json
from pathlib import Path
import re
import shutil
import statistics

from benchmark import canonical, rows
from llm_image_protocol import payload
from llm_image_publication_history import local_historical_path
from repo_layout import ROOT, MANIFEST
from score import load_key
import publish_local_images_2026_10_25 as previous

NAME='llm_reference_2026-10-25'
DEST=ROOT/'results/releases'/NAME
OLD=ROOT/'results/releases/local_images_2026-10-25'
CAPTURE=ROOT.parent/'text-decision-hardening/runs/image_llm_references_2026-10-25'
TEXT=ROOT.parent/'jev-1.14-comparison-benchmark/results/releases/local_additions_2026-10-25/statistics.json'
IDS={'sol':'reference_sol','sonnet':'reference_sonnet','opus':'reference_opus5','qwen':'reference_qwen'}
PURPLE,BLUE,YELLOW='#7c3aed','#16728c',(.95,.83,.42,.60)
KEY_HASH='f62348cb73594146497858473fb01c4f78bb06a0649a857329ca47197688fe7c'
FIELDS={'model_id','model_requested','request_index','candidate_id','family_id','attempt','status','latency_ms',
        'request_payload_sha256','request_body_bytes','image_sha256','reported_reasoning_tokens','reasoning_text_present',
        'reasoning_verification','reported_cost_usd','reported_hypercredits','model_returned','provider'}
digest,write,dump=previous.digest,previous.write,previous.dump


def money(m,normalized=False):
    return previous.amount(m,normalized)


def load(key_path):
    assert digest(key_path)==KEY_HASH
    key=load_key(key_path);questions={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')}
    seal=json.loads((CAPTURE/'seal.json').read_text())
    for name,h in seal['files'].items():assert digest(CAPTURE/name)==h,name
    report=json.loads((CAPTURE/'final_report.json').read_text());audit=json.loads((CAPTURE/'audit_receipt.json').read_text())
    assert audit['status']=='PASS' and audit['scored_first_attempts']==260 and audit['all_dispatches_resolved']
    manifest=json.loads((CAPTURE/'manifest.json').read_text())
    assert report['question_sha256']==digest(ROOT/'data/questions.jsonl')==manifest['question_sha256']
    assert set(key)==set(questions) and len(key)==200
    png=CAPTURE.parent/'local_image_png_2026-10-25/image_variant_manifest.json'
    assert digest(png)==manifest['image_variant_manifest_sha256']
    assets=json.loads(png.read_text())['assets']
    old=json.loads((OLD/'summary.json').read_text());combined=deepcopy(old)
    timing=[];stops=[];metadata={}
    for mid,cfg in manifest['models'].items():
        folder=CAPTURE/mid;rr=rows(folder/'attempts.jsonl');dd=rows(folder/'dispatches.jsonl');v=report['models'][mid]
        assert len(rr)==len(dd)==(200 if mid=='sol' else 20)
        assert [r['candidate_id'] for r in rr]==manifest['question_order'][:len(rr)]
        assert all(r['attempt']==1 and r['status']=='ok' for r in rr)
        assert sum(r['choice']==key[r['candidate_id']] for r in rr)==v['correct']
        for r,d in zip(rr,dd):
            q=questions[r['candidate_id']];images=[Path(assets[a]['path']).read_bytes() for a in q['asset_ids']]
            assert sha256(canonical(payload(mid,q,images))).hexdigest()==r['request_payload_sha256']==d['request_payload_sha256']
            timing.append({k:r[k] for k in FIELDS if k in r}|{'model_id':IDS[mid],'model_requested':cfg['model'],'image_variant':manifest['input_variant']})
        sample=deepcopy(v);sample.update(model_id=IDS[mid],model_requested=cfg['model'],date='2026-10-25')
        if mid=='sol':
            assert v['state']=='complete' and v['correct']==147 and v['usable']==200
            model=dict(model_id=IDS[mid],label=cfg['label'],model_requested=cfg['model'],model_kind='llm_reference',
                execution_location='hosted_llm',route='OpenRouter → OpenAI, standard service tier',date='2026-10-25',
                complete=True,reused=False,n=200,correct=147,accuracy=.735,usable=200,accuracy_usable=.735,
                mean_ms=v['mean_ms'],median_ms=v['median_ms'],p95_ms=v['p95_ms'],status_counts=v['statuses'],retries=0,
                families={f:dict(n=c['n'],correct=c['correct'],usable=c['n']) for f,c in v['families'].items()},
                cost_source='api_reported',core_cost=dict(known_api_usd=v['cost']['known_usd'],reported_records=200,missing_api_records=0),
                core_cost_per_1000_known_usd=str(Decimal(v['cost']['known_usd'])*5),public_free_access=False,
                reasoning_setting='reasoning.enabled=false; reasoning.effort=none; no tools',
                reasoning_verification='200 successful first attempts explicitly report zero reasoning tokens and no reasoning content',
                reported_output_tokens=sum(r['usage'].get('completion_tokens',0) for r in rr),reported_reasoning_text=0,
                image_variant=manifest['input_variant'],probe_cost_usd=v['probe_cost']['known_usd'],output_contract='Bare numeric option ID; max_tokens=16')
            combined['models'][IDS[mid]]=model
        else:
            assert v['state']=='stopped_slow' and v['median_ms']>2000
            sample.update(complete=False,included_in_full_ranking=False,stop_reason='Cumulative median above 2000 ms after 20 first attempts',
                sample_warning='Partial 20-question sample; no full 200-question score or normalized full-run cost',
                reasoning_setting='between_tools/high; no tools; JSON choice' if mid=='sonnet' else 'disabled/high; JSON choice' if mid=='opus' else 'requested reasoning_effort=none; omitted token telemetry remains unknown')
            stops.append(sample)
        meta=json.loads((CAPTURE/(mid+'_metadata.json')).read_text())
        if mid=='qwen':selected=meta['data'][0]
        else:
            tag='openai' if mid=='sol' else 'anthropic'
            endpoints=[e for e in meta['data']['endpoints'] if e['tag']==tag and e['status']==0 and not e.get('service_tier')]
            assert len(endpoints)==1;selected={k:endpoints[0].get(k) for k in ('name','tag','pricing','context_length','supported_parameters')}
        metadata[IDS[mid]]=dict(model_requested=cfg['model'],catalog_snapshot=cfg['snapshot'],host=cfg['host'],path=cfg['path'],
            provider=cfg['provider'],selected_catalog=selected,image_input=True,endpoint_identity_and_tariff_unchanged_at_end=True,
            settings={k:v for k,v in payload(mid,questions[manifest['question_order'][0]],[b'']).items() if k!='messages'})
    text=json.loads(TEXT.read_text());selection={mid:{k:text['models'][mid][k] for k in ('label','n','correct','accuracy','reasoning_setting')} for mid in text['reference_model_ids']}
    assert max(selection,key=lambda x:selection[x]['correct'])=='reference_sol'
    assert selection['reference_sol']['correct']==1143 and selection['reference_sol']['n']==1342
    basis=dict(claim='Highest-scoring non-reasoning-capable general-LLM reference in our completed text comparison',
        scope='Four selected completed LLM configurations on the frozen 1342-question text bank',models=selection,
        statistics_sha256=digest(TEXT),source='https://etsabary.github.io/system-1-decision-benchmark/local_additions_2026-10-25/statistics.json',
        model_capability_source='https://developers.openai.com/api/docs/models/gpt-6-sol',
        limit='Selection claim is bounded to this tested reference set; image performance is measured separately.')
    combined.update(version='image-llm-reference-20261025-v1',updated_date_toronto='2026-10-25',complete_routes=18,
        decision_models_ranked=17,complete_llm_reference_count=1,llm_references_tested=4,reference_model_ids=['reference_sol'],
        decision_model_ids=old['rank_order'],llm_speed_stops=stops,prior_summary_sha256=digest(OLD/'summary.json'),
        complete_first_attempt_cases=3600,partial_llm_first_attempt_cases=60,llm_reference_first_attempt_cases=260,
        selection_basis=basis,location_colors={'local':PURPLE,'hosted':BLUE,'llm_reference':'rgba(242,212,107,0.6)'},
        input_variant_note='New Sol and speed-stopped LLM references use the recorded PNG variant shared with local runs. Earlier 15 hosted decision records retain original mixed PNG/JPEG bytes.')
    combined['rank_order']=sorted(combined['models'],key=lambda mid:(-combined['models'][mid]['correct'],combined['models'][mid]['median_ms']))
    assert all(combined['models'][mid]==m for mid,m in old['models'].items()) and combined['exclusions']==old['exclusions']
    return combined,timing,stops,metadata,manifest,audit


def speed_table(stops):
    text=['| LLM reference | Outcome | Correct / attempted | Sample accuracy | Mean | Median | p95 | Actual sample cost |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |']
    for m in stops:
        cost='$'+f"{Decimal(m['cost']['known_usd']):.6f}"+(' quota-equivalent' if m['model_id']=='reference_qwen' else '')
        text.append('| '+' | '.join([m['label'],'**SPEED STOP · partial**',f"{m['correct']}/20",f"{m['accuracy']:.1%}"]+[f"{m[k]:.0f} ms" for k in ('mean_ms','median_ms','p95_ms')]+[cost])+' |')
    return '\n'.join(text)


def table(s):
    text=['| Model | Type / inputs | Correct / 200 | Accuracy | Usable | Mean | Median | p95 | Actual 200 cost | Cost / 1,000 | Date |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |']
    for mid in s['rank_order']:
        m=s['models'][mid];kind='LLM reference · reasoning off · PNG' if mid=='reference_sol' else 'Local RTX 2060 6 GB · PNG' if previous.is_local(m) else 'Hosted decision · original PNG/JPEG'
        text.append('| '+' | '.join([m['label'],kind,f"{m['correct']}/200",f"{m['accuracy']:.1%}",f"{m['usable']}/200"]+[f"{m[k]:.0f} ms" for k in ('mean_ms','median_ms','p95_ms')]+[money(m),money(m,True),m['date']+(' (reused)' if m['reused'] else '')])+' |')
    return '\n'.join(text)


def narrative(s):
    old_notes=(OLD/'analysis.md').read_text().split('## Local hosting:',1)[1]
    intro='''The comparison now contains **18 complete routes: 15 hosted decision models, two local models and GPT-6 Sol as a non-reasoning LLM reference**. Every complete row has200 first attempts. Sonnet5.5, Opus5 and Qwen3.8-Max are separately marked **speed stops after20 questions**, outside the complete ranking. All17 previous records retain their exact scores, timings, costs and dates.

**GPT-6 Sol scored147/200 (73.5%), with1787/1637/3028ms mean/median/p95 and200 usable decisions.** It passed the retained two-second median rule. Its reported200-question cost was **$0.591634**, or **$2.958170 per1,000**, with another **$0.007185** for two admission probes. Pale yellow with transparency identifies this LLM reference; purple continues to identify local hosting.

Amos1 Large remains the highest-scoring complete route at159/200 (79.5%), followed by Fastino GLiDE at158/200 (79.0%) and hosted d3-turbo at155/200 (77.5%). Sol matched kettei-fat's147 correct answers. The one-answer Amos/Fastino gap remains statistically unresolved.

## Why Sol is the strongest non-reasoning-capable LLM reference

**Sol was the highest-scoring non-reasoning-capable general LLM in our completed text comparison:1,143/1,342 (85.2%).** The other selected text references scored1,109 for Opus5,1,070 for Sonnet5.5 and967 for Qwen3.8-Max. That is the measured basis for selecting Sol as the strongest—or “smartest”—non-reasoning-capable LLM reference here. The selection claim is bounded to those four tested configurations on the text bank; its image score is measured separately.

Sol supports image input and a reasoning effort of `none`, as documented in the [official model documentation](https://developers.openai.com/api/docs/models/gpt-6-sol). This image run used the same OpenRouter → OpenAI standard route, `reasoning.enabled=false`, `reasoning.effort=none`, no tools and a16-token output cap. All200 scored responses explicitly reported **zero reasoning tokens and no reasoning content**. These are observed API facts; the model's weights are not independently attested.

The [text comparison](https://etsabary.github.io/system-1-decision-benchmark/report.html) and [captured text statistics](https://etsabary.github.io/system-1-decision-benchmark/local_additions_2026-10-25/statistics.json) establish the selection population and scores. This is an immediate fixed-choice comparison without tools, crop/zoom operations or iterative reasoning.

## Sol on the image bank

Sol finished12 answers behind Amos and11 behind GLiDE. Its1,637ms median was longer than Amos's340ms, GLiDE's359ms and kettei-fat's410ms. Their weights, preprocessing, serving hardware, input file formats and dates differ; these are route-specific measurements.

Sol scored **10/10 on sequential state tracking, charts, interface-state decisions and inspection against a reference**. Attribute/set filtering, spatial relationships, perspective/knowledge tracking and recognizing insufficient evidence were9/10. Geometry/folding/fit and constraint satisfaction were each3/10; connectivity4/10, navigation/planning and document reconciliation5/10. Each category contains ten questions, so one answer changes its score by ten percentage points.

With exactly the same PNG inputs as the local runs, Sol answered30 more questions correctly than H2O Lightning and37 more than Fovea. Both local routes had shorter mean and median response times. This comparison does not isolate hosting location, because the model weights, hardware and serving routes also differ.

## LLM speed stops

The two-second **cumulative median** cutoff was retained explicitly for all four LLM references. Sonnet5.5 stopped at20 with a3,150ms median; Opus5 stopped at20 with2,628ms; Qwen3.8-Max stopped at20 with2,837ms. All60 partial first attempts returned usable outputs. These rows describe partial samples, with no full-bank score, full-run cost or entry in the360-cell category ranking.

<!-- SPEED_STOPS -->

Sonnet's18/20 (90.0%) is a promising partial result; it does not establish90% accuracy on the200-question bank. Its mode was `thinking.type=between_tools`, high effort, no tools and constrained JSON choice. Opus used disabled thinking at high effort with the same JSON-choice contract. All40 scored Claude responses reported zero thinking tokens and no thinking blocks. Qwen requested catalog-supported `reasoning_effort=none`; its20 responses omitted reasoning-token telemetry, which remains **unknown**, with no reasoning text. Hyper Charm cost values are reported USD-equivalent prepaid quota debits, not cash invoices.

Sol passed20 at a1,746ms median, then the separate offline100-case accuracy gate at73/100 before continuation. The cumulative median stayed at or below2,000ms throughout200. All four retained their text-reference routes and output contracts; JSON enums followed each image question's3/4/5 choices. No failed-format, wrong-answer or scored transport retries were made in this cohort.

## LLM timing, input and cost qualifications

New LLM calls used **PNG-lossless-from-reviewed-decoded-RGB-v1**, the exact PNG bytes used by the two local runs. Earlier15 hosted decision models retain their original mixed PNG/JPEG bytes. The original questions, rules, option IDs, option order and image order remain frozen. No model was rerun to change a presentation or produce this publication.

At most two distinct hosted model streams overlapped, with one request per model. Sol continuation ran alone. Timings include fresh HTTPS connection, PNG upload and the complete response; local encoding and between-phase waits are excluded. Two image admission probes per route have separate timings and costs.

The complete Sol cost is its actual200-question reported charge; cost/1,000 is a normalization, not another1,000 calls. The three speed-stopped rows show only their actual20-question sample costs. Probe charges remain separate in the exports. In this new cohort there were260 first attempts and8 admission probes, with zero retries. No inference was performed for publication.

Public LLM timing/status evidence is answer-free: it contains request/image hashes, measured durations, returned identity, reported costs and reasoning telemetry. Private model choices, answer labels, per-item correctness, credentials, LAN addresses and account state are excluded. Accuracy was verified offline against the unchanged external key, and cannot be independently recreated from aggregates alone.
'''
    text=intro+'\n## Local hosting:'+old_notes
    replacements={'has200':'has 200','after20':'after 20','All17':'All 17','scored147':'scored 147','with1787':'with 1787','3028ms':'3028 ms','and200':'and 200','reported200':'reported 200','per1,000':'per 1,000','Amos1':'Amos 1','at159':'at 159','at158':'at 158','at155':'at 155',"fat's147":"fat's 147",'comparison:1,143':'comparison: 1,143','scored1,109':'scored 1,109',',1,070':', 1,070','and967':'and 967','Opus5':'Opus 5','Sonnet5.5':'Sonnet 5.5','a16':'a 16','All200':'All 200','finished12':'finished 12','and11':'and 11','Its1,637ms':'Its 1,637 ms',"Amos's340ms":"Amos's 340 ms", "GLiDE's359ms":"GLiDE's 359 ms","fat's410ms":"fat's 410 ms",'were9/10':'were 9/10','each3/10':'each 3/10','connectivity4/10':'connectivity 4/10','reconciliation5/10':'reconciliation 5/10','answered30':'answered 30','and37':'and 37','at20':'at 20','a3,150ms':'a 3,150 ms','with2,628ms':'with 2,628 ms','with2,837ms':'with 2,837 ms','All60':'All 60','the360':'the 360',"Sonnet's18/20":"Sonnet's 18/20",'establish90%':'establish 90%','the200':'the 200','All40':'All 40','its20':'its 20','passed20':'passed 20','a1,746ms':'a 1,746 ms','offline100':'offline 100','at73/100':'at 73/100','below2,000ms':'below 2,000 ms','throughout200':'throughout 200',"question's3/4/5":"question's 3/4/5",'Earlier15':'Earlier 15','actual200':'actual 200','another1,000':'another 1,000','actual20':'actual 20','were260':'were 260','and8':'and 8'}
    for a,b in replacements.items():text=text.replace(a,b)
    return text.replace('<!-- SPEED_STOPS -->',speed_table(s['llm_speed_stops']))


def reference_names(html,s):
    label=escape(s['models']['reference_sol']['label'])
    html=html.replace('<tr class="hosted-model" data-summary-model="reference_sol">','<tr class="llm-reference" data-summary-model="reference_sol">')
    html=html.replace('<tr class="hosted-model" data-model="'+label+'">','<tr class="llm-reference" data-model="'+label+'">')
    return html.replace('<th scope="row">'+label+'</th>','<th scope="row">'+label+'<span class="reference-badge">LLM · reasoning off · PNG</span></th>')


def bind_layout():
    m=json.loads(MANIFEST.read_text());paths=set(m['current_files'])|{p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*.py')}|{'documents/LLM_IMAGE_REFERENCES.md'}
    m['current_files']={name:digest(ROOT/name) for name in sorted(paths)};dump(MANIFEST,m)


def mirror():shutil.copytree(DEST,ROOT/'docs'/NAME,dirs_exist_ok=True)


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
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'sol-image-reference-20261025'}):
        def save(fig,stem):
            for ext in ('png','svg'):fig.savefig(DEST/(stem+'.'+ext),dpi=160,facecolor='white',metadata={'Date':None} if ext=='svg' else {})
            svg=DEST/(stem+'.svg');write(svg,'\n'.join(line.rstrip() for line in svg.read_text().splitlines()));plt.close(fig)
        fig,axes=plt.subplots(1,3,figsize=(18,12.5),sharey=True,gridspec_kw={'width_ratios':[1.2,1.1,1.25]})
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
        fig.suptitle('18 complete routes · 15 hosted decisions + 2 local + Sol reasoning-off reference',fontsize=18,y=.98)
        handles=[Patch(color=BLUE,label='Hosted decisions'),Patch(color=PURPLE,label='Local RTX 2060 6 GB'),Patch(color=YELLOW,label='LLM reference, reasoning off')]
        fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.955),ncol=3,frameon=False)
        fig.text(.025,.025,'Sol: 147/200, 1787/1637/3028 ms mean/median/p95; strongest completed non-reasoning LLM reference on our text bank (1143/1342).\nSonnet 5.5, Opus 5 and Qwen3.8-Max stopped after 20 above the two-second median cutoff; partial results are outside this figure.\nNew LLM/local inputs share the PNG variant; earlier hosted rows keep original PNG/JPEG bytes. Dates, routes and hardware differ.\nPurple locals use the deliberately chosen older RTX 2060 6 GB; hardware/electricity unmeasured. † Free access is not a production tariff; ~ tariff calculation; * missing charges.',fontsize=9)
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


def build(key_path):
    assert not (DEST/'manifest.json').exists(),'Never overwrite sealed dated evidence'
    s,timing,stops,metadata,protocol,private_audit=load(key_path);DEST.mkdir(parents=True,exist_ok=True)
    dump(DEST/'summary.json',s);dump(DEST/'llm_speed_stops.json',stops);dump(DEST/'llm_model_metadata.json',metadata);dump(DEST/'selection_basis.json',s['selection_basis'])
    write(DEST/'llm_timing_evidence.jsonl','\n'.join(json.dumps(r,ensure_ascii=False,allow_nan=False) for r in timing))
    for filename in ('image_variant_manifest.json','local_model_metadata.json','local_timing_evidence.jsonl','local_admission_findings.json'):
        shutil.copyfile(OLD/filename,DEST/filename)
    clean={k:v for k,v in protocol.items() if k not in ('source_sha256','created_at')};clean['models']={mid:{k:v for k,v in cfg.items() if k!='guard'} for mid,cfg in clean['models'].items()}
    dump(DEST/'llm_execution_protocol.json',clean);dump(DEST/'execution_source_hashes.json',{'image_llm_runner.py':protocol['source_sha256']})
    with io.StringIO() as b:
        w=csv.writer(b,lineterminator='\n');w.writerow(['model_id','model','kind','correct','questions','accuracy','usable','mean_ms','median_ms','p95_ms','actual_200_cost','cost_per_1000','date'])
        for mid in s['rank_order']:
            m=s['models'][mid];w.writerow([mid,m['label'],'llm_reference' if mid=='reference_sol' else 'local' if previous.is_local(m) else 'hosted_decision',m['correct'],200,m['accuracy'],m['usable'],m['mean_ms'],m['median_ms'],m['p95_ms'],money(m),money(m,True),m['date']])
        write(DEST/'leaderboard.csv',b.getvalue())
    with io.StringIO() as b:
        w=csv.writer(b,lineterminator='\n');w.writerow(['model_id','model','family_id','family','correct','questions','accuracy'])
        for mid in s['rank_order']:
            for f,definition in s['families'].items():
                c=s['models'][mid]['families'][f]['correct'];w.writerow([mid,s['models'][mid]['label'],f,definition['name'],c,10,c/10])
        write(DEST/'family_scores.csv',b.getvalue())
    with io.StringIO() as b:
        w=csv.writer(b,lineterminator='\n');w.writerow(['model_id','model','status','correct','attempted','sample_accuracy','usable','mean_ms','median_ms','p95_ms','actual_sample_cost','cost_scope','included_in_full_ranking'])
        for m in stops:w.writerow([m['model_id'],m['label'],'SPEED_STOP',m['correct'],20,m['accuracy'],20,m['mean_ms'],m['median_ms'],m['p95_ms'],m['cost']['known_usd'],m['cost_scope'],False])
        write(DEST/'speed_stops.csv',b.getvalue())
    notes=narrative(s);write(DEST/'analysis.md',notes);plot(s)
    intro,detail=notes.split('## Why Sol',1)
    legend='**Colour key:** blue `#16728c` = hosted decisions; purple `#7c3aed` = local RTX 2060 6 GB; pale yellow with transparency = general LLM reference with reasoning off. Accuracy cells retain the fixed 0–100% scale; speed/cost bands are unchanged.'
    charts='\n\n'.join(f'![Named category scores, part {i}](results/releases/{NAME}/abilities_{i}.png)' for i in range(1,5))
    defs='\n'.join(f"- **[{f} {v['name']}](data/questions/{f}.md)**: {v['description']}" for f,v in s['families'].items())
    links=f'[Aggregate results](results/releases/{NAME}/summary.json) · [Category CSV](results/releases/{NAME}/family_scores.csv) · [LLM speed stops](results/releases/{NAME}/speed_stops.csv) · [Answer-free LLM timing](results/releases/{NAME}/llm_timing_evidence.jsonl) · [Selection evidence](results/releases/{NAME}/selection_basis.json) · [Audit](results/releases/{NAME}/audit_receipt.json) · [LLM method](documents/LLM_IMAGE_REFERENCES.md)'
    report='# Image-grounded System 1 decision benchmark\n\n'+intro.strip()+'\n\n[Open the colour-coded report](https://etsabary.github.io/visual-decision-benchmark/report.html)'+f'\n\n![Accuracy, speed and cost](results/releases/{NAME}/overview.png)\n\n'+legend+'\n\n## Overall results\n\n'+table(s)+'\n\n## Why Sol'+detail+'\n\n## Results by named category\n\n'+charts+'\n\n## What the categories test\n\n'+defs+'\n\n'+links+'\n\n[Questions and sources](data/questions/README.md) · [Gallery](docs/gallery.html) · [Attribution](documents/THIRD_PARTY_NOTICES.md) · [Local method](documents/LOCAL_IMAGE_RUNS.md)\n'
    write(ROOT/'README.md',report)
    import markdown
    md=report.replace(f'results/releases/{NAME}/',NAME+'/').replace('(data/questions/','(questions/').replace('(docs/gallery.html)','(gallery.html)')
    for filename in ('LLM_IMAGE_REFERENCES.md','LOCAL_IMAGE_RUNS.md','THIRD_PARTY_NOTICES.md'):md=md.replace('(documents/'+filename+')','('+filename+')')
    content=markdown.markdown(md,extensions=['tables','fenced_code','toc'])
    first=content.index('<table>');end=content.index('</table>',first)+len('</table>');content=content[:first]+reference_names(previous.summary_html(s),s)+content[end:]
    first=content.index('<p><img alt="Named category scores, part 1"');end=content.index('<h2 id="what-the-categories-test"',first);content=content[:first]+reference_names(previous.categories_html(s),s)+content[end:]
    # The partial-result table is kept separate from the 18 complete summary rows.
    heading=content.index('<h2 id="llm-speed-stops"');first=content.index('<table>',heading);end=content.index('</table>',first)+len('</table>')
    partial=content[first:end]
    for m in stops:partial=partial.replace('<tr>\n<td>'+escape(m['label'])+'</td>','<tr data-speed-stop="'+m['model_id']+'">\n<td>'+escape(m['label'])+'</td>')
    content=content[:first]+'<div class="table-scroll speed-stops">'+partial+'</div>'+content[end:]
    old_html=local_historical_path('docs/report.html').read_text();css=re.search(r'<style>(.*?)</style>',old_html,re.S).group(1);js=re.search(r'<script>(.*?)</script>',old_html,re.S).group(1)
    css+='\n.llm-reference th:first-child{color:#795b00;border-left:5px solid #e7bc39;background:rgba(242,212,107,.24)}.reference-badge{display:block;font-size:11px;font-weight:500;color:#795b00;background:rgba(242,212,107,.6);padding:3px 5px;margin-top:5px;border:1px solid #e7c568;border-radius:4px}.speed-stops table{min-width:1200px}.speed-stops strong{color:#99400d}.summary th:first-child{min-width:235px}'
    legend_html='<div class="legend"><span><i class="swatch" style="background:#16728c"></i>Hosted decisions</span><span><i class="swatch" style="background:#7c3aed"></i>Local RTX 2060 6 GB</span><span><i class="swatch" style="background:rgba(242,212,107,.6)"></i>LLM reference, reasoning off</span></div>'
    content=content.replace('<h2 id="overall-results">',legend_html+'<h2 id="overall-results">')
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Image decisions · 18 complete routes · Sol reasoning-off reference</title><style>'+css+'</style></head><body><nav><a href="#">Overview</a><a href="#overall-results">Scores, speed &amp; cost</a><a href="#why-sol-is-the-strongest-non-reasoning-capable-llm-reference">Why Sol</a><a href="#llm-speed-stops">Speed stops</a><a href="#results-by-named-category">Categories</a><a href="gallery.html">Questions &amp; images</a><a href="https://github.com/etsabary/visual-decision-benchmark">GitHub evidence</a></nav><main>'+content+'</main><footer>Updated October 25, 2026. 17 prior route records preserved; stopped LLM samples remain outside the complete ranking.</footer><script>'+js+'</script></body></html>'
    write(ROOT/'docs/report.html',page)
    dated=page.replace(NAME+'/','')
    for href in ('gallery.html','LLM_IMAGE_REFERENCES.md','LOCAL_IMAGE_RUNS.md','THIRD_PARTY_NOTICES.md'):dated=dated.replace('href="'+href+'"','href="../'+href+'"')
    dated=dated.replace('href="questions/','href="../questions/');write(DEST/'report.html',dated)
    guide='# Matched non-reasoning image LLM references\n\n'+notes+'\n\n[Full image report](https://etsabary.github.io/visual-decision-benchmark/report.html) · [Input-format method](LOCAL_IMAGE_RUNS.md)\n'
    write(ROOT/'documents/LLM_IMAGE_REFERENCES.md',guide);write(ROOT/'documents/native_image_analysis.md',notes)
    method=(ROOT/'documents/METHODOLOGY.md').read_text()
    if not method.startswith('# Current LLM reference addition'):write(ROOT/'documents/METHODOLOGY.md','# Current LLM reference addition — October 25, 2026\n\nThe current comparison adds Sol as one complete non-reasoning LLM reference and separately records three 20-question speed stops. See [LLM reference method](LLM_IMAGE_REFERENCES.md). Existing 17 complete records remain unchanged; the new LLMs use the existing PNG variant.\n\n'+method)
    releases=(ROOT/'documents/RELEASE_NOTES.md').read_text()
    if not releases.startswith('# Matched image LLM reference'):write(ROOT/'documents/RELEASE_NOTES.md','# Matched image LLM reference — October 25, 2026\n\n- Added Sol 147/200 (73.5%), 1787/1637/3028 ms mean/median/p95, 200 usable, zero reported reasoning tokens and $0.591634 primary cost.\n- Explained selection as the highest-scoring of four completed non-reasoning LLM text-reference configurations (1143/1342).\n- Marked Sonnet 5.5, Opus 5 and Qwen3.8-Max as speed stops after 20; their samples remain outside complete rankings.\n- Preserved all 17 prior records and seals. Added pale-yellow LLM styling, 360 category cells, answer-free timing, selection evidence and public offline validation; no inference during publication.\n\n'+releases)
    write(ROOT/'results/README.md','# Dated image results\n\n- [Current: 18 complete routes](releases/'+NAME+'/summary.json): 15 hosted decisions, two local and Sol reasoning-off LLM reference. [Speed stops](releases/'+NAME+'/speed_stops.csv) are partial samples.\n- [Prior 17-route release](releases/local_images_2026-10-25/summary.json): unchanged.\n- [Earlier 15 hosted release](releases/fastino_2026-10-23/summary.json): unchanged.\n- [Earlier 14 models](releases/native_images_2026-10-20/summary.json) and [original October 15 results](original_2026-10-15/summary.json).\n\nPresentation snapshots under archives/ preserve historical seals. New LLMs share local PNG inputs; earlier hosted rows retain original mixed-format bytes.\n')
    dump(DEST/'audit_receipt.json',dict(status='VERIFIED_SOL_200_WITH_THREE_SPEED_STOPS',prior_17_records_unchanged=True,
        question_sha256=digest(ROOT/'data/questions.jsonl'),key_sha256=KEY_HASH,private_seal_sha256=digest(CAPTURE/'seal.json'),
        scored_attempts=260,complete_sol_attempts=200,correct_sol=147,usable_sol=200,partial_attempts=60,admission_probes=8,retries=0,
        cutoff_ms=2000,publication_inference_calls=0,explicit_zero_reasoning_scored_responses=240,qwen_unknown_reasoning_scored_responses=20,
        text_selection_statistics_sha256=digest(TEXT),selection_scope='Four completed non-reasoning text-reference configurations',
        privacy='Answer-free new timing exports; no choices, answer labels, per-item correctness, raw account data, credentials or private paths.',
        accuracy_reproducibility='Verified offline against external frozen key; public aggregates alone do not independently recreate private-key correctness.'))
    mirror();bind_layout();print('Built unsealed 18-route publication, 360 category cells and three separately marked speed stops; no inference.')


def seal():
    assert not (DEST/'manifest.json').exists(),'Never overwrite sealed evidence'
    dump(DEST/'manifest.json',dict(version='image-llm-reference-20261025-v1',complete_routes=18,questions_each=200,
        complete_llm_references=1,speed_stopped_llm_references=3,question_sha256=digest(ROOT/'data/questions.jsonl'),
        prior_summary_sha256=digest(OLD/'summary.json'),artifacts={p.relative_to(DEST).as_posix():digest(p) for p in sorted(DEST.rglob('*')) if p.is_file()}))
    mirror();bind_layout();paths={ROOT/name for name in json.loads(MANIFEST.read_text())['current_files']};paths.add(MANIFEST);paths.update(p for p in DEST.rglob('*') if p.is_file())
    dump(DEST/'release_checksums.json',{p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)});mirror();print('Sealed Sol reference publication and exact dated docs mirror')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--answer-key',type=Path);p.add_argument('--seal',action='store_true');a=p.parse_args()
    if a.seal:seal()
    else:
        assert a.answer_key,'Explicit frozen external key required for offline verification';build(a.answer_key)
