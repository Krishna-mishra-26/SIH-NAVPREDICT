"""
Main Flask API for NavPredict GNSS Error Forecasting System
"""
import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
import io

from config import (
    UPLOAD_FOLDER, PREDICTIONS_FOLDER, MODELS_FOLDER,
    ERROR_COLUMNS, SATELLITE_TYPES, SEQUENCE_LENGTH, PREDICTION_HORIZON,
    BATCH_SIZE, EPOCHS, LEARNING_RATE
)
from data_preprocessor import DataPreprocessor
from ml_models import LSTMForecaster, ARIMAForecaster, GaussianProcessForecaster, TransformerForecaster, MetricsCalculator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config')
CORS(app)

# Global state for tracking training
training_state = {
    'status': 'idle',  # idle, training, completed, error
    'progress': 0,
    'current_model': None,
    'metrics': {}
}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'NavPredict Backend'}), 200


@app.route('/upload', methods=['POST'])
def upload_data():
    """Upload satellite error data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only CSV and JSON files allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filename}")
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': filename,
            'filepath': filepath
        }), 200
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/preprocess', methods=['POST'])
def preprocess_data():
    """Preprocess uploaded data"""
    try:
        data = request.json
        filepath = data.get('filepath')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'Invalid filepath'}), 400
        
        preprocessor = DataPreprocessor(sequence_length=SEQUENCE_LENGTH)
        processed_df = preprocessor.preprocess(filepath, ERROR_COLUMNS)
        
        # Save preprocessed data
        processed_filename = f"processed_{os.path.basename(filepath)}"
        processed_path = os.path.join(UPLOAD_FOLDER, processed_filename)
        processed_df.to_csv(processed_path, index=False)
        
        logger.info(f"Data preprocessed: {processed_filename}")
        
        return jsonify({
            'success': True,
            'message': 'Data preprocessed successfully',
            'shape': processed_df.shape,
            'columns': list(processed_df.columns),
            'processed_filepath': processed_path,
            'data_sample': processed_df.head(5).to_dict(orient='records')
        }), 200
        
    except Exception as e:
        logger.error(f"Preprocessing error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/train', methods=['POST'])
def train_model():
    """Train ML model"""
    try:
        global training_state
        
        data = request.json
        filepath = data.get('filepath')
        model_type = data.get('model_type', 'lstm')  # lstm, arima, transformer, gp
        satellite_type = data.get('satellite_type', 'MEO')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'Invalid filepath'}), 400
        
        training_state['status'] = 'training'
        training_state['current_model'] = model_type
        training_state['progress'] = 0
        
        # Load preprocessed data
        df = pd.read_csv(filepath)
        
        # Extract error columns
        error_data = df[ERROR_COLUMNS].values
        
        # Normalize data
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(error_data)
        
        # Create sequences
        preprocessor = DataPreprocessor(sequence_length=SEQUENCE_LENGTH)
        X, y = preprocessor.get_sequences(normalized_data, ERROR_COLUMNS)
        
        # Split data
        train_size = int(len(X) * 0.7)
        val_size = int(len(X) * 0.15)
        
        X_train = X[:train_size]
        y_train = y[:train_size]
        X_val = X[train_size:train_size + val_size]
        y_val = y[train_size:train_size + val_size]
        X_test = X[train_size + val_size:]
        y_test = y[train_size + val_size:]
        
        logger.info(f"Training {model_type} model with shapes: X_train={X_train.shape}, X_test={X_test.shape}")
        
        # Train appropriate model
        if model_type == 'lstm':
            model = LSTMForecaster(
                input_dim=len(ERROR_COLUMNS),
                sequence_length=SEQUENCE_LENGTH,
                hidden_dim=128,
                num_layers=2
            )
            model.build_model()
            model.train(X_train, y_train, X_val, y_val, epochs=EPOCHS, batch_size=BATCH_SIZE)
            y_pred = model.predict(X_test)
            
        elif model_type == 'transformer':
            model = TransformerForecaster(
                input_dim=len(ERROR_COLUMNS),
                sequence_length=SEQUENCE_LENGTH,
                num_heads=8,
                num_layers=2
            )
            model.build_model()
            model.train(X_train, y_train, X_val, y_val, epochs=EPOCHS, batch_size=BATCH_SIZE)
            y_pred = model.predict(X_test)
            
        elif model_type == 'arima':
            # For ARIMA, use univariate approach on first error component
            data_to_fit = df[ERROR_COLUMNS[0]].values
            model = ARIMAForecaster(order=(5, 1, 2))
            model.fit(data_to_fit[:train_size])
            y_pred = model.predict(len(X_test))
            y_test = y_test[:, 0]  # First component only
            
        else:  # gp
            model = GaussianProcessForecaster()
            X_train_flat = np.arange(len(y_train))
            model.fit(X_train_flat, y_train[:, 0])
            X_test_flat = np.arange(len(y_test))
            y_pred, _ = model.predict(X_test_flat)
            y_test = y_test[:, 0]
        
        # Calculate metrics
        metrics = MetricsCalculator.calculate_metrics(y_test, y_pred)
        training_state['metrics'] = metrics
        training_state['status'] = 'completed'
        training_state['progress'] = 100
        
        logger.info(f"Training completed. Metrics: {metrics}")
        
        return jsonify({
            'success': True,
            'message': f'{model_type} model trained successfully',
            'model_type': model_type,
            'metrics': metrics,
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }), 200
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        training_state['status'] = 'error'
        return jsonify({'error': str(e)}), 500


@app.route('/training-status', methods=['GET'])
def get_training_status():
    """Get current training status"""
    return jsonify(training_state), 200


@app.route('/predict', methods=['POST'])
def predict():
    """Make predictions for future errors"""
    try:
        data = request.json
        filepath = data.get('filepath')
        model_type = data.get('model_type', 'lstm')
        horizon_days = data.get('horizon_days', 1)
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'Invalid filepath'}), 400
        
        # Load data
        df = pd.read_csv(filepath)
        last_timestamp = pd.to_datetime(df['utc_time'].iloc[-1])
        
        # Prepare prediction data
        error_data = df[ERROR_COLUMNS].values
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(error_data)
        
        # Use last sequence for prediction
        last_sequence = normalized_data[-SEQUENCE_LENGTH:]
        
        # Generate predictions
        predictions = []
        timestamps = []
        current_time = last_timestamp
        
        for i in range(horizon_days * 96):  # 96 * 15min = 24h
            current_time += timedelta(minutes=15)
            timestamps.append(current_time)
            
            # Simple naive forecast: use last value
            # In production, would use trained model
            pred = normalized_data[-1] + np.random.normal(0, 0.01, len(ERROR_COLUMNS))
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Denormalize
        predictions_denorm = scaler.inverse_transform(predictions)
        
        # Create results dataframe
        results_df = pd.DataFrame({
            'utc_time': timestamps,
            'x_error_pred (m)': predictions_denorm[:, 0],
            'y_error_pred (m)': predictions_denorm[:, 1],
            'z_error_pred (m)': predictions_denorm[:, 2],
            'satclockerror_pred (m)': predictions_denorm[:, 3]
        })
        
        # Save predictions
        pred_filename = f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        pred_path = os.path.join(PREDICTIONS_FOLDER, pred_filename)
        results_df.to_csv(pred_path, index=False)
        
        logger.info(f"Predictions generated: {pred_filename}")
        
        return jsonify({
            'success': True,
            'message': 'Predictions generated successfully',
            'predictions_file': pred_filename,
            'predictions_filepath': pred_path,
            'total_predictions': len(results_df),
            'data_sample': results_df.head(10).to_dict(orient='records')
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/export-predictions', methods=['GET'])
def export_predictions():
    """Download predictions as CSV"""
    try:
        filename = request.args.get('filename')
        filepath = os.path.join(PREDICTIONS_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename), 200
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/models', methods=['GET'])
def get_available_models():
    """Get list of available models"""
    return jsonify({
        'models': [
            {'name': 'LSTM', 'value': 'lstm', 'description': 'Long Short-Term Memory RNN'},
            {'name': 'Transformer', 'value': 'transformer', 'description': 'Transformer with attention'},
            {'name': 'ARIMA', 'value': 'arima', 'description': 'AutoRegressive Integrated Moving Average'},
            {'name': 'Gaussian Process', 'value': 'gp', 'description': 'Gaussian Process Regression'}
        ]
    }), 200


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'json'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
