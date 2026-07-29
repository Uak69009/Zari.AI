"use client";

import dynamic from "next/dynamic";
import { ScanLine, ArrowRight } from "lucide-react";

const MotionDiv = dynamic(() => import("framer-motion").then((mod) => mod.motion.div), { ssr: false }) as any;
const MotionButton = dynamic(() => import("framer-motion").then((mod) => mod.motion.button), { ssr: false }) as any;

export default function DiagnosisShowcase() {
  return (
    <section className="w-full py-24 bg-[#0A1A10] text-gray-200 overflow-hidden relative">
      
      {/* Subtle Background Glow */}
      <div className="absolute top-1/2 left-1/4 w-[400px] h-[400px] bg-[#1A4D2E] opacity-30 rounded-full blur-[120px] pointer-events-none -translate-y-1/2" />

      <div className="container mx-auto px-6 lg:px-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          
          {/* Left Column: Text & Animated Button */}
          <MotionDiv 
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="flex flex-col items-start gap-6"
          >
            <h2 className="text-4xl lg:text-5xl font-bold text-white leading-tight">
              Diagnose your sick crop <br />
              <span className="text-[#00FFA3]">in seconds.</span>
            </h2>
            
            <p className="text-lg text-gray-400 max-w-md">
              Upload a photo of your leaf and let our edge-powered computer vision model instantly identify the disease and generate a localized treatment protocol.
            </p>

            {/* Animated Call to Action Button */}
            <MotionButton
              whileHover={{ 
                scale: 1.05, 
                boxShadow: "0px 0px 20px rgba(0, 255, 163, 0.5)" 
              }}
              whileTap={{ scale: 0.95 }}
              className="mt-4 bg-gradient-to-r from-[#1A4D2E] to-[#4F6F52] border border-[#00FFA3]/50 text-white px-8 py-4 rounded-full font-semibold text-lg flex items-center gap-3 hover:from-[#4F6F52] hover:to-[#1A4D2E] transition-all group"
            >
              <ScanLine className="w-5 h-5 text-[#00FFA3]" />
              Get a free diagnosis
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </MotionButton>
          </MotionDiv>

          {/* Right Column: Animated Phone Mockup */}
          <MotionDiv 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex justify-center lg:justify-end"
          >
            {/* Phone Frame */}
            <div className="relative w-[320px] h-[650px] bg-[#050B07] border-[12px] border-[#112A18] rounded-[3rem] overflow-hidden shadow-2xl shadow-[#00FFA3]/10">
              
              {/* Phone Top Notch */}
              <div className="absolute top-0 inset-x-0 h-7 bg-[#112A18] rounded-b-2xl w-40 mx-auto z-20 flex justify-center items-end pb-2">
                <div className="w-12 h-1.5 bg-gray-800 rounded-full"></div>
              </div>

              {/* Scrolling Screen Content (The "Animated Pictures") */}
              <MotionDiv
                animate={{ y: [0, -250, 0] }}
                transition={{ 
                  repeat: Infinity, 
                  duration: 15, 
                  ease: "easeInOut",
                  repeatType: "reverse"
                }}
                className="absolute top-0 left-0 w-full p-4 pt-12 flex flex-col gap-4 bg-[#0A1A10]"
              >
                {/* Mock Image Upload Area */}
                <div className="w-full h-48 bg-[#1A4D2E]/40 rounded-xl border border-[#00FFA3]/20 flex items-center justify-center overflow-hidden relative">
                   <div className="text-[#00FFA3]/50 flex flex-col items-center">
                      <ScanLine className="w-10 h-10 mb-2" />
                      <span className="text-sm">Analyzing late_blight...</span>
                   </div>
                   {/* Scanning Line Animation */}
                   <MotionDiv 
                     animate={{ y: [-100, 100] }}
                     transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                     className="absolute w-full h-1 bg-[#00FFA3] shadow-[0_0_10px_#00FFA3] opacity-70"
                   />
                </div>

                {/* Mock Diagnosis Results */}
                <div className="w-full bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                  <h3 className="text-[#00FFA3] font-semibold mb-2">Detected: Late Blight</h3>
                  <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden mb-4">
                    <MotionDiv 
                      initial={{ width: 0 }}
                      whileInView={{ width: "94%" }}
                      className="h-full bg-gradient-to-r from-[#1A4D2E] to-[#00FFA3]"
                    />
                  </div>
                  <p className="text-xs text-gray-400">Confidence Score: 94%</p>
                </div>

                {/* Mock Symptoms Section */}
                <div className="w-full bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                  <h4 className="text-white text-sm font-medium mb-3">Symptoms</h4>
                  <div className="space-y-2">
                    <div className="h-3 w-3/4 bg-gray-600/50 rounded animate-pulse"></div>
                    <div className="h-3 w-full bg-gray-600/50 rounded animate-pulse"></div>
                    <div className="h-3 w-5/6 bg-gray-600/50 rounded animate-pulse"></div>
                  </div>
                </div>

                {/* Mock Treatment Section */}
                <div className="w-full bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                  <h4 className="text-white text-sm font-medium mb-3">Llama-3 Treatment Plan</h4>
                  <div className="space-y-2">
                    <div className="h-3 w-full bg-[#1A4D2E] rounded"></div>
                    <div className="h-3 w-4/5 bg-[#1A4D2E] rounded"></div>
                    <div className="h-3 w-full bg-[#1A4D2E] rounded"></div>
                    <div className="h-3 w-2/3 bg-[#1A4D2E] rounded"></div>
                  </div>
                </div>
                
              </MotionDiv>
            </div>
          </MotionDiv>
          
        </div>
      </div>
    </section>
  );
}
