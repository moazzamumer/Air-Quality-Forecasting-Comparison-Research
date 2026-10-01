"""Authored response prose. Reviewer quotations are read from the preserved scaffold."""

RESPONSES = {
    "R1.1": {
        "paragraphs": [
            "We agree that the original 21-week SARIMAX result was not directly comparable with the complete runs. We have repeated the primary experiments and completed SARIMAX at all 23 weekly forecast origins, as also requested in Reviewer 2's major comment 4. The revised comparison therefore supersedes the incomplete original run rather than retaining a 21-week result with a qualification.",
            "All primary models, regimes and seeds are evaluated on the same 3,624 observed hours within 3,864 scheduled hours. Nineteen weeks have complete scoring coverage; four have 120, 120, 48 and 144 scored hours. Missing targets are not imputed for evaluation. The revised SARIMAX weekly-refit pooled MAE/RMSE are 30.43/46.88 micrograms per cubic metre. The Abstract, Results and Conclusion now refer to the completed matched comparison. The earlier memory failure was specific to the original implementation and environment; it is not presented as an intrinsic limitation of SARIMAX."
        ],
        "locations": ["Abstract, p. 1", "sec:results", "subsec:impl_data", "subsec:impl_evaluation", "tab:regime1_results", "Conclusion, p. 22"]
    },
    "R1.2": {
        "paragraphs": [
            "We have clarified that this is a retrospective Perfect Prognosis comparison: actual future NO, NO2, CO and SO2 are supplied, while future PM2.5 is withheld from prediction. Highly accurate externally available gas forecasts could approximate this information setting, but their forecast errors would be absent from our experiment. Without such inputs, this remains an idealized conditional evaluation.",
            "We have narrowed the Abstract and Conclusion and changed 'Operational' to 'Adaptive' in the title. We do not claim demonstrated deployment readiness or skill with gas inputs available at the forecast origin. Prospective evaluation with externally forecast predictors and independently verified station targets is identified as future work. This treatment is consistent with Reviewer 2's major comment 1."
        ],
        "locations": ["Title and Abstract, p. 1", "sec:methodology", "Discussion and future work, p. 21", "Limitations, pp. 21–22", "Conclusion, p. 22"]
    },
    "R1.3": {
        "paragraphs": [
            "We now report the initial frozen-fit SARIMAX and Prophet regressor coefficients, expressed as target change per one initial training-input standard deviation. For NO, NO2, CO and SO2 respectively, these are −36.62, 5.17, 237.06 and 3.22 for SARIMAX, and −46.32, 35.40, 265.48 and −24.94 for Prophet, in micrograms per cubic metre.",
            "We also describe coefficient stability across the 23 refits after conversion to raw-input units, and Prophet's mean absolute trend, seasonal and regressor contributions across the frozen evaluation. Component averages weight each of the 3,624 scored hours equally. These are conditional fitted associations: correlated regressors, temporal terms and cancelling signed components prevent interpreting them as causal effects or independent feature-importance scores."
        ],
        "locations": ["Model interpretation and computational measurements, pp. 18–21", "tab:effects", "Limitations, pp. 21–22"]
    },
    "R1.4": {
        "paragraphs": [
            "We have checked NeuralProphet's normalization, contiguous training episodes, finite training losses, forecast timestamps and extraction of the 168 origin-specific leads. Training samples do not cross missing intervals, and predictions are returned to the original target scale. Completing 50 epochs is not interpreted as proof of optimization to a global minimum.",
            "Repeated runs with seeds 42, 123 and 2026 show substantial variability: frozen pooled MAE is 46.88 ± 10.40 across seeds, compared with 39.61 ± 4.33 for refits (mean ± sample SD). Seed 2026 is appreciably better before correction and becomes slightly worse after it. On the small high-concentration subset, seed-42 NeuralProphet outperforms the other frozen families. We distinguish these documented findings from tentative explanations involving optimization or seasonal generalization, and no longer infer an inherent weakness of NeuralProphet."
        ],
        "locations": ["subsec:impl_models", "tab:seeds", "Lead time, concentration, and sensitivity, pp. 17–18", "Discussion and future work, p. 21"]
    },
    "R1.5": {
        "paragraphs": [
            "We have replaced the unexplained original orders with a documented, bounded training-only selection procedure. Four weekly validation origins run from 16 December 2024 to 6 January 2025, before the test period. The SARIMAX grid fixes p=q=P=Q=1 and s=24 and considers d,D in {0,1}. Candidates are ranked by mean weekly MAE, with pooled RMSE as tie-breaker; a nonconverged candidate is excluded.",
            "The selected specification is (1,0,1) × (1,0,1,24), without a constant. Its validation MAE is 14.99. These orders replace the original (1,1,1) × (1,1,1,24) specification and are used unchanged in both revised regimes. The manuscript states the grid, criterion, failed candidate and limited winter validation scope. This is not presented as exhaustive order optimization."
        ],
        "locations": ["subsec:impl_models", "tab:configuration", "eq:sarimax"]
    },
    "R1.6": {
        "paragraphs": [
            "All revised models ran on the same AMD Ryzen 5 5500U CPU system, with two configured model threads and approximately 14.96 GiB of reported system RAM. No GPU was used, including for NeuralProphet. The Implementation section lists the relevant Python and library versions.",
            "We have also corrected the timing interpretation. SARIMAX fit timers cover optimization, whereas Prophet and NeuralProphet timers include initialization/import; preprocessing and prediction are excluded from the reported fit table and recorded separately. First-origin reuse retains the source computation cost. Because these boundaries differ, the revised manuscript reports measured times with explicit definitions and withdraws a controlled cross-family speed-ratio claim."
        ],
        "locations": ["Implementation, pp. 7–8", "tab:timing", "Model interpretation and computational measurements, pp. 20–21"]
    },
    "R1.7": {
        "paragraphs": [
            "We have added a causal sensitivity replay with α=0.1, 0.2, 0.3, 0.5, 0.7 and 1.0, alongside the uncorrected base. The original α=0.3 remains predefined and is not replaced using test scores. α=1.0 is the previous-week mean-residual correction requested by Reviewer 2.",
            "The conclusions are conditional rather than uniform. SARIMAX mean weekly MAE is 29.50, 30.17 and 31.33 at α=0.1, 0.3 and 1.0, respectively, versus 30.66 without correction. Prophet improves at all tested nonzero factors. NeuralProphet seeds 42/123 improve, while seed 2026 becomes slightly worse throughout the tested range. The revised text reports this sensitivity and avoids claiming α=0.3 is optimal."
        ],
        "locations": ["subsec:impl_regimes", "Lead time, concentration, and sensitivity, pp. 17–18", "fig:correction", "tab:seeds"]
    },
    "R1.8": {
        "paragraphs": [
            "Tables 6 and 7 now distinguish pooled hourly MAE/RMSE from equally weighted mean weekly MAE/RMSE and include sample standard deviations across the 23 matched weeks. Figures 4–6 show the weekly distributions and chronology. Weekly RMSE is not labelled as pooled RMSE.",
            "We have added paired weekly MAE comparisons with descriptive 95% moving-block bootstrap intervals, using 2,000 replicates, a primary three-week block and two-/four-week sensitivities. For corrected SARIMAX minus corrected Prophet, the mean weekly difference is −7.90 with a primary interval of [−11.33, −3.63]. SARIMAX correction minus its own base is −0.49 with interval [−3.91, 2.25]. These comparisons use identical scoring masks. With only 23 dependent weeks and no multiplicity adjustment, they do not establish broad population-level significance."
        ],
        "locations": ["subsec:impl_evaluation", "tab:regime1_results", "tab:regime2_results", "tab:paired", "fig:regimes", "fig:chronology", "fig:weekly_distribution"]
    },
    "R1.9": {
        "paragraphs": [
            "We have condensed Related work into a focused discussion and a short comparison table, emphasizing the distinction between representation learning and the update policies evaluated here. We have also removed repeated deployment and superiority claims and tightened the Discussion, Limitations and Conclusion so that findings, unresolved constraints and future work have distinct roles.",
            "The six selected best-/worst-week illustrations have been replaced with all-week summaries and lead-time/correction diagnostics. We retained the preprocessing, validation and uncertainty details needed to address the methodological comments, while placing exact settings in Implementation rather than repeating them in Methodology."
        ],
        "locations": ["Related work, pp. 3–4", "sec:methodology", "sec:implementation", "Discussion, Limitations and Conclusion, pp. 21–22", "Figures 4–9, pp. 15–19"]
    },
    "R1.10": {
        "paragraphs": [
            "We have added a descriptive table for the original observed PM2.5 targets in each full chronological partition, including the unused final test remainder. Training has 35,736 observed values, with mean 217.54, sample SD 227.30, median 140.59 and range 0.91–1825.93 micrograms per cubic metre. Testing has 3,787 observed values, with mean 155.34, sample SD 216.57, median 72.02 and range 0.00–1407.51.",
            "The table also reports the interquartile interval. Its scope differs explicitly from the 3,624 hours used for the primary forecast scores. We identify the series as API-derived estimates rather than authenticated station measurements, so these summaries describe the supplied series and should not be treated as an independently verified description of Beijing exposure."
        ],
        "locations": ["subsec:impl_data", "tab:descriptive", "Limitations, pp. 21–22"]
    },
    "R2.M1": {
        "paragraphs": [
            "We have followed the proposed route of consistently restricting claims to Perfect Prognosis. We have not added an experiment with forecast-origin gas inputs and do not imply that such an operational experiment has been performed. The information set and the distinction between future covariates and withheld future targets are now explicit.",
            "The title uses 'Adaptive' in place of 'Operational', and the Abstract, contributions, Discussion and Conclusion describe a retrospective conditional comparison of the three model families. We explain when accurate external gas forecasts might approximate this setting and why their errors would require separate evaluation. Operational skill and validation against independently verified station targets remain untested."
        ],
        "locations": ["Title and Abstract, p. 1", "Introduction, p. 2", "sec:methodology", "Discussion, Limitations and Conclusion, pp. 21–22"]
    },
    "R2.M2": {
        "paragraphs": [
            "We now report the requested coordinate (39.906217, 116.3912757), the CSV coordinate (39.9062, 116.3913), and the source endpoints: OpenWeather's /data/2.5/air_pollution/history and Open-Meteo's /v1/era5 archive endpoint. The source has 39,523 unique hourly rows from 25 November 2020 01:00 to 29 June 2025 19:00. The regular calendar has 40,267 hours, with 744 missing timestamps across 21 intervals. Training ends on 13 January 2025 00:00; testing starts at 01:00. Training/test counts are 36,240/4,027 calendar hours and 35,736/3,787 observed targets.",
            "The primary evaluation uses 23 weekly origins and 3,624 shared observed hours and ends on 23 June 2025 00:00. The final 163-hour calendar remainder is excluded from fixed 168-hour scoring. Four partial weeks are explicitly counted. The January–June period cannot support year-round conclusions.",
            "Some requested provenance cannot be recovered. UTC interpretation is supported by the extraction and provider defaults, but original response archives and retrieval dates are unavailable. Positional pollutant-field extraction cannot be independently authenticated, and the source starts before the provider-documented historical start. We disclose these unresolved limitations rather than invent retrieval metadata. The series is explicitly described as API-derived model/gridded estimates, not station ground truth."
        ],
        "locations": ["subsec:impl_data", "subsec:impl_evaluation", "tab:descriptive", "Limitations, pp. 21–22"]
    },
    "R2.M3": {
        "paragraphs": [
            "The audit found that the original notebook's global upper-tail row filtering did not match the manuscript's winsorization description. We have corrected this mismatch and repeated the revised primary experiments using all original observed target values, without positive target clipping or outlier removal. Four invalid −9999 predictor cells in training (two NO2, one O3 and one PM10) are masked as missing in a working copy; the raw file, PM2.5 targets and valid negative weather values are preserved. Affected predictor analysis, validation and fitting were repeated.",
            "A separate control clips predictors only at training-derived 1st/99th percentiles and scores against unchanged test targets. Clipping increases frozen MAE for all three families. We also report the 158 scored high-concentration hours above the training 95th percentile, 691.34 micrograms per cubic metre: frozen seed-42 NeuralProphet MAE is 32.32, versus 51.02 for SARIMAX and 50.60 for Prophet. These events span only six weeks, so the subset cannot establish general performance on extremes."
        ],
        "locations": ["subsec:impl_data", "Lead time, concentration, and sensitivity, pp. 17–18", "tab:controls", "Limitations, pp. 21–22"]
    },
    "R2.M4": {
        "paragraphs": [
            "We have added last-observed-value, daily seasonal-persistence and weekly seasonal-persistence references on the same 3,624 scored hours. Their pooled MAEs are 125.74, 121.52 and 152.90, respectively. Missing historical context is handled by the documented causal filling policy, while the last-value reference uses the latest genuinely observed target. No future target is used to construct a reference forecast.",
            "All primary SARIMAX refits now complete the same 23 origins as Prophet and NeuralProphet, resolving the original 21-versus-23-week mismatch. We have narrowed comparative claims to the three evaluated families and these references rather than claiming superiority over advanced architectures. Target-only references lack the actual future gases supplied to the main models; no-input model controls and this information disadvantage are explicitly reported."
        ],
        "locations": ["subsec:impl_data", "subsec:impl_evaluation", "tab:regime1_results", "tab:controls", "Discussion and future work, p. 21"]
    },
    "R2.M5": {
        "paragraphs": [
            "A bounded chronological validation within training now compares four SARIMAX differencing combinations, additive/multiplicative Prophet seasonality and 30/50 NeuralProphet epochs over four weekly origins. Selection uses mean weekly MAE and pooled RMSE as tie-breaker. Seven of eight candidates complete. The selected settings are (1,0,1) × (1,0,1,24), additive Prophet and 50-epoch NeuralProphet, with the remaining explicit settings reported in Table 4. This replaces an unexplained configuration choice with reproducible screening, while acknowledging that the grid and winter validation period are limited.",
            "NeuralProphet uses global normalization learned from pre-origin complete episodes, 168 lags and 168 direct leads, batch size 128 and learning rate 0.001. Finite losses, retained episode/sample counts, timestamps and lead extraction were checked, including prevention of samples crossing missing intervals. Seeds 42, 123 and 2026 are reported separately and summarized. These checks support correct execution and alignment; completing epochs does not prove optimization convergence to a global optimum. The remaining seed variation is reported without interpreting it as inherent architectural inferiority."
        ],
        "locations": ["subsec:impl_data", "subsec:impl_models", "tab:configuration", "tab:seeds", "Limitations, pp. 21–22"]
    },
    "R2.M6": {
        "paragraphs": [
            "'Frozen' now explicitly means fixed model parameters and the initial predictor scaler, with refreshed pre-origin state/context. SARIMAX filters newly revealed history without parameter fitting; NeuralProphet receives the latest 168-hour target context, including documented causal filling where history is missing; Prophet uses the actual future dates and Perfect Prognosis covariates. Walk-forward refits re-estimate parameters and transformations from expanding pre-origin history.",
            "Table 5 gives the weekly pseudocode and Figure 1 the workflow. The already available bias is added before the current week's targets are revealed. After the week, the correction is updated from observed base residuals only. No fitting or scoring target is imputed. The same forecast origins and observed-hour scoring mask are used throughout."
        ],
        "locations": ["subsec:regimes", "subsec:impl_data", "subsec:impl_regimes", "tab:pseudocode", "fig:framework", "eq:ewma"]
    },
    "R2.M7": {
        "paragraphs": [
            "We agree that high target association is relevance, not evidence of redundancy between predictors. The revised manuscript reports training-only Pearson and continuous mutual-information rankings on 35,732 complete rows. Continuous MI uses the nearest-neighbor estimator with seed 42. Descriptive mRMR uses MIQ on a target-first input table, with training-only quintile discretization of the target and candidates, removal of duplicate bin edges and five requested predictors. Its first five are PM10, dew point, NO2, NO and CO.",
            "The four gases are now described as a predefined study subset retained from the original experiment, not an optimal mRMR selection. Frozen no-input and nine-input controls retain the selected model settings. Broad inputs add O3, NH3, temperature, dew point and PM10; Prophet/NeuralProphet pooled MAEs improve to 15.87/22.35, with actual future PM10 providing additional information. No-input MAEs are 115.24, 134.07 and 119.50 for SARIMAX, Prophet and NeuralProphet.",
            "The broad-input SARIMAX control did not converge in either bounded attempt and has no accepted score. We disclose this incomplete control rather than infer a complete broad-input family ranking. The controls do not establish optimal predictor subsets or separately tuned model performance."
        ],
        "locations": ["subsec:impl_feature_selection", "tab:features", "fig:corr_heatmap", "fig:mi_bar", "tab:controls", "Limitations, pp. 21–22"]
    },
    "R2.M8": {
        "paragraphs": [
            "We now describe EWMA as an established bias-tracking method applied within the evaluation, not a new algorithm. α=0.3 remains predefined; sensitivities cover 0.1, 0.2, 0.5, 0.7 and 1.0, where 1.0 is the previous-week mean-residual correction. The available bias is applied before outcomes and updated afterwards using that week's observed base residual mean. Partial weeks update only from their observed scoring hours.",
            "The corrected experiments do not reproduce a uniform worsening for NeuralProphet. Mean weekly MAE reductions at α=0.3 are 14.83 and 13.53 for seeds 42/123, while seed 2026 worsens by 0.59. SARIMAX and Prophet reductions are 0.49 and 6.13. Figure 9 shows base residuals, the previously available bias and weekly benefits; the sensitivity text explains that tracking persistent offsets can help, while subsequent level changes can cause overcorrection. The previous-week alternative is not uniformly worse: for example, it benefits Prophet but worsens SARIMAX relative to no correction. We do not claim exponential smoothing always dominates it or select α from test performance."
        ],
        "locations": ["eq:residual", "eq:corrected", "eq:ewma", "subsec:impl_regimes", "tab:seeds", "Lead time, concentration, and sensitivity, pp. 17–18", "fig:correction"]
    },
    "R2.M9": {
        "paragraphs": [
            "We have separated pooled hourly MAE/RMSE from equally weighted mean weekly MAE/RMSE. Each main table reports both aggregations and weekly sample SD. This distinction matters with partial weeks, and mean weekly RMSE is not mathematically equivalent to pooled RMSE.",
            "Figures 4–6 cover weekly error distributions and chronology; Figures 7 and 8 report errors by each of the 168 hourly leads and by forecast day, with matched observed-hour counts. Paired weekly differences use 2,000 moving-block bootstrap replicates with three-week blocks and two-/four-week sensitivities. NeuralProphet contrasts average seed-level weekly losses, not predictions. We state the short-series and multiple-comparison limitations and distinguish seed variation from temporal variability. For example, the seed-averaged correction interval excludes zero with three-week blocks but includes it with four-week blocks; this prevents an unqualified significance claim."
        ],
        "locations": ["subsec:evaluation", "subsec:impl_evaluation", "tab:regime1_results", "tab:regime2_results", "tab:paired", "fig:regimes", "fig:chronology", "fig:weekly_distribution", "fig:lead_hour", "fig:lead_day"]
    },
    "R2.M10": {
        "paragraphs": [
            "We now show initial frozen-fit SARIMAX/Prophet coefficients, selected raw-unit stability ranges across 23 refits, and frozen Prophet trend/seasonal/regressor summaries weighted equally over scored hours. We explain conditioning, correlated gases and cancellation of signed components, and avoid causal or independent-importance interpretations.",
            "The Implementation section identifies the CPU, reported system RAM, two configured threads, software versions and absence of GPU use. Table 12 distinguishes optimization-only SARIMAX timings from Prophet/NeuralProphet timings including initialization/import; preprocessing and prediction are recorded separately and excluded from that table. Isolated correction arithmetic is approximately 0.002 seconds per complete stream, excluding fitting, file I/O and plotting. Sampled process-tree memory and recorded attempt time are qualified rather than treated as total project cost.",
            "All revised primary SARIMAX fits completed. The original memory failure is acknowledged here as implementation/environment-specific, while the revised manuscript avoids generalizing it to the model family. Different timer boundaries prevent a controlled speed-ratio claim."
        ],
        "locations": ["Implementation, pp. 7–8", "tab:effects", "tab:timing", "Model interpretation and computational measurements, pp. 18–21", "Discussion and Limitations, pp. 21–22"]
    },
    "R2.M11": {
        "paragraphs": [
            "We have assessed and incorporated four substantively relevant suggested studies: the wavelet/feature-optimization Bi-LSTM study (10.1371/journal.pone.0330465), winter temporal transfer with multi-head attention (10.1038/s41598-025-16664-4), spatial–temporal attention ConvLSTM multi-step forecasting (10.1109/ACCESS.2024.3509142), and centralized cross-pollutant transfer and attention (10.1088/2631-8695/ae2826). Related work and Table 1 discuss their distinct roles in multi-station representation, feature optimization, attention, transfer and interpretation. Existing distributed/federated-learning literature is retained; the optional fifth suggested citation is not added solely to expand the bibliography.",
            "We position our contribution as a comparison of parameter updating and scalar bias correction within three established families, with explicit computational boundaries and conditional fitted interpretations. The single-location, 168-hour Perfect Prognosis evaluation differs from the cited spatial, seasonal and transfer protocols. We make no numerical ranking across different datasets or claim superiority over those architectures."
        ],
        "locations": ["Related work, pp. 3–4", "tab:lr", "Discussion and future work, p. 21", "References, pp. 22–25"]
    },
    "R2.m1": {
        "paragraphs": [
            "The SARIMAX equation, now Eq. (3), is rewritten in multiplicative lag-polynomial form with separate seasonal/nonseasonal autoregressive and moving-average factors and differencing operators acting on the regression residual. The polynomial products retain cross terms. Implementation specifies the selected p=q=P=Q=1, d=D=0, s=24 and no constant, matching the fitted revised specification rather than implying differencing that was not used."
        ],
        "locations": ["eq:sarimax", "subsec:impl_models", "tab:configuration"]
    },
    "R2.m2": {
        "paragraphs": [
            "We have replaced the one-step wording with an origin-/lead-indexed multi-step residual. Equation (7) defines the observed target minus its base prediction for week w and lead h. Equations (8) and (9) then apply the previously available scalar bias to all leads and update it from the completed week's observed base residual mean. The 168-hour horizon is specified in Implementation."
        ],
        "locations": ["eq:residual", "eq:corrected", "eq:ewma", "subsec:impl_evaluation"]
    },
    "R2.m3": {
        "paragraphs": [
            "We have removed the unsupported promise of Kalman bias-correction implementation details and state that no separate Kalman bias-correction alternative is evaluated. SARIMAX's standard state filtering remains part of the frozen-model forecasting protocol; it is distinct from adding a separate bias-correction algorithm. The evaluated correction is the explicitly defined EWMA procedure."
        ],
        "locations": ["subsec:impl_regimes", "eq:ewma", "tab:pseudocode"]
    },
    "R2.m4": {
        "paragraphs": [
            "We have replaced the selected best-/worst-week illustrations with summaries covering every evaluation week: chronological frozen versus refitted weekly errors, the frozen-model chronology, and base versus corrected distributions. Hourly/day lead-time plots and correction diagnostics supplement these summaries. Captions identify the actual regime, seed and observed-hour coverage; selected weeks are no longer used as evidence of stability."
        ],
        "locations": ["fig:regimes", "fig:chronology", "fig:weekly_distribution", "fig:lead_hour", "fig:lead_day", "fig:correction"]
    },
    "R2.m5": {
        "paragraphs": [
            "The reviewer is correct that the displayed original subtraction gives 7.94 rather than 7.93. The original claim has been superseded by the corrected reruns, and we have not retained either obsolete reduction. All revised differences are computed from saved full-precision errors and displayed consistently to two decimals, with pooled and weekly differences identified separately.",
            "For Prophet, the revised pooled frozen MAE changes from 43.93 to 37.69; the full-precision reduction rounds to 6.24. The equally weighted mean weekly reduction is 6.13. These are different aggregations, not an attempt to reconcile them through rounding."
        ],
        "locations": ["tab:regime2_results", "tab:paired", "subsec:evaluation", "subsec:impl_evaluation"]
    },
    "R2.m6": {
        "paragraphs": [
            "The revision code and saved results are versioned locally. The package separates preprocessing/validation, fitting and saved-forecast analysis, documents dependencies and seeds, and includes a presentation notebook and table/figure generation scripts. The current environment's execution and saved-evidence checks have completed; we do not claim a fresh clean-environment reproduction or a published corrected release has already occurred.",
            "The existing GitHub repository link is retained in Code availability. A DOI-linked versioned archive, a defensible data-availability statement and clean-environment reproduction remain to be finalized. This response is therefore provisional on the release requirement, as is our response to editorial requirement E4."
        ],
        "locations": ["Implementation, pp. 7–8", "subsec:impl_models", "Data and Code availability, p. 26"],
        "pending": "Before submission: finalize the versioned public code/data release, DOI, availability wording and clean-environment reproduction."
    },
    "E1": {
        "paragraphs": [
            "We have revised all result-dependent claims using the corrected matched 23-week evidence, preserved original observed targets and completed the primary SARIMAX run. Perfect Prognosis, API-derived targets, missing provenance, partial coverage, bounded validation, seed variability, the failed broad-input control and uncertainty/timing limitations are now explicit. Operational readiness, optimal-subset and general architecture-superiority claims have been narrowed."
        ],
        "locations": ["Abstract, p. 1", "Results, pp. 14–21", "Discussion, Limitations and Conclusion, pp. 21–22"]
    },
    "E2": {
        "paragraphs": [
            "This document reproduces and responds individually to all 10 Reviewer 1 comments, all 11 major and six minor Reviewer 2 comments, and the editorial requirements. Each reply identifies the change or remaining limitation and its location in revised v1. Shared work is explained under each relevant point, including the completed common-period comparison. Release-related requirements remain visibly pending rather than being described as fulfilled."
        ],
        "locations": ["This response document; revised v1 throughout"]
    },
    "E3": {
        "paragraphs": [
            "We have shortened and refocused Related work, reduced repetitive claims and replaced selected-week illustrations with all-week summaries. Methodology explains the general methods; exact preprocessing, model settings and evaluation choices are consolidated in Implementation. The original journal LaTeX class and bibliography style are preserved. Yellow highlighting identifies changed text, equations, tables, captions, figures and new references in the accompanying manuscript."
        ],
        "locations": ["Related work, Methodology and Implementation, pp. 3–14", "Discussion, Limitations and Conclusion, pp. 21–22"]
    },
    "E4": {
        "paragraphs": [
            "This requirement is not yet complete. The existing GitHub link identifies the project repository, but does not meet the editor's separate DOI-archive requirement. The corrected code is versioned locally and can be prepared for deposit; no published archive or DOI is claimed. Code availability currently contains an author-input placeholder. The final response must identify the deposited version and its actual DOI after the archive is reviewed and published."
        ],
        "locations": ["Code availability, p. 26"],
        "pending": "Author decision required: provide an existing DOI record, or select the DOI-assigning repository for a reviewed versioned deposit."
    },
    "E5": {
        "paragraphs": [
            "A separately maintained, yellow-highlighted revised manuscript and this point-by-point response have been prepared for supervisor/author review. They have not been submitted to the journal. After author review, the archive and availability requirements must be completed, manuscript locations refreshed for any edits, and both final PDFs checked before submission."
        ],
        "locations": ["Revised v1 manuscript and this response document"],
        "pending": "Before submission: resolve the marked release items and obtain author approval of the final manuscript and response."
    },
}
