# R2.M7 — PM10 exclusion and leakage terminology

Moazzam requested a researched, concrete explanation on 1 October 2026. This is a reporting clarification of the existing gas-only primary experiment; no predictor set, forecast, selection rule or numerical result was changed.

The primary comparison deliberately stays within the retained gas-conditioned scope. PM10 is a same-hour particulate aggregate containing the fine fraction being predicted, and the saved training correlation is 0.992. Excluding this close target proxy gives the gas-only comparison a defined scope; it does not establish that the four gases are optimal or that PM10 is irrelevant.

The following primary sources were read and added to the revised bibliography:

- [United States EPA, What is Particle Pollution?](https://www.epa.gov/pmcourse/what-particle-pollution) defines PM10 as including fine and coarse fractions. PM10 is therefore physically overlapping with PM2.5, but not an exact duplicate. This definition does not authenticate an additive identity between the particular API fields or establish how their provider generated them.
- [Kapoor and Narayanan (2023), Patterns 4(9):100804](https://doi.org/10.1016/j.patter.2023.100804), particularly taxonomy L2, discusses outcome proxies and the task-specific legitimacy of predictors. Correlation alone is not a leakage diagnosis.

[Official scikit-learn guidance](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage), also checked, emphasizes information that would not be available at prediction time. It is supporting technical context, not an additional manuscript reference.

For this study, actual future PM10 would be unavailable information if scores were claimed to establish operational forecasts. The same availability qualification applies to the actual future gases used by the primary models. The disclosed Perfect Prognosis controls instead answer a conditional question. We do not label their successful predictions as invalid simply because the input correlates strongly with the target. Lagged or independently forecast PM10 can be legitimate in a different information protocol.

The broad control adds five predictors together. Its improvement cannot isolate the effect of PM10 alone, and the failed broad SARIMAX control still prevents a complete broad-family ranking. Existing broad-set results are retained with these qualifications.

The revised response states the physical-overlap rationale without claiming it was a documented original selection rule. This avoids rewriting the experiment's history after viewing results. Implementation explains the exclusion; Results qualifies the grouped ablation; the Introduction's former description of PM10 as coarse-only is corrected. Added citations and changed text remain yellow in the manuscript. No new experiment is warranted by this wording clarification.

Remaining author/release obligations are unchanged. The original manuscript, raw data, all experimental inputs and results remain preserved.
