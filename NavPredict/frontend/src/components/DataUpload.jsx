import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

export const DataUpload = ({ onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadFile(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    if (!file.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        onUploadProgress: (event) => {
          const progress = Math.round((event.loaded * 100) / event.total);
          setUploadProgress(progress);
        },
      });

      toast.success('File uploaded successfully');
      onUploadComplete?.(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          isDragging
            ? 'border-neon-blue bg-neon-blue/10'
            : 'border-neon-blue/50 hover:border-neon-blue'
        }`}
      >
        <Upload className="mx-auto mb-4 text-neon-blue" size={48} />
        <h3 className="text-white font-poppins text-lg mb-2">Drop your CSV file here</h3>
        <p className="text-neon-blue/70 text-sm mb-4">or click to browse</p>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileInput}
          disabled={uploading}
          className="hidden"
          id="file-input"
        />
        <label htmlFor="file-input">
          <button
            disabled={uploading}
            className="bg-neon-blue text-space-dark px-6 py-2 rounded font-poppins font-semibold hover:bg-neon-yellow transition-colors disabled:opacity-50"
            onClick={() => document.getElementById('file-input')?.click()}
          >
            {uploading ? `Uploading... ${uploadProgress}%` : 'Select File'}
          </button>
        </label>
      </motion.div>

      {uploading && (
        <div className="bg-space-blue/50 rounded-lg p-4">
          <div className="w-full bg-space-dark rounded-full h-2">
            <div
              className="bg-neon-blue h-2 rounded-full transition-all"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-neon-blue text-xs mt-2">{uploadProgress}% uploaded</p>
        </div>
      )}
    </div>
  );
};
