import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Download, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

export const ExportPanel = ({ predictions, modelMetrics }) => {
  const [exporting, setExporting] = useState(false);

  const exportAsCSV = () => {
    if (!predictions || predictions.length === 0) {
      toast.error('No predictions to export');
      return;
    }

    setExporting(true);
    try {
      const csv = [
        ['utc_time', 'x_error_pred (m)', 'y_error_pred (m)', 'z_error_pred (m)', 'satclockerror_pred (m)'],
        ...predictions.map((p) => [
          p.utc_time,
          p['x_error_pred (m)'],
          p['y_error_pred (m)'],
          p['z_error_pred (m)'],
          p['satclockerror_pred (m)'],
        ]),
      ]
        .map((row) => row.join(','))
        .join('\n');

      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `predictions_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();

      toast.success('Predictions exported successfully');
    } catch (error) {
      toast.error('Export failed');
    } finally {
      setExporting(false);
    }
  };

  const exportAsJSON = () => {
    if (!predictions || predictions.length === 0) {
      toast.error('No predictions to export');
      return;
    }

    setExporting(true);
    try {
      const data = {
        exportDate: new Date().toISOString(),
        metrics: modelMetrics,
        predictions,
      };

      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `predictions_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();

      toast.success('Report exported successfully');
    } catch (error) {
      toast.error('Export failed');
    } finally {
      setExporting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30"
    >
      <h3 className="text-white font-poppins font-semibold mb-4">Export Results</h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={exportAsCSV}
          disabled={exporting}
          className="bg-neon-blue text-space-dark px-6 py-3 rounded font-poppins font-semibold hover:bg-neon-yellow transition-colors disabled:opacity-50 flex items-center gap-2 justify-center"
        >
          <Download size={18} />
          Download CSV
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={exportAsJSON}
          disabled={exporting}
          className="bg-space-purple text-white px-6 py-3 rounded font-poppins font-semibold hover:bg-space-purple/80 transition-colors disabled:opacity-50 flex items-center gap-2 justify-center"
        >
          <FileText size={18} />
          Download Report
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          className="bg-neon-yellow text-space-dark px-6 py-3 rounded font-poppins font-semibold hover:bg-neon-blue transition-colors flex items-center gap-2 justify-center"
        >
          <Download size={18} />
          Export Model
        </motion.button>
      </div>
    </motion.div>
  );
};
