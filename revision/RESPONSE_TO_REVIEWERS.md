# Response to reviewers — working scaffold

Manuscript: Interpretable PM2.5 Forecasting for Urban Air Quality: A Comparative Study of Operational Time-Series Models

Journal: Scientific Reports. Decision: Major Revision.

Status: incomplete planning scaffold. Bracketed fields must be replaced with verified facts before PDF generation. Do not submit this version.

The response will explain revisions individually and identify manuscript locations. Do not write that an experiment was performed, an error was resolved, or a DOI was deposited until the tracker contains the evidence. If results or configurations change, state that transparently.

## Reviewer 1

### R1.1

> The SARIMAX walk-forward run stops at week 21 of 23 because increasing memory usage prevented completion in the available computing environment, yet the abstract, Results and Discussion often present it alongside the two fully completed models (Prophet, NeuralProphet) without flagging this difference. Please state explicitly, wherever SARIMAX walk-forward performance is mentioned, that the reported MAE/RMSE are cumulative over 21 of 23 weeks, and avoid phrasing that implies a like-for-like comparison with the complete runs. This is not a fatal flaw, but as written it could mislead readers about the comparability of the three models under this regime.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.2

> The Perfect Prognosis setting is used as an experimental simplification, with future values of the exogenous gases (NO, NO₂, CO, SO₂) supplied from the held-out test segment. In real deployment, these values would not normally be available as "observations" at the time of forecasting. Please add a short paragraph clarifying when this assumption reasonably approximates practice and when it remains an idealisation, so readers can properly calibrate the operational claims in the abstract and conclusion.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.3

> Interpretability claims. The manuscript repeatedly calls Prophet and SARIMAX "interpretable," but does not show what the exogenous drivers (NO, NO₂, CO, SO₂) actually contribute inside the fitted models. If available from the fitted models, please report, even briefly, the SARIMAX β coefficients and/or Prophet regressor effect sizes; otherwise, please moderate the interpretability claim. If estimates are reported, specify the relevant fitted model or aggregation procedure.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.4

> NeuralProphet's performance deserves a fuller explanation. Please expand this briefly with a diagnosis of possible causes, clearly distinguishing documented results from tentative explanations.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.5

> SARIMAX order selection. The order (1,1,1) and seasonal order (1,1,1,24) are stated in 4.3.1 but the manuscript does not indicate how they were chosen criterion search or fixed a priori from the known 24-hour cycle. Please clarify the selection procedure, since this affects how the SARIMAX–Prophet comparison should be read.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.6

> It is not stated whether SARIMAX (statsmodels) and Prophet also ran with any hardware acceleration. Since these are typically CPU-bound implementations, please confirm the computing setup used for each model, so that the reported execution-time differences (Tables 2–3) can be attributed to the models themselves rather than partly to the hardware.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.7

> Sensitivity of the residual-correction mechanism. The EWMA bias correction uses a fixed smoothing factor (α = 0.3) throughout the manuscript. Please state whether nearby values of α were tried and, if so, whether they produced qualitatively similar conclusions. If not, acknowledge the absence of this sensitivity analysis as a limitation.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.8

> Figure 1 lists "MAE, RMSE (Mean ± Std)" as part of the evaluation protocol, but Tables 2 and 3 report only the mean MAE/RMSE, with no accompanying measure of dispersion across the 23 weekly windows. Given that week-level MAE varies considerably for every model, please report the standard deviation or interquartile range of the weekly errors alongside each mean, so that comparisons between models — such as the corrected SARIMAX vs. Prophet result in Table 3 — can be assessed against this variability rather than as single point estimates. A paired comparison across the matched weekly windows would also help support the model ranking.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.9

> Manuscript length and density. At its current length, the manuscript is considerably longer than the journal's suggested format, and this affects readability. The Related Work section in particular could be shortened substantially without losing its core message. Similarly, the Discussion, Limitations and Conclusion sections partly repeat the same points and could be consolidated into fewer, more tightly written paragraphs.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R1.10

> Descriptive information on the PM2.5 series: Consider adding a brief descriptive summary of the PM2.5 series, including the mean and a clearly defined measure of range or variability, so that readers unfamiliar with Beijing's pollution levels can judge the practical magnitude of the reported MAE/RMSE values.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

## Reviewer 2 — major comments

### R2.M1

> Forecasting assumptions and operational relevance
> Sections 3–4 explicitly assume that the actual future values of NO, NO2, CO, and SO2 are available throughout each 168-hour forecast window. This is a legitimate Perfect Prognosis experiment, but it does not establish performance under realistic operational conditions. The authors should either add an experiment using predictors available at the forecast origin or consistently restrict their claims to the Perfect Prognosis setting. The Abstract and Conclusion currently overstate readiness for real-world deployment.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M2

> Dataset provenance and evaluation coverage
> Please report the geographic coordinates, specific API endpoints, retrieval dates, time zone, exact date boundaries, and total observation counts. Provide the training and test dates, the number of evaluated hours, and the handling of any incomplete final weekly window. Because the target comprises model-based gridded estimates rather than direct station measurements, this distinction and its implications for validation should be emphasized. The approximately 23-week test period also limits conclusions about year-round performance.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M3

> Winsorization and evaluation of pollution extremes
> Sections 3.1 and 4.1 describe percentile-based clipping, but it is unclear whether the held-out PM2.5 target was also clipped. Please specify which variables and data partitions were transformed. Performance should be reported against the original, unclipped test target, since high pollution concentrations may represent genuine events rather than measurement errors. A sensitivity analysis without winsorization would help establish whether the conclusions depend on suppressing extremes.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M4

> Benchmark adequacy and fair comparison
> Include persistence and seasonal-persistence baselines to demonstrate forecasting skill beyond simple reference methods. Claims of competitiveness against more advanced approaches should either be supported by an appropriate additional comparator under the same protocol or narrowed to the three evaluated model families. Furthermore, Table 2 compares SARIMAX over 21 weeks with the other models over 23 weeks. Please provide a common-period comparison for all models and, if possible, complete the SARIMAX evaluation.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M5

> Model selection and NeuralProphet performance
> Please justify the SARIMAX orders, Prophet configuration, and NeuralProphet training settings using a time-ordered validation procedure within the training data. The unusually large NeuralProphet errors warrant checks of training convergence, normalization, forecast–target alignment, and the extraction of its 168-step predictions. Report repeated runs with different seeds where relevant. The present results should not be interpreted as demonstrating an inherent weakness of NeuralProphet without these checks.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M6

> Frozen-model forecasting protocol
> Clarify whether “frozen” means fixed parameters only or also a fixed internal model state. For each weekly forecast origin, specify whether SARIMAX incorporates newly observed target values through state updating and whether NeuralProphet receives the latest 168 observed target values. Provide concise pseudocode showing the information available to each model and when residual correction is applied. This distinction is essential for reproducibility and fair comparison.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M7

> Feature-selection procedure
> Report the correlation and mutual-information rankings, mRMR configuration, any discretization, and the rule used to select four predictors. The exclusion of PM10 because it is strongly associated with the target requires clearer justification: relevance to the target is not the same as redundancy among predictors. An ablation comparing the selected subset with a broader predictor set and a model without exogenous inputs would clarify the value of feature selection.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M8

> Residual correction and sensitivity analysis
> The fixed EWMA smoothing parameter, α = 0.3, requires justification. Please provide a sensitivity analysis or select this parameter using historical validation data only. Comparison with a simple previous-week mean-residual correction would help establish the benefit of exponential smoothing. The authors should also explain why correction improves Prophet and SARIMAX but worsens NeuralProphet, using residual-bias patterns rather than speculation. EWMA correction should be positioned as an established technique applied within this evaluation, unless a distinct methodological innovation is demonstrated.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M9

> Performance aggregation and uncertainty
> Sections 3.5–3.6 describe averaging weekly metrics, whereas the tables label them as overall MAE and RMSE. Please distinguish mean weekly RMSE from pooled RMSE across all forecasted hours, as these are not equivalent. Report weekly error distributions and uncertainty around paired performance differences using an approach that respects temporal dependence. Also provide performance by forecast lead time, because an aggregate 168-hour score can conceal deterioration at longer horizons.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M10

> Interpretability and computational claims
> Interpretability is central to the title but is not demonstrated sufficiently through the reported results. Please present relevant model components, regressor effects, or other interpretable outputs and discuss their stability and limitations without treating associations as causal effects. For runtime comparisons, report CPU, system RAM, software versions, actual GPU use, and whether training, preprocessing, and prediction are included. The SARIMAX memory failure should be described as an observation in the specific implementation and environment rather than a general property of the model.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.M11

> Recent literature and positioning
> The literature review should more clearly position this work against recent particulate-matter prediction research involving multi-station modelling, advanced temporal learning, attention mechanisms, feature optimization, interpretability, and distributed learning. Where directly relevant, the authors may consider the following suggested studies, or suitable alternatives: 10.1371/journal.pone.0330465, 10.1038/s41598-025-16664-4, 10.1109/ACCESS.2024.3509142, 10.1088/2631-8695/ae2826, and 10.1016/j.rineng.2026.111937.
> The purpose should be critical positioning, not merely expanding the reference list. Explain what the present comparison contributes regarding adaptation, computational cost, and interpretability, while distinguishing its single-city Perfect Prognosis setting from other forecasting protocols. Numerical results from different datasets should not be presented as directly comparable. These specific citations are optional and should be included only when substantively relevant.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

## Reviewer 2 — minor comments

### R2.m1

> Revise Equation (4) to accurately represent the implemented seasonal and non-seasonal differencing and multiplicative SARIMAX structure.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.m2

> Equation (8) describes a “one-step residual,” although the evaluation uses 168-step forecasts. Please correct this terminology.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.m3

> Remove the statement that Kalman-filter implementation details are provided unless this alternative is actually described and evaluated.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.m4

> Supplement the best- and worst-week figures with a summary covering all evaluation weeks; these selected examples alone do not establish stability.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.m5

> Reconcile the reported Prophet MAE reduction of 7.93 with the displayed values, 45.61 − 37.67 = 7.94, or explain rounding from unrounded results.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

### R2.m6

> Provide a versioned code release, dependency specifications, seeds, data-processing instructions, and scripts reproducing each table and figure.

**Response:** [Describe the completed action and relevant finding. If not fully addressed, explain precisely why and what evidence or limitation is supplied.]

**Evidence:** [Verified artifact/table/figure; link to tracker entry.]

**Manuscript changes:** [Section and final page/line references; brief changed-text excerpt where useful.]

## Editorial requirements

### E1

> Please ensure the results are accurately reported, any overstated conclusions are rewritten and the limitations of the work fully explained.

**Response:** [Verified action, resulting artifact and manuscript location. For E4 insert the actual published version DOI.]

### E2

> Revise the manuscript thoroughly, addressing each reviewer comment.

**Response:** [Verified action, resulting artifact and manuscript location. For E4 insert the actual published version DOI.]

### E3

> Improve clarity, structure, and language where necessary.

**Response:** [Verified action, resulting artifact and manuscript location. For E4 insert the actual published version DOI.]

### E4

> Please note that if your manuscript uses any custom or bespoke computational tool or code, or reports a new algorithm, tool, software, or a pipeline (even if individual components are not new), the underlying code must be deposited in a recognised DOI-assigning repository (e.g. zenodo) and linked either from Methods or a dedicated Code Availability section.

**Response:** [Verified action, resulting artifact and manuscript location. For E4 insert the actual published version DOI.]

### E5

> When your revision is ready, please submit the updated manuscript and a point-by-point response.

**Response:** [Verified action, resulting artifact and manuscript location. For E4 insert the actual published version DOI.]
