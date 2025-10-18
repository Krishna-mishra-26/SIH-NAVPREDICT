import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, ChevronDown } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

export const ModelTrainer = ({ uploadedFile, onTrainingComplete }) => {
  const [selectedModel, setSelectedModel] = useState('lstm');
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);

  const models = [
    { value: 'lstm', label: 'LSTM', description: 'Long Short-Term Memory RNN' },
    { value: 'transformer', label: 'Transformer', description: 'Attention-based Model' },
    { value: 'arima', label: 'ARIMA', description: 'Statistical Forecasting' },
    { value: 'gp', label: 'Gaussian Process', description: 'Probabilistic Modeling' },
  ];

  const startTraining = async () => {
    if (!uploadedFile?.filepath) {
      toast.error('Please upload data first');
      return;
    }

    setIsTraining(true);
    setMetrics(null);
    setLogs([]);
    const newLogs = [`Starting ${selectedModel.toUpperCase()} training...`];
    setLogs(newLogs);

    try {
      const response = await axios.post('http://localhost:5000/train', {
        filepath: uploadedFile.filepath,
        model_type: selectedModel,
      });

      newLogs.push('Model training completed ✓');
      setLogs(newLogs);
      setMetrics(response.data.metrics);
      setTrainingProgress(100);
      toast.success('Training completed successfully');
      onTrainingComplete?.(response.data);
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Training failed';
      newLogs.push(`Error: ${errorMsg}`);
      setLogs(newLogs);
      toast.error(errorMsg);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Model Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        {models.map((model) => (
          <motion.button
            key={model.value}
            onClick={() => setSelectedModel(model.value)}
            whileHover={{ scale: 1.02 }}
            className={`p-4 rounded-lg border-2 text-left transition-all ${
              selectedModel === model.value
                ? 'border-neon-blue bg-neon-blue/10'
                : 'border-neon-blue/30 hover:border-neon-blue/60'
            }`}
          >
            <h4 className="text-white font-poppins font-semibold">{model.label}</h4>
            <p className="text-neon-blue/70 text-sm">{model.description}</p>
          </motion.button>
        ))}
      </motion.div>

      {/* Training Controls */}
      <div className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-poppins font-semibold">Training Settings</h3>
          <button
            onClick={startTraining}
            disabled={isTraining}
            className="bg-neon-blue text-space-dark px-6 py-2 rounded font-poppins font-semibold hover:bg-neon-yellow transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {isTraining ? <Pause size={18} /> : <Play size={18} />}
            {isTraining ? 'Training...' : 'Start Training'}
          </button>
        </div>

        {isTraining && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-neon-blue text-sm">Progress</p>
              <p className="text-white font-semibold">{trainingProgress}%</p>
            </div>
            <div className="w-full bg-space-dark rounded-full h-3">
              <motion.div
                animate={{ width: `${trainingProgress}%` }}
                className="bg-gradient-to-r from-neon-blue to-neon-yellow h-3 rounded-full"
              />
            </div>
          </div>
        )}
      </div>

      {/* Training Logs */}
      <div className="bg-space-dark/50 rounded-lg p-4 border border-neon-blue/30 h-32 overflow-y-auto font-mono text-xs">
        {logs.length === 0 ? (
          <p className="text-neon-blue/50">Logs will appear here...</p>
        ) : (
          logs.map((log, idx) => (
            <p key={idx} className="text-neon-blue/70">
              {'>'} {log}
            </p>
          ))
        )}
      </div>

      {/* Metrics Display */}
      {metrics && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          <div className="bg-space-blue/50 rounded-lg p-4 border border-neon-green/30">
            <p className="text-neon-blue text-xs font-poppins">RMSE</p>
            <p className="text-white text-2xl font-bold font-poppins">
              {metrics.rmse?.toFixed(4)}
            </p>
          </div>
          <div className="bg-space-blue/50 rounded-lg p-4 border border-neon-green/30">
            <p className="text-neon-blue text-xs font-poppins">MAE</p>
            <p className="text-white text-2xl font-bold font-poppins">
              {metrics.mae?.toFixed(4)}
            </p>
          </div>
          <div className="bg-space-blue/50 rounded-lg p-4 border border-neon-green/30">
            <p className="text-neon-blue text-xs font-poppins">MAPE</p>
            <p className="text-white text-2xl font-bold font-poppins">
              {(metrics.mape * 100)?.toFixed(2)}%
            </p>
          </div>
          <div className="bg-space-blue/50 rounded-lg p-4 border border-neon-green/30">
            <p className="text-neon-blue text-xs font-poppins">Normality</p>
            <p className="text-white text-2xl font-bold font-poppins">
              {(metrics.normality * 100)?.toFixed(2)}%
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
};
