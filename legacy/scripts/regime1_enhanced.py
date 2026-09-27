"""
Regime 1: Weekly Walk-forward Refit Implementation - Enhanced
Implements 3 models (NeuralProphet, FBProphet, SARIMAX) × 2 targets (pm2.5, pm10)
90/10 Train/Test split
Includes regressors: 'no', 'no2', 'co', 'so2'
"""

import pandas as pd
import numpy as np
from neuralprophet import NeuralProphet
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import warnings
import os
warnings.filterwarnings('ignore')

# Create directory for weekly plots
os.makedirs('./regime1_weekly_plots', exist_ok=True)

print('='*80)
print('REGIME 1: WEEKLY WALK-FORWARD REFIT - ENHANCED')
print('='*80)

# Load preprocessed data
df = pd.read_csv('./data/beijing_preprocessed_unscaled.csv', parse_dates=['datetime'])
df = df.sort_values('datetime').reset_index(drop=True)

# 90/10 Train/Test split
n_total = len(df)
n_train = int(n_total * 0.9)
df_train_initial = df.iloc[:n_train].copy()
df_test = df.iloc[n_train:].copy()

print(f'\nData Split:')
print(f'  Total rows: {n_total}')
print(f'  Train rows: {len(df_train_initial)} (90%)')
print(f'  Train days: {len(df_train_initial) / 24:.1f}')
print(f'  Test rows: {len(df_test)} (10%)')
print(f'  Test days: {len(df_test) / 24:.1f}')

# Walk-forward parameters
step_size = 168  # 7 days * 24 hours
forecast_horizon = 168
num_weeks = len(df_test) // step_size
print(f'  Number of weeks in test period: {num_weeks}')

# Regressors
regressors = ['no', 'no2', 'co', 'so2']
print(f'  Regressors: {regressors}')

# Storage for results
results = {}

# ============================================================================
# MODEL 1: NeuralProphet with Regressors
# ============================================================================

def neuralprophet_with_regressors(target_variable):
    print(f'\n{"="*80}')
    print(f'NeuralProphet - {target_variable.upper()}')
    print(f'{"="*80}')
    
    all_forecasts = []
    all_actuals = []
    
    for week_idx in range(num_weeks):
        # Training window
        test_start_idx = week_idx * step_size
        if test_start_idx == 0:
            # First iteration: use only initial training data (90%)
            df_train_current = df_train_initial.copy()
        else:
            # Subsequent iterations: add observed test data
            df_train_current = pd.concat([
                df_train_initial,
                df_test.iloc[:test_start_idx]
            ], ignore_index=True)
        
        train_days = len(df_train_current) / 24
        print(f'\nWeek {week_idx + 1}/{num_weeks}')
        print(f'  Train size: {len(df_train_current)} rows ({train_days:.1f} days)')
        
        # Initialize model
        model = NeuralProphet(
            n_lags=168,
            n_forecasts=forecast_horizon,
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            epochs=50,
            batch_size=128,
            learning_rate=0.001
        )
        
        # Add regressors
        for reg in regressors:
            model.add_lagged_regressor(reg, n_lags=168)
        
        # Prepare training data
        train_data = df_train_current[['datetime', target_variable] + regressors].copy()
        train_data.columns = ['ds', 'y'] + regressors
        
        # Fit model
        model.fit(train_data, freq='H')
        
        # Prepare future data for forecasting
        future_df = model.make_future_dataframe(train_data, periods=forecast_horizon)
        
        # Make forecast
        forecast = model.predict(future_df)
        week_forecast = forecast.iloc[-forecast_horizon:]['yhat1'].values
        
        # Get actuals
        test_end_idx = min(test_start_idx + step_size, len(df_test))
        week_actual = df_test.iloc[test_start_idx:test_end_idx][target_variable].values
        
        # Weekly plot
        plt.figure(figsize=(12, 5))
        plt.plot(range(len(week_actual)), week_actual, label='Actual', color='black', linewidth=2)
        plt.plot(range(len(week_actual)), week_forecast[:len(week_actual)], 
                label='Forecast', color='blue', linewidth=2, alpha=0.7)
        plt.title(f'NeuralProphet - {target_variable.upper()} - Week {week_idx + 1}', 
                 fontweight='bold', fontsize=14)
        plt.xlabel('Hour')
        plt.ylabel(target_variable.upper())
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'./regime1_weekly_plots/neuralprophet_{target_variable}_week{week_idx + 1}.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        
        # Store results
        all_forecasts.extend(week_forecast[:len(week_actual)])
        all_actuals.extend(week_actual)
        
        print(f'  Forecast MAE this week: {mean_absolute_error(week_actual, week_forecast[:len(week_actual)]):.2f}')
    
    # Calculate overall metrics
    all_forecasts = np.array(all_forecasts)
    all_actuals = np.array(all_actuals)
    mae = mean_absolute_error(all_actuals, all_forecasts)
    rmse = np.sqrt(mean_squared_error(all_actuals, all_forecasts))
    
    print(f'\nNeuralProphet - {target_variable.upper()} Overall Results:')
    print(f'  MAE: {mae:.2f}')
    print(f'  RMSE: {rmse:.2f}')
    
    return {
        'forecasts': all_forecasts,
        'actuals': all_actuals,
        'mae': mae,
        'rmse': rmse
    }

# Run NeuralProphet for both targets
results['NeuralProphet_pm2.5'] = neuralprophet_with_regressors('pm2_5')
results['NeuralProphet_pm10'] = neuralprophet_with_regressors('pm10')

# ============================================================================
# MODEL 2: FBProphet with Regressors
# ============================================================================

def fbprophet_with_regressors(target_variable):
    print(f'\n{"="*80}')
    print(f'FBProphet - {target_variable.upper()}')
    print(f'{"="*80}')
    
    all_forecasts = []
    all_actuals = []
    
    for week_idx in range(num_weeks):
        # Training window
        test_start_idx = week_idx * step_size
        if test_start_idx == 0:
            df_train_current = df_train_initial.copy()
        else:
            df_train_current = pd.concat([
                df_train_initial,
                df_test.iloc[:test_start_idx]
            ], ignore_index=True)
        
        train_days = len(df_train_current) / 24
        print(f'\nWeek {week_idx + 1}/{num_weeks}')
        print(f'  Train size: {len(df_train_current)} rows ({train_days:.1f} days)')
        
        # Initialize model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            seasonality_mode='multiplicative'
        )
        
        # Add regressors
        for reg in regressors:
            model.add_regressor(reg)
        
        # Prepare training data
        train_data = df_train_current[['datetime', target_variable] + regressors].copy()
        train_data.columns = ['ds', 'y'] + regressors
        
        # Fit model
        model.fit(train_data)
        
        # Prepare future data
        future_df = model.make_future_dataframe(periods=forecast_horizon, freq='H')
        
        # Combine train + test for full regressor data
        # Note: test_end_idx here is for the regressors needed for the forecast horizon
        regressor_test_end_idx = min(test_start_idx + forecast_horizon, len(df_test))
        df_full = pd.concat([df_train_current, df_test.iloc[test_start_idx:regressor_test_end_idx]], ignore_index=True)
        
        # Add regressors to future_df (need full length matching future_df)
        for reg in regressors:
            future_df[reg] = df_full[reg].values[:len(future_df)]
            
        # Make forecast
        forecast = model.predict(future_df)
        week_forecast = forecast.iloc[-forecast_horizon:]['yhat'].values
        
        # Get actuals
        week_actual = df_test.iloc[test_start_idx:test_end_idx][target_variable].values
        
        # Weekly plot
        plt.figure(figsize=(12, 5))
        plt.plot(range(len(week_actual)), week_actual, label='Actual', color='black', linewidth=2)
        plt.plot(range(len(week_actual)), week_forecast[:len(week_actual)], 
                label='Forecast', color='green', linewidth=2, alpha=0.7)
        plt.title(f'FBProphet - {target_variable.upper()} - Week {week_idx + 1}', 
                 fontweight='bold', fontsize=14)
        plt.xlabel('Hour')
        plt.ylabel(target_variable.upper())
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'./regime1_weekly_plots/fbprophet_{target_variable}_week{week_idx + 1}.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        
        # Store results
        all_forecasts.extend(week_forecast[:len(week_actual)])
        all_actuals.extend(week_actual)
        
        print(f'  Forecast MAE this week: {mean_absolute_error(week_actual, week_forecast[:len(week_actual)]):.2f}')
    
    # Calculate overall metrics
    all_forecasts = np.array(all_forecasts)
    all_actuals = np.array(all_actuals)
    mae = mean_absolute_error(all_actuals, all_forecasts)
    rmse = np.sqrt(mean_squared_error(all_actuals, all_forecasts))
    
    print(f'\nFBProphet - {target_variable.upper()} Overall Results:')
    print(f'  MAE: {mae:.2f}')
    print(f'  RMSE: {rmse:.2f}')
    
    return {
        'forecasts': all_forecasts,
        'actuals': all_actuals,
        'mae': mae,
        'rmse': rmse
    }

# Run FBProphet for both targets
results['FBProphet_pm2.5'] = fbprophet_with_regressors('pm2_5')
results['FBProphet_pm10'] = fbprophet_with_regressors('pm10')

# ============================================================================
# MODEL 3: SARIMAX with Exogenous Variables
# ============================================================================

def sarimax_with_exog(target_variable):
    print(f'\n{"="*80}')
    print(f'SARIMAX - {target_variable.upper()}')
    print(f'{"="*80}')
    
    all_forecasts = []
    all_actuals = []
    
    for week_idx in range(num_weeks):
        # Training window
        test_start_idx = week_idx * step_size
        if test_start_idx == 0:
            df_train_current = df_train_initial.copy()
        else:
            df_train_current = pd.concat([
                df_train_initial,
                df_test.iloc[:test_start_idx]
            ], ignore_index=True)
        
        train_days = len(df_train_current) / 24
        print(f'\nWeek {week_idx + 1}/{num_weeks}')
        print(f'  Train size: {len(df_train_current)} rows ({train_days:.1f} days)')
        
        # Prepare training data
        train_series = df_train_current[target_variable].values
        train_exog = df_train_current[regressors].values
        
        # Initialize and fit SARIMAX
        model = SARIMAX(
            train_series,
            exog=train_exog,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 24),
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        model_fit = model.fit(disp=False)
        
        # Prepare exogenous variables for forecast
        test_end_idx = min(test_start_idx + forecast_horizon, len(df_test))
        forecast_exog = df_test.iloc[test_start_idx:test_end_idx][regressors].values
        
        # Make forecast
        week_forecast = model_fit.forecast(steps=len(forecast_exog), exog=forecast_exog)
        
        # Get actuals
        week_actual = df_test.iloc[test_start_idx:test_end_idx][target_variable].values
        
        # Weekly plot
        plt.figure(figsize=(12, 5))
        plt.plot(range(len(week_actual)), week_actual, label='Actual', color='black', linewidth=2)
        plt.plot(range(len(week_actual)), week_forecast[:len(week_actual)], 
                label='Forecast', color='red', linewidth=2, alpha=0.7)
        plt.title(f'SARIMAX - {target_variable.upper()} - Week {week_idx + 1}', 
                 fontweight='bold', fontsize=14)
        plt.xlabel('Hour')
        plt.ylabel(target_variable.upper())
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'./regime1_weekly_plots/sarimax_{target_variable}_week{week_idx + 1}.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        
        # Store results
        all_forecasts.extend(week_forecast[:len(week_actual)])
        all_actuals.extend(week_actual)
        
        print(f'  Forecast MAE this week: {mean_absolute_error(week_actual, week_forecast[:len(week_actual)]):.2f}')
    
    # Calculate overall metrics
    all_forecasts = np.array(all_forecasts)
    all_actuals = np.array(all_actuals)
    mae = mean_absolute_error(all_actuals, all_forecasts)
    rmse = np.sqrt(mean_squared_error(all_actuals, all_forecasts))
    
    print(f'\nSARIMAX - {target_variable.upper()} Overall Results:')
    print(f'  MAE: {mae:.2f}')
    print(f'  RMSE: {rmse:.2f}')
    
    return {
        'forecasts': all_forecasts,
        'actuals': all_actuals,
        'mae': mae,
        'rmse': rmse
    }

# Run SARIMAX for both targets
results['SARIMAX_pm2.5'] = sarimax_with_exog('pm2_5')
results['SARIMAX_pm10'] = sarimax_with_exog('pm10')

# ============================================================================
# COMPARISON AND VISUALIZATION
# ============================================================================

print('\n' + '='*80)
print('MODEL COMPARISON')
print('='*80)

# Create comparison tables
print('\n--- PM2.5 Results ---')
pm25_comparison = pd.DataFrame({
    'Model': ['NeuralProphet', 'FBProphet', 'SARIMAX'],
    'MAE': [
        results['NeuralProphet_pm2.5']['mae'],
        results['FBProphet_pm2.5']['mae'],
        results['SARIMAX_pm2.5']['mae']
    ],
    'RMSE': [
        results['NeuralProphet_pm2.5']['rmse'],
        results['FBProphet_pm2.5']['rmse'],
        results['SARIMAX_pm2.5']['rmse']
    ]
}).sort_values('MAE')
print(pm25_comparison.to_string(index=False))

print('\n--- PM10 Results ---')
pm10_comparison = pd.DataFrame({
    'Model': ['NeuralProphet', 'FBProphet', 'SARIMAX'],
    'MAE': [
        results['NeuralProphet_pm10']['mae'],
        results['FBProphet_pm10']['mae'],
        results['SARIMAX_pm10']['mae']
    ],
    'RMSE': [
        results['NeuralProphet_pm10']['rmse'],
        results['FBProphet_pm10']['rmse'],
        results['SARIMAX_pm10']['rmse']
    ]
}).sort_values('MAE')
print(pm10_comparison.to_string(index=False))

# Overall visualization
fig, axes = plt.subplots(2, 3, figsize=(20, 10))
fig.suptitle('Regime 1: Weekly Walk-forward Refit - All Models (with Regressors)', 
             fontsize=16, fontweight='bold')

models_pm25 = ['NeuralProphet_pm2.5', 'FBProphet_pm2.5', 'SARIMAX_pm2.5']
models_pm10 = ['NeuralProphet_pm10', 'FBProphet_pm10', 'SARIMAX_pm10']
colors = ['blue', 'green', 'red']

# PM2.5 plots
for idx, (model_key, color) in enumerate(zip(models_pm25, colors)):
    ax = axes[0, idx]
    result = results[model_key]
    ax.plot(result['actuals'], label='Actual', alpha=0.7, color='black', linewidth=1)
    ax.plot(result['forecasts'], label='Forecast', alpha=0.7, color=color, linewidth=1)
    ax.set_title(f"{model_key.replace('_', ' ').upper()}\\nMAE: {result['mae']:.2f}, RMSE: {result['rmse']:.2f}",
                fontweight='bold')
    ax.set_ylabel('PM2.5')
    ax.legend()
    ax.grid(True, alpha=0.3)

# PM10 plots
for idx, (model_key, color) in enumerate(zip(models_pm10, colors)):
    ax = axes[1, idx]
    result = results[model_key]
    ax.plot(result['actuals'], label='Actual', alpha=0.7, color='black', linewidth=1)
    ax.plot(result['forecasts'], label='Forecast', alpha=0.7, color=color, linewidth=1)
    ax.set_title(f"{model_key.replace('_', ' ').upper()}\\nMAE: {result['mae']:.2f}, RMSE: {result['rmse']:.2f}",
                fontweight='bold')
    ax.set_xlabel('Hour')
    ax.set_ylabel('PM10')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('./regime1_overall_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# Save results
all_results_df = pd.DataFrame({
    'actual_pm2.5': results['NeuralProphet_pm2.5']['actuals'],
    'actual_pm10': results['NeuralProphet_pm10']['actuals'],
    'NeuralProphet_pm2.5': results['NeuralProphet_pm2.5']['forecasts'],
    'NeuralProphet_pm10': results['NeuralProphet_pm10']['forecasts'],
    'FBProphet_pm2.5': results['FBProphet_pm2.5']['forecasts'],
    'FBProphet_pm10': results['FBProphet_pm10']['forecasts'],
    'SARIMAX_pm2.5': results['SARIMAX_pm2.5']['forecasts'],
    'SARIMAX_pm10': results['SARIMAX_pm10']['forecasts']
})

all_results_df.to_csv('./regime1_all_forecasts.csv', index=False)
pm25_comparison.to_csv('./regime1_pm25_comparison.csv', index=False)
pm10_comparison.to_csv('./regime1_pm10_comparison.csv', index=False)

print('\n' + '='*80)
print('Results saved to:')
print('  - ./regime1_all_forecasts.csv (all forecasts and actuals)')
print('  - ./regime1_pm25_comparison.csv (PM2.5 comparison table)')
print('  - ./regime1_pm10_comparison.csv (PM10 comparison table)')
print('  - ./regime1_overall_comparison.png (overall visualization)')
print(f'  - ./regime1_weekly_plots/ (weekly plots for each model-week combination)')
print('='*80)
