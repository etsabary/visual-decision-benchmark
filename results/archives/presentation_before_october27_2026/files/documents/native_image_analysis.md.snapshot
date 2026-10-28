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

## Why Sol is the strongest non-reasoning-capable LLM reference

**Sol was the highest-scoring non-reasoning-capable general LLM in our completed text comparison: 1,143/1,342 (85.2%).** The other selected text references scored 1,109 for Opus 5, 1,070 for Sonnet 5.5 and 967 for Qwen3.8-Max. That is the measured basis for selecting Sol as the strongest—or “smartest”—non-reasoning-capable LLM reference here. The selection claim is bounded to those four tested configurations on the text bank; its image score is measured separately.

Sol supports image input and a reasoning effort of `none`, as documented in the [official model documentation](https://developers.openai.com/api/docs/models/gpt-6-sol). This image run used the same OpenRouter → OpenAI standard route, `reasoning.enabled=false`, `reasoning.effort=none`, no tools and a 16-token output cap. All 200 scored responses explicitly reported **zero reasoning tokens and no reasoning content**. These are observed API facts; the model's weights are not independently attested.

The [text comparison](https://etsabary.github.io/system-1-decision-benchmark/report.html) and [captured text statistics](https://etsabary.github.io/system-1-decision-benchmark/local_additions_2026-10-25/statistics.json) establish the selection population and scores. This is an immediate fixed-choice comparison without tools, crop/zoom operations or iterative reasoning.

## Sol on the image bank

Sol finished 12 answers behind Amos and 11 behind GLiDE. Its 1,637 ms median was longer than Amos's 340 ms, GLiDE's 359 ms and kettei-fat's 410 ms. Their weights, preprocessing, serving hardware, input file formats and dates differ; these are route-specific measurements.

Sol scored **10/10 on sequential state tracking, charts, interface-state decisions and inspection against a reference**. Attribute/set filtering, spatial relationships, perspective/knowledge tracking and recognizing insufficient evidence were 9/10. Geometry/folding/fit and constraint satisfaction were each 3/10; connectivity 4/10, navigation/planning and document reconciliation 5/10. Each category contains ten questions, so one answer changes its score by ten percentage points.

With exactly the same PNG inputs as the local runs, Sol answered 30 more questions correctly than H2O Lightning and 37 more than Fovea. Both local routes had shorter mean and median response times. This comparison does not isolate hosting location, because the model weights, hardware and serving routes also differ.

## LLM speed stops

The two-second **cumulative median** cutoff was retained explicitly for all four LLM references. Sonnet 5.5 stopped at 20 with a 3,150 ms median; Opus 5 stopped at 20 with 2,628 ms; Qwen3.8-Max stopped at 20 with 2,837 ms. All 60 partial first attempts returned usable outputs. These rows describe partial samples, with no full-bank score, full-run cost or entry in the 380-cell category ranking.

| LLM reference | Outcome | Correct / attempted | Sample accuracy | Mean | Median | p95 | Actual sample cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Sonnet 5.5 — no thinking, JSON-choice | **SPEED STOP · partial** | 18/20 | 90.0% | 3026 ms | 3150 ms | 3900 ms | $0.066222 |
| Opus 5 — no thinking, JSON-choice | **SPEED STOP · partial** | 16/20 | 80.0% | 2507 ms | 2628 ms | 3128 ms | $0.165305 |
| Qwen3.8-Max — none, Hyper Charm | **SPEED STOP · partial** | 13/20 | 65.0% | 2914 ms | 2837 ms | 4290 ms | $0.041894 quota-equivalent |

Sonnet's 18/20 (90.0%) is a promising partial result; it does not establish 90% accuracy on the 200-question bank. Its mode was `thinking.type=between_tools`, high effort, no tools and constrained JSON choice. Opus used disabled thinking at high effort with the same JSON-choice contract. All 40 scored Claude responses reported zero thinking tokens and no thinking blocks. Qwen requested catalog-supported `reasoning_effort=none`; its 20 responses omitted reasoning-token telemetry, which remains **unknown**, with no reasoning text. Hyper Charm cost values are reported USD-equivalent prepaid quota debits, not cash invoices.

Sol passed 20 at a 1,746 ms median, then the separate offline 100-case accuracy gate at 73/100 before continuation. The cumulative median stayed at or below 2,000 ms throughout 200. All four retained their text-reference routes and output contracts; JSON enums followed each image question's 3/4/5 choices. No failed-format, wrong-answer or scored transport retries were made in this cohort.

## LLM timing, input and cost qualifications

New LLM calls used **PNG-lossless-from-reviewed-decoded-RGB-v1**, the exact PNG bytes used by the two local runs. Earlier 15 hosted decision models retain their original mixed PNG/JPEG bytes. The original questions, rules, option IDs, option order and image order remain frozen. No model was rerun to change a presentation or produce this publication.

At most two distinct hosted model streams overlapped, with one request per model. Sol continuation ran alone. Timings include fresh HTTPS connection, PNG upload and the complete response; local encoding and between-phase waits are excluded. Two image admission probes per route have separate timings and costs.

The complete Sol cost is its actual 200-question reported charge; cost/1,000 is a normalization, not another 1,000 calls. The three speed-stopped rows show only their actual 20-question sample costs. Probe charges remain separate in the exports. In this new cohort there were 260 first attempts and 8 admission probes, with zero retries. No inference was performed for publication.

Public LLM timing/status evidence is answer-free: it contains request/image hashes, measured durations, returned identity, reported costs and reasoning telemetry. Private model choices, answer labels, per-item correctness, credentials, LAN addresses and account state are excluded. Accuracy was verified offline against the unchanged external key, and cannot be independently recreated from aggregates alone.

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
