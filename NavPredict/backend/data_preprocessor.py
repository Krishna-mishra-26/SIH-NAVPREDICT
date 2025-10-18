"""
Data preprocessing module for GNSS satellite error data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handles data cleaning, alignment, and feature engineering"""
    
    def __init__(self, sequence_length=96):
        self.sequence_length = sequence_length
        
    def load_data(self, filepath):
        """Load CSV data"""
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded data with shape {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def parse_datetime(self, df):
        """Parse UTC time column"""
        df['utc_time'] = pd.to_datetime(df['utc_time'], format='%m/%d/%Y %H:%M', errors='coerce')
        df = df.dropna(subset=['utc_time'])
        df = df.sort_values('utc_time').reset_index(drop=True)
        return df
    
    def align_to_15min(self, df):
        """Align data to 15-minute intervals"""
        df = self.parse_datetime(df)
        
        # Round to nearest 15 minutes
        df['utc_time'] = df['utc_time'].dt.round('15min')
        
        # Set time index and resample
        df_aligned = df.set_index('utc_time')
        
        # Interpolate to fill missing 15-min intervals
        time_range = pd.date_range(
            start=df['utc_time'].min(),
            end=df['utc_time'].max(),
            freq='15min'
        )
        df_aligned = df_aligned.reindex(time_range)
        
        # Forward fill, then backward fill for missing values
        for col in df_aligned.columns:
            if df_aligned[col].dtype in [np.float64, np.int64]:
                df_aligned[col] = df_aligned[col].fillna(method='ffill').fillna(method='bfill')
        
        df_aligned = df_aligned.reset_index()
        df_aligned.columns = ['utc_time'] + list(df_aligned.columns[1:])
        
        logger.info(f"Aligned to 15-min intervals. Final shape: {df_aligned.shape}")
        return df_aligned
    
    def handle_missing_values(self, df, error_columns):
        """Handle missing values with interpolation and forward-fill"""
        for col in error_columns:
            if col in df.columns:
                # Linear interpolation for gaps
                df[col] = df[col].interpolate(method='linear', limit_direction='both')
                # Forward fill for remaining NaNs
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
        
        logger.info("Handled missing values")
        return df
    
    def outlier_detection(self, df, error_columns, threshold=3):
        """Detect and smooth outliers using IQR method"""
        for col in error_columns:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
                if outliers.sum() > 0:
                    # Replace outliers with mean of neighbors
                    for idx in df[outliers].index:
                        if idx > 0 and idx < len(df) - 1:
                            df.loc[idx, col] = (df.loc[idx-1, col] + df.loc[idx+1, col]) / 2
                        else:
                            df.loc[idx, col] = df[col].median()
        
        logger.info("Detected and smoothed outliers")
        return df
    
    def feature_engineering(self, df, error_columns):
        """Create lag features, rolling averages, and time-based features"""
        # Lag features (previous 1, 2, 4, 8 steps)
        for lag in [1, 2, 4, 8]:
            for col in error_columns:
                df[f'{col}_lag{lag}'] = df[col].shift(lag)
        
        # Rolling averages
        for window in [3, 6, 12]:
            for col in error_columns:
                df[f'{col}_ma{window}'] = df[col].rolling(window=window, min_periods=1).mean()
        
        # Rolling standard deviation
        for window in [3, 6, 12]:
            for col in error_columns:
                df[f'{col}_std{window}'] = df[col].rolling(window=window, min_periods=1).std()
        
        # Time-based features
        df['hour'] = df['utc_time'].dt.hour
        df['day_of_week'] = df['utc_time'].dt.dayofweek
        df['day_of_month'] = df['utc_time'].dt.day
        
        # Cyclical encoding for hour
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Drop NaN values created by lag/rolling features
        df = df.dropna()
        df = df.reset_index(drop=True)
        
        logger.info(f"Feature engineering completed. New features added. Shape: {df.shape}")
        return df
    
    def preprocess(self, filepath, error_columns):
        """Main preprocessing pipeline"""
        df = self.load_data(filepath)
        df = self.align_to_15min(df)
        df = self.handle_missing_values(df, error_columns)
        df = self.outlier_detection(df, error_columns)
        df = self.feature_engineering(df, error_columns)
        
        logger.info(f"Preprocessing complete. Final shape: {df.shape}")
        return df
    
    def get_sequences(self, data, error_columns):
        """Convert time series data into sequences for LSTM"""
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        
        return np.array(X), np.array(y)
