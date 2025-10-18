"""
ML Models for GNSS error forecasting
"""
import numpy as np
import pandas as pd
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from scipy.stats import normaltest, kstest
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate evaluation metrics"""
    
    @staticmethod
    def rmse(y_true, y_pred):
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    @staticmethod
    def mae(y_true, y_pred):
        return mean_absolute_error(y_true, y_pred)
    
    @staticmethod
    def mape(y_true, y_pred):
        return mean_absolute_percentage_error(y_true, y_pred)
    
    @staticmethod
    def normality_score(residuals):
        """
        Calculate normality score using Shapiro-Wilk test
        Returns p-value (0-1): Higher is better (closer to 1 = more normal)
        """
        try:
            _, p_value = normaltest(residuals)
            return min(p_value, 1.0)
        except:
            return 0.0
    
    @staticmethod
    def calculate_metrics(y_true, y_pred):
        """Calculate all metrics"""
        residuals = y_true - y_pred
        return {
            'rmse': MetricsCalculator.rmse(y_true, y_pred),
            'mae': MetricsCalculator.mae(y_true, y_pred),
            'mape': MetricsCalculator.mape(y_true, y_pred),
            'normality': MetricsCalculator.normality_score(residuals)
        }


class LSTMForecaster:
    """LSTM model for time series forecasting"""
    
    def __init__(self, input_dim, sequence_length, hidden_dim=128, num_layers=2, dropout=0.2):
        self.input_dim = input_dim
        self.sequence_length = sequence_length
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        self.model = None
        self.scaler = MinMaxScaler()
    
    def build_model(self):
        """Build LSTM model"""
        model = keras.Sequential()
        
        # Input layer
        model.add(keras.Input(shape=(self.sequence_length, self.input_dim)))
        
        # LSTM layers
        for i in range(self.num_layers):
            return_sequences = i < self.num_layers - 1
            model.add(layers.LSTM(
                self.hidden_dim,
                return_sequences=return_sequences,
                dropout=self.dropout
            ))
        
        # Dense layers
        model.add(layers.Dense(64, activation='relu'))
        model.add(layers.Dropout(self.dropout))
        model.add(layers.Dense(self.input_dim))
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        logger.info(f"Built LSTM model with input_dim={self.input_dim}")
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """Train LSTM model"""
        if self.model is None:
            self.build_model()
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        logger.info("LSTM training completed")
        return history
    
    def predict(self, X):
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)
    
    def evaluate(self, y_true, y_pred):
        """Evaluate model"""
        return MetricsCalculator.calculate_metrics(y_true, y_pred)


class ARIMAForecaster:
    """ARIMA model for time series forecasting"""
    
    def __init__(self, order=(1, 1, 1)):
        self.order = order
        self.model = None
        self.fitted_model = None
    
    def fit(self, data):
        """Fit ARIMA model"""
        try:
            self.fitted_model = ARIMA(data, order=self.order).fit()
            logger.info(f"Fitted ARIMA{self.order} model")
            return self
        except Exception as e:
            logger.error(f"ARIMA fitting failed: {e}")
            raise
    
    def predict(self, steps):
        """Make predictions"""
        if self.fitted_model is None:
            raise ValueError("Model not fitted yet")
        
        try:
            forecast = self.fitted_model.get_forecast(steps=steps)
            return forecast.predicted_mean.values
        except Exception as e:
            logger.error(f"ARIMA prediction failed: {e}")
            raise
    
    def evaluate(self, y_true, y_pred):
        """Evaluate model"""
        return MetricsCalculator.calculate_metrics(y_true, y_pred)


class GaussianProcessForecaster:
    """Gaussian Process for probabilistic forecasting"""
    
    def __init__(self, kernel_type='rbf', alpha=1e-6):
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, Matern
        
        if kernel_type == 'rbf':
            kernel = RBF(1.0)
        else:
            kernel = Matern(nu=1.5)
        
        self.model = GaussianProcessRegressor(
            kernel=kernel,
            alpha=alpha,
            normalize_y=True,
            n_restarts_optimizer=10
        )
        self.scaler = MinMaxScaler()
    
    def fit(self, X_train, y_train):
        """Fit GP model"""
        X_scaled = self.scaler.fit_transform(X_train.reshape(-1, 1))
        self.model.fit(X_scaled, y_train)
        logger.info("Fitted Gaussian Process model")
        return self
    
    def predict(self, X_test):
        """Predict with uncertainty"""
        X_scaled = self.scaler.transform(X_test.reshape(-1, 1))
        predictions, std = self.model.predict(X_scaled, return_std=True)
        return predictions, std
    
    def evaluate(self, y_true, y_pred):
        """Evaluate model"""
        return MetricsCalculator.calculate_metrics(y_true, y_pred)


class TransformerForecaster:
    """Transformer model for time series forecasting"""
    
    def __init__(self, input_dim, sequence_length, num_heads=8, num_layers=2, d_model=128):
        self.input_dim = input_dim
        self.sequence_length = sequence_length
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.d_model = d_model
        self.model = None
        self.scaler = MinMaxScaler()
    
    def build_model(self):
        """Build Transformer model"""
        inputs = keras.Input(shape=(self.sequence_length, self.input_dim))
        x = inputs
        
        # Transformer blocks
        for _ in range(self.num_layers):
            # Multi-head attention
            attention_output = layers.MultiHeadAttention(
                num_heads=self.num_heads,
                key_dim=self.d_model // self.num_heads
            )(x, x)
            x = layers.Add()([x, attention_output])
            x = layers.LayerNormalization()(x)
            
            # Feed forward
            ffn_output = layers.Dense(self.d_model * 2, activation='relu')(x)
            ffn_output = layers.Dense(self.d_model)(ffn_output)
            x = layers.Add()([x, ffn_output])
            x = layers.LayerNormalization()(x)
        
        # Output layer
        x = layers.GlobalAveragePooling1D()(x)
        outputs = layers.Dense(self.input_dim)(x)
        
        model = keras.Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        logger.info("Built Transformer model")
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """Train Transformer model"""
        if self.model is None:
            self.build_model()
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        logger.info("Transformer training completed")
        return history
    
    def predict(self, X):
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)
    
    def evaluate(self, y_true, y_pred):
        """Evaluate model"""
        return MetricsCalculator.calculate_metrics(y_true, y_pred)
