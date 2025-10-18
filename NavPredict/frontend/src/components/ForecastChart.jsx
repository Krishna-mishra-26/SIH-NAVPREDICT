import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Area, AreaChart } from 'recharts';
import { ChevronDown } from 'lucide-react';

export const ForecastChart = ({ predictions }) => {
  const [selectedError, setSelectedError] = useState('x_error_pred (m)');
  const [timeHorizon, setTimeHorizon] = useState('24h');

  const errorTypes = [
    'x_error_pred (m)',
    'y_error_pred (m)',
    'z_error_pred (m)',
    'satclockerror_pred (m)',
  ];

  const filterDataByHorizon = () => {
    if (!predictions) return [];
    const horizonMap = {
      '15m': 1,
      '1h': 4,
      '6h': 24,
      '24h': 96,
    };
    return predictions.slice(0, horizonMap[timeHorizon]);
  };

  const chartData = filterDataByHorizon();

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[200px]">
          <label className="text-neon-blue text-sm font-poppins block mb-2">Error Type</label>
          <select
            value={selectedError}
            onChange={(e) => setSelectedError(e.target.value)}
            className="w-full bg-space-blue border border-neon-blue rounded px-3 py-2 text-white font-poppins"
          >
            {errorTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1 min-w-[200px]">
          <label className="text-neon-blue text-sm font-poppins block mb-2">Time Horizon</label>
          <div className="flex gap-2">
            {['15m', '1h', '6h', '24h'].map((horizon) => (
              <button
                key={horizon}
                onClick={() => setTimeHorizon(horizon)}
                className={`px-4 py-2 rounded font-poppins text-sm font-semibold transition-all ${
                  timeHorizon === horizon
                    ? 'bg-neon-blue text-space-dark'
                    : 'bg-space-blue border border-neon-blue text-neon-blue hover:bg-space-blue/50'
                }`}
              >
                {horizon}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30"
      >
        <h3 className="text-white font-poppins font-semibold mb-4">Prediction Forecast</h3>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPred" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00e0ff" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#00e0ff" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#00e0ff33" />
            <XAxis
              dataKey="utc_time"
              stroke="#00e0ff"
              style={{ fontSize: '12px' }}
            />
            <YAxis stroke="#00e0ff" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a3a5c',
                border: '1px solid #00e0ff',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#ffd700' }}
            />
            <Area
              type="monotone"
              dataKey={selectedError}
              stroke="#00e0ff"
              fillOpacity={1}
              fill="url(#colorPred)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Distribution Info */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 gap-4"
      >
        <div className="bg-space-blue/50 rounded-lg p-4 border border-neon-blue/30">
          <p className="text-neon-blue text-xs font-poppins">Mean Error</p>
          <p className="text-white text-2xl font-bold font-poppins">
            {chartData.length > 0
              ? (
                  chartData.reduce((acc, d) => acc + (d[selectedError] || 0), 0) /
                  chartData.length
                ).toFixed(4)
              : 'N/A'}
          </p>
        </div>
        <div className="bg-space-blue/50 rounded-lg p-4 border border-neon-blue/30">
          <p className="text-neon-blue text-xs font-poppins">Std. Deviation</p>
          <p className="text-white text-2xl font-bold font-poppins">
            {chartData.length > 1
              ? Math.sqrt(
                  chartData.reduce(
                    (acc, d) => acc + Math.pow(d[selectedError] || 0, 2),
                    0
                  ) / chartData.length
                ).toFixed(4)
              : 'N/A'}
          </p>
        </div>
      </motion.div>
    </div>
  );
};
