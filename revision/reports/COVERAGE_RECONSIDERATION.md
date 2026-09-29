# Coverage reconsideration before Phase 3

Moazzam requested reconsideration of the strict whole-week exclusion policy.
Phase 3 is deferred while the wider evaluation is implemented and verified.
The completed strict-availability experiment remains preserved under
`artifacts/phase2/`; its 16-week results are a sensitivity reference.

The 23 full calendar weeks contain 3,864 scheduled hours, of which 3,624 have
original PM2.5 and all broad-set PP covariates. Missing future data affects weeks
8, 11, 12 and 14. Weeks 9, 13 and 15 have complete future observations and were
previously excluded solely for incomplete historical context. The final 163-hour
remainder stays separately reported rather than treated as a full week.

The broader evaluation will retain the same raw source, chronological calendar
split, weekly origins, selected configurations, model families, seeds and fitting
data policies. It will explicitly distinguish full and partially scored weeks.
It does not recreate the original notebook's irregular 168-row chunks.

Proposed amendment, subject to executable checks:

- Score only original observed target hours with observed PP covariates, using
  one common hourly mask for all methods. Never fill a scoring target.
- Retain training target handling unchanged. For models/baselines requiring
  dense inference history, fill only missing historical context with the value
  168 hours earlier, recursively using past values only. Preserve observations
  and record the number of filled historical hours. This is an explicit
  assumption, particularly consequential for the 120-hour context gap.
- At missing future-input timestamps that are never scored, use computational
  placeholders only if changing those placeholders leaves every scored forecast
  unchanged. Verify this on actual fitted models, not just an architectural
  assumption. No conditional prediction at an unavailable-input hour is reported
  as an observed-covariate PP forecast.
- Reuse existing forecasts only where the fitted model, preprocessing, origin,
  context and information set are unchanged. Record exact source evidence and
  account for shared computation. Correction must be recomputed on the wider
  chronological schedule, using observed-hour base residuals after each week.

Before adoption: test causal history filling, missing-hour scoring masks,
placeholder invariance and preservation of the 16-week evidence. Compare the
broader result with the strict subset transparently; coverage decisions are not
selected to reproduce model rankings or errors. The broader protocol changes
will have their own configuration/signature and artifacts.
