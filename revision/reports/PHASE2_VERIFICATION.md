# Phase 2 verification

Exit evidence ready: **True**. Completed tasks: 94/94; original failed attempts: 6; recovered: 6; unresolved: 0; pending: 0.

All 21 original fingerprinted files checked. Baselines: 3. Correction streams: 35.

Integrity errors: none.

## Coverage exceptions

| run_id | family | regime | variant | seed | week | reason | resolved | recovery_run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| core_sarimax_walk_w02_s42 | sarimax | walk | selected | 42 | 2.0 | RuntimeError: SARIMAX did not converge under bounded optimizer policy | True | recover_core_sarimax_walk_w02_s42 |
| core_sarimax_walk_w17_s42 | sarimax | walk | selected | 42 | 17.0 | RuntimeError: SARIMAX did not converge under bounded optimizer policy | True | recover_core_sarimax_walk_w17_s42 |
| core_sarimax_walk_w18_s42 | sarimax | walk | selected | 42 | 18.0 | RuntimeError: SARIMAX did not converge under bounded optimizer policy | True | recover_core_sarimax_walk_w18_s42 |
| core_sarimax_walk_w20_s42 | sarimax | walk | selected | 42 | 20.0 | RuntimeError: SARIMAX did not converge under bounded optimizer policy | True | recover_core_sarimax_walk_w20_s42 |
| core_sarimax_walk_w21_s42 | sarimax | walk | selected | 42 | 21.0 | RuntimeError: SARIMAX did not converge under bounded optimizer policy | True | recover_core_sarimax_walk_w21_s42 |
| ablate_sarimax_clip | sarimax | frozen | clip | 42 |  | RuntimeError: SARIMAX did not converge under bounded optimizer policy | True | recover_ablate_sarimax_clip |

## Completed forecast coverage

| family | regime | variant | seed | windows | hours | recovered_windows |
| --- | --- | --- | --- | --- | --- | --- |
| neuralprophet | frozen | broad | 42 | 16 | 2688 | 0 |
| neuralprophet | frozen | clip | 42 | 16 | 2688 | 0 |
| neuralprophet | frozen | no_inputs | 42 | 16 | 2688 | 0 |
| neuralprophet | frozen | selected | 42 | 16 | 2688 | 0 |
| neuralprophet | frozen | selected | 123 | 16 | 2688 | 0 |
| neuralprophet | frozen | selected | 2026 | 16 | 2688 | 0 |
| neuralprophet | walk | selected | 42 | 16 | 2688 | 0 |
| neuralprophet | walk | selected | 123 | 16 | 2688 | 0 |
| neuralprophet | walk | selected | 2026 | 16 | 2688 | 0 |
| prophet | frozen | broad | 42 | 16 | 2688 | 0 |
| prophet | frozen | clip | 42 | 16 | 2688 | 0 |
| prophet | frozen | no_inputs | 42 | 16 | 2688 | 0 |
| prophet | frozen | selected | 42 | 16 | 2688 | 0 |
| prophet | walk | selected | 42 | 16 | 2688 | 0 |
| sarimax | frozen | broad | 42 | 16 | 2688 | 0 |
| sarimax | frozen | clip | 42 | 16 | 2688 | 16 |
| sarimax | frozen | no_inputs | 42 | 16 | 2688 | 0 |
| sarimax | frozen | selected | 42 | 16 | 2688 | 0 |
| sarimax | walk | selected | 42 | 16 | 2688 | 5 |

Unconverged fits have no scored forecast stream. Valid numerical recoveries are separately identified and retain the selected settings and training cutoff. Phase 3 must compare methods on matching successful windows and report available coverage, recovery effort, and any unresolved failure. A verified completed matrix can still contain explicitly documented failed-fit exceptions.
