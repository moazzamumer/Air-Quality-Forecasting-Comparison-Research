# Corrected first-origin SARIMAX recovery

The default 50-iteration fit plus 150-iteration bounded retry failed at the first test origin (2025-01-13 01:00 UTC). The final retry made no progress. Its metadata and log are preserved in `../artifacts/coverage_reconsideration/failed_attempts/core_sarimax_frozen_s42/`; no forecast from that attempt enters the analysis.

A diagnostic retry from those failed estimates also failed. A second training-only diagnostic used the already selected, converged corrected validation fit (cutoff 2024-12-16 01:00 UTC), adjusting predictor slopes for the new training scales. Complex-step L-BFGS-B with maxiter 200/maxls 100 converged in 83 iterations, increasing training log likelihood from −132436.969 to −132373.753. Neither diagnostic evaluated test forecast errors.

The versioned runner now applies this fixed initialization policy at the first origin and initializes later fits and controls from the corrected first-origin fit. Each model is optimized on all history before its own origin, with the selected order unchanged. The actual runner repeated the successful fit and saved all 23 frozen forecasts. Convergence, finite estimates, initialization cutoff and nondecreasing training likelihood are checked. Validation settings and their signature remain unchanged; the experiment signature changed, requiring regeneration of the earlier matrix outputs.

Supervisor timing records include finalized attempts only. The interrupted NeuralProphet attempt and the two standalone diagnostic fits have no finalized supervisor records; they must not be included in claims of total campaign time or controlled algorithm speed.
