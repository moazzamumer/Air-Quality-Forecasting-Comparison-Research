"""Assemble revised v1 from the preserved template and approved corrected evidence.
No model fitting or numerical selection occurs in this script.
"""
from pathlib import Path
import csv,json,hashlib,re
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'PM_Forecasting_Environmental_Modeling_Assessment_Submission'
DEST=ROOT/'revision/manuscript/revised_v1'
EVID=ROOT/'revision/corrected/artifacts'
NOTES=Path(__file__).parent
original=(BASE/'manuscript.tex').read_text()
parts=[]
def raw(s):parts.append(s.strip()+'\n\n')
def P(s):raw('\\rev{'+s.strip()+'}')
def section(title,label=None,level='section'):
 heading=title
 if ('\\'+level+'{'+title+'}') not in original:
  heading=r'\texorpdfstring{\rev{'+title+'}}{'+title+'}'
 raw('\\'+level+'{'+heading+'}'+('\\label{'+label+'}' if label else ''))
def eq(s,label):raw('\\begin{equation}\n\\revmath{'+s+'}\n\\label{'+label+'}\n\\end{equation}')
def fig(n,caption,label):
 raw(r'\begin{figure}[htbp]'+'\n'+r'\centering'+'\n'+r'\fcolorbox{yellow}{white}{\includegraphics[width=0.96\linewidth,keepaspectratio]{Fig'+str(n)+r'.png}}'+'\n'+r'\caption{\rev{'+caption+'}}\n'+r'\label{'+label+'}\n'+r'\end{figure}')
def table(caption,label,header,rows,align):
 raw(r'\begin{table}[htbp]'+'\n'+r'\caption{\rev{'+caption+'}}\n'+r'\label{'+label+'}\n'+r'\begingroup\small\setlength{\tabcolsep}{4pt}\rowcolors{1}{yellow}{yellow}'+'\n'+r'\begin{tabularx}{\linewidth}{@{}'+align+r'@{}}'+'\n'+r'\toprule'+'\n'+' & '.join(header)+r' \\'+'\n'+r'\midrule'+'\n'+'\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n'+r'\botrule'+'\n'+r'\end{tabularx}\endgroup'+'\n'+r'\end{table}')
def records(name):return list(csv.DictReader((EVID/'phase3'/name).open()))
performance={r['stream']:r for r in records('performance.csv')}
def num(row,key):return f"{float(row[key]):.2f}"
def pmrow(name,label):
 r=performance[name]
 return [label,num(r,'pooled_mae'),num(r,'pooled_rmse'),num(r,'mean_weekly_mae')+r' $\pm$ '+num(r,'weekly_mae_sd'),num(r,'mean_weekly_rmse')+r' $\pm$ '+num(r,'weekly_rmse_sd')]

preamble=original.split('\\begin{document}')[0]
preamble=preamble.replace('% Springer Nature manuscript for Environmental Modeling & Assessment','% Revised v1 for Scientific Reports; original Springer Nature template retained.')
preamble=preamble.replace('\\usepackage{placeins}',r'''\usepackage{placeins}
\usepackage{xcolor}
\usepackage{soul}
\usepackage{colortbl}
\sethlcolor{yellow}
\newcommand{\rev}[1]{\hl{#1}}
\newcommand{\revmath}[1]{\colorbox{yellow}{$\displaystyle #1$}}
\soulregister\citep7
\soulregister\citet7
\soulregister\ref7
\soulregister\textsubscript1
\soulregister\texttt1
\soulregister\url7
\soulregister\doi7
\soulregister\natexlab1''')
preamble=preamble.replace('\\newcommand{\\PMunit}{\\ensuremath{\\mu\\mathrm{g}\\,\\mathrm{m}^{-3}}}',r'\newcommand{\PMunit}{\ensuremath{\mu\mathrm{g}\,\mathrm{m}^{-3}}}'+'\n'+r'\soulregister\PMunit0')
preamble=preamble.replace('Operational Time-Series Models','Adaptive Time-Series Models')
raw(preamble)
raw(r'\begin{document}')
front=original.split('\\begin{document}',1)[1].split('\\abstract{',1)[0]
front=front.replace('Operational Time-Series Models',r'\rev{Adaptive} Time-Series Models')
raw(front)
raw(r'\abstract{\rev{Accurate air-quality forecasting requires balancing predictive performance, interpretation, and model updating. We compare SARIMAX, Facebook Prophet, and NeuralProphet for hourly PM\textsubscript{2.5} in Beijing using API-derived estimates. Weekly refitting and frozen parameters with EWMA residual correction are evaluated under Perfect Prognosis, supplying actual future gas concentrations. Training-only validation and preprocessing precede a matched evaluation of 23 weekly origins and 3,624 observed hours. Weekly-refit pooled mean absolute errors are 30.43, 38.72, and 41.95~\PMunit{} for SARIMAX, Prophet, and NeuralProphet (seed 42). Predefined correction reduces frozen-model errors from 30.48 to 29.94, 43.93 to 37.69, and 53.39 to 37.62~\PMunit{}, respectively. Across three NeuralProphet seeds, frozen and refitted errors average 46.88 and 39.61~\PMunit{}, with standard deviations of 10.40 and 4.33. Correction benefits vary by seed, and the paired weekly interval for the SARIMAX improvement includes zero. Regressor effects and components provide conditional interpretations, while different timing boundaries limit speed comparisons. The findings characterize adaptation within a retrospective Perfect Prognosis evaluation; operational skill with forecast gas inputs and independently verified station targets remains untested.}}')
raw(r'\keywords{PM\textsubscript{2.5} forecasting, air quality, SARIMAX, Facebook Prophet, NeuralProphet, online residual correction}')
raw(r'\maketitle')
section('Introduction','sec1')
intro=original.split('\\section{Introduction}\\label{sec1}',1)[1].split('\\section{Related work}',1)[0]
# Preserve the opening three paragraphs verbatim; narrow subsequent framing.
opening=intro.strip().split('\n\n')[:3]
for s in opening:
 s=s.replace(r'coarse particles (PM\textsubscript{10})',r'\rev{inhalable particles} (PM\textsubscript{10})')
 raw(s)
P(r'''Research spans classical statistical methods, machine learning, deep learning, and hybrid decompositions. Recurrent networks, decomposition--reconstruction pipelines, and distributed learning have expanded the range of air-quality forecasting methods \citep{bib5,bib6,bib7,bib9,bib10,bib11}. Alongside predictive accuracy, repeated forecasting requires decisions about updating model parameters, incorporating recent observations, and managing computational cost. These decisions can be studied within established forecasting families without proposing a new architecture.''')
P(r'''In this study, we revisit hourly particulate matter forecasting for Beijing through a transparent comparison of SARIMAX, Facebook Prophet, and NeuralProphet. We examine how their performance changes under weekly expanding-window refitting and frozen parameters with an established EWMA bias correction. Experiments use Perfect Prognosis, which supplies actual future exogenous gases and isolates conditional forecasting and adaptation from the separate problem of predicting those gases. Our comparison is restricted to these three families, a predefined four-gas input set, and the evaluated period.''')
raw('Our contributions are threefold:\n'+r'\begin{itemize}'+'\n'+r'''\item \rev{A documented hourly forecasting workflow with chronological validation, explicit data-gap handling, and a common observed-hour evaluation mask under Perfect Prognosis.}
\item \rev{A matched 23-week comparison of three time-series families under weekly refitting and frozen parameters, supplemented by persistence references, predictor controls, lead-time errors, and repeated NeuralProphet seeds.}
\item \rev{An assessment of the benefits and limits of online bias correction, supported by paired weekly uncertainty, fitted regressor effects, and separately defined computational measurements.}'''+ '\n'+r'\end{itemize}')
section('Related work')
P(r'''Classical time-series models offer explicit representations of temporal dependence and seasonality. ARIMA and neural-network comparisons in Beijing illustrate the distinction between linear and nonlinear formulations \citep{bib13}, while SARIMA--Prophet comparisons examine additive seasonal forecasting \citep{bib14}. Broader comparisons show that machine-learning methods can remain competitive with deep and additive models, depending on the region and forecast horizon \citep{bib15,bib16}. Tree ensembles, spatio-temporal feature engineering, and temporally weighted learning extend these approaches to richer inputs and changing conditions \citep{bib17,bib18,bib19,bib21}.''')
P(r'''Deep and hybrid models address temporal, spatial, and multiscale relationships. Examples include attention-based Bi-LSTM estimation \citep{bib22}, optimized recurrent models \citep{bib23}, continuous-time neural formulations \citep{bib24}, and decomposition or architecture fusion \citep{bib7,bib27,bib28}. Recent BiGRU--1DCNN, imputation-based RNN--BiGRU, and CNN--BiLSTM--XGBoost studies further examine multi-station learning and missing-data treatment \citep{bibr1-1,bibr1-2,bibr1-3}. These methods answer different questions about representation and information use; their reported errors cannot establish a ranking under our protocol.''')
P(r'''Recent Delhi studies provide more specific points of comparison. Sankar and Arasu combine wavelet extraction, PCA, hybrid feature optimization, and Bi-LSTM learning, using SHAP to describe feature contributions \citep{revWavelet}. Lakshmi and Krishnamoorthy use a bidirectional ConvLSTM encoder--decoder with spatial--temporal attention for multi-step PM$_{2.5}$ and PM$_{10}$ forecasting over horizons of 6--48 hours \citep{revSTA}. These studies emphasize feature representation and spatial information, whereas our single-location evaluation holds the primary input set fixed and examines repeated 168-hour forecasts under alternative update policies.''')
P(r'''Temporal and cross-pollutant transfer also address adaptation. A winter-season TL-LSTM with multi-head attention combines temporal transfer with CorrXGBoost feature selection \citep{revWinter}; a subsequent centralized framework extends transfer to multiple pollutants and stations with feature-level and cross-pollutant attention \citep{revCrossPollutant}. Their adaptation and interpretability mechanisms differ from the fixed-parameter bias correction and explicit coefficients examined here. Distributed learning provides another route to sharing information across monitoring networks, with privacy, non-IID data, and communication constraints \citep{bib30,bib4}. Our experiments do not assess spatial transfer, federated training, or superiority over these architectures. They contribute a controlled comparison of updating strategies within three established families, with future-input availability and computational boundaries made explicit.''')
P(r'''Table~\ref{tab:lr} summarizes these distinctions. Differences in datasets, target scaling, predictor availability, forecast horizons, and validation design prevent direct numerical comparison with the cited studies.''')
table('Selected literature and its relation to the present evaluation.','tab:lr',['Study','Focus','Relation to this study'],[
[r'\citep{bib14,bib15}','Statistical, additive, and ML comparisons','Motivates established model families; regions and protocols differ.'],
[r'\citep{revWavelet}','Wavelet/PCA, optimized features, Bi-LSTM, SHAP','Feature optimization and explanation; our four-gas set is predefined.'],
[r'\citep{revSTA}','Multi-station spatial--temporal attention; 6--48 h','Spatial representation and shorter horizons; our horizon is 168 h.'],
[r'\citep{revWinter}','Winter temporal transfer and multi-head attention','Learned adaptation across seasons; our correction updates a scalar bias.'],
[r'\citep{revCrossPollutant}','Centralized cross-pollutant transfer and attention','Multiple targets/stations; our target is one Beijing PM$_{2.5}$ series.'],
[r'\citep{bib30}','Distributed/federated forecasting','Data locality and client heterogeneity are outside our experiment.']], r'l>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X')
section('Methodology','sec:methodology')
P(r'''We formulate hourly PM\textsubscript{2.5} forecasting as a multistep prediction task with exogenous drivers. At forecast origin $o_w$, a model predicts $y_{o_w+h-1}$ for leads $h=1,\ldots,H$, where $H$ denotes the forecast horizon. Chronological partitioning and validation separate model development from subsequent evaluation. We compare parameter refitting with fixed-parameter forecasting and online residual correction; the specific experimental settings are given in Section~\ref{sec:implementation}.''')
P(r'''Under Perfect Prognosis, future values of the exogenous regressors are treated as known over the forecast horizon. Future PM\textsubscript{2.5} is withheld from prediction and used only for scoring and subsequent updates. This assumption can approximate a setting with highly accurate external predictor forecasts, but those forecasts would introduce errors absent here. Without such externally available inputs, the evaluation remains an idealized conditional comparison and cannot establish operational forecast skill.''')
section('Data preprocessing','subsec:preprocessing','subsection')
P(r'''Hourly timestamps are ordered on a regular calendar so that missing intervals retain their temporal meaning. Input validity and missingness are distinguished from high pollutant concentrations, which may represent genuine events. The original target scale is retained for interpretation and evaluation.''')
P(r'''To avoid information leakage, transformations are estimated using data available before each fitting origin. Standardization expresses predictors relative to historical means and standard deviations. Missing-data handling must respect temporal order and distinguish fitting labels, inference history, and scoring targets; the model-specific policies are described in the implementation.''')
section('Predictor analysis','subsec:feature_selection','subsection')
P(r'''Pearson correlation and mutual information describe linear and potentially nonlinear associations between candidate predictors and PM\textsubscript{2.5}, using training data only. For continuous variables, their definitions are''')
eq(r'\rho_{X,Y}=\frac{\mathrm{Cov}(X,Y)}{\sigma_X\sigma_Y}', 'eq:pearson')
eq(r'I(X;Y)=\iint p(x,y)\log\!\left(\frac{p(x,y)}{p(x)p(y)}\right)\,dx\,dy', 'eq:mi')
P(r'''Minimum redundancy--maximum relevance (mRMR) balances association with the target against dependence among selected predictors. In the relevance-to-redundancy quotient formulation (MIQ), candidate relevance $I(X_j;Y)$ is divided by its average mutual information with already selected predictors; the initial step uses relevance alone. These analyses describe associations, not causal effects. Strong target association indicates relevance and does not by itself establish redundancy among predictors.''')
section('Forecasting models','subsec:models','subsection')
P(r'''We benchmark a classical state-space regression model (SARIMAX), a decomposable additive model (Facebook Prophet), and its autoregressive neural extension (NeuralProphet). Each supports multistep forecasting with external drivers under Perfect Prognosis.''')
section('SARIMAX',level='subsubsection')
P(r'''SARIMAX combines a regression on exogenous predictors with seasonal and nonseasonal temporal dependence. For predictor vector $x_t$, regression residual $u_t=y_t-\beta^{\mathsf T}x_t$, and lag operator $B$, a general multiplicative form is''')
eq(r'\phi(B)\Phi(B^s)(1-B)^d(1-B^s)^D u_t=c+\theta(B)\Theta(B^s)\varepsilon_t', 'eq:sarimax')
P(r'''Here $s$ is the seasonal period, $d$ and $D$ are nonseasonal and seasonal differencing orders, and $c$ is a constant where included. The polynomials $\phi$ and $\Phi$ represent autoregressive terms of orders $p$ and $P$, while $\theta$ and $\Theta$ represent moving-average terms of orders $q$ and $Q$. Their products retain seasonal/nonseasonal cross terms. The regression coefficients describe conditional associations given the temporal structure and other inputs; the selected specification is reported in Section~\ref{subsec:impl_models}.''')
section('Facebook Prophet (FBP)',level='subsubsection')
P(r'''Prophet represents a series through a trend, recurring seasonal patterns, and external-regressor contributions. In the additive formulation,''')
eq(r'y_t=g(t)+s(t)+\beta^{\mathsf T}x_t+\varepsilon_t', 'eq:prophet')
P(r'''The trend $g(t)$ can accommodate changepoints, while $s(t)$ represents periodic structure through Fourier terms. External regressors provide additional explanatory components. This decomposition permits inspection of trend, seasonal, and regressor contributions; the seasonalities and transformation choices used here are specified in the implementation.''')
section('NeuralProphet (NP)',level='subsubsection')
P(r'''NeuralProphet extends decomposable forecasting with learned autoregressive and regressor components. A representation combining trend, seasonality, lagged targets, and future-known inputs is''')
eq(r'\hat y_{w,h}=T_{w,h}+S_{w,h}+A_h(y_{o_w-L:o_w-1})+F_h(x_{o_w:o_w+H-1})', 'eq:neuralprophet')
P(r'''Here $L$ denotes the historical target-context length, $H$ the forecast horizon, and $h$ the forecast lead. The autoregressive contribution $A_h$ summarizes recent target history, while $F_h$ represents future-known regressors. The component parameterization and training configuration determine the flexibility of the model; their specific choices are reported in Section~\ref{subsec:impl_models}.''')
section('Adaptive forecasting regimes','subsec:regimes','subsection')
P(r'''The two regimes differ in parameter updating while sharing forecast origins and evaluation criteria. Each may use observations revealed before the current origin.''')
section('Regime 1: Weekly walk-forward refit',level='subsubsection')
P(r'''At the beginning of week $w$, each model is fitted using the initial training period and the observed portions of earlier test weeks:''')
eq(r'\mathcal D^{(w)}=\mathcal D_{\mathrm{train}}\cup\mathcal D_{1:w-1}', 'eq:expanding')
P(r'''Model parameters and preprocessing are re-estimated from this expanding history. Earlier test outcomes may enter subsequent fitting, but the current forecast week's target remains unavailable. This regime incorporates newly revealed data at the cost of repeated parameter estimation.''')
section('Regime 2: Frozen base model with online residual correction',level='subsubsection')
P(r'''A base model is fitted once and retains its parameters and preprocessing during evaluation. Recent observations can still refresh its state or inference context. Adaptation is introduced through a bias applied to its forecast, with the model-specific information handling described in Section~\ref{subsec:impl_regimes}. The base multi-step residual for week $w$ and lead $h$ is''')
eq(r'e_{w,h}=y_{o_w+h-1}-\hat y^{\mathrm{base}}_{w,h}', 'eq:residual')
P(r'''Let $S_w$ contain the scored leads in week $w$. Apply the previously available bias $b_w$ before revealing that week's outcomes, then update it after the week using the observed base residual mean:''')
eq(r'\hat y^{\mathrm{final}}_{w,h}=\hat y^{\mathrm{base}}_{w,h}+b_w,\qquad b_1=0', 'eq:corrected')
eq(r'\bar e_w=\frac{1}{|S_w|}\sum_{h\in S_w}e_{w,h},\qquad b_{w+1}=\alpha\bar e_w+(1-\alpha)b_w', 'eq:ewma')
P(r'''The smoothing factor $\alpha$ controls the weight assigned to the latest completed week's residual mean. Larger values respond more strongly to recent bias; $\alpha=1$ gives the previous-week mean-residual correction. EWMA is an established bias-tracking method applied within this comparison.''')
section('Rolling evaluation protocol','subsec:evaluation','subsection')
P(r'''Forecasts are evaluated at consecutive weekly origins using a common observed-hour mask. Incomplete coverage is reported separately, and only original available target values enter scoring. This keeps the evaluated information and timestamps comparable across methods.''')
P(r'''Pooled hourly MAE and RMSE give each scored hour equal weight:''')
eq(r'\mathrm{MAE}=\frac{1}{N}\sum_{i=1}^{N}|y_i-\hat y_i|,\qquad \mathrm{RMSE}=\sqrt{\frac{1}{N}\sum_{i=1}^{N}(y_i-\hat y_i)^2}', 'eq:metrics')
P(r'''Separately, mean weekly MAE and mean weekly RMSE give each origin equal weight; their sample standard deviations summarize variation across weeks. Mean weekly RMSE is not pooled RMSE. Lead-specific errors reveal how performance changes over the horizon. MAPE and SMAPE are omitted because near-zero concentrations make percentage errors unstable.''')
P(r'''Persistence repeats the last observed target before an origin. Seasonal persistence repeats a preceding seasonal pattern across the forecast horizon. Such references use past targets only and therefore have a different information set from models supplied with future covariates under Perfect Prognosis.''')
section('Statistical analysis',level='subsection')
P(r'''Paired weekly error differences compare methods on identical origins and scoring masks. Moving-block bootstrap intervals retain contiguous groups of weekly differences to account for temporal dependence. Negative A--B differences favor A. With a short dependent evaluation period, the intervals are descriptive and do not establish broad population-level significance. Variation across repeated training seeds is distinguished from temporal variation across forecast weeks.''')
section('Implementation','sec:implementation')
fig(1,'Revised forecasting workflow. All fitting and preprocessing use history before each origin. Actual future covariates are supplied under Perfect Prognosis; future targets enter only scoring and subsequent updates.','fig:framework')

P(r'''All revised fits used the same local AMD Ryzen 5 5500U system on CPU, with two configured model threads and approximately 14.96 GiB of reported system RAM; no GPU was used. The environment used Python 3.11.2, NumPy 1.26.4, pandas 2.3.1, scikit-learn 1.7.0, statsmodels 0.14.5, Prophet 1.1.7, NeuralProphet 0.9.0, and PyTorch 2.6.0. Descriptive mRMR used pymrmr 0.1.11 and figures used matplotlib. Model fitting, analysis, and notebook presentation are separate reproducible stages.''')
section('Data assembly and preprocessing','subsec:impl_data','subsection')
P(r'''Pollutant concentrations were assembled through the OpenWeather Air Pollution history API \citep{bibOpenWeather}, and temperature and dew point through the Open-Meteo ERA5 archive endpoint \citep{bibOpenMeteo}. These series are API-derived model or gridded estimates at a requested Beijing coordinate, rather than authenticated observations from an identifiable monitoring station. Pollutants are expressed in \PMunit{} and weather variables in degrees Celsius under provider defaults.''')
P(r'''The source timestamps are sorted and reindexed to an hourly calendar without compressing gaps. Four chemically invalid predictor values of $-9999$ (two NO$_2$, one O$_3$, and one PM$_{10}$) are treated as missing in a working copy; the raw file and every PM$_{2.5}$ value are preserved. Negative temperatures and dew points remain valid. No positive target extremes are removed or clipped in the primary evaluation. A separate sensitivity clips predictors only at training-derived 1st and 99th percentiles.''')
P(r'''Input standardization uses means and standard deviations from complete predictor rows before the fitting origin. Frozen fits retain their initial scaler; refits recompute it from expanding history. Prophet fits observed complete target--predictor rows. SARIMAX retains missing targets in its state-space likelihood and forward-fills historical exogenous inputs using past values only. NeuralProphet trains on complete contiguous episodes of at least 336 hours, with shared model parameters and global target/time normalization. Its 168-lag/168-lead samples never cross a missing interval. Fitting and scoring targets are never imputed.''')
P(r'''For inference requiring dense history, missing past values are filled causally from the value 168 hours earlier, recursively where necessary, with the latest preceding value as fallback. NeuralProphet consumes the latest 168-hour context; seasonal-persistence references also use this filled history. This policy changes computational context only. Missing future inputs receive temporary mean placeholders to construct a forecast, but unavailable-input hours are masked from saved predictions and scoring. Perturbing those placeholders to 10 standardized units leaves every scored prediction unchanged in the implemented models.''')

P(r'''The requested coordinate was $(39.906217,116.3912757)$, stored in the CSV as $(39.9062,116.3913)$. The extraction uses the OpenWeather air-pollution history endpoint and Open-Meteo's ERA5 archive endpoint. The source contains 39,523 unique hourly rows from 25 November 2020 01:00 to 29 June 2025 19:00. Reindexing produces 40,267 hours with 744 absent timestamps across 21 intervals. The initial training period ends on 13 January 2025 00:00; testing begins one hour later. Training contains 36,240 calendar hours and 35,736 observed targets; testing contains 4,027 calendar hours and 3,787 observed targets.''')
P(r'''Timestamps are interpreted as UTC based on the source's UNIX-second conversion and omitted weather time-zone option, but original execution logs and API responses are unavailable. Retrieval dates cannot be recovered reliably. The extraction used positional pollutant-component values rather than named lookup, so the historical field mapping cannot be independently authenticated. The CSV start also precedes the provider-documented historical start of 27 November 2020; this discrepancy remains unresolved. These limitations prevent treating the target as independently verified station truth.''')
P(r'''The primary weekly evaluation ends on 23 June 2025 00:00. Nineteen weeks have 168 scored hours; the four partial weeks have 120, 120, 48, and 144. Table~\ref{tab:descriptive} describes original observed targets over the full training/test partitions, including the test remainder. All original observed targets are preserved; predictor-only clipping is evaluated separately from primary preprocessing.''')
desc=json.loads((EVID/'phase1/data_audit.json').read_text())['descriptive']
rows=[]
for key,label in [('training','Training'),('test','Test')]:
 r=desc[key];rows.append([label,str(r['observed_n']),f"{r['mean']:.2f}",f"{r['sd']:.2f}",f"{r['median']:.2f}",f"{r['q25']:.2f}--{r['q75']:.2f}",f"{r['min']:.2f}--{r['max']:.2f}"])
table(r'Original observed PM$_{2.5}$ distributions. Concentrations are in \PMunit{}; SD denotes sample standard deviation and Q1--Q3 the interquartile interval.','tab:descriptive',['Partition','$n$','Mean','SD','Median','Q1--Q3','Min--max'],rows,'lrrrrrX')
section('Predictor analysis','subsec:impl_feature_selection','subsection')
P(r'''Continuous MI is estimated with scikit-learn's nearest-neighbor estimator using seed 42. Descriptive mRMR uses the MIQ relevance-to-redundancy criterion after training-only quintile discretization, removing duplicate bin edges. At each selection step, candidate relevance $I(X_j;Y)$ is divided by its average mutual information with the already selected predictors; the initial step uses relevance alone. Five predictors are requested. These analyses describe associations, not causality.''')
P(r'''The primary four-gas set $\{\mathrm{NO},\mathrm{NO}_2,\mathrm{CO},\mathrm{SO}_2\}$ is retained as a predefined subset to build on the original experiment. It is not claimed to be the optimal mRMR output. A broader nine-predictor set adds O$_3$, NH$_3$, temperature, dew point, and PM$_{10}$; no-input controls remove all exogenous variables. All frozen controls retain the selected model settings, so they assess input changes rather than separately tuned competitors.''')
P(r'''Excluding PM$_{10}$ from the primary set keeps this comparison conditioned on gases rather than a contemporaneous particulate aggregate containing the fine fraction. PM$_{10}$ includes both fine and coarse particles, so it is not identical to PM$_{2.5}$ \citep{revPMFractions}. Its training correlation of 0.992 makes actual same-hour PM$_{10}$ a particularly close target proxy in this series. Leakage concerns depend on whether a feature is legitimate for the prediction task, not correlation alone \citep{revLeakage}. Actual future PM$_{10}$ would be unavailable to an operational forecast unless supplied externally, as would the actual future gases. The broad-set experiment is therefore an explicitly conditional Perfect Prognosis control, not evidence of operational skill. Lagged or independently forecast PM$_{10}$ could be legitimate inputs in a different protocol; the present exclusion is a scope restriction, not a claim that PM$_{10}$ is irrelevant.''')

P(r'''Training-only complete-row analysis uses 35,732 hours. PM$_{10}$ has the largest Pearson correlation and MI with PM$_{2.5}$, followed by CO and NO (Table~\ref{tab:features}; Figs.~\ref{fig:corr_heatmap}--\ref{fig:mi_bar}). MIQ mRMR ranks PM$_{10}$, dew point, NO$_2$, NO, and CO as its first five predictors. This differs from the primary four-gas subset and does not validate that subset as optimal. High target association is relevance, not evidence of redundancy among predictors; the broader-input control examines the consequences of excluding PM$_{10}$ and other candidates.''')
features=list(csv.DictReader((EVID/'phase1/feature_rankings_training_only.csv').open()))
labels={'no':'NO','no2':'NO$_2$','co':'CO','so2':'SO$_2$','o3':'O$_3$','nh3':'NH$_3$','temperature':'Temperature','dewpt':'Dew point','pm10':'PM$_{10}$'}
table('Training-only predictor rankings. MI is estimated on continuous inputs; mRMR uses separately discretized inputs.','tab:features',['Predictor','Pearson $r$','MI','Absolute-$r$ rank','MI rank'],[[labels[r['feature']],f"{float(r['pearson_r']):.3f}",f"{float(r['mutual_information']):.3f}",r['absolute_correlation_rank'],r['MI_rank']] for r in features],'Xrrrr')
fig(2,'Pearson correlations on 35,732 complete initial-training rows after invalid-input masking. Associations do not establish causal effects.','fig:corr_heatmap')
fig(3,'Training-only continuous mutual information between each candidate predictor and the original target. These descriptive scores do not select the primary four-gas subset.','fig:mi_bar')
section('Model configuration','subsec:impl_models','subsection')
P(r'''For SARIMAX, the selected specification sets $p=q=P=Q=1$, $d=D=0$, $s=24$, and $c=0$ in Eq.~\ref{eq:sarimax}; the multiplicative seasonal/nonseasonal cross terms are retained.''')
P(r'''Daily, weekly, and yearly seasonalities and default changepoint handling are retained. Additional regressor standardization is disabled because inputs have already been transformed using training-only statistics.''')
P(r'''The configuration uses 168 lags and 168 direct forecast leads, daily/weekly/yearly seasonalities, and default linear autoregressive and future-regressor modules. Events, holidays, lagged exogenous regressors, and hidden autoregressive layers are not added. Global normalization is learned from the retained pre-origin training episodes and predictions are returned to the original concentration scale. Finite training losses and exact origin/lead extraction are checked; completing the specified epochs does not prove optimization to a global minimum.''')

P(r'''Time-ordered validation uses four consecutive weekly origins from 16 December 2024 01:00 through 6 January 2025 01:00, all before testing. The screening base fit precedes the first validation origin and produces the subsequent weekly forecasts with frozen parameters and refreshed state/context. The bounded grid contains four SARIMAX combinations with $p=q=P=Q=1$, $d,D\in\{0,1\}$, and period 24; additive/multiplicative Prophet seasonality; and 30/50 NeuralProphet epochs. Candidates are selected by mean weekly MAE, with pooled RMSE as tie-breaker. Seven of eight candidates complete; SARIMAX $(1,0,1)\times(1,1,1,24)$ fails and is excluded. This limited winter validation is not an exhaustive hyperparameter search.''')
table('Selected training-only configurations, used unchanged in both regimes.','tab:configuration',['Family','Configuration','Validation MAE'],[
['SARIMAX','$(1,0,1)\times(1,0,1,24)$; no constant; stationarity/invertibility constraints disabled','14.99'],
['Prophet','Additive; daily/weekly/yearly seasonalities; default trend/changepoints; no additional regressor scaling','28.52'],
['NeuralProphet','168 lags/leads; 50 epochs; batch 128; learning rate 0.001; no early stopping; global normalization','27.59']], r'l>{\raggedright\arraybackslash}Xr')
P(r'''NeuralProphet uses seeds 42, 123, and 2026 for both regimes; validation and predictor controls use seed 42. Training losses, episode sample counts, forecast timestamps, and the 168 extracted leads are checked. SARIMAX's test fits use an earlier converged, corrected training fit for initialization and complex-step L-BFGS-B with at most 200 iterations and 100 line searches. Acceptance requires finite parameters, solver convergence, and nondecreasing training likelihood, without consulting test errors. The broad-input SARIMAX control also receives one bounded 400-iteration conditional-sum-of-squares initialization attempt, which remains nonconverged; no predictions from this failed control are scored.''')
section('Adaptive regime implementation','subsec:impl_regimes','subsection')
P(r'''In the frozen regime, SARIMAX filters newly revealed history without refitting, NeuralProphet receives the latest 168-hour target context, and Prophet evaluates the actual future dates and covariates. Walk-forward refits re-estimate their parameters and scaler using all observed pre-origin history. The first-origin fit and forecast are identical to the corresponding frozen fit and are reused only after exact configuration and signature checks.''')
P(r'''The primary smoothing factor $\alpha=0.3$ is predefined. Sensitivities use 0.1, 0.2, 0.5, 0.7, and 1.0; the latter is the previous-week mean-residual correction. No value is selected from test performance. Four partial weeks update the primary bias using their observed scoring hours. EWMA is an established bias-tracking method applied here, rather than a new algorithm; no separate Kalman bias-correction alternative is evaluated.''')

P(r'''Walk-forward refits use all available pre-origin history at each week. Frozen streams retain their initial scaler and parameters while refreshing the model-specific state/context described above. EWMA is applied before outcomes and updated afterwards from base residuals. The common observed-only score mask is identical across models, regimes, seeds, and controls. The strict 16-week sensitivity carries the bias forward across excluded weeks and updates only after eligible weeks, whereas the primary 23-week policy also updates after partially observed weeks.''')
table('Weekly forecasting sequence and information boundaries.','tab:pseudocode',['Step','Operation'],[
['1','At origin $o_w$, isolate history with timestamps earlier than $o_w$ and obtain future covariates under Perfect Prognosis.'],
['2','Refit parameters/scaler from history (Regime 1), or retain them and refresh state/context (Regime 2).'],
['3','Produce 168 aligned base predictions; apply $b_w$ for frozen correction before current outcomes are revealed.'],
['4','After the week, score only shared observed target/covariate hours; retain partial-week coverage counts.'],
['5','Use base residuals from scored hours to update $b_{w+1}$; make revealed history available at the next origin.']], r'l>{\raggedright\arraybackslash}X')
section('Evaluation and statistical settings','subsec:impl_evaluation','subsection')
P(r'''The complete hourly calendar is split chronologically into 90\% initial training and 10\% testing. Forecast horizon and origin step are both 168 hours.''')
P(r'''The primary schedule retains all 23 complete calendar weeks (3,864 scheduled hours), including four partially observed weeks. A shared mask requires the original target and all broad-set covariates to be observed, producing 3,624 scored hours for every method. The final 163-hour calendar remainder is reported but excluded from the fixed 168-hour evaluation. A secondary sensitivity uses 16 weeks with fully observed future and prior 168-hour context (2,688 hours); it is not the primary result.''')
P(r'''Paired weekly MAE differences use identical origins and scoring masks. Descriptive 95\% intervals are obtained from 2,000 moving-block bootstrap replicates with a primary block length of three weeks and sensitivities of two and four weeks. NeuralProphet paired losses average the three seed-level weekly losses, rather than averaging forecasts. Negative A--B differences favor A. Intervals are not adjusted for multiple comparisons and rely on only 23 dependent weeks; they do not establish broad population-level significance. Seed means and sample standard deviations are reported separately from temporal dispersion.''')
P(r'''The revised test period had already been examined during the original research and earlier revision analysis. This is therefore a revised retrospective evaluation, rather than a previously untouched confirmatory test. The corrected-input rule, candidate grid, primary scoring coverage, and EWMA factor were specified before inspecting corrected test results.''')
section('Results','sec:results')
P(r'''All primary results use 23 origins and 3,624 scored hours. Pooled hourly errors and equally weighted weekly mean errors are reported separately; dispersion denotes sample SD across the 23 weeks. NeuralProphet uses seed 42 in the main family comparison, with all seeds reported subsequently. Every primary SARIMAX refit completed all 23 origins. All errors are in \PMunit{}.''')
section('Regime 1: Weekly walk-forward refitting','subsec:results_regime1','subsection')
P(r'''SARIMAX has the lowest pooled MAE and RMSE in the matched walk-forward comparison (30.43 and 46.88), followed by Prophet (38.72 and 51.13) and seed-42 NeuralProphet (41.95 and 56.51). Weekly MAE dispersion remains substantial for every family (Table~\ref{tab:regime1_results}). Figure~\ref{fig:regimes} compares the two parameter-update regimes, and Fig.~\ref{fig:chronology} shows every evaluation week rather than selected extremes.''')
header=['Model','Pooled MAE','Pooled RMSE','Weekly MAE $\pm$ SD','Weekly RMSE $\pm$ SD']
table('Weekly walk-forward results on the common observed-hour mask. Weekly and pooled aggregations are distinct.','tab:regime1_results',header,[pmrow('sarimax_walk_s42','SARIMAX'),pmrow('prophet_walk_s42','Prophet'),pmrow('neuralprophet_walk_s42','NP (42)')],'Xrrrr')
fig(4,'Chronological weekly MAE comparison of frozen base forecasts and weekly refitting on 23 origins and 3,624 shared scoring hours. NeuralProphet uses seed 42.','fig:regimes')
fig(5,'Chronological weekly MAE of frozen base forecasts for all 23 origins. NeuralProphet uses seed 42; partial weeks contribute only their observed scoring hours.','fig:chronology')
section('Regime 2: Frozen forecasting with online residual correction','subsec:results_regime2','subsection')
P(r'''With $\alpha=0.3$, frozen SARIMAX has the lowest pooled corrected MAE (29.94) and RMSE (43.80). Prophet's MAE decreases from 43.93 to 37.69, while seed-42 NeuralProphet decreases from 53.39 to 37.62 (Table~\ref{tab:regime2_results}). These are differences in pooled hourly MAE; paired weekly differences below use equal origin weights. Figure~\ref{fig:weekly_distribution} shows the distributions of frozen and corrected weekly errors.''')
table(r'Frozen base and EWMA-corrected results. Correction uses the previously available bias, with predefined $\alpha=0.3$.','tab:regime2_results',header,[pmrow('sarimax_frozen_s42','SAR base'),pmrow('sarimax_frozen_s42_ewma03','SAR + EWMA'),pmrow('prophet_frozen_s42','FBP base'),pmrow('prophet_frozen_s42_ewma03','FBP + EWMA'),pmrow('neuralprophet_frozen_s42','NP (42) base'),pmrow('neuralprophet_frozen_s42_ewma03','NP + EWMA')],'Xrrrr')
fig(6,'Weekly MAE distributions for frozen base and EWMA-corrected models over 23 origins. NeuralProphet uses seed 42; the plot summarizes temporal variation rather than uncertainty across training seeds.','fig:weekly_distribution')
section('Paired comparisons and seed variability',level='subsection')
contrasts=records('paired_contrasts.csv')[:5]
clabels=['SAR EWMA -- base','FBP EWMA -- base','NP EWMA -- base','SAR EWMA -- FBP EWMA','FBP EWMA -- FBP refit']
table(r'Paired mean weekly MAE differences and descriptive 95\% moving-block intervals (2,000 replicates; block length three). Negative values favor the first method; NP losses average three seeds.','tab:paired',['Comparison','Difference','95\% interval'],[[label,num(r,'mean_weekly_mae_difference'),f"[{float(r['ci95_block3_low']):.2f}, {float(r['ci95_block3_high']):.2f}]"] for label,r in zip(clabels,contrasts)],'Xrr')
P(r'''The interval for SARIMAX's small EWMA improvement includes zero. Prophet's correction interval excludes zero for the primary and two-/four-week block lengths. The seed-averaged NeuralProphet correction interval excludes zero with a three-week block but includes zero with a four-week block. Corrected Prophet and refitted Prophet have a paired weekly difference of $-0.94$ with an interval spanning zero; this is not an equivalence test.''')
rows=[]
for seed in [42,123,2026]:
 rows.append([str(seed),num(performance[f'neuralprophet_frozen_s{seed}'],'pooled_mae'),num(performance[f'neuralprophet_walk_s{seed}'],'pooled_mae'),num(performance[f'neuralprophet_frozen_s{seed}_ewma03'],'pooled_mae')])
table('NeuralProphet pooled MAE by training seed. These are individual runs, not an ensemble.','tab:seeds',['Seed','Frozen base','Weekly refit','Frozen + EWMA'],rows,'Xrrr')
P(r'''Across seeds, mean pooled MAE is $46.88\pm10.40$ for frozen forecasts and $39.61\pm4.33$ for refits (mean $\pm$ sample SD). Seed 2026 is more accurate than seeds 42/123 before correction; its corrected MAE slightly increases from 34.89 to 35.46. Thus, the revised evidence does not reproduce an inherent NeuralProphet weakness or a uniform correction benefit. Normalization, contiguous training episodes, and lead extraction were audited; remaining seed variation is observed, while explanations involving optimization or seasonal generalization remain tentative.''')
section('Lead time, concentration, and sensitivity',level='subsection')
P(r'''Figures~\ref{fig:lead_hour} and \ref{fig:lead_day} expose variation over the 168-hour horizon. Each lead is aggregated over the available matched observed targets, so its count can differ because of missing hours. The high-concentration threshold is the training 95th percentile, 691.34~\PMunit{}. On 158 scored hours clustered in six weeks, frozen seed-42 NeuralProphet has MAE 32.32, compared with 51.02 for SARIMAX and 50.60 for Prophet. This reverses the aggregate base-model ordering and limits claims of uniformly better performance.''')
fig(7,'MAE by hourly lead for frozen base forecasts, weekly refits, and frozen EWMA correction. NeuralProphet uses seed 42; lead-specific scoring counts reflect observed-hour coverage.','fig:lead_hour')
fig(8,'MAE by forecast day over the seven-day horizon, using matched observed hours. NeuralProphet uses seed 42.','fig:lead_day')
P(r'''The predefined alpha sensitivity shows that correction response differs across families and seeds. Figure~\ref{fig:correction} shows the base residuals, available bias, and correction benefit for seed 42. For SARIMAX, equally weighted weekly MAE is 29.50 at $\alpha=0.1$, 30.17 at 0.3, and 31.33 at 1.0, versus 30.66 without correction. Prophet improves over its base at all evaluated nonzero factors; seed-2026 NeuralProphet becomes slightly worse across those factors. These descriptive test sensitivities are not used to choose a replacement alpha. A bias estimated from the previous week can help a persistent offset but may overcorrect when the level changes.''')
fig(9,r'Frozen-model correction diagnostics for the predefined $\alpha=0.3$. Residuals are base-model residuals; bias is available before the forecast week and updated only afterwards. NeuralProphet seed-specific behavior is reported in the text and tables.','fig:correction')
P(r'''The secondary 16-week complete-context comparison retains the same corrected base forecasts. Strict-policy corrected MAEs are 29.09 for SARIMAX, 39.16 for Prophet, and 38.67 for seed-42 NeuralProphet. On those same hours, the primary partial-week update policy gives 29.15, 35.78, and 34.26, respectively. The differences show that both week inclusion and bias-update opportunities matter; the 23-week results remain primary.''')
section('Persistence references and predictor controls',level='subsection')
table('Frozen predictor controls and persistence references: pooled errors on the same 3,624 scored hours. NP controls use seed 42; broad-input SARIMAX is unavailable because of nonconvergence.','tab:controls',['Method','MAE','RMSE'],[[label,num(performance[name],'pooled_mae'),num(performance[name],'pooled_rmse')] for name,label in [('persistence','Last observed value'),('daily_persistence','Daily persistence'),('weekly_persistence','Weekly persistence'),('sarimax_frozen_no_inputs','SAR no inputs'),('prophet_frozen_no_inputs','FBP no inputs'),('neuralprophet_frozen_no_inputs','NP no inputs'),('prophet_frozen_broad','FBP broad inputs'),('neuralprophet_frozen_broad','NP broad inputs'),('sarimax_frozen_clip','SAR clipped inputs'),('prophet_frozen_clip','FBP clipped inputs'),('neuralprophet_frozen_clip','NP clipped inputs')]],'Xrr')
P(r'''The four-gas models outperform the target-only references on aggregate, but receive actual future gases unavailable to those references. No-input controls retain the selected settings and have MAEs of 115.24, 134.07, and 119.50 for SARIMAX, Prophet, and NeuralProphet. Broad-input Prophet and NeuralProphet improve to 15.87 and 22.35 with actual future PM$_{10}$ among their inputs. This result highlights the information gained from additional predictors and argues against claiming the four gases are optimal. Because five predictors are added together, the control does not isolate PM$_{10}$'s individual contribution. Its contemporaneous particulate input also changes the conditioning information, as explained in Section~\ref{subsec:impl_feature_selection}. Broad-input SARIMAX fails both bounded optimizer attempts, preventing a complete broad-input family ranking. Predictor-only clipping increases MAE for all three selected-input frozen models; high target concentrations remain unmodified.''')
section('Model interpretation and computational measurements',level='subsection')
coeff=records('coefficients.csv')
rows=[]
for feature in ['no','no2','co','so2']:
 vals=[]
 for family in ['sarimax','prophet']:
  r=next(z for z in coeff if z['family']==family and z['regime']=='frozen' and z['feature']==feature and z['run_id'].endswith('_s42'))
  vals.append(f"{float(r['coefficient_scaled_input']):.2f}")
 rows.append([labels[feature]]+vals)
table(r'Initial frozen-model regressor coefficients, expressed as a PM$_{2.5}$ change in \PMunit{} per one training-input standard deviation, conditional on other inputs and temporal terms.','tab:effects',['Input','SARIMAX','Prophet'],rows,'Xrr')
P(r'''The frozen coefficients are shown in Table~\ref{tab:effects}. Because refit input scales change, stability is assessed using coefficients converted to raw-input units. Across 23 refits, SARIMAX's NO coefficient ranges from $-0.1996$ to $-0.1992$ and CO from 0.09596 to 0.09598; Prophet's corresponding ranges are $-0.2519$ to $-0.2410$ and 0.1061 to 0.1075. Positive marginal correlations alongside negative conditional NO coefficients illustrate the effect of correlated regressors and model conditioning, rather than a causal protective effect.''')
P(r'''For frozen Prophet, component means weight each of the 3,624 scored hours equally. Mean absolute contributions are 237.53 for CO, 43.55 for NO$_2$, 38.45 for NO, 25.02 for SO$_2$, 221.48 for trend, and 19.18, 4.05, and 10.12 for daily, weekly, and yearly seasonality. Signed contributions may cancel, so component magnitude is not an independent feature-importance measure. These outputs demonstrate explicit model interpretation without identifying emission mechanisms.''')
table('New walk-forward fit times for origins 2--23, excluding preprocessing and prediction. Boundaries differ across implementations and do not support a controlled speed ratio.','tab:timing',['Family','Fits','Timer boundary','Median (s)','Range (s)'],[
['SARIMAX','22','Optimization only','110.13','51.18--215.06'],
['Prophet','22','Including initialization/import','23.91','16.22--33.74'],
['NeuralProphet','66','Including initialization/import','182.02','170.63--202.59']], 'lrlrX')
P(r'''Fit timings in Table~\ref{tab:timing} are separated by boundary. Preprocessing, SARIMAX state updates, model prediction, and verification are recorded separately; first-origin reused forecasts retain their source computation cost. Frozen correction arithmetic takes approximately 0.002 seconds for a complete stream in repeated isolated measurements, excluding fitting, CSV I/O, and plotting. Recorded broader supervisor attempts total 6.63 hours, including failures and superseded completed attempts, with a largest sampled process-tree RSS of 1,845 MiB. These records exclude interrupted or standalone diagnostic work and are not total project time. All primary SARIMAX fits complete in this implementation. Memory requirements depend on implementation and environment, as well as model specification.''')
section('Discussion and future work')
P(r'''The comparison shows that updating all model parameters each week does not provide the same benefit for every family. SARIMAX's frozen and refitted aggregate errors are close, whereas Prophet and the seed-42/123 NeuralProphet runs improve with refitting. An established scalar EWMA correction also reduces their persistent error component, without a repeated parameter fit. Its smaller SARIMAX benefit is uncertain in the paired weekly analysis, and its adverse effect on NeuralProphet seed 2026 shows that adaptation can overcorrect an already competitive base forecast.''')
P(r'''These findings support a conditional comparison of update policies, rather than a universal preference for statistical or neural architectures. NeuralProphet's performance varies across seeds and improves relative to the other families on the small high-concentration subset. Broader-input controls also show that predictor availability can change errors more than the choice of update strategy. Model interpretability is limited to fitted associations and decomposed forecasts; correlated gases and API-derived targets prevent causal conclusions.''')
P(r'''Computationally, correction arithmetic is inexpensive and avoids repeated parameter optimization. However, frozen SARIMAX still refreshes its state, NeuralProphet still consumes recent history, and all models require future gas inputs under the present protocol. Differing fit timers and sampled memory measurements prevent a single controlled cross-model speed claim. Deployment would require externally forecast or otherwise available covariates and a prospective evaluation of their errors.''')
P(r'''Future work should first examine forecast-available gas inputs and independently verified station targets over additional seasons and locations. Longer chronological validation and additional seeds could assess the stability of settings and correction behavior. Attention, temporal/cross-pollutant transfer, and distributed learning offer complementary extensions \citep{revSTA,revWinter,revCrossPollutant,bib30}; they require evaluation under matched information sets before claims of improved accuracy or efficiency.''')
section('Limitations')
P(r'''Several limitations should be acknowledged. First, the source is a coordinate-specific API estimate series, not station ground truth. Original response archives and retrieval dates are unavailable, pollutant field mapping cannot be independently authenticated, and the source-start discrepancy remains unresolved. Forecasting the provided series does not demonstrate accuracy against physical measurements.''')
P(r'''Second, missing timestamps, four invalid predictor values, and partial-week coverage require explicit handling. Causal seasonal filling supplies inference history only, but its assumptions may be weak across long gaps, including a 120-hour interval. The observed-hour mask does not establish accuracy during missing periods. Primary targets remain unclipped; high-event findings use only 158 hours clustered in six weeks.''')
P(r'''Third, actual future covariates make this a retrospective Perfect Prognosis experiment. Target-only baselines have a different information set, and future PM$_{10}$ benefits the broader controls. The broad-input SARIMAX control is unavailable after nonconvergence. Four winter validation weeks, three NeuralProphet seeds, and 23 January--June test origins restrict seasonal and geographic generalization; earlier examination of the test period further limits confirmatory claims.''')
P(r'''Finally, the bounded grid does not establish optimal settings, solver convergence does not prove global optimality, and short-series bootstrap intervals are descriptive. Conditional coefficients and components are not causal effects. Runtime boundaries differ and memory is sampled, so neither universal computational rankings nor production-level speedups can be inferred.''')
section('Conclusion')
P(r'''This study examined hourly PM\textsubscript{2.5} prediction for Beijing using SARIMAX, Facebook Prophet, and NeuralProphet under weekly refitting and frozen parameters with EWMA correction. The workflow preserves original observed targets, uses training-only validation and transformations, and compares all primary streams on the same 23 origins and 3,624 observed hours under Perfect Prognosis.''')
P(r'''SARIMAX yields the lowest aggregate errors in the selected four-gas comparison, while refitting and residual correction provide model- and seed-dependent benefits. NeuralProphet's seed variability and high-concentration performance, alongside improvements from broader predictors, limit a universal family ordering. Explicit regressor effects and component summaries provide conditional interpretations, and isolated correction timings show low arithmetic overhead. These results characterize adaptation within the evaluated information setting; prospective testing with available-at-origin gas inputs and authenticated station measurements is required before operational conclusions.''')
raw(r'\backmatter')
raw(r'\bibliography{references}')
# Preserve all author-supplied declarations, except availability assertions that require author input.
declarations=original.split('\\section*{Statements and Declarations}',1)[1].split('\\end{document}',1)[0]
for heading in ['Data availability','Code availability']:
 pattern=r'(\\bmhead\{'+heading+r'\}\s*).*?(?=\\bmhead|$)'
 if heading=='Code availability':
  text=r'\rev{The project repository is} \url{https://github.com/moazzamumer/Adaptive-Air-Quality-Forcasting}. \rev{[Author input pending: add the DOI-linked versioned archive required by the editor.]}'+'\n\n'
 else:
  text=r'\rev{[Author input pending: confirm the revised data archive and applicable redistribution conditions.]}'+'\n\n'
 declarations=re.sub(pattern,lambda m:m.group(1)+text,declarations,flags=re.S)
raw(r'\section*{Statements and Declarations}')
raw(declarations)
raw(r'\end{document}')
(DEST/'manuscript.tex').write_text(''.join(parts).rstrip()+'\n')
newbib=r'''
%% Additional literature assessed from author-supplied full texts, 1 October 2026.
@article{revWavelet,
 author = "Sankar, Lakshmi and Arasu, Krishnamoorthy",
 title = "Efficient multi-station air quality prediction in {Delhi} with wavelet and optimization-based models",
 journal = "PLOS ONE", volume = "20", number = "8", pages = "e0330465", year = "2025",
 doi = "10.1371/journal.pone.0330465"
}
@article{revWinter,
 author = "Lakshmi, S. and Krishnamoorthy, A.",
 title = "Deep transfer learning and attention based {P2.5} forecasting in {Delhi} using a decade of winter season data",
 journal = "Scientific Reports", volume = "15", pages = "31787", year = "2025",
 doi = "10.1038/s41598-025-16664-4"
}
@article{revSTA,
 author = "Lakshmi, S. and Krishnamoorthy, A.",
 title = "Effective Multi-Step {PM2.5} and {PM10} Air Quality Forecasting Using Bidirectional {ConvLSTM} Encoder-Decoder With {STA} Mechanism",
 journal = "IEEE Access", volume = "12", pages = "179628--179647", year = "2024",
 doi = "10.1109/ACCESS.2024.3509142"
}
@article{revCrossPollutant,
 author = "Lakshmi, S. and Krishnamoorthy, A.",
 title = "Centralized transfer-learning {LSTM} with multi-head attention for interpretable multi-pollutant forecasting in {Delhi}'s winter smog episodes",
 journal = "Engineering Research Express", volume = "7", pages = "0452e2", year = "2025",
 doi = "10.1088/2631-8695/ae2826"
}
'''
(DEST/'references.bib').write_text((BASE/'references.bib').read_text()+newbib)
print('Revised manuscript source assembled:',len(''.join(parts).split()),'whitespace-delimited tokens')
