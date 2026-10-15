# Public release on October 15 2026

## What is included

This release contains all 200 blind questions, twenty family definitions, 1,000 primary request bindings, 1,003 sanitized scored-attempt records and four separately labeled compatibility probes. Model identities, provider metadata, timestamps, request and image hashes, output text, choices, confidence/probability fields where returned, usage, cost and timing are retained. The aggregate results, family scores, exploratory confidence thresholds, two charts, question galleries and offline validation/re-scoring tools accompany those records.

The image directory contains 221 exact tested C1 files. Each has a recorded source, creator/credit, license, modification notice, geometry and SHA256 hash. The MIT license covers software and original documentation; third-party images keep the licenses listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Six images are referenced rather than redistributed

| Asset | Chart | Reason for withholding |
|---|---|---|
| CCA0010 | Share of the population using the Internet | Third-party source terms not independently cleared |
| CCA0059 | GDP per capita | Third-party source terms not independently cleared |
| CCA0062 | Primary energy use per person | Third-party source terms not independently cleared |
| CCA0065 | Annual CO2 emissions | Third-party source terms not independently cleared |
| CCA0134 | Child mortality rate | Third-party source terms not independently cleared |
| CCA0135 | Maternal mortality ratio | Third-party source terms not independently cleared |

Their source links, tested hashes, dimensions, questions and response measurements remain public. The bank still has 200 scored questions per model; 194 questions have all image bytes packaged. A current download is not a guaranteed match to the frozen snapshot. The [Our World in Data FAQ](https://ourworldindata.org/faqs) distinguishes its own reusable material from material governed by third-party terms; this release retains the unresolved source-review flags rather than extending them into a blanket redistribution claim.

## What is excluded

Gold answers and derivations remain outside Git. Public response rows do not contain per-item correctness flags. The release also excludes API credentials, environment files, authorization headers, account state, local filesystem paths, private curation conversations and drafts, source archives, backup images and the original unsafe receipt image. Only its reviewed safe input crop is eligible for the tested corpus. The original private execution packets and their frozen source files remain unchanged.

The external-key policy matches the companion text benchmark. It means readers can inspect the questions and model outputs, reproduce available request bodies and verify cost/coverage arithmetic, but cannot independently re-score accuracy from the public files alone. The private audit receipt reports the completed raw-response check; it is not a substitute for access to the reference key.

## Validation boundary

The public validator verifies checksums, all 221 included image hashes, 200 questions, 1,000 distinct item/model pairs, the attempt/retry ledger, image ordering, cost arithmetic and internal aggregate consistency. It reconstructs 970 exact historical request payloads. The remaining thirty require the six withheld images. Re-scoring with the external key reproduced the published five-model totals before publication.

No additional paid inference, resized replacement test or new model configuration was run to prepare this release. The original twenty-item pilot, full extension and earlier Decisions measurements remain identifiable in the exported records. Future changes to keys, images or prompts should receive a new version and must not silently rewrite this reference.
