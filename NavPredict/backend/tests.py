"""
Unit tests for NavPredict backend
"""
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import os

from data_preprocessor import DataPreprocessor
from ml_models import (
    MetricsCalculator, LSTMForecaster, ARIMAForecaster,
    TransformerForecaster, GaussianProcessForecaster
)


class TestDataPreprocessor(unittest.TestCase):
    """Test data preprocessing functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.preprocessor = DataPreprocessor(sequence_length=96)
        
        # Create sample data
        dates = pd.date_range('2025-01-01', periods=100, freq='15min')
        self.df = pd.DataFrame({
            'utc_time': dates,
            'x_error (m)': np.random.randn(100) * 0.1,
            'y_error (m)': np.random.randn(100) * 0.1,
            'z_error (m)': np.random.randn(100) * 0.1,
            'satclockerror (m)': np.random.randn(100) * 0.05,
        })
    
    def test_parse_datetime(self):
        """Test datetime parsing"""
        df_parsed = self.preprocessor.parse_datetime(self.df.copy())
        self.assertIsNotNone(df_parsed)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_parsed['utc_time']))
    
    def test_align_to_15min(self):
        """Test 15-minute alignment"""
        df_aligned = self.preprocessor.align_to_15min(self.df.copy())
        self.assertGreaterEqual(len(df_aligned), len(self.df))
    
    def test_handle_missing_values(self):
        """Test missing value handling"""
        df_with_nan = self.df.copy()
        df_with_nan.loc[10:15, 'x_error (m)'] = np.nan
        
        df_clean = self.preprocessor.handle_missing_values(
            df_with_nan, ['x_error (m)', 'y_error (m)', 'z_error (m)', 'satclockerror (m)']
        )
        
        self.assertEqual(df_clean.isnull().sum().sum(), 0)
    
    def test_outlier_detection(self):
        """Test outlier detection"""
        df_with_outliers = self.df.copy()
        df_with_outliers.loc[5, 'x_error (m)'] = 10.0  # Obvious outlier
        
        df_clean = self.preprocessor.outlier_detection(df_with_outliers, ['x_error (m)'])
        
        # Value should be modified
        self.assertNotEqual(df_clean.loc[5, 'x_error (m)'], 10.0)
    
    def test_feature_engineering(self):
        """Test feature engineering"""
        df_engineered = self.preprocessor.feature_engineering(
            self.df.copy(), ['x_error (m)', 'y_error (m)']
        )
        
        # Check new features were created
        self.assertIn('x_error (m)_lag1', df_engineered.columns)
        self.assertIn('hour_sin', df_engineered.columns)


class TestMetricsCalculator(unittest.TestCase):
    """Test metrics calculation"""
    
    def setUp(self):
        """Set up test data"""
        self.y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.y_pred = np.array([1.1, 1.9, 3.1, 3.9, 5.1])
    
    def test_rmse(self):
        """Test RMSE calculation"""
        rmse = MetricsCalculator.rmse(self.y_true, self.y_pred)
        self.assertGreater(rmse, 0)
        self.assertLess(rmse, 0.2)  # Should be small for close predictions
    
    def test_mae(self):
        """Test MAE calculation"""
        mae = MetricsCalculator.mae(self.y_true, self.y_pred)
        self.assertGreater(mae, 0)
        self.assertLess(mae, 0.2)
    
    def test_mape(self):
        """Test MAPE calculation"""
        mape = MetricsCalculator.mape(self.y_true, self.y_pred)
        self.assertGreaterEqual(mape, 0)
        self.assertLess(mape, 1.0)
    
    def test_normality_score(self):
        """Test normality scoring"""
        normal_residuals = np.random.normal(0, 1, 100)
        score = MetricsCalculator.normality_score(normal_residuals)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)


class TestLSTMForecaster(unittest.TestCase):
    """Test LSTM model"""
    
    def setUp(self):
        """Set up test data"""
        self.input_dim = 4
        self.sequence_length = 96
        
        # Create dummy data
        self.X_train = np.random.randn(100, self.sequence_length, self.input_dim)
        self.y_train = np.random.randn(100, self.input_dim)
        self.X_test = np.random.randn(20, self.sequence_length, self.input_dim)
        self.y_test = np.random.randn(20, self.input_dim)
    
    def test_model_building(self):
        """Test LSTM model building"""
        model = LSTMForecaster(
            input_dim=self.input_dim,
            sequence_length=self.sequence_length
        )
        model.build_model()
        
        self.assertIsNotNone(model.model)
    
    def test_prediction_shape(self):
        """Test prediction output shape"""
        model = LSTMForecaster(
            input_dim=self.input_dim,
            sequence_length=self.sequence_length
        )
        model.build_model()
        
        predictions = model.predict(self.X_test)
        
        self.assertEqual(predictions.shape, self.y_test.shape)


class TestDataIntegration(unittest.TestCase):
    """Integration tests for data pipeline"""
    
    def setUp(self):
        """Set up test data"""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, 'test_data.csv')
        
        # Create test CSV
        dates = pd.date_range('2025-01-01', periods=200, freq='15min')
        df = pd.DataFrame({
            'utc_time': dates.strftime('%m/%d/%Y %H:%M'),
            'x_error (m)': np.random.randn(200) * 0.1,
            'y_error (m)': np.random.randn(200) * 0.1,
            'z_error (m)': np.random.randn(200) * 0.1,
            'satclockerror (m)': np.random.randn(200) * 0.05,
        })
        df.to_csv(self.csv_path, index=False)
    
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline"""
        preprocessor = DataPreprocessor(sequence_length=96)
        
        df = preprocessor.preprocess(
            self.csv_path,
            ['x_error (m)', 'y_error (m)', 'z_error (m)', 'satclockerror (m)']
        )
        
        # Check output
        self.assertGreater(len(df), 0)
        self.assertIn('hour_sin', df.columns)
        self.assertEqual(df.isnull().sum().sum(), 0)


class TestModelEvaluation(unittest.TestCase):
    """Test model evaluation functionality"""
    
    def test_metrics_calculation(self):
        """Test comprehensive metrics"""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 1.9, 3.1, 3.9, 5.1])
        
        metrics = MetricsCalculator.calculate_metrics(y_true, y_pred)
        
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('mape', metrics)
        self.assertIn('normality', metrics)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
