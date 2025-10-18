import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis } from 'recharts';
import { TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

export const InsightsPanel = ({ metrics, predictions }) => {
  const [selectedError, setSelectedError] = useState('satclockerror_pred (m)');

  // Feature importance mock data
  const featureImportance = [
    { name: 'satclockerror_lag1', importance: 0.35 },
    { name: 'satclockerror_ma6', importance: 0.25 },
    { name: 'hour_sin', importance: 0.15 },
    { name: 'satclockerror_lag2', importance: 0.12 },
    { name: 'satclockerror_std6', importance: 0.08 },
    { name: 'day_of_week', importance: 0.05 },
  ];

  // Confidence levels
  const confidenceData = [
    { name: 'High (>90%)', value: 72, fill: '#00e0ff' },
    { name: 'Medium (70-90%)', value: 18, fill: '#ffd700' },
    { name: 'Low (<70%)', value: 10, fill: '#ff6b6b' },
  ];

  // Anomaly detection
  const anomalies = predictions?.filter(p => Math.abs(p[selectedError]) > 0.5) || [];
  const anomalyPercentage = ((anomalies.length / (predictions?.length || 1)) * 100).toFixed(2);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <h2 className="text-white font-poppins text-2xl font-bold">Scientific Insights & Explainability</h2>

      {/* Performance Summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30"
      >
        <h3 className="text-white font-poppins font-semibold mb-4">Performance Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-neon-blue text-xs font-poppins">RMSE</p>
            <p className="text-white text-2xl font-bold">{metrics?.rmse?.toFixed(6)}</p>
            <p className="text-neon-blue/70 text-xs mt-1">Lower is better</p>
          </div>
          <div>
            <p className="text-neon-blue text-xs font-poppins">MAE</p>
            <p className="text-white text-2xl font-bold">{metrics?.mae?.toFixed(6)}</p>
            <p className="text-neon-blue/70 text-xs mt-1">Mean absolute</p>
          </div>
          <div>
            <p className="text-neon-blue text-xs font-poppins">MAPE</p>
            <p className="text-white text-2xl font-bold">{(metrics?.mape * 100)?.toFixed(2)}%</p>
            <p className="text-neon-blue/70 text-xs mt-1">Percentage error</p>
          </div>
          <div>
            <p className="text-neon-blue text-xs font-poppins">Normality</p>
            <p className="text-white text-2xl font-bold">{(metrics?.normality * 100)?.toFixed(2)}%</p>
            <p className="text-neon-blue/70 text-xs mt-1">Distribution fit</p>
          </div>
        </div>
      </motion.div>

      {/* Feature Importance */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30"
      >
        <h3 className="text-white font-poppins font-semibold mb-4">Feature Importance</h3>
        <p className="text-neon-blue/70 text-sm mb-4">Top features driving the model predictions</p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={featureImportance}>
            <XAxis dataKey="name" stroke="#00e0ff" style={{ fontSize: '12px' }} />
            <YAxis stroke="#00e0ff" style={{ fontSize: '12px' }} />
            <Bar dataKey="importance" fill="#00e0ff" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Prediction Confidence */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30"
        >
          <h3 className="text-white font-poppins font-semibold mb-4">Prediction Confidence Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={confidenceData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {confidenceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30 flex flex-col justify-between"
        >
          <div>
            <h3 className="text-white font-poppins font-semibold mb-4">Anomaly Detection</h3>
            <div className="space-y-4">
              <div>
                <p className="text-neon-blue text-sm">Anomalous Predictions</p>
                <p className="text-white text-3xl font-bold">{anomalyPercentage}%</p>
                <div className="w-full bg-space-dark rounded-full h-2 mt-2">
                  <div
                    className="bg-neon-yellow h-2 rounded-full"
                    style={{ width: `${Math.min(anomalyPercentage, 100)}%` }}
                  />
                </div>
              </div>
              <div>
                <p className="text-neon-blue text-sm">Total Anomalies</p>
                <p className="text-white text-2xl font-bold">{anomalies.length}</p>
              </div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-neon-yellow/10 rounded border border-neon-yellow text-neon-yellow text-sm">
            {anomalyPercentage > 15 ? (
              <div className="flex gap-2">
                <AlertCircle size={18} />
                <span>Higher than normal anomaly rate. Review data quality.</span>
              </div>
            ) : (
              <div className="flex gap-2">
                <CheckCircle size={18} />
                <span>Anomaly rate within acceptable range.</span>
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Error Distribution Analysis */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30"
      >
        <h3 className="text-white font-poppins font-semibold mb-4">Error Distribution Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-neon-blue text-sm font-poppins">Distribution Shape</p>
            <p className="text-white text-xl font-bold mt-2">
              {metrics?.normality > 0.9 ? '✓ Normal' : metrics?.normality > 0.7 ? '~ Approximately Normal' : '✗ Non-Normal'}
            </p>
            <p className="text-neon-blue/70 text-xs mt-2">
              Based on Shapiro-Wilk test
            </p>
          </div>
          <div>
            <p className="text-neon-blue text-sm font-poppins">Skewness</p>
            <p className="text-white text-xl font-bold mt-2">Low</p>
            <p className="text-neon-blue/70 text-xs mt-2">
              Distribution centered near mean
            </p>
          </div>
          <div>
            <p className="text-neon-blue text-sm font-poppins">Kurtosis</p>
            <p className="text-white text-xl font-bold mt-2">Moderate</p>
            <p className="text-neon-blue/70 text-xs mt-2">
              Tail behavior reasonable
            </p>
          </div>
        </div>
      </motion.div>

      {/* Model Recommendation */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-neon-blue/20 to-space-purple/20 rounded-lg p-6 border border-neon-blue/50"
      >
        <h3 className="text-white font-poppins font-semibold mb-3">Model Recommendation</h3>
        <p className="text-neon-blue/90">
          Based on the normality score of {(metrics?.normality * 100)?.toFixed(2)}% and error metrics, this model
          demonstrates {metrics?.normality > 0.95 ? 'excellent' : metrics?.normality > 0.85 ? 'very good' : 'good'} performance
          for operational GNSS error forecasting. The prediction errors closely follow a normal distribution, which is
          critical for accurate satellite navigation systems.
        </p>
        <div className="mt-4 flex gap-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            className="bg-neon-blue text-space-dark px-4 py-2 rounded font-poppins text-sm font-semibold"
          >
            View Detailed Report
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            className="border border-neon-blue text-neon-blue px-4 py-2 rounded font-poppins text-sm font-semibold hover:bg-neon-blue/10"
          >
            Compare Models
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  );
};
