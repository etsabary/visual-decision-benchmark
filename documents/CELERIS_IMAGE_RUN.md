# Celeris 1.1 image decisions

The comparison contains **19 complete routes: 16 hosted decision models, two local models and GPT-6 Sol as a non-reasoning LLM reference**. Every complete row has 200 first attempts across 20 categories. All 18 prior records and the three separate LLM speed stops are unchanged.

**Celeris 1.1 Decision scored 143/200 (71.5%), with 667/585/1120 ms mean/median/p95 and 200 usable decisions.** It passed the existing two-second cumulative-median cutoff. Blue identifies its hosted route; purple identifies local RTX 2060 runs and pale yellow identifies Sol.

Amos 1 Large remains highest at 159/200 (79.5%), followed by GLiDE at 158 (79.0%) and d3-turbo at 155 (77.5%). Sol retains 147 (73.5%). Every previous score, cost, duration, date and exclusion is preserved; publication used saved evidence without new model calls.

## Celeris: accuracy, speed and cost

Celeris answered four fewer questions correctly than Sol, a two-percentage-point gap, with a 585 ms median versus Sol's 1,637 ms. It finished 16 answers behind Amos and 15 behind GLiDE. These observed gaps on one developing bank do not establish a general ability ordering. Celeris is the ninth complete route in the accuracy-sorted table.

Its estimated 200-question cost is **~$0.01175164**, or **~$0.05875820 per 1,000**. This is 293,791 reported input tokens times the captured USD 0.04/million tariff, not monetary receipts. Five separate image-binding probes cost an estimated $0.00042344. Sol's reported bank charge was $0.591634; GLiDE's usage-times-tariff estimate was $0.00767264. Local hardware and electricity cost remains unmeasured.

## Celeris category profile

**10/10:** Charts and quantitative comparisons 10/10; Interface state decisions 10/10; Insufficient evidence 10/10.

**3/10:** Visual rule application 3/10; Perspective and knowledge tracking 3/10.

Every category has ten questions, so one answer changes a category score by ten percentage points. The full 380-cell matrix preserves all model profiles; a category's measured score is not a promise of reliability on other tasks.

## Celeris image settings and timing

The exact requested and returned model was `celeris-1.1-decision`, using the direct native SystemOne endpoint with explanations disabled. Images were named `image_1`, `image_2`, etc. in `x_celeris.images`, supplied as base64 PNG URLs in original order, with corresponding state markers. Question wording, rules, option IDs, order and the frozen answer key were unchanged. Variable three/four/five-choice outputs were checked against each question's exact choices.

The run used the exact recorded PNG bytes shared with Sol and the two local models. No image was resized, replaced with OCR or captioned. `max_soft_tokens=1120` selected the highest resolution control in the captured [Celeris image documentation](https://docs.celeris.ai/images). Its internal preprocessing is provider-controlled. Earlier 15 hosted decision records retain their original mixed PNG/JPEG bytes. File format, resolution, route, hardware, date and load qualify accuracy and timing comparisons.

Five synthetic probes checked red/blue recognition, reversed pair order and a three-image input; all passed. The initial 20 scored requests measured 677/572/1105 ms mean/median/p95. The cumulative median stayed below 2,000 ms through all 200. All first attempts are retained; no retries or accuracy-only stopping. Fresh HTTPS calls were serial, at least 0.25 seconds between dispatch starts; PNG/base64/JSON preparation and idle pacing were excluded, upload and complete response included.

All 200 outputs were native typed choices with probability distributions, zero reported output tokens and no generated explanation. These facts do not independently attest to hidden computation, model weights or per-item processed-input delivery. Start/end model catalogs matched. The [captured protocol](../results/releases/celeris_2026-10-26/celeris_execution_protocol.json) and [answer-free timing/usage evidence](../results/releases/celeris_2026-10-26/celeris_timing_evidence.jsonl) retain settings and bindings without publishing model choices or answer labels.



[Full image report](https://etsabary.github.io/visual-decision-benchmark/report.html)
