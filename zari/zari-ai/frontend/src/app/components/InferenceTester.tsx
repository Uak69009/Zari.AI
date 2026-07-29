"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import { UploadCloud, CheckCircle, AlertTriangle, FileAudio, Activity } from "lucide-react";

const MotionDiv = dynamic(() => import("framer-motion").then((mod) => mod.motion.div), { ssr: false }) as any;
const MotionButton = dynamic(() => import("framer-motion").then((mod) => mod.motion.button), { ssr: false }) as any;
const AnimatePresenceWrapper = dynamic(() => import("framer-motion").then((mod) => mod.AnimatePresence), { ssr: false }) as any;

interface PredictionResult {
  status: string;
  confidence?: number;
  class_name?: string;
  advisory?: string;
  audio_url?: string;
  message?: string;
}

export default function InferenceTester() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to reach the API server.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || "An error occurred during inference.");
      } else {
        setError("An unknown error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center w-full space-y-8">
      {/* Upload Zone */}
      <MotionDiv 
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        className="w-full flex flex-col items-center justify-center border-2 border-dashed border-emerald-300 rounded-2xl p-10 bg-emerald-50/40 hover:bg-emerald-50 transition-colors relative cursor-pointer"
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
        />
        <div className="text-center flex flex-col items-center">
          <div className="w-16 h-16 rounded-full bg-emerald-100 border border-emerald-200 flex items-center justify-center mb-4">
            <UploadCloud className="text-emerald-700 w-8 h-8" />
          </div>
          <p className="text-gray-900 font-bold text-lg mb-1">Drag & drop leaf image here</p>
          <p className="text-sm text-gray-500 font-medium">Or click to browse (JPG, PNG)</p>
        </div>
      </MotionDiv>

      {/* Preview & Action */}
      <AnimatePresenceWrapper>
        {preview && (
          <MotionDiv 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="flex flex-col items-center space-y-6 w-full"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img 
              src={preview} 
              alt="Crop Preview" 
              className="max-h-72 object-contain rounded-2xl shadow-md border border-gray-200" 
            />
            <MotionButton
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleAnalyze}
              disabled={loading}
              className="px-10 py-4 bg-emerald-700 hover:bg-emerald-800 border border-emerald-800 text-white font-extrabold rounded-full shadow-md disabled:opacity-70 disabled:cursor-not-allowed transition-all w-full max-w-sm flex items-center justify-center space-x-3"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Running Inference...</span>
                </>
              ) : (
                <>
                  <Activity className="w-5 h-5 text-white" />
                  <span>Run AI Diagnostic</span>
                </>
              )}
            </MotionButton>
          </MotionDiv>
        )}
      </AnimatePresenceWrapper>

      {/* Error State */}
      {error && (
        <MotionDiv initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-lg w-full font-medium flex items-center space-x-3">
          <AlertTriangle size={24} className="text-red-500" />
          <span>{error}</span>
        </MotionDiv>
      )}

      {/* Results Dashboard */}
      <AnimatePresenceWrapper>
        {result && result.status !== "error" && (
          <MotionDiv 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full grid grid-cols-1 md:grid-cols-2 gap-6 pt-4"
          >
            
            {/* CV Inference Card */}
            <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200 flex flex-col h-full">
              <div className="flex items-center space-x-3 mb-6 border-b border-gray-100 pb-4">
                <div className="p-2 bg-emerald-100 rounded-lg">
                  <CheckCircle className="text-emerald-700" size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900">Diagnostic Result</h3>
              </div>
              
              <div className="flex-1 flex flex-col justify-center">
                <h4 className="text-3xl font-extrabold text-gray-900 mb-6 text-center">
                  {result.class_name ? result.class_name.replace(/_/g, " ") : "Unknown"}
                </h4>
                
                <div className="w-full bg-gray-100 rounded-full h-3.5 mb-2 overflow-hidden shadow-inner border border-gray-200">
                  <MotionDiv 
                    initial={{ width: 0 }}
                    animate={{ width: `${(result.confidence || 0) * 100}%` }}
                    transition={{ duration: 1, delay: 0.2 }}
                    className={`h-full rounded-full ${result.confidence && result.confidence >= 0.85 ? 'bg-emerald-600' : 'bg-amber-500'}`} 
                  ></MotionDiv>
                </div>
                <div className="flex justify-between text-sm font-semibold text-gray-600">
                  <span>Confidence Level</span>
                  <span className="text-emerald-700 font-bold">{((result.confidence || 0) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* LLM Advisory Card */}
            {result.advisory && (
              <div className="bg-white shadow-md rounded-2xl p-6 border border-gray-200 flex flex-col h-full md:row-span-2">
                <div className="flex items-center justify-between mb-6 border-b border-gray-100 pb-4">
                  <h3 className="text-lg font-bold text-gray-900">ZARI Expert Advisory</h3>
                  <div className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold tracking-wide border border-emerald-200">LLM SYNTHESIS</div>
                </div>
                <p className="flex-1 text-right text-xl md:text-2xl leading-loose text-gray-800 font-serif" dir="rtl">
                  {result.advisory}
                </p>
              </div>
            )}

            {/* Audio Player Card */}
            {result.audio_url && (
              <div className="bg-emerald-800 border border-emerald-700 shadow-md rounded-2xl p-6 text-white flex flex-col justify-center">
                <div className="flex items-center space-x-3 mb-4">
                  <FileAudio size={24} className="text-emerald-200" />
                  <h3 className="text-lg font-bold">Listen to Advisory</h3>
                </div>
                <audio controls className="w-full rounded-lg" key={result.audio_url}>
                  <source src={result.audio_url} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
            
          </MotionDiv>
        )}
      </AnimatePresenceWrapper>
    </div>
  );
}
