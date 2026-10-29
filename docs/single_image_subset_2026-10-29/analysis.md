## October 29: image decisions on the same 177 questions

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
