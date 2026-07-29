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
      {/* 3D Flip Upload Zone Wrapper */}
      <div className="w-full max-w-3xl flex flex-col items-center space-y-4">
        <div className="w-full perspective-[1200px] h-72 cursor-pointer group">
          <MotionDiv 
            className="w-full h-full relative"
            style={{ transformStyle: "preserve-3d" }}
            initial={false}
            animate={{ rotateY: 0 }}
            whileHover={{ rotateY: 180 }}
            transition={{ duration: 0.7, type: "spring", stiffness: 100, damping: 20 }}
          >
            {/* Front Face (Summary / Info) */}
            <div 
              className="absolute inset-0 w-full h-full flex flex-col items-center justify-center p-8 bg-white dark:bg-[#112417] border border-gray-200 dark:border-gray-800 rounded-2xl shadow-lg transition-colors"
              style={{ backfaceVisibility: "hidden" }}
            >
              <div className="flex items-center gap-3 mb-4">
                <Activity className="text-emerald-600 dark:text-emerald-400 w-6 h-6" />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Why Field Monitoring Matters</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-center text-sm mb-4 leading-relaxed px-4">
                Agriculture forms the backbone of Pakistan's economy. Integrating AI technology ensures early disease detection, higher crop yields, and national food security.
              </p>
              <h4 className="text-lg font-serif text-emerald-800 dark:text-emerald-300 text-center leading-relaxed" dir="rtl">
                زراعت پاکستان کی معیشت کی ریڑھ کی ہڈی ہے۔ جدید ٹیکنالوجی کے ذریعے فصلوں کی بروقت نگرانی یقینی بناتی ہے کہ بیماریاں پہلے سے پکڑی جائیں اور پیداوار بڑھے۔
              </h4>
              
              {/* Interactive hint */}
              <div className="absolute bottom-4 flex items-center justify-center w-full text-xs text-gray-400 dark:text-gray-500 font-bold uppercase tracking-widest animate-pulse">
                Hover to Upload
              </div>
            </div>

            {/* Back Face (Actual Upload Zone) */}
            <div 
              className="absolute inset-0 w-full h-full flex flex-col items-center justify-center border-2 border-dashed border-emerald-300 dark:border-emerald-700 rounded-2xl p-10 bg-emerald-50/90 dark:bg-emerald-900/40 hover:bg-emerald-50 dark:hover:bg-emerald-900/60 transition-colors backdrop-blur-sm shadow-xl"
              style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
            >
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div className="text-center flex flex-col items-center">
                <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-800/80 border border-emerald-200 dark:border-emerald-700 flex items-center justify-center mb-4 shadow-sm">
                  <UploadCloud className="text-emerald-700 dark:text-emerald-400 w-8 h-8" />
                </div>
                <p className="text-emerald-900 dark:text-emerald-100 font-bold text-xl mb-2">Drop your crop image here</p>
                <p className="text-sm text-emerald-700/70 dark:text-emerald-400/70 font-medium bg-emerald-100/50 dark:bg-emerald-900/30 px-4 py-1.5 rounded-full">
                  Click to browse (JPG, PNG)
                </p>
              </div>
            </div>
          </MotionDiv>
        </div>

        {/* Instructional Text Below Card */}
        <p className="text-sm text-gray-500 dark:text-gray-400 font-medium text-center">
          Hover over the card to reveal the upload dropzone. Upload a clear, well-lit image of your crop leaf to run the AI diagnostics.
        </p>
      </div>

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
            <div className="bg-white dark:bg-[#112417] shadow-md rounded-2xl p-6 border border-gray-200 dark:border-gray-800 flex flex-col h-full transition-colors">
              <div className="flex items-center space-x-3 mb-6 border-b border-gray-100 dark:border-gray-800 pb-4">
                <div className="p-2 bg-emerald-100 dark:bg-emerald-900/40 rounded-lg">
                  <CheckCircle className="text-emerald-700 dark:text-emerald-400" size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Diagnostic Result</h3>
              </div>
              
              <div className="flex-1 flex flex-col justify-center">
                <h4 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-6 text-center">
                  {result.class_name ? result.class_name.replace(/_/g, " ") : "Unknown"}
                </h4>
                
                <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-3.5 mb-2 overflow-hidden shadow-inner border border-gray-200 dark:border-gray-700">
                  <MotionDiv 
                    initial={{ width: 0 }}
                    animate={{ width: `${(result.confidence || 0) * 100}%` }}
                    transition={{ duration: 1, delay: 0.2 }}
                    className={`h-full rounded-full ${result.confidence && result.confidence >= 0.85 ? 'bg-emerald-600 dark:bg-emerald-500' : 'bg-amber-500 dark:bg-amber-400'}`} 
                  ></MotionDiv>
                </div>
                <div className="flex justify-between text-sm font-semibold text-gray-600 dark:text-gray-400">
                  <span>Confidence Level</span>
                  <span className="text-emerald-700 dark:text-emerald-400 font-bold">{((result.confidence || 0) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* LLM Advisory Card */}
            {result.advisory && (
              <div className="bg-white dark:bg-[#112417] shadow-md rounded-2xl p-6 border border-gray-200 dark:border-gray-800 flex flex-col h-full md:row-span-2 transition-colors">
                <div className="flex items-center justify-between mb-6 border-b border-gray-100 dark:border-gray-800 pb-4">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">ZARI Expert Advisory</h3>
                  <div className="px-3 py-1 bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 rounded-full text-xs font-bold tracking-wide border border-emerald-200 dark:border-emerald-800/50">LLM SYNTHESIS</div>
                </div>
                <p className="flex-1 text-right text-xl md:text-2xl leading-loose text-gray-800 dark:text-gray-200 font-serif" dir="rtl">
                  {result.advisory}
                </p>
              </div>
            )}

            {/* Audio Player Card */}
            {result.audio_url && (
              <div className="bg-emerald-800 dark:bg-emerald-900 border border-emerald-700 dark:border-emerald-800 shadow-md rounded-2xl p-6 text-white flex flex-col justify-center transition-colors">
                <div className="flex items-center space-x-3 mb-4">
                  <FileAudio size={24} className="text-emerald-200 dark:text-emerald-300" />
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
