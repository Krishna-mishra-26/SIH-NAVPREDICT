"""
Advanced ML model implementations and utilities for NavPredict
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class EnsembleForecaster:
    """Ensemble of multiple models for better predictions"""
    
    def __init__(self, models, weights=None):
        self.models = models
        if weights is None:
            weights = [1.0 / len(models)] * len(models)
        self.weights = np.array(weights) / np.sum(weights)
    
    def predict(self, X):
        """Make ensemble predictions"""
        predictions = []
        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Weighted average
        ensemble_pred = np.average(
            predictions,
            axis=0,
            weights=self.weights
        )
        return ensemble_pred


class HybridForecaster:
    """Hybrid model combining statistical and deep learning approaches"""
    
    def __init__(self, arima_model=None, lstm_model=None, arima_weight=0.3):
        self.arima_model = arima_model
        self.lstm_model = lstm_model
        self.arima_weight = arima_weight
        self.lstm_weight = 1.0 - arima_weight
    
    def predict(self, X_arima, X_lstm):
        """Hybrid prediction"""
        arima_pred = self.arima_model.predict(len(X_arima)) if self.arima_model else 0
        lstm_pred = self.lstm_model.predict(X_lstm) if self.lstm_model else 0
        
        return (self.arima_weight * arima_pred + 
                self.lstm_weight * lstm_pred)


class AdaptiveForecaster:
    """Adaptive forecaster that adjusts model parameters based on data characteristics"""
    
    def __init__(self):
        self.volatility_history = []
        self.model = None
    
    def update_parameters(self, recent_data):
        """Update model parameters based on recent volatility"""
        volatility = np.std(recent_data)
        self.volatility_history.append(volatility)
        
        # Adjust hyperparameters if volatility changes significantly
        if len(self.volatility_history) > 1:
            volatility_change = abs(
                self.volatility_history[-1] - self.volatility_history[-2]
            ) / self.volatility_history[-2]
            
            if volatility_change > 0.5:  # Significant change
                logger.info(f"Volatility changed by {volatility_change*100:.2f}%")
                self._adapt_model()
    
    def _adapt_model(self):
        """Adapt model parameters"""
        # Implementation depends on specific model type
        pass


class ConfidenceIntervalCalculator:
    """Calculate confidence intervals for predictions"""
    
    @staticmethod
    def bootstrap_ci(predictions, residuals, n_bootstrap=1000, ci=0.95):
        """Calculate confidence intervals using bootstrap"""
        np.random.seed(42)
        bootstrap_samples = []
        
        for _ in range(n_bootstrap):
            bootstrap_residuals = np.random.choice(residuals, size=len(residuals))
            bootstrap_pred = predictions + bootstrap_residuals.mean()
            bootstrap_samples.append(bootstrap_pred)
        
        bootstrap_samples = np.array(bootstrap_samples)
        alpha = 1 - ci
        lower = np.percentile(bootstrap_samples, alpha/2 * 100, axis=0)
        upper = np.percentile(bootstrap_samples, (1 - alpha/2) * 100, axis=0)
        
        return lower, upper
    
    @staticmethod
    def quantile_ci(predictions, residuals, ci=0.95):
        """Calculate confidence intervals using quantiles"""
        residual_std = np.std(residuals)
        z_score = 1.96  # 95% CI
        margin = z_score * residual_std
        
        lower = predictions - margin
        upper = predictions + margin
        
        return lower, upper


class HorizonSpecificEvaluator:
    """Evaluate model performance at different prediction horizons"""
    
    def __init__(self, horizons=[1, 2, 4, 8, 96]):
        self.horizons = horizons
        self.results = {}
    
    def evaluate(self, y_true, y_pred):
        """Evaluate at multiple horizons"""
        from ml_models import MetricsCalculator
        
        for horizon in self.horizons:
            if horizon <= len(y_true):
                y_true_h = y_true[:horizon]
                y_pred_h = y_pred[:horizon]
                metrics = MetricsCalculator.calculate_metrics(y_true_h, y_pred_h)
                self.results[horizon] = metrics
        
        return self.results
    
    def get_summary(self):
        """Get summary of results across horizons"""
        summary = []
        for horizon, metrics in self.results.items():
            summary.append({
                'horizon_steps': horizon,
                'horizon_hours': horizon * 0.25,
                'rmse': metrics['rmse'],
                'mae': metrics['mae'],
                'mape': metrics['mape'],
                'normality': metrics['normality']
            })
        return pd.DataFrame(summary)


class SatelliteTypeSpecificModel:
    """Model specialized for different satellite types (GEO, MEO)"""
    
    def __init__(self, satellite_type='MEO'):
        self.satellite_type = satellite_type
        self.model = None
        self._set_hyperparameters()
    
    def _set_hyperparameters(self):
        """Set hyperparameters based on satellite type"""
        if self.satellite_type == 'GEO':
            # GEO satellites are more stable
            self.learning_rate = 0.0005
            self.epochs = 50
        elif self.satellite_type == 'MEO':
            # MEO satellites have more variation
            self.learning_rate = 0.001
            self.epochs = 100
        else:
            # Default
            self.learning_rate = 0.001
            self.epochs = 100
