import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Activity, Target } from 'lucide-react';

export const KPICard = ({ title, value, unit, trend, icon: Icon = TrendingUp }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.05 }}
      className="bg-gradient-to-br from-space-blue to-space-dark border border-neon-blue rounded-lg p-6 shadow-lg"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-neon-blue text-sm font-poppins">{title}</p>
          <p className="text-white text-3xl font-bold font-poppins mt-2">
            {value}
            <span className="text-lg text-neon-yellow ml-1">{unit}</span>
          </p>
          {trend && (
            <p className={`text-xs mt-2 ${trend > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(2)}%
            </p>
          )}
        </div>
        <div className="p-3 bg-neon-blue rounded-full">
          <Icon size={32} className="text-space-dark" />
        </div>
      </div>
    </motion.div>
  );
};
