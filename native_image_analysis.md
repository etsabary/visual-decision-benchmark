Amos 1 Large recorded the highest image score: **159/200 (79.5%)**, with a **340 ms median** complete response. d3-turbo followed at **155/200 (77.5%)**, then Perplexity Decider v1.2 at **152/200 (76%)**. All three returned usable typed choices on every question. These are the highest observed scores in this bank, not a universal intelligence ranking.

The expanded comparison now contains **14 specialized decision models**, each measured on the same 200 image-grounded questions. Twelve completed new runs on October 20; Jev 1.14 and Luna Decisions retain their completed October 15 results. Span- 02 crossed the prespecified two-second median limit and was stopped; ScaleDown's current route rejected images. The earlier general LLM runs remain accessible as reference results rather than the focus of the current comparison.

<!-- DETAILS -->

## What changed in the picture

Jev 1.14 led the original image comparison at 70.5%. Amos's 79.5% adds 18 correct answers on the unchanged bank. The result also changes the order seen in text: Amos is sixth among specialized models in the current text benchmark, behind d3 and Perplexity, but has the highest image score here. Span remains the text leader and has no completed image score because it failed this run's speed screen. Nimble's text result has no native-image counterpart through its documented interface.

Amos, d3 and Perplexity are close enough that their exact order needs more evidence. Amos answered 14 questions correctly that d3 missed; d3 answered 10 that Amos missed. Against Perplexity, the corresponding counts are 20 and 13. The unadjusted paired exact p-values are 0.541 and 0.296; neither difference is statistically resolved on this selected 200-question bank. These item-level tests also do not remove dependence between related visual tasks or uncertainty about future inputs.

## Different strengths behind similar totals

**Amos has a broad profile rather than one dominant specialty.** It scored 9/10 on conditional counting, sequential state tracking, cross-image matching and image/text consistency;8/10 on perspective/knowledge tracking; and 10/10 on interface states and reference inspection. No category fell below 6/10. It still missed 41 of 200 questions. Connectivity, rotation and constraint satisfaction each remained 6/10. Its 13/13 perception controls and 146/187 reasoning/grounded decisions separate straightforward visual recognition from the more demanding part of the bank.

**d3 is particularly strong on charts and correspondence.** It scored 10/10 on charts, sequential state tracking, interface states, reference inspection, matching across images and image/text consistency. For example, matching asks whether an object in one image corresponds to a reference in another; sequential tracking asks what state remains after a series of visible changes. Its visual-rule and constraint-satisfaction scores were each 5/10, and perspective/knowledge tracking was 6/10. High performance on reading and matching does not establish dependable abstract rule execution.

**Perplexity is the strongest observed metered option overall.** Its 152/200 cost$0.00431642 for the entire 200, equivalent to$0.0215821 per 1,000. It reached 9/10 on causal/counterfactual questions and 10/10 on charts, but only 4/10 on connectivity and constraint satisfaction. Its Flash counterpart was faster at 275 ms versus 476 ms median, but scored 129/200 rather than 152/200. The speed saving came with 23 fewer correct decisions in this run.

**Sqwish kettei-fat is the least expensive metered route in this cohort.** Its 147/200 (73.5%) cost$0.00213102 for 200, or$0.0106551 per 1,000, with a410 ms median and 775 ms p95. It scored 9/10 on spatial relations and flowcharts, and 8/10 on perspective/knowledge tracking. Connectivity was 4/10; document reconciliation and constraint satisfaction were 5/10. Its low price and aggregate score do not make every application category equally suitable.

**Liquid d1-ultra trades more cost and latency for more correct answers than d1.** Ultra scored 149/200 at 343 ms median, versus 135/200 at 240 ms for d1. Ultra's flowchart score was 9/10 and its document reconciliation score 8/10, but visual rules were 3/10 and perspective/knowledge tracking 4/10. A flowchart question means following branches such as “if the measurement exceeds this limit, use the left path” to the final action; it is a different demand from merely recognizing a symbol.

**Several lower-ranked models retain category-specific value.** Cloudflare Clef scored 10/10 on spatial relations and sequential state tracking, and 7/10 on constraint satisfaction, above Amos's 6/10 in that category. Luna Decisions recorded the highest rotation/reflection score,8/10, compared with Amos and d3 at 6/10. Luna's measurement is from October 15. Each comparison is only ten questions per category; one answer changes a displayed percentage by ten points.

**Cloudflare's names do not predict its order here.** Clef scored 145/200, Clef Flash 126/200 and Clef Omni 105/200. Flash's observed median was 761 ms, slower than Clef's 567 ms, while Omni's 455 ms did not compensate for its lower accuracy. These are endpoint/date observations, not conclusions about all workloads or why the models differ.

## Where the bank separates useful vision from dependable decisions

Across the 14 complete models, interface states and reference inspection averaged 9.57/10, while visual-rule application averaged 4.21/10, connectivity 4.64/10 and constraint satisfaction 4.71/10. In a constraint question, several visible placements or relationships must all hold simultaneously; satisfying most of them is not enough. The best model's total remains below 80%, despite near-perfect scores on some simpler visual functions.

Jev 1.13 scored 142/200 and the earlier Jev 1.14 run 141/200. Both rejected the same five images through their tested OpenRouter routes, and both returned 195 usable first answers. Jev 1.13 was faster in the October 20 measurement (229 ms median versus the earlier 307 ms for 1.14), but the different dates and routes' operational conditions prevent attributing that speed difference to the model version. One extra correct answer does not establish a meaningful version-level intelligence change. The files were not resized to remove these failures.

Eleven of the 12 newly completed routes returned valid probability distributions for every usable first answer; Jev 1.13 had one probability warning, retained as a usable choice rather than retried. None of the 12 needed a scored transient retry. Returning a valid choice is not the same as choosing the correct one. Confidence filtering illustrates a possible narrower workflow: at a provider-reported cutoff of 0.9, Amos retained 77/200 and answered 76 correctly; Perplexity retained 84 and answered 83 correctly. Those are exploratory, post-run thresholds, not independently calibrated production settings. Calls rejected by a confidence filter still cost money and time.

## Cost, speed and exclusions

The new scored work—including Span's stopped 21 questions—has **$0.144871244 in known API charges**. Admission probes add **$0.001893180**, for **$0.146764424 known total**. Five scored Jev 1.13 error charges and one ScaleDown admission error charge were not reported; this is not a complete invoice. Amos and d3's 400 scored calls and five admission calls used currently free public access rather than priced receipts. The earlier reused results were not billed again.

Among fully priced completed runs, Perplexity costs roughly 5.6 times less than Jev 1.14's known cost while recording 11 more correct answers. Sqwish costs roughly 11.3 times less than that Jev amount and records six more correct answers. Jev's error charges are incomplete and the runs have different dates. These comparisons describe the observed routes and this image mix, not guaranteed future tariffs or throughput.

Span's image median reached 2.166 seconds after 21 questions (mean 1.400 seconds), triggering the declared median rule. Its 14/21 correct partial result is not a200-question accuracy estimate and is excluded from the main graphics. ScaleDown was not speed-screened: its current pinned route rejected native image parts with HTTP 400 despite catalog support. Neither exclusion is a zero accuracy score.

The completed primary cohort has 2,800 first decisions:2,400 new and 400 reused. Span contributes 21 separate partial decisions. The three older LLMs remain outside that count and the current specialized ranking. No new general LLMs were tested overnight.
