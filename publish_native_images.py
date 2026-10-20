"""Build the expanded image benchmark presentation from sealed offline aggregates."""
import csv
from decimal import Decimal
import html
import io
import json
from pathlib import Path
import shutil

import markdown

from image_publication_history import preserve
from plot_native_images import plot,speed_color,cost_color

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'native_images_2026-10-20'
REPO='https://github.com/etsabary/visual-decision-benchmark'
ORIGINAL=REPO+'/blob/433f9368c7e3f594febf7f42c6cefaae75cafca7/README.md'
TEXT='https://github.com/etsabary/system-1-decision-benchmark'

def amount(s,per1000=False):
    if s['public_free_access']:return 'Free access†'
    value=Decimal(s['core_cost_per_1000_known_usd'] if per1000 else s['core_cost']['known_api_usd'])
    return f'${value:.6f}'+('*' if s['core_cost']['missing_api_records'] else '')

def table(d):
    lines=['| Decision model | Correct / 200 | Accuracy | Usable | Mean | Median | p95 | Actual 200 cost | Cost / 1,000 | Test date |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for mid in d['rank_order']:
        s=d['models'][mid]
        lines.append(f"| {s['label']} | {s['correct']}/200 | {s['accuracy']:.1%} | {s['usable']}/200 | {s['mean_ms']/1000:.3f} s | {s['median_ms']/1000:.3f} s | {s['p95_ms']/1000:.3f} s | {amount(s)} | {amount(s,True)} | {s['date']}{' (reused)' if s['reused'] else ''} |")
    return '\n'.join(lines)

def build():
    preserve(ROOT);d=json.loads((DATA/'summary.json').read_text());plot()
    analysis=(ROOT/'native_image_analysis.md').read_text();intro,body=analysis.split('<!-- DETAILS -->',1)
    intro=intro.strip();body=body.strip()
    exclusions=['| Model | Status | First attempts | Observed median |','|---|---|---:|---:|']
    for e in d['exclusions']:
        med=f"{e['partial']['median_ms']/1000:.3f} s" if e.get('partial') else 'Not scored'
        reason='Stopped: median above 2 seconds' if e['reason']=='MEDIAN_ABOVE_2000_MS' else e['reason']
        exclusions.append(f"| {e['label']} | {reason} | {e['n']} | {med} |")
    cap=ROOT.parent/'jev-1.14-comparison-benchmark/direct_additions_2026-10-20/image_capabilities.json'
    shutil.copy2(cap,DATA/'image_capabilities.json')
    excluded='\n'.join(exclusions)
    charts='\n\n'.join(f'![Named category scores, part {i}](native_images_2026-10-20/abilities_{i}.png)' for i in range(1,5))
    definitions='\n'.join(f"- **[{f} {v['name']}](questions/{f}.md)**: {v['description']}" for f,v in d['families'].items())
    methods="""Every ranked model has the same **200 questions**, original options, original order and exact reviewed image bytes. Accuracy uses all 200 first attempts; HTTP errors and unusable choices are unsuccessful. Wrong choices and invalid formatting are not retried. One recovery is allowed only for transport failures or HTTP 408/429/5xx, with recovery charges included in core cost. All reported accuracy here is first-attempt accuracy.

The speed rule was set before these runs: after the first 20 questions, and after every subsequent question, stop a route if its cumulative **median exceeds 2 seconds**. This is a median cutoff, not a mean or p95 cutoff. Partial runs do not enter the full-bank ranking. No accuracy cutoff was applied to the eligible native decision models.

Timing includes a fresh HTTPS connection, image upload and the complete response body; it excludes local image encoding, request construction and deliberate rate/retry waits. At most four model streams ran together, with one request at a time per model. Different labs, endpoints, dates and image preprocessors remain part of the observed route comparison. This is not an isolated comparison of weights or architecture.

**Cost / 1,000 is a normalization of each actual 200-question run**, not an additional 1,000 questions per model. * Asterisked prices are known sums with missing error charges, so they are lower bounds. † d3 and Amos currently offer free public access; that is **not an API-reported metered price of $0**, and it is not a promise of future free service. Admission probes and stopped runs are accounted separately from ranked-model core totals.

Speed colours: green ≤0.5 s, yellow ≤1 s, orange ≤2 s, red >2 s. Cost colours per 1,000: green ≤$0.05, yellow ≤$0.15, orange ≤$0.50, red above $0.50. Free access is neutral grey. These are display thresholds, not provider performance guarantees. Accuracy colours use the same fixed 0–100% scale across all categories.

Jev 1.14 and Luna Decisions retain their completed **October 15** measurements; the other ranked image runs are from **October 20, 2026 (America/Toronto)**. Reusing them avoids paying to ask unchanged questions again, but means the entire table is not contemporaneous. Explicit returned identities and routes are preserved in the evidence.

The models use native typed-choice interfaces. Output-token telemetry is recorded rather than assumed to be zero; a token count alone does not establish internal reasoning or model architecture. The benchmark measures a bounded decision interface, not audio generation, agentic iteration or extended chain-of-thought performance."""
    evidence=f"""The bank contains **20 categories × 10 questions**, using 227 tested compressed image files (177 single-image questions, 19 pairs and four triples). There are 187 reasoning/grounded-decision questions and 13 perception controls. Options vary: 64 questions have five choices, 135 have four, and one has three. Uniform guessing therefore averages **{d['random_uniform_baseline']:.2%}**, not 20% or 25% for every question.

The existing C1 preparation reduced 75.73 MiB to 54.36 MiB (28.2% fewer bytes). No images were recompressed or resized for this expansion. Smaller file size does not necessarily mean fewer billed image tokens. **221 of 227 images are redistributable in this packet**; six Our World in Data charts remain withheld pending third-party source-terms review. Their original private snapshots were used in all scored runs, not replacement downloads. Public hashes, source links, questions and results remain available.

The supplied key was kept outside execution and unchanged during these runs. Offline scoring reproduces **all five original model totals**, including the archived LLMs. This is a consistency check against the existing reference, not a new independent verification of every gold answer. A 10/10 category score has a wide uncertainty interval and is not a reliability certificate. No image file is shared across primary questions and the manifest assigns 200 scene groups, but source collections and task types recur. Item-level confidence intervals and pairwise tests should not be read as independent population estimates.

[Browse questions and source images](questions/README.md) · [Image gallery](gallery.html) · [Attribution and licenses](THIRD_PARTY_NOTICES.md) · [Expanded evidence](native_images_2026-10-20/summary.json) · [Family CSV](native_images_2026-10-20/family_scores.csv) · [Native route ledger](native_images_2026-10-20/attempts.jsonl) · [Admission probes](native_images_2026-10-20/compatibility_probes.jsonl) · [Model identities](native_images_2026-10-20/model_manifests.json) · [Audit receipt](native_images_2026-10-20/audit_receipt.json).

The three earlier general LLM runs are preserved in the [original five-model report]({ORIGINAL}) and [original results](results/summary.json): regular Luna 117/200, Gemini 2.5 Flash-Lite 75/200 and GPT-5.4 nano 70/200. They are not deleted, rescored, or silently replaced. They are outside the current specialized-model ranking and graphics; they are not frontier LLM references.

The separate [System 1 text benchmark]({TEXT}) uses 1,342 text questions. Its percentages and image percentages must not be combined into one score.

## Offline verification

```bash
python3 validate.py
python3 validate_native_images.py
python3 -m unittest -v test_benchmark test_image_models_2026_10_20 test_native_analysis test_native_publication
# Optional, with the original external key; never needed for API execution:
python3 score_native_images.py --answer-key /path/to/reference_key.jsonl
```

The original checksums remain intact, with superseded presentation files preserved under `archive_2026-10-16/`. The new release has a separate seal. Public validation checks file integrity, input identity, allowed choices, coverage, timing and exact-decimal costs, without network calls or credentials. Re-scoring requires the external key. Six withheld charts prevent complete request-body reconstruction using the public images alone; no validator substitutes new chart versions."""
    report=f"# Image-grounded System 1 decision benchmark\n\n{intro}\n\n[Open the readable, colour-coded report](https://etsabary.github.io/visual-decision-benchmark/report.html)\n\n![Accuracy, speed and cost for the native decision models](native_images_2026-10-20/overview.png)\n\n## Overall results\n\n{table(d)}\n\n{methods}\n\n{body}\n\n## Results by named category\n\nEvery category has ten questions. Cells show correct / 10; one answer is ten percentage points. Full names and definitions are included below and in the interactive report.\n\n{charts}\n\n## What the categories test\n\n{definitions}\n\n## Excluded routes and eligibility\n\n{excluded}\n\nSpan's 21-question partial accuracy is reported only in the evidence; it is not comparable to a full-bank score. ScaleDown's catalog advertises image input, but its pinned route returned HTTP 400 rejecting `image_url` parts. No caption or OCR replacement was used. Nimble, Microsoft Decision, Drex, Kev, Tev and Solar have no documented native-image route in the current reviewed access. A successful response to encoded image-shaped JSON alone is not proof of pixel decoding. See the [dated capability review](native_images_2026-10-20/image_capabilities.json).\n\n## Bank, reference results and limitations\n\n{evidence}\n"
    (ROOT/'README.md').write_text(report)
    # CSV is an explicit model/category mapping, with no individual gold labels.
    buffer=io.StringIO();writer=csv.writer(buffer,lineterminator='\n');writer.writerow(['model_id','model','family_id','family','correct','questions','accuracy'])
    for mid in d['rank_order']:
        s=d['models'][mid]
        for fid,v in d['families'].items():writer.writerow([mid,s['label'],fid,v['name'],s['families'][fid]['correct'],10,s['families'][fid]['correct']/10])
    (DATA/'family_scores.csv').write_text(buffer.getvalue())
    buffer=io.StringIO();writer=csv.writer(buffer,lineterminator='\n');writer.writerow(['model_id','model','correct','questions','accuracy','usable','mean_ms','median_ms','p95_ms','api_known_usd_200','api_missing_records','public_free_access','test_date','reused'])
    for mid in d['rank_order']:
        s=d['models'][mid];writer.writerow([mid,s['label'],s['correct'],200,s['accuracy'],s['usable'],s['mean_ms'],s['median_ms'],s['p95_ms'],s['core_cost']['known_api_usd'],s['core_cost']['missing_api_records'],s['public_free_access'],s['date'],s['reused']])
    (DATA/'leaderboard.csv').write_text(buffer.getvalue())
    content=markdown.markdown(report,extensions=['tables','fenced_code'])
    # Replace long static category figures with accessible named, colour-coded tables.
    matrix=''
    for block in range(4):
        fs=list(d['families'])[5*block:5*block+5]
        heads=''.join(f'<th title="{html.escape(d["families"][f]["description"],quote=True)}">{html.escape(d["families"][f]["name"])}<small>{f} · n=10</small></th>' for f in fs)
        rr=''
        for mid in d['rank_order']:
            s=d['models'][mid];cells=''.join(f'<td class="accuracy" data-ratio="{s["families"][f]["correct"]/10}">{s["families"][f]["correct"]}/10</td>' for f in fs)
            rr+=f'<tr data-model="{html.escape(s["label"],quote=True)}"><th scope="row">{html.escape(s["label"])}</th>{cells}</tr>'
        matrix+=f'<div class="table-scroll"><table class="family-table"><thead><tr><th>Decision model</th>{heads}</tr></thead><tbody>{rr}</tbody></table></div>'
    matrix='<label class="filter">Find a model <input id="model-filter" placeholder="Type a model name…" autocomplete="off"></label>'+matrix
    # Figures remain separately linked and embedded in the GitHub README.
    start=content.index('<p><img alt="Named category scores, part 1"')
    end=content.index('<h2>What the categories test</h2>',start)
    content=content[:start]+matrix+content[end:]
    css="""*{box-sizing:border-box}body{margin:0;color:#183044;background:#f3f7fa;font:17px/1.65 system-ui,-apple-system,sans-serif}main{max-width:1480px;margin:auto;padding:32px 42px 90px;background:white}h1{font-size:clamp(30px,4vw,48px);line-height:1.13;max-width:1050px;letter-spacing:-.03em}h2{margin-top:2.4em;line-height:1.25;color:#163e5b}h3{margin-top:1.8em}p,li{max-width:1100px}a{color:#06669a}nav{position:sticky;top:0;background:#123d58;color:white;z-index:5;padding:12px 28px;display:flex;gap:24px;flex-wrap:wrap;font-size:14px}nav a{color:white;text-decoration:none}img{display:block;width:100%;height:auto;margin:24px 0}table{border-collapse:separate;border-spacing:0;width:100%;font-size:15px;line-height:1.45;margin:18px 0 32px}th,td{padding:13px 12px;border-bottom:1px solid #dce5eb;text-align:right;vertical-align:middle}th{color:#183c56;background:#edf3f7}th:first-child,td:first-child{text-align:left}thead th{position:sticky;top:0;z-index:2}tbody tr:hover td,tbody tr:hover th{outline:1px solid #8199aa;outline-offset:-1px}small{display:block;font-weight:400;margin-top:5px;font-size:12px;color:#526b80}.table-scroll{overflow:auto;max-width:100%;margin:18px 0 36px;max-height:780px;border:1px solid #dce5eb;border-radius:10px}.table-scroll table{margin:0;min-width:840px}.family-table{table-layout:fixed}.family-table th:first-child{width:220px;position:sticky;left:0;z-index:1}.family-table thead th:first-child{z-index:3}.family-table td{font-weight:650;font-size:19px;text-align:center}.family-table thead th{text-align:center;min-width:140px}.filter{display:block;background:#edf5fa;border-radius:8px;padding:15px}input{font:inherit;border:1px solid #93adbf;border-radius:6px;padding:9px 12px;margin-left:12px}pre{overflow:auto;padding:20px;background:#edf3f7;border-radius:9px;font-size:14px}code{font-size:.88em}details{margin:24px 0}footer{font-size:13px;margin-top:50px;color:#587083}@media(max-width:700px){main{padding:20px 16px 60px}nav{gap:14px;padding:10px 16px;font-size:12px}body{font-size:16px}th,td{padding:10px}input{margin:8px 0 0;width:100%}}"""
    js="""for(const h of document.querySelectorAll('h2'))h.id=h.textContent.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/-$/,'');
function tint(v){const a=[255,244,208],b=[24,63,122];return `rgb(${a.map((x,i)=>Math.round(x+(b[i]-x)*v)).join(',')})`}
for(const c of document.querySelectorAll('.accuracy')){const v=+c.dataset.ratio;c.style.background=tint(v);c.style.color=v>=.65?'white':'#183044'}
document.querySelector('#model-filter').addEventListener('input',e=>{const q=e.target.value.toLowerCase();for(const r of document.querySelectorAll('[data-model]'))r.hidden=!r.dataset.model.toLowerCase().includes(q)});
for(const t of document.querySelectorAll('table:not(.family-table)')){const wrap=document.createElement('div');wrap.className='table-scroll';t.before(wrap);wrap.append(t)}
const overall=[...document.querySelectorAll('table')].find(t=>t.querySelector('thead')?.textContent.includes('Actual 200 cost'));
if(overall){for(const r of overall.tBodies[0].rows){const a=parseFloat(r.cells[2].textContent)/100;r.cells[2].style.background=tint(a);r.cells[2].style.color=a>=.65?'white':'#183044';
for(const i of [4,5,6]){const ms=parseFloat(r.cells[i].textContent)*1000;r.cells[i].style.background=ms<=500?'#d9efdf':ms<=1000?'#fff0be':ms<=2000?'#ffe0c9':'#f6d3da'}
const text=r.cells[8].textContent;if(text.includes('Free')){r.cells[8].style.background='#edf0f3'}else{const v=parseFloat(text.replace(/[^0-9.]/g,''));r.cells[8].style.background=v<=.05?'#d9efdf':v<=.15?'#fff0be':v<=.5?'#ffe0c9':'#f6d3da'}}}
"""
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Image decisions · '+str(len(d['rank_order']))+' specialized models · 200 questions</title><style>'+css+'</style></head><body><nav><a href="#">Overview</a><a href="#overall-results">Scores, speed & cost</a><a href="#results-by-named-category">Named categories</a><a href="#excluded-routes-and-eligibility">Exclusions</a><a href="gallery.html">Questions & images</a><a href="'+REPO+'">GitHub evidence</a></nav><main>'+content+'<footer>Reviewed image benchmark · October 20, 2026 · Exact source and result records on GitHub.</footer></main><script>'+js+'</script></body></html>'
    (ROOT/'report.html').write_text(page)
    (ROOT/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=report.html"><title>Image decision benchmark</title><a href="report.html">Open the image decision benchmark report</a>\n')
    print(json.dumps({'published_models':len(d['rank_order']),'named_category_cells':len(d['rank_order'])*20}))

if __name__=='__main__':build()
