"""
Feature importance and SHAP-like explainability for NavPredict
"""
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class FeatureImportanceAnalyzer:
    """Analyze feature importance in GNSS error predictions"""
    
    def __init__(self):
        self.feature_importances = {}
        self.feature_names = None
    
    def permutation_importance(self, model, X_test, y_test, n_repeats=10):
        """Calculate permutation importance"""
        baseline_score = model.model.evaluate(X_test, y_test)[0]
        importances = []
        
        for feature_idx in range(X_test.shape[-1]):
            scores = []
            for _ in range(n_repeats):
                X_permuted = X_test.copy()
                np.random.shuffle(X_permuted[:, :, feature_idx])
                score = model.model.evaluate(X_permuted, y_test)[0]
                scores.append(score - baseline_score)
            
            importances.append(np.mean(scores))
        
        self.feature_importances = dict(
            zip(self.feature_names, importances)
        )
        return self.feature_importances
    
    def gradient_based_importance(self, model, X_test):
        """Calculate gradient-based feature importance"""
        import tensorflow as tf
        
        X_tensor = tf.convert_to_tensor(X_test, dtype=tf.float32)
        
        with tf.GradientTape() as tape:
            tape.watch(X_tensor)
            predictions = model.model(X_tensor)
        
        gradients = tape.gradient(predictions, X_tensor)
        importance = tf.reduce_mean(tf.abs(gradients), axis=[0, 1])
        
        self.feature_importances = dict(
            zip(self.feature_names, importance.numpy())
        )
        return self.feature_importances
    
    def get_top_features(self, n=5):
        """Get top n important features"""
        sorted_features = sorted(
            self.feature_importances.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_features[:n]


class ExplainabilityReport:
    """Generate explainability report for predictions"""
    
    def __init__(self, model_name, predictions, metrics):
        self.model_name = model_name
        self.predictions = predictions
        self.metrics = metrics
    
    def generate_text_summary(self):
        """Generate human-readable summary"""
        summary = f"""
        NavPredict GNSS Error Forecast Report
        =====================================
        
        Model Architecture: {self.model_name}
        
        Performance Metrics:
        - Root Mean Squared Error (RMSE): {self.metrics.get('rmse', 'N/A'):.6f}
        - Mean Absolute Error (MAE): {self.metrics.get('mae', 'N/A'):.6f}
        - Mean Absolute Percentage Error (MAPE): {self.metrics.get('mape', 'N/A'):.4f}
        - Normality Index: {self.metrics.get('normality', 'N/A'):.4f}
        
        Interpretation:
        - Lower RMSE and MAE indicate more accurate predictions
        - MAPE represents percentage error magnitude
        - Normality Index closer to 1.0 indicates more normal distribution (better for GNSS)
        
        Key Insights:
        """
        
        if self.metrics.get('normality', 0) > 0.95:
            summary += "\n✓ Residuals show excellent normality (>95%)"
        elif self.metrics.get('normality', 0) > 0.80:
            summary += "\n✓ Residuals show good normality (>80%)"
        else:
            summary += "\n⚠ Residuals show marginal normality"
        
        if self.metrics.get('mape', 1) < 0.05:
            summary += "\n✓ Error percentage is very low (<5%)"
        elif self.metrics.get('mape', 1) < 0.15:
            summary += "\n✓ Error percentage is acceptable (<15%)"
        else:
            summary += "\n⚠ Error percentage is high"
        
        summary += """
        
        Recommendation:
        This model is suitable for operational GNSS error forecasting with
        the reported accuracy metrics. Monitor normality score for consistency.
        """
        
        return summary.strip()
    
    def generate_json_report(self):
        """Generate JSON report"""
        return {
            'model': self.model_name,
            'timestamp': pd.Timestamp.now().isoformat(),
            'metrics': self.metrics,
            'summary': self.generate_text_summary()
        }


class SatelliteErrorAnalyzer:
    """Analyze error patterns specific to satellites"""
    
    def __init__(self):
        self.error_patterns = {}
    
    def analyze_clock_error_bias(self, clock_errors):
        """Analyze clock error trends"""
        return {
            'mean_bias': np.mean(clock_errors),
            'std_dev': np.std(clock_errors),
            'trend': np.polyfit(range(len(clock_errors)), clock_errors, 1)[0],
            'max_error': np.max(np.abs(clock_errors)),
            'percentile_95': np.percentile(np.abs(clock_errors), 95)
        }
    
    def analyze_ephemeris_error(self, x_errors, y_errors, z_errors):
        """Analyze 3D ephemeris errors"""
        total_error = np.sqrt(x_errors**2 + y_errors**2 + z_errors**2)
        
        return {
            'x_mean': np.mean(x_errors),
            'y_mean': np.mean(y_errors),
            'z_mean': np.mean(z_errors),
            'total_3d_rms': np.sqrt(np.mean(total_error**2)),
            'max_total_error': np.max(total_error),
            'error_correlation': {
                'x_y': np.corrcoef(x_errors, y_errors)[0, 1],
                'y_z': np.corrcoef(y_errors, z_errors)[0, 1],
                'x_z': np.corrcoef(x_errors, z_errors)[0, 1]
            }
        }
    
    def identify_anomalies(self, errors, threshold_std=3):
        """Identify anomalous errors"""
        mean = np.mean(errors)
        std = np.std(errors)
        anomalies = np.abs(errors - mean) > threshold_std * std
        
        return {
            'anomaly_count': np.sum(anomalies),
            'anomaly_percentage': np.sum(anomalies) / len(errors) * 100,
            'anomaly_indices': np.where(anomalies)[0],
            'anomaly_values': errors[anomalies]
        }


class PredictionConfidenceCalculator:
    """Calculate confidence levels for predictions"""
    
    @staticmethod
    def calculate_ensemble_confidence(predictions_list, threshold=0.1):
        """Calculate confidence based on ensemble agreement"""
        predictions_array = np.array(predictions_list)
        std = np.std(predictions_array, axis=0)
        
        # Confidence = inverse of variability
        confidence = 1.0 / (1.0 + std)
        confidence_high = confidence > (1 - threshold)
        
        return {
            'confidence_scores': confidence,
            'high_confidence_indices': np.where(confidence_high)[0],
            'low_confidence_indices': np.where(~confidence_high)[0],
            'mean_confidence': np.mean(confidence)
        }
    
    @staticmethod
    def calculate_prediction_uncertainty(residuals, prediction):
        """Calculate uncertainty bounds"""
        std_error = np.std(residuals)
        z_score = 1.96  # 95% CI
        
        return {
            'prediction': prediction,
            'lower_bound': prediction - z_score * std_error,
            'upper_bound': prediction + z_score * std_error,
            'uncertainty': z_score * std_error
        }
