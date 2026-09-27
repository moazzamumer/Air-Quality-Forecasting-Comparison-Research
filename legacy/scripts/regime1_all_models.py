"""
Regime 1: Weekly Walk-forward Refit Implementation
Implements 3 models (NeuralProphet, FBProphet, SARIMAX) × 2 targets (pm2.5, pm10) = 6 forecasting tasks
90/10 Train/Test split
"""

import pandas as pd
import numpy as np
from neuralprophet import NeuralProphet
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# STEP 1: Load Data and Create 90/10 Split
# ============================================================================

print('='*80)
print('REGIME 1: WEEKLY WALK-FORWARD REFIT')
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
print(f'  Test rows: {len(df_test)} (10%)')

# Weekly walk-forward parameters
step_size = 168  # 7 days * 24 hours
forecast_horizon = 168
num_weeks = len(df_test) // step_size
print(f'  Number of weeks in test period: {num_weeks}')

# Storage for results
results = {}

# ============================================================================
# HELPER FUNCTION: Walk-forward Loop
# ============================================================================

def walk_forward_forecast(model_name, target_variable, model_fn):
    """
    Generic walk-forward forecasting function
    
    Args:
        model_name: Name of the model (e.g., 'NeuralProphet')
        target_variable: 'pm2_5' or 'pm10'
        model_fn: Function that creates and returns (model, fit_fn, predict_fn)
    """
    print(f'\n{"="*80}')
    print(f'{model_name} - {target_variable.upper()}')
    print(f'{"="*80}')
    
    all_forecasts = []
    all_actuals = []
    
    for week_idx in range(num_weeks):
        print(f'\nWeek {week_idx + 1}/{num_weeks}')
        
        # Define the training window
        test_start_idx = week_idx * step_size
        df_train_current = pd.concat([
            df_train_initial,
            df_test.iloc[:test_start_idx]
        ], ignore_index=True)
        
        print(f'  Train size: {len(df_train_current)}')
        
        # Create model
        model, fit_fn, predict_fn = model_fn()
        
        # Prepare training data
        train_data = df_train_current[['datetime', target_variable]].copy()
        
        # Fit model
        model_fit = fit_fn(model, train_data)
        
        # Make forecast
        week_forecast = predict_fn(model_fit, forecast_horizon, train_data)
        
        # Get actuals
        test_end_idx = min(test_start_idx + step_size, len(df_test))
        week_actual = df_test.iloc[test_start_idx:test_end_idx][target_variable].values
        
        # Store results
        all_forecasts.extend(week_forecast[:len(week_actual)])
        all_actuals.extend(week_actual)
    
    # Calculate metrics
    all_forecasts = np.array(all_forecasts)
    all_actuals = np.array(all_actuals)
    mae = mean_absolute_error(all_actuals, all_forecasts)
    rmse = np.sqrt(mean_squared_error(all_actuals, all_forecasts))
    
    print(f'\n{model_name} - {target_variable.upper()} Results:')
    print(f'  MAE: {mae:.2f}')
    print(f'  RMSE: {rmse:.2f}')
    
    return {
        'forecasts': all_forecasts,
        'actuals': all_actuals,
        'mae': mae,
        'rmse': rmse
    }

# ============================================================================
# MODEL 1: NeuralProphet
# ============================================================================

def create_neuralprophet():
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
    
    def fit_fn(model, train_data):
        train_data.columns = ['ds', 'y']
        metrics = model.fit(train_data, freq='H')
        return train_data
    
    def predict_fn(train_data, periods, _):
        future_df = model.make_future_dataframe(train_data, periods=periods)
        forecast = model.predict(future_df)
        return forecast.iloc[-periods:]['yhat1'].values
    
    return model, fit_fn, predict_fn

# Forecast pm2.5
results['NeuralProphet_pm2.5'] = walk_forward_forecast(
    'NeuralProphet', 'pm2_5', create_neuralprophet
)

# Forecast pm10
results['NeuralProphet_pm10'] = walk_forward_forecast(
    'NeuralProphet', 'pm10', create_neuralprophet
)

# ============================================================================
# MODEL 2: FBProphet
# ============================================================================

def create_fbprophet():
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True,
        seasonality_mode='multiplicative'
    )
    
    def fit_fn(model, train_data):
        train_data.columns = ['ds', 'y']
        model.fit(train_data)
        return model
    
    def predict_fn(model, periods, _):
        future_df = model.make_future_dataframe(periods=periods, freq='H')
        forecast = model.predict(future_df)
        return forecast.iloc[-periods:]['yhat'].values
    
    return model, fit_fn, predict_fn

# Forecast pm2.5
results['FBProphet_pm2.5'] = walk_forward_forecast(
    'FBProphet', 'pm2_5', create_fbprophet
)

# Forecast pm10
results['FBProphet_pm10'] = walk_forward_forecast(
    'FBProphet', 'pm10', create_fbprophet
)

# ============================================================================
# MODEL 3: SARIMAX
# ============================================================================

def create_sarimax():
    def fit_fn(_, train_data):
        train_series = train_data.iloc[:, 1].values  # Get the target variable
        model = SARIMAX(
            train_series,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 24),
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        model_fit = model.fit(disp=False)
        return model_fit
    
    def predict_fn(model_fit, periods, _):
        return model_fit.forecast(steps=periods)
    
    return None, fit_fn, predict_fn

# Forecast pm2.5
results['SARIMAX_pm2.5'] = walk_forward_forecast(
    'SARIMAX', 'pm2_5', create_sarimax
)

# Forecast pm10
results['SARIMAX_pm10'] = walk_forward_forecast(
    'SARIMAX', 'pm10', create_sarimax
)

# ============================================================================
# COMPARISON AND VISUALIZATION
# ============================================================================

print('\n' + '='*80)
print('MODEL COMPARISON')
print('='*80)

# Create comparison tables for each target
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

# Visualization
fig, axes = plt.subplots(2, 3, figsize=(20, 10))
fig.suptitle('Regime 1: Weekly Walk-forward Refit - All Models', fontsize=16, fontweight='bold')

# PM2.5 plots
models_pm25 = ['NeuralProphet_pm2.5', 'FBProphet_pm2.5', 'SARIMAX_pm2.5']
colors = ['blue', 'green', 'red']

for idx, (model_key, color) in enumerate(zip(models_pm25, colors)):
    ax = axes[0, idx]
    result = results[model_key]
    ax.plot(result['actuals'], label='Actual', alpha=0.7, color='black', linewidth=1)
    ax.plot(result['forecasts'], label='Forecast', alpha=0.7, color=color, linewidth=1)
    ax.set_title(f"{model_key.replace('_', ' - ').replace('pm2.5', 'PM2.5')}\n"
                 f"MAE: {result['mae']:.2f}, RMSE: {result['rmse']:.2f}", 
                 fontweight='bold')
    ax.set_ylabel('PM2.5')
    ax.legend()
    ax.grid(True, alpha=0.3)

# PM10 plots
models_pm10 = ['NeuralProphet_pm10', 'FBProphet_pm10', 'SARIMAX_pm10']

for idx, (model_key, color) in enumerate(zip(models_pm10, colors)):
    ax = axes[1, idx]
    result = results[model_key]
    ax.plot(result['actuals'], label='Actual', alpha=0.7, color='black', linewidth=1)
    ax.plot(result['forecasts'], label='Forecast', alpha=0.7, color=color, linewidth=1)
    ax.set_title(f"{model_key.replace('_', ' - ').upper()}\n"
                 f"MAE: {result['mae']:.2f}, RMSE: {result['rmse']:.2f}", 
                 fontweight='bold')
    ax.set_xlabel('Hour')
    ax.set_ylabel('PM10')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('./regime1_all_models_both_targets.png', dpi=300, bbox_inches='tight')
plt.show()

# Save all results to CSV
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
print('  - ./regime1_all_models_both_targets.png (visualization)')
print('='*80)
