"""Build three data/protocol figures and copy six audited analysis figures.
No training, tuning, or mutation of existing experimental evidence.
"""
from pathlib import Path
import sys,json,shutil,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from revision.corrected.code.protocol import load_calendar,split_position
DEST=ROOT/'revision/manuscript/revised_v1'
NOTES=Path(__file__).parent
EVID=ROOT/'revision/corrected/artifacts'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':250})
manifest={}
def save(fig,n,evidence):
 fig.savefig(DEST/f'Fig{n}.png',bbox_inches='tight',facecolor='white')
 fig.savefig(NOTES/f'Fig{n}.pdf',bbox_inches='tight',facecolor='white')
 plt.close(fig)
 manifest[f'Fig{n}.png']={'source':evidence,'sha256':hashlib.sha256((DEST/f'Fig{n}.png').read_bytes()).hexdigest()}
fig,ax=plt.subplots(figsize=(10,9));ax.set_xlim(0,1);ax.set_ylim(-.055,1);ax.axis('off')
boxes=[(.5,.925,'Immutable API-derived series\nHourly calendar; invalid pollutant cells become missing'),(.5,.795,'Chronological 90/10 calendar split\nFour training-only validation weeks; bounded configurations'),(.5,.665,'At each weekly origin: isolate past data\nTraining-only transformations; actual future gases (Perfect Prognosis)'),(.255,.50,'Weekly expanding refit\nRefit parameters and scaler\nUse all observed pre-origin history'),(.745,.50,'Frozen parameters and scaler\nRefresh SARIMAX state / NP context\nApply previously available EWMA bias'),(.5,.315,'168-hour forecast; next origin after 168 hours\nFuture targets withheld until after prediction'),(.5,.17,'Reveal outcomes; score common observed hours\n23 origins; 3,624 hours; 19 complete + 4 partial weeks\nUpdate bias from base residuals for the next origin'),(.5,.025,'Pooled and weekly errors; paired block intervals; seeds\nLead times, controls, components, and timing boundaries')]
for x,y,t in boxes:
 w=.44 if y==.5 else .90;h=.105
 ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.008',facecolor='#edf4fa',edgecolor='#27658a',linewidth=1.2))
 ax.text(x,y,t,ha='center',va='center',fontsize=9.4)
for a,b in [(0,1),(1,2),(2,3),(2,4),(3,5),(4,5),(5,6),(6,7)]:
 x,y,_=boxes[a];xx,yy,_=boxes[b]
 ax.annotate('',xy=(xx,yy+.059),xytext=(x,y-.059),arrowprops={'arrowstyle':'->','color':'#27658a','lw':1.3})
save(fig,1,'Approved corrected protocol; validation windows; shared scoring coverage')
_,grid=load_calendar();columns=['pm2_5','no','no2','co','so2','o3','nh3','temperature','dewpt','pm10']
train=grid.iloc[:split_position(grid)][columns].dropna()
assert len(train)==35732
labels=['PM$_{2.5}$','NO','NO$_2$','CO','SO$_2$','O$_3$','NH$_3$','Temperature','Dew point','PM$_{10}$']
corr=train.corr()
fig,ax=plt.subplots(figsize=(8,7));im=ax.imshow(corr,vmin=-1,vmax=1,cmap='RdBu_r')
ax.set_xticks(range(10),labels,rotation=65,ha='right');ax.set_yticks(range(10),labels)
for i in range(10):
 for j in range(10):
  v=corr.iloc[i,j];ax.text(j,i,f'{v:.2f}',ha='center',va='center',fontsize=8,color='white' if abs(v)>.7 else '#222')
fig.colorbar(im,ax=ax,label='Pearson correlation');ax.set_title('Complete initial-training rows (n = 35,732)')
save(fig,2,'Corrected hourly calendar before initial test origin; 35,732 complete training rows')
d=pd.read_csv(EVID/'phase1/feature_rankings_training_only.csv').sort_values('mutual_information')
lookup=dict(zip(columns,labels));fig,ax=plt.subplots(figsize=(8,4.8))
colors=['#287ca8' if x in ['no','no2','co','so2'] else '#aebcc7' for x in d.feature]
ax.barh([lookup[x] for x in d.feature],d.mutual_information,color=colors)
ax.set_xlabel('Estimated mutual information (nats)');ax.set_title('Initial-training predictor associations')
for j,value in enumerate(d.mutual_information):ax.text(value+.035,j,f'{value:.3f}',va='center',fontsize=9)
ax.set_xlim(0,float(d.mutual_information.max())*1.15)
save(fig,3,'phase1/feature_rankings_training_only.csv; continuous MI estimator, seed 42')
for n,stem in [(4,'regime_comparison'),(5,'weekly_mae_chronology'),(6,'weekly_mae_distribution'),(7,'lead_hour_mae'),(8,'lead_day_mae'),(9,'correction_diagnostics')]:
 source=EVID/'phase3/figures'/f'{stem}.png';shutil.copyfile(source,DEST/f'Fig{n}.png')
 manifest[f'Fig{n}.png']={'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
# Improve the distribution and lead-hour summaries using already saved metrics.
colors={'sarimax':'#277da1','prophet':'#e67e22','neuralprophet':'#7b3fa0'}
fig,axes=plt.subplots(1,3,figsize=(10,4.4),sharey=True)
for ax,family in zip(axes,colors):
 names=[f'{family}_frozen_s42',f'{family}_frozen_s42_ewma03']
 values=[pd.read_csv(EVID/'phase3'/f'weekly_{name}.csv').mae for name in names]
 ax.boxplot(values,tick_labels=['Base','EWMA'],showfliers=True)
 ax.set_title({'sarimax':'SARIMAX','prophet':'Prophet','neuralprophet':'NeuralProphet'}[family]);ax.grid(axis='y',alpha=.2)
axes[0].set_ylabel(r'Weekly MAE ($\mu$g m$^{-3}$)')
fig.tight_layout();save(fig,6,'Saved weekly frozen base and EWMA alpha=0.3 metrics; seed 42')
d=pd.read_csv(EVID/'phase3/lead_hour.csv')
fig,axes=plt.subplots(3,1,figsize=(10,7.5),sharex=True)
for ax,family in zip(axes,colors):
 for suffix,label,color in [('frozen_s42','Frozen base','#277da1'),('walk_s42','Weekly refit','#e67e22'),('frozen_s42_ewma03','Frozen + EWMA','#38875a')]:
  a=d[d.stream.eq(f'{family}_{suffix}')]
  ax.plot(a.lead_hour,a.mae,label=label,color=color,linewidth=1)
 ax.set_title({'sarimax':'SARIMAX','prophet':'Prophet','neuralprophet':'NeuralProphet'}[family],fontsize=10);ax.set_ylabel(r'MAE ($\mu$g m$^{-3}$)');ax.grid(alpha=.2)
axes[0].legend(frameon=False,ncol=3,fontsize=9)
axes[-1].set_xlabel('Forecast lead hour (1–168)');axes[-1].set_xlim(1,168)
fig.tight_layout();save(fig,7,'phase3/lead_hour.csv; frozen/refit/EWMA; seed 42; observed-hour scores')
(NOTES/'FIGURE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('Nine manuscript figures prepared from corrected evidence.')
