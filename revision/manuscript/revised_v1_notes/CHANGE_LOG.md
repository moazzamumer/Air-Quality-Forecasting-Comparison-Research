# Revised v1 change ledger

Baseline: original Environmental Modeling & Assessment submission, preserved byte-for-byte. Working copy: `../revised_v1/`. Moazzam approved Phase 4A and authorized Phase 4B on 1 October 2026; he subsequently supplied four literature PDFs and authorized inclusion according to relevance. All four were included with distinct purposes.

The manuscript retains the original author details, Springer Nature class, numbered reference style, top-level scientific section sequence, and flat Fig1–Fig9 layout. The introduction opening and author-supplied declarations are preserved where applicable. Changed prose/equations/tables, new headings/citations and new reference entries are yellow; replaced figures have yellow frames and captions. Deleted passages are recorded here rather than displayed as strikethrough in the paper. The proposed title changes one word, Operational → Adaptive, to narrow its implications; author review of the title remains welcome.

The corrected 23-week package is the primary evidence. The 16-week complete-context analysis remains secondary. No new fitting, test-based selection or numerical experimentation was performed for this draft. Main tables, feature ranks and coefficients are populated from saved evidence; updated plots use approved data or saved metrics. The raw source, previous notebook, earlier results, and original manuscript are untouched.

| Point | Draft treatment | Manuscript location | Status / remaining work |
| --- | --- | --- | --- |
| R1.1 | Replaced incomplete 21-week comparison with completed, matched 23-origin results; disclosed partial scoring coverage. | Results opening; Regime 1; Table 6; data assembly | Draft incorporated; response verification pending. |
| R1.2 | Restricted claims to Perfect Prognosis; explained external forecast approximation and untested operational inputs. | Abstract; Methodology; Discussion; Conclusion | Draft incorporated. |
| R1.3 | Initial scaled-input coefficients, raw-unit refit stability examples, and hourly-weighted Prophet components. | Model interpretation; Table 11 | Draft incorporated; associations explicitly noncausal. |
| R1.4 | Documented target normalization, contiguous episodes, forecast extraction checks, seed-dependent errors and high-event reversal. | Models/configuration; seed/concentration results; Table 9 | Draft incorporated; explanations remain tentative. |
| R1.5 | Four chronological validation weeks, bounded order grid, selection criterion, excluded failed candidate and fixed selected settings. | Model configuration; Table 5 | Draft incorporated. |
| R1.6 | CPU-only hardware/software and separate fit/preparation/prediction boundaries; no incompatible speed ratio. | Implementation; computational measurements; Table 12 | Draft incorporated. |
| R1.7 | Predefined alpha and sensitivity including previous-week residual mean; mixed correction benefits. | Frozen regime; sensitivity results; Fig. 9 | Draft incorporated; alpha not selected using test score. |
| R1.8 | Both pooled and equally weighted weekly mean errors with weekly sample SD; matched temporal-block intervals. | Evaluation/statistics; Tables 6–8; Figs. 4–6 | Draft incorporated; intervals descriptive. |
| R1.9 | Shortened literature table and narrative; removed repetitive deployment claims and six selected best/worst figures. | Related work; Discussion/Conclusion; figure replacements | Draft incorporated; density still requires author review. |
| R1.10 | Original train/test target counts, mean, SD, median, quartiles and full range. | Data assembly; Table 3 | Draft incorporated; units and partition scope explicit. |
| R2.M1 | Consistent conditional information set and narrower operational claims; no new operational scenario. | Abstract; Methodology; Discussion/Conclusion | Draft incorporated, follows approved PP-only route. |
| R2.M2 | Exact coordinates/endpoints/calendar bounds/counts/missingness/tail; time-zone evidence and unrecoverable provenance limitations. | Preprocessing; data assembly; Limitations | Draft incorporated; retrieval archives/dates and field mapping remain unavailable. |
| R2.M3 | Original target preserved; invalid predictor masking and train-only predictor clipping separated; high-event results reported. | Preprocessing; concentration/control results; Limitations | Draft incorporated. Prior notebook/text mismatch belongs in response history, not final scientific prose. |
| R2.M4 | Three persistence references and input ablations on common hours; all primary SARIMAX origins completed; information disadvantage stated. | Evaluation; Regime 1; Table 10 | Draft incorporated; no broad architecture superiority claim. |
| R2.M5 | Training-only screening and selected configuration, normalization/episodes/finite-loss/extraction checks and three seeds. | Model configuration; Table 5; Table 9 | Draft incorporated; neither exhaustive search nor global optimality claimed. |
| R2.M6 | Fixed parameters versus refreshed state/context; pre-origin information and apply-before-observe correction sequence. | Regimes; Table 2; Fig. 1 | Draft incorporated. |
| R2.M7 | Continuous correlation/MI ranks, MIQ with quintiles and target-first schema, predefined gas subset, broader/no-input controls. | Predictor analysis; Table 4; Table 10 | Draft incorporated; no optimal-subset claim; failed broad SARIMAX disclosed. |
| R2.M8 | Established EWMA mechanism, observed-hour residual mean, alpha grid, previous-week baseline and mixed seed benefits. | Frozen regime; correction/seed/sensitivity results | Draft incorporated. |
| R2.M9 | Explicit pooled versus mean weekly RMSE, temporal dispersion, paired block intervals and hourly/day leads. | Evaluation/statistics; Tables 6–8; Figs. 7–8 | Draft incorporated. |
| R2.M10 | Conditional coefficients/components and fit-specific aggregation, stability examples, resources/timing limits. | Interpretation/computational measurements; Tables 11–12 | Draft incorporated. Earlier memory failure is addressed in response history rather than generalized in the paper. |
| R2.M11 | All four supplied relevant papers assessed and critically positioned; existing federated-learning reference retained. | Related work; Table 1; Discussion; references | Draft incorporated; see LITERATURE_DECISION.md. |
| R2.m1 | Multiplicative SARIMAX equation matches d=D=0, selected orders, regression errors and cross terms. | Equation 3; SARIMAX subsection | Draft incorporated. |
| R2.m2 | Replaced one-step residual by week/origin/lead-indexed multi-step error. | Equation 7; frozen regime | Draft incorporated. |
| R2.m3 | Removed unsupported Kalman bias-correction implementation promise. | Frozen regime | Draft incorporated. SARIMAX state filtering remains distinct from a separate bias algorithm. |
| R2.m4 | Replaced selected best/worst examples with all-week summaries and lead-time/correction diagnostics. | Figs. 4–9 | Draft incorporated; captions specify actual streams and coverage. |
| R2.m5 | Replaced obsolete error-reduction figures with regenerated full-precision sources and consistent two-decimal display. | Tables 6–10; main result text | Draft incorporated; pooled and weekly differences distinguished. |
| R2.m6 | Code/dependencies/seeds and evidence already versioned locally; manuscript release statements not fabricated. | Availability statements | Pending DOI archive, clean-environment reproduction and final release. |
| E1 | Revised all result-dependent claims and explicit limitations from the corrected evidence. | Throughout | Draft prepared; final author/content verification pending. |
| E2 | Every reviewer point linked individually to draft treatment in this ledger. | This file; reviewer tracker | Point-by-point response PDF remains Phase 5; no point closed here. |
| E3 | Shortened/restructured text while retaining original journal template and baseline voice. | Throughout | Author review pending. |
| E4 | DOI-linked code release required by editor is visibly marked pending, not represented as already public. | Code availability | Author repository/record decision required. |
| E5 | Highlighted manuscript PDF prepared in separate directory. | manuscript.pdf | Author inputs, response PDF and final submission checks pending. |

All locations refer to revised v1, not the original submission. The manuscript itself cites academic tables, figures and references rather than local evidence paths. Final response page/line references must be regenerated after author changes. No reviewer point is marked closed solely because a draft paragraph exists.
