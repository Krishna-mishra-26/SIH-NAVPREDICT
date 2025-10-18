import React, { useState } from 'react';
import { KPICard } from './KPICard';
import { SatelliteOrbit } from './SatelliteOrbit';
import { DataUpload } from './DataUpload';
import { ModelTrainer } from './ModelTrainer';
import { ForecastChart } from './ForecastChart';
import { ExportPanel } from './ExportPanel';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './Tabs';
import { motion } from 'framer-motion';
import { Zap, Activity, Target, BarChart3 } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

export const Dashboard = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [processedData, setProcessedData] = useState(null);
  const [trainingMetrics, setTrainingMetrics] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [activeTab, setActiveTab] = useState('home');
  const [preprocessingStatus, setPreprocessingStatus] = useState('');

  const handleUpload = async (data) => {
    setUploadedFile(data);
    setActiveTab('preprocess');

    // Auto-preprocess
    try {
      setPreprocessingStatus('Aligning to 15-minute intervals...');
      const response = await axios.post('http://localhost:5000/preprocess', {
        filepath: data.filepath,
      });
      setProcessedData(response.data);
      setPreprocessingStatus('Preprocessing complete ✓');
      toast.success('Data preprocessed successfully');
    } catch (error) {
      toast.error('Preprocessing failed');
      setPreprocessingStatus('Preprocessing failed');
    }
  };

  const handleTrainingComplete = async (data) => {
    setTrainingMetrics(data.metrics);

    // Auto-predict
    try {
      toast('Generating predictions...');
      const response = await axios.post('http://localhost:5000/predict', {
        filepath: processedData.processed_filepath,
        model_type: data.model_type,
        horizon_days: 1,
      });
      setPredictions(response.data.data_sample);
      setActiveTab('forecast');
      toast.success('Predictions generated');
    } catch (error) {
      toast.error('Prediction generation failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-space-dark via-space-blue to-space-dark">
      {/* Header */}
      <div className="bg-gradient-to-r from-space-blue to-space-dark border-b border-neon-blue/30 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-neon-blue rounded-full">
              <Zap className="text-space-dark" size={24} />
            </div>
            <div>
              <h1 className="text-white font-poppins text-2xl font-bold">NavPredict</h1>
              <p className="text-neon-blue text-xs">GNSS Error Forecasting System</p>
            </div>
          </div>
          <div className="hidden md:flex gap-6 items-center">
            <div className="text-right">
              <p className="text-neon-blue text-xs">Status</p>
              <p className="text-white font-semibold">{activeTab.toUpperCase()}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Tabs Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-4 gap-2 bg-space-blue/50 p-2 rounded-lg border border-neon-blue/30">
            <TabsTrigger value="home">🏠 Dashboard</TabsTrigger>
            <TabsTrigger value="preprocess">📊 Upload</TabsTrigger>
            <TabsTrigger value="train">🤖 Train</TabsTrigger>
            <TabsTrigger value="forecast">📈 Forecast</TabsTrigger>
          </TabsList>

          {/* Home Tab */}
          <TabsContent value="home" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
              <div className="space-y-4">
                <h2 className="text-white font-poppins text-2xl font-bold">System Overview</h2>
                <p className="text-neon-blue/70 text-sm">
                  Predict GNSS satellite clock and ephemeris errors with AI/ML models trained on 7 days
                  of satellite data. Support for multiple architectures: LSTM, Transformer, ARIMA, and
                  Gaussian Process.
                </p>
                <div className="grid grid-cols-2 gap-4 mt-6">
                  <KPICard
                    title="Clock Error RMSE"
                    value="0.0023"
                    unit="ms"
                    trend={-12.5}
                    icon={Target}
                  />
                  <KPICard
                    title="Ephemeris MAE"
                    value="0.145"
                    unit="m"
                    trend={5.2}
                    icon={Activity}
                  />
                </div>
              </div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="rounded-lg border border-neon-blue/30 overflow-hidden bg-space-blue/50 p-4"
              >
                <SatelliteOrbit />
              </motion.div>
            </motion.div>

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                onClick={() => setActiveTab('preprocess')}
                className="bg-gradient-to-r from-neon-blue to-neon-yellow text-space-dark px-6 py-4 rounded-lg font-poppins font-bold hover:shadow-lg hover:shadow-neon-blue/50 transition-all"
              >
                📊 Predict Errors
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                onClick={() => setActiveTab('preprocess')}
                className="bg-gradient-to-r from-space-purple to-pink-500 text-white px-6 py-4 rounded-lg font-poppins font-bold hover:shadow-lg transition-all"
              >
                🛰 Upload Satellite Data
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                className="bg-gradient-to-r from-green-500 to-teal-500 text-white px-6 py-4 rounded-lg font-poppins font-bold hover:shadow-lg transition-all"
              >
                📈 View Model Insights
              </motion.button>
            </motion.div>
          </TabsContent>

          {/* Upload Tab */}
          <TabsContent value="preprocess" className="space-y-6">
            <h2 className="text-white font-poppins text-2xl font-bold">Data Upload & Preprocessing</h2>
            <DataUpload onUploadComplete={handleUpload} />
            
            {preprocessingStatus && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-space-blue/50 rounded-lg p-4 border border-neon-blue/30"
              >
                <p className="text-neon-blue font-poppins">{preprocessingStatus}</p>
              </motion.div>
            )}

            {processedData && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-space-blue/50 rounded-lg p-6 border border-neon-blue/30"
              >
                <h3 className="text-white font-poppins font-semibold mb-4">Processing Steps</h3>
                <div className="space-y-2 text-neon-blue/70 text-sm">
                  <p>✓ Data aligned to 15-minute intervals</p>
                  <p>✓ Missing values handled with interpolation</p>
                  <p>✓ Outliers detected and smoothed</p>
                  <p>✓ Lag features (1, 2, 4, 8 steps) created</p>
                  <p>✓ Rolling averages computed (3, 6, 12 windows)</p>
                  <p>✓ Time-based features engineered</p>
                  <p className="text-neon-yellow mt-4">Shape: {processedData.shape}</p>
                </div>
              </motion.div>
            )}
          </TabsContent>

          {/* Training Tab */}
          <TabsContent value="train" className="space-y-6">
            <h2 className="text-white font-poppins text-2xl font-bold">Model Training & Selection</h2>
            {processedData ? (
              <ModelTrainer uploadedFile={uploadedFile} onTrainingComplete={handleTrainingComplete} />
            ) : (
              <div className="bg-space-blue/50 rounded-lg p-6 border border-neon-yellow/30 text-center">
                <p className="text-neon-blue">Please upload and preprocess data first</p>
              </div>
            )}
          </TabsContent>

          {/* Forecast Tab */}
          <TabsContent value="forecast" className="space-y-6">
            <h2 className="text-white font-poppins text-2xl font-bold">Prediction & Forecast</h2>
            {predictions ? (
              <>
                <ForecastChart predictions={predictions} />
                <ExportPanel predictions={predictions} modelMetrics={trainingMetrics} />
              </>
            ) : (
              <div className="bg-space-blue/50 rounded-lg p-6 border border-neon-yellow/30 text-center">
                <p className="text-neon-blue">Train a model first to generate predictions</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
