"""
Configuration settings for NavPredict backend
"""
import os
from datetime import timedelta

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
ALLOWED_EXTENSIONS = {'csv', 'json'}

# Model Configuration
MODELS_FOLDER = os.path.join(os.path.dirname(__file__), 'models')
PREDICTIONS_FOLDER = os.path.join(os.path.dirname(__file__), 'predictions')

# Data Configuration
SEQUENCE_LENGTH = 96  # 96 * 15min = 24 hours lookback window
PREDICTION_HORIZON = 96  # Predict next 24 hours (96 * 15min intervals)
SATELLITE_TYPES = ['GEO', 'MEO']
ERROR_COLUMNS = ['x_error (m)', 'y_error (m)', 'z_error (m)', 'satclockerror (m)']

# ML Model Configuration
LSTM_HIDDEN_DIM = 128
LSTM_NUM_LAYERS = 2
LSTM_DROPOUT = 0.2
BATCH_SIZE = 32
EPOCHS = 100
LEARNING_RATE = 0.001
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# Evaluation Metrics
PREDICTION_HORIZONS = [1, 2, 4, 8, 96]  # 15min, 30min, 1h, 2h, 24h
NORMALITY_TEST_THRESHOLD = 0.05  # p-value threshold for normality tests

# Create required folders
for folder in [UPLOAD_FOLDER, MODELS_FOLDER, PREDICTIONS_FOLDER]:
    os.makedirs(folder, exist_ok=True)
