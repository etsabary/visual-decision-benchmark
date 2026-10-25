# October 20 native-image expansion

The current report ranks 14 specialized models: 12 new completed 200-question runs and the unchanged October 15 Jev 1.14 and Luna Decisions runs. The three original general LLM runs remain historical references outside this primary cohort. The original protocol follows below, explicitly as the October 15 protocol; its five-model comparisons do not describe the expanded cohort.

`image_models_2026_10_20.py` is the answer-blind executor. It reads frozen public questions, an old blind image-path manifest and exact compressed C1 image bytes, and never imports the offline scorer or reads the gold key. It binds model, provider, ordered image hashes, wording, rules, options, request-body SHA256 and its own software hashes before scoring. No question, key or image was changed in the expansion.

OpenRouter calls use its native Decisions endpoint with an explicit provider pin and no fallback. Amos receives documented top-level bare-base64 `images`; d3 receives top-level base64 data URLs; Sqwish receives image URL parts in `state`. These are provider-specific image transports for the same pixels, not OCR or caption substitutes. Admission used one image and an ordered three-image set. Admission does not guarantee success on every later file.

The first admission pass incorrectly treated nonzero output-token telemetry as proof of generation rather than a native typed choice. Before any scored call, this check was removed: four already-saved valid probe responses were reinterpreted without repeat inference, and the original raw evidence and parser review were retained privately. d3's first unscored bare-base64 probe was rejected; its documented data-URL encoding then passed with the same pixels. All of these controls and their charges remain separate from scored results. Token telemetry is published; internal reasoning is not inferred from that field.

After 20 first attempts and after each later first attempt, a cumulative median above 2,000 ms stops the route. Span crossed this at question21 and was stopped. No partial score enters the full-bank table. ScaleDown's current pinned route rejected image parts despite catalog image support, so it received no scored cases. The other 12 new routes completed200. No native-model accuracy cutoff was applied.

Primary accuracy counts every scheduled first attempt; errors are unsuccessful. Only transport failures or HTTP408/429/5xx can receive one recovery. No wrong valid answer, formatting failure, or deterministic HTTP400 is retried. Retry costs are included in core cost while primary accuracy and timing use first attempts only. Dispatches, attempts, results and completion receipts are separately journalled. An unresolved possibly billed dispatch is not silently replayed.

Each timer starts before a fresh HTTPS connection and includes upload and complete response-body receipt. Local encoding, request construction and rate/retry waits are excluded. At most four independent serial model streams run concurrently. Summaries include mean, median and linearly interpolated inclusive p95 on all first attempts, not just usable answers. This is a route-and-date comparison, not same-weights mode isolation.

Money is summed with exact-decimal arithmetic from API receipts. Missing error charges remain missing, not zero. d3 and Amos currently offer free public access and no metered cost receipt; they are not represented as measured $0 prices. Costs per1,000 normalize each actual200. Probes, retries and stopped runs have their own accounting. The executor's $5 guard applies only to known scored charges, so unreported or in-flight costs prevent a hard spending guarantee.

Offline analysis uses the original key SHA256 from the frozen October15 manifest. All five original totals were reproduced before comparison. Public results contain no gold labels or item-level correctness. The old seal remains unchanged with superseded presentation snapshots under `archive_2026-10-16/`; the new dated bundle has a separate seal. External-key scoring is available independently of private execution state. This is not a new blind audit of the gold answers.

## Original October 15 protocol (historical)

# Methodology for the October 15 2026 image benchmark

## Frozen questions and image inputs

The bank was frozen before target results. It has 200 questions, twenty ability families, and ten questions per family. Question wording, rules, option IDs, option order, image order and reference answers stayed fixed. Every model received exactly the same reviewed compressed C1 image bytes for a given question. The original bank digest is retained in [data/benchmark_manifest.json](../data/benchmark_manifest.json); the public blind question file is byte-identical to the frozen question file.

The tested image corpus contained 227 files. No image file is shared across primary questions, and the manifest assigns 200 distinct scene groups. Shared source collections and task families can nevertheless introduce correlations. There are 38 questions proposed as straightforward, 107 moderate and 55 demanding. Those difficulty labels describe the pre-test design, not a model-independent measure of item difficulty.

The model inputs contained only the question, explicit rules, answer options and ordered image parts. Gold labels, derivations, source titles, source filenames, family labels, difficulty, supplier metadata, review notes and earlier model answers were not sent. Source names and credits in the public gallery were not part of the API prompts.

## Routes and model identities

| Requested model | Returned response identity | Pinned provider or route |
|---|---|---|
| `typesafe/jev-1.14` | `typesafe/jev-1.14-20261014` | TypeSafe through OpenRouter alpha Decisions |
| `openai/gpt-6-luna-decisions` | `openai/gpt-6-luna-decisions-20261006` | OpenAI through OpenRouter alpha Decisions |
| `openai/gpt-6-luna` | `openai/gpt-6-luna` | OpenAI standard endpoint, no fallback |
| `openai/gpt-5.4-nano` | `openai/gpt-5.4-nano` | OpenAI standard endpoint, no fallback |
| `google/gemini-2.5-flash-lite` | `google/gemini-2.5-flash-lite` | Google AI Studio standard endpoint, no fallback |

The saved regular Luna endpoint name contains `20260922`; the saved nano endpoint name contains `20260317`. General-LLM responses use undated aliases. Endpoint names and pricing metadata matched between pilot and extension, and successful returned identities/providers were checked for changes. These checks do not prove that an alias maps to immutable hidden weights.

The Decisions requests used `https://openrouter.ai/api/alpha/decisions`. General LLM requests used `https://openrouter.ai/api/v1/chat/completions`. Neither Jev direct through TypeSafe nor a native OpenAI comparison was run in this image experiment. The complete measured windows, including UTC offsets, are in [data/model_manifest.json](../data/model_manifest.json). All tests occurred on October 15, 2026, America/Toronto. Decisions were measured earlier than the general LLMs, so this is not a simultaneous five-route latency experiment.

## Exact request profiles

Decisions requests place the ordered inline PNG/JPEG data URLs in `state`, with one typed choice question named `decision`. Its instructions are the exact question, two newline characters, `Rules: ` and the rules. Its criteria map the frozen option IDs to their text. No generic chat output instruction or output-token cap was added to that route.

General LLM requests have one user message. The first part is the following text, followed by the ordered inline image URL parts:

```text
{exact question}

Rules: {exact rules}

Options:
{option ID}: {option text}
{remaining options in frozen order}

Return only the numeric option ID, without explanation.
```

The general LLM bodies set `max_tokens: 32`, `stream: false`, `usage.include: true` and `reasoning.enabled: false`. OpenAI models also set `reasoning.effort: "none"`. Provider routing sets `only` to the recorded provider slug, `allow_fallbacks: false` and `require_parameters: true`. Sampling, seed, image detail and default cache behavior were not overridden. No schema-constrained JSON, forced-choice decoding, tool use or explanation was requested. Visible explanation text still counts as output even when hidden reasoning is disabled.

[benchmark.py](../scripts/benchmark.py) reconstructs these exact historical bodies from the public questions and images. [data/request_plan.jsonl](../data/request_plan.jsonl) retains their canonical JSON SHA256 hashes and byte counts. The module contains no credential handling or HTTP transport. It is a request-reproduction aid, not a claim that today's provider behavior is unchanged.

## Selection and execution order

The initial general-LLM pilot selected the first encountered question in each family from the frozen randomized stage-one order. It did not select based on prior model accuracy. The resulting twenty questions and sixty successful calls were reused. The extension excluded those IDs and covered all remaining 180 questions on each of the three general LLMs.

General LLM calls were serial and interleaved within groups of three, one per model on the same question. A seeded six-permutation cycle balanced their positions, with sixty extension questions per position for each model. The earlier Decisions run used paired calls with balanced first/second positions within each 100-question stage. Pilot, extension and Decisions measurements remain separate phases in the ledger.

There were 1,000 scheduled primary item/model pairs. Including bounded retries, the scored run has 1,003 attempts: 400 Decisions first attempts plus two retries, and 600 general-LLM first attempts plus one retry. Four earlier Decisions compatibility probes are stored separately and excluded from core accuracy and core cost.

## Scoring and retries

The primary result is first-attempt correct out of all 200 scheduled questions per model. Usable means an allowed discrete option ID. The strict general-LLM parser requires the complete trimmed text to equal an allowed option ID and the finish reason to be `stop`. A truncated response is unusable even if an option ID occurs inside it. An explanation, a bare computed value outside the option IDs or a malformed output is also unusable.

A valid wrong answer is never retried. Transport failures and HTTP 408, 429 or 5xx responses can receive one retry. HTTP 400 input rejections and invalid answer formats are not retried. A retry does not overwrite the first-attempt record. Eventual coverage and correctness remain separate measurements. Probability-distribution validation is separate from choice validation: malformed probabilities do not discard an otherwise valid discrete Decisions choice.

The external gold key remains private, following the text benchmark's policy. Before publication, the sanitized public response records were re-scored locally against that key and reproduced all five model totals. [score.py](../scripts/score.py) accepts an external CSV or JSONL with fields `candidate_id` and `correct_option_id`. It writes results to standard output and makes no API calls. No key revision or replacement question was introduced after seeing target results.

## Timing and cost arithmetic

The original runners used a monotonic timer from dispatch through complete response-body receipt, including connection and upload. Local image reading, base64 encoding, request construction and SSL-context preparation are outside that route timer. Retry waiting is separate. The connection timeout was ten seconds and the total request timeout ninety seconds. Median, p90 and p95 use linear interpolation at `(n-1) × quantile` over first attempts. Both all-first-attempt and usable-first-attempt latency summaries are retained.

Cost is the actual returned `usage.cost` for text, images and output, including any default cache charges. Summation uses decimal arithmetic. Missing error charges are unknown, not zero. Jev has five missing core error charges, Luna Decisions three and Gemini one. The known scored-core sum is **$0.135269676** across 1,003 attempts. The four unscored probes add **$0.000573136**, for **$0.135842812** known across all 1,007 attempts. These are returned request charges, not account-invoice reconciliations; they exclude curation and preparation.

Regular Luna reported 177,928 cache-write tokens and zero cached-read tokens. The other general LLMs reported zero cache-write tokens. Default cache behavior was retained, so the measured totals reflect that run rather than a hypothetical cache-free price. File compression savings are not treated as billed image-token savings. Token counts differ across providers and vision preprocessing; equal token counts are not assumed to represent equal image work.

Cost per first correct answer divides all core attempt cost, including retries, by first-attempt correct answers. Where charges are missing, that ratio is also a known lower bound. Normalized dollars per 1,000 questions in the figure are a rescaling of these observed 200-question costs, not a volume discount, vendor list price or new 1,000-question experiment.

## Statistical and confidence summaries

The aggregate file retains item-level Wilson 95% intervals and unadjusted exact two-sided McNemar comparisons for all model pairs. The bank is purpose-built, with ten items per family, rather than a random sample from all visual decisions. Those summaries do not correct for possible family/source correlations, deliberate category selection or multiple comparisons. A non-significant difference does not establish equivalence.

Confidence filtering uses the separate provider-reported Decisions `confidence` field, only on usable first answers with numeric confidence in [0,1]. Coverage always divides by 200 scheduled questions. Boolean and invalid confidence values are excluded. The published cutoffs were examined after the run and have no independent holdout validation. General LLM confidence or comparable option probabilities were not collected.

The blind key was authored/reviewed before the target run, but the bank has no independent blind second-reader certification of every printed question. Public source images have unknown training exposure. A later demonstrated key or wording defect should produce a versioned correction applied to every model's saved responses, while preserving this original reference.
