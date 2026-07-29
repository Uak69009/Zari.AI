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
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full flex flex-col items-center justify-center border-2 border-dashed border-[#00FFA3]/50 rounded-2xl p-10 bg-black/20 hover:bg-[#00FFA3]/5 transition-colors relative cursor-pointer"
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
        />
        <div className="text-center flex flex-col items-center">
          <UploadCloud className="text-[#00FFA3] w-16 h-16 mb-4" />
          <p className="text-white font-medium text-lg mb-1">Drag & drop leaf image here</p>
          <p className="text-sm text-gray-400 font-medium">Or click to browse (JPG, PNG)</p>
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
              className="max-h-72 object-contain rounded-2xl shadow-[0_0_20px_rgba(0,255,163,0.15)] border border-[#00FFA3]/30" 
            />
            <MotionButton
              whileHover={{ scale: 1.05, boxShadow: "0px 0px 15px rgba(0, 255, 163, 0.4)" }}
              whileTap={{ scale: 0.95 }}
              onClick={handleAnalyze}
              disabled={loading}
              className="px-10 py-4 bg-gradient-to-r from-[#1A4D2E] to-[#4F6F52] border border-[#00FFA3]/30 text-white font-extrabold rounded-full shadow-lg hover:from-[#4F6F52] hover:to-[#1A4D2E] disabled:opacity-70 disabled:cursor-not-allowed transition-all w-full max-w-sm flex items-center justify-center space-x-3"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Running Inference...</span>
                </>
              ) : (
                <>
                  <Activity className="w-5 h-5 text-[#00FFA3]" />
                  <span>Run AI Diagnostic</span>
                </>
              )}
            </MotionButton>
          </MotionDiv>
        )}
      </AnimatePresenceWrapper>

      {/* Error State */}
      {error && (
        <MotionDiv initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 bg-red-900/30 border-l-4 border-red-500 text-red-200 rounded-lg w-full font-medium flex items-center space-x-3 backdrop-blur-md">
          <AlertTriangle size={24} className="text-red-400" />
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
            <div className="bg-black/30 shadow-xl rounded-2xl p-6 border border-white/10 flex flex-col h-full backdrop-blur-md">
              <div className="flex items-center space-x-3 mb-6 border-b border-white/10 pb-4">
                <div className="p-2 bg-[#00FFA3]/10 rounded-lg">
                  <CheckCircle className="text-[#00FFA3]" size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-200">Diagnostic Result</h3>
              </div>
              
              <div className="flex-1 flex flex-col justify-center">
                <h4 className="text-3xl font-extrabold text-white mb-6 text-center">
                  {result.class_name ? result.class_name.replace(/_/g, " ") : "Unknown"}
                </h4>
                
                <div className="w-full bg-white/10 rounded-full h-3 mb-2 overflow-hidden shadow-inner">
                  <MotionDiv 
                    initial={{ width: 0 }}
                    animate={{ width: `${(result.confidence || 0) * 100}%` }}
                    transition={{ duration: 1, delay: 0.2 }}
                    className={`h-3 rounded-full ${result.confidence && result.confidence >= 0.85 ? 'bg-[#00FFA3] shadow-[0_0_10px_#00FFA3]' : 'bg-amber-400'}`} 
                  ></MotionDiv>
                </div>
                <div className="flex justify-between text-sm font-semibold text-gray-400">
                  <span>Confidence Level</span>
                  <span className="text-[#00FFA3]">{((result.confidence || 0) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* LLM Advisory Card */}
            {result.advisory && (
              <div className="bg-black/30 shadow-xl rounded-2xl p-6 border border-white/10 flex flex-col h-full md:row-span-2 backdrop-blur-md">
                <div className="flex items-center justify-between mb-6 border-b border-white/10 pb-4">
                  <h3 className="text-lg font-bold text-gray-200">ZARI Expert Advisory</h3>
                  <div className="px-3 py-1 bg-[#00FFA3]/10 text-[#00FFA3] rounded-full text-xs font-bold tracking-wide border border-[#00FFA3]/30">LLM SYNTHESIS</div>
                </div>
                <p className="flex-1 text-right text-xl md:text-2xl leading-loose text-gray-300 font-serif" dir="rtl">
                  {result.advisory}
                </p>
              </div>
            )}

            {/* Audio Player Card */}
            {result.audio_url && (
              <div className="bg-gradient-to-br from-[#1A4D2E]/80 to-[#0A1A10] border border-[#00FFA3]/20 shadow-xl rounded-2xl p-6 text-white flex flex-col justify-center backdrop-blur-md">
                <div className="flex items-center space-x-3 mb-4">
                  <FileAudio size={24} className="text-[#00FFA3]" />
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

      {/* Backend Error State from API Response */}
      {result && result.status === "error" && (
        <MotionDiv initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 bg-red-900/30 border-l-4 border-red-500 text-red-200 rounded-lg w-full font-medium flex items-center space-x-3 backdrop-blur-md">
          <AlertTriangle size={24} className="text-red-400" />
          <span>{result.message || "An unknown backend error occurred."}</span>
        </MotionDiv>
      )}
    </div>
  );
}
