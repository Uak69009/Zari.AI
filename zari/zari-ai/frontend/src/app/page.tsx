"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Globe2, Leaf, MessageCircle, Activity, ScanLine } from "lucide-react";
import InferenceTester from "./components/InferenceTester";
import DiagnosisShowcase from "./components/DiagnosisShowcase";

const MotionDiv = dynamic(() => import("framer-motion").then((mod) => mod.motion.div), { ssr: false }) as any;
const AnimatePresenceWrapper = dynamic(() => import("framer-motion").then((mod) => mod.AnimatePresence), { ssr: false }) as any;

// A custom component to flip English text to Urdu on hover
const FlipText = ({ english, urdu }: { english: string; urdu: string }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="relative inline-block cursor-default perspective-1000"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onTouchStart={() => setIsHovered(!isHovered)}
    >
      <AnimatePresenceWrapper mode="wait">
        {!isHovered ? (
          <MotionDiv
            key="english"
            initial={{ rotateX: -90, opacity: 0 }}
            animate={{ rotateX: 0, opacity: 1 }}
            exit={{ rotateX: 90, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="inline-block"
          >
            {english}
          </MotionDiv>
        ) : (
          <MotionDiv
            key="urdu"
            initial={{ rotateX: -90, opacity: 0 }}
            animate={{ rotateX: 0, opacity: 1 }}
            exit={{ rotateX: 90, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="inline-block text-[#00FFA3] font-serif"
            dir="rtl"
          >
            {urdu}
          </MotionDiv>
        )}
      </AnimatePresenceWrapper>
    </div>
  );
};

export default function Home() {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  // Earth map pulse points
  const pulsePoints = [
    { top: "35%", left: "68%", duration: 3.5, delay: 0 },   
    { top: "38%", left: "66%", duration: 4.2, delay: 1.5 }, 
    { top: "45%", left: "18%", duration: 5.0, delay: 0.5 }, 
    { top: "55%", left: "75%", duration: 3.8, delay: 2.1 }, 
    { top: "60%", left: "45%", duration: 4.5, delay: 1.0 }, 
    { top: "25%", left: "52%", duration: 3.2, delay: 0.8 }, 
  ];

  return (
    <main className="min-h-screen bg-[#0A1A10] text-gray-200 relative overflow-x-hidden font-sans">
      
      {/* 1. Animated World Map Background (Restored) */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0 flex items-center justify-center">
        <div 
          className="absolute w-full h-[800px] opacity-15 bg-no-repeat bg-center bg-contain"
          style={{ 
            backgroundImage: "url('https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg')",
            filter: "brightness(0) saturate(100%) invert(88%) sepia(49%) saturate(4035%) hue-rotate(95deg) brightness(108%) contrast(106%)" // Converts SVG to #00FFA3 roughly
          }}
        ></div>
        
        {/* Blurry Glow Effects */}
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-[#00FFA3] opacity-10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-[#1A4D2E] opacity-40 rounded-full blur-[150px]" />

        {/* Pulse Points on the Map */}
        {mounted && pulsePoints.map((point, idx) => (
          <MotionDiv
            key={idx}
            className="absolute w-3 h-3 md:w-4 md:h-4 bg-[#00FFA3] rounded-full shadow-[0_0_15px_#00FFA3]"
            style={{ top: point.top, left: point.left }}
            animate={{ scale: [1, 1.8, 1], opacity: [0.6, 0.2, 0.6] }}
            transition={{ duration: point.duration, repeat: Infinity, delay: point.delay, ease: "easeInOut" }}
          />
        ))}
      </div>

      <div className="relative z-10 container mx-auto px-6 py-20 flex flex-col items-center">
        
        {/* Header Section with Urdu Hover Flip */}
        <MotionDiv 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16 max-w-4xl"
        >
          <div className="flex justify-center items-center gap-3 mb-4">
            <Globe2 className="text-[#00FFA3] w-10 h-10" />
            <h1 className="text-5xl font-extrabold text-white tracking-tight">
              ZARI<span className="text-[#00FFA3]">.ai</span>
            </h1>
          </div>
          
          {/* Flip Title */}
          <h2 className="text-3xl md:text-4xl font-bold text-gray-100 mb-6 flex flex-col items-center gap-2">
            <FlipText 
              english="Autonomous agricultural intelligence." 
              urdu="خودمختار زرعی ذہانت۔" 
            />
          </h2>
          
          <p className="text-lg text-gray-400 mb-2">
            <FlipText 
              english="Upload a leaf scan for instant, edge-powered disease diagnostics and localized treatment protocols." 
              urdu="فوری، جدید بیماریوں کی تشخیص اور مقامی علاج کے لیے پتے کی تصویر اپ لوڈ کریں۔" 
            />
          </p>
          <p className="text-sm text-[#00FFA3]/70 font-mono tracking-widest uppercase mt-4">
            [Hover text to translate to Urdu]
          </p>
        </MotionDiv>

        {/* Glassmorphism Diagnostic Zone */}
        <MotionDiv 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="w-full max-w-4xl"
        >
          <div className="relative group">
            {/* Animated neon border effect behind the glass */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-[#1A4D2E] to-[#00FFA3] rounded-3xl blur opacity-30 group-hover:opacity-60 transition duration-1000 group-hover:duration-200"></div>
            
            {/* The Glass Card housing the Inference Tester */}
            <div className="relative bg-black/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8 md:p-12 shadow-2xl">
              <InferenceTester />
            </div>
          </div>
        </MotionDiv>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 w-full max-w-5xl">
          {[
            { title: "Computer Vision", desc: "Powered by EfficientNetV2-S for rapid, high-accuracy inference.", icon: <Activity className="w-6 h-6 text-[#00FFA3]" /> },
            { title: "LLM Advisory", desc: "Actionable, localized treatment protocols generated via Llama-3.3.", icon: <Globe2 className="w-6 h-6 text-[#00FFA3]" /> },
            { title: "Voice & Edge", desc: "Accessible globally via WhatsApp integration and Edge-TTS.", icon: <Leaf className="w-6 h-6 text-[#00FFA3]" /> }
          ].map((feature, idx) => (
            <MotionDiv 
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 + (idx * 0.1) }}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors"
            >
              <div className="bg-[#1A4D2E]/50 w-12 h-12 rounded-lg flex items-center justify-center mb-4 border border-[#00FFA3]/20">
                {feature.icon}
              </div>
              <h3 className="text-white font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-400">{feature.desc}</p>
            </MotionDiv>
          ))}
        </div>

        {/* WhatsApp Direct Integration Section */}
        <MotionDiv
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-32 w-full max-w-5xl bg-gradient-to-br from-[#06180C] to-[#11311C] border border-[#00FFA3]/30 rounded-3xl p-10 md:p-16 flex flex-col md:flex-row items-center gap-10 shadow-[0_0_50px_rgba(0,255,163,0.05)]"
        >
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-[#25D366]/20 p-3 rounded-full">
                <MessageCircle className="w-8 h-8 text-[#25D366]" />
              </div>
              <h2 className="text-3xl font-bold text-white">WhatsApp Integration</h2>
            </div>
            <h3 className="text-xl font-semibold text-gray-200 mb-4">
              <FlipText 
                english="No internet? No web app? No problem." 
                urdu="انٹرنیٹ نہیں؟ ویب ایپ نہیں؟ کوئی مسئلہ نہیں۔" 
              />
            </h3>
            <p className="text-gray-400 text-lg leading-relaxed mb-8">
              ZARI.ai runs a dedicated WhatsApp webhook node. Farmers directly in the field can simply take a photo of an infected crop and send it to our automated WhatsApp number. ZARI will reply instantly with voice notes (via Edge-TTS) detailing the exact diagnosis and cure in fluent Urdu.
            </p>
            <button className="bg-[#25D366] hover:bg-[#1EBE5A] text-[#0A1A10] font-bold px-8 py-3 rounded-full flex items-center gap-2 transition-transform hover:scale-105">
              <MessageCircle className="w-5 h-5" />
              Message ZARI on WhatsApp
            </button>
          </div>
          
          {/* WhatsApp Mockup Preview */}
          <div className="w-full md:w-[300px] h-[450px] bg-[#0B141A] rounded-3xl border-8 border-gray-900 shadow-2xl relative overflow-hidden flex flex-col">
            <div className="bg-[#202C33] p-4 flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#1A4D2E] to-[#00FFA3] rounded-full flex items-center justify-center">
                <Leaf className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="text-white font-semibold text-sm">ZARI.ai Bot</h4>
                <p className="text-[#00FFA3] text-xs">online</p>
              </div>
            </div>
            <div className="flex-1 p-4 bg-[#0B141A] bg-[url('https://i.imgur.com/4p99V1D.png')] bg-cover bg-blend-overlay flex flex-col gap-3">
              {/* User Msg */}
              <div className="self-end bg-[#005C4B] text-white p-2 rounded-lg rounded-tr-none max-w-[80%] text-sm">
                <div className="flex items-center justify-center w-full h-24 bg-black/30 rounded mb-1 border border-white/10">
                  <ScanLine className="w-6 h-6 text-white/50" />
                </div>
                What's wrong with my potato crop?
              </div>
              {/* ZARI Msg */}
              <div className="self-start bg-[#202C33] text-white p-3 rounded-lg rounded-tl-none max-w-[90%] text-sm border border-white/5">
                <span className="text-[#00FFA3] font-bold block mb-1">Diagnosis: Late Blight (98%)</span>
                یہ فنگس کا حملہ ہے۔ فوری طور پر مینکو زیب سپرے کریں۔ (Voice Note Attached)
                <div className="mt-2 w-full h-8 bg-black/40 rounded-full flex items-center px-3 border border-white/10">
                  <div className="w-0 h-0 border-t-4 border-t-transparent border-l-6 border-l-[#00FFA3] border-b-4 border-b-transparent mr-2"></div>
                  <div className="h-1 flex-1 bg-gray-600 rounded-full overflow-hidden">
                     <div className="w-1/3 h-full bg-[#00FFA3]"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </MotionDiv>
      </div>

      <DiagnosisShowcase />
    </main>
  );
}
