"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { Globe2, Leaf, MessageCircle, Activity, ScanLine } from "lucide-react";
import InferenceTester from "./components/InferenceTester";
import DiagnosisShowcase from "./components/DiagnosisShowcase";
import CropCards from "./components/CropCards";
import Footer from "./components/Footer";

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
            className="inline-block text-emerald-700 font-serif"
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

  return (
    <main className="min-h-screen bg-white text-gray-900 relative overflow-x-hidden font-sans">

      <div className="relative z-10 container mx-auto px-6 py-16 flex flex-col items-center">
        
        {/* Header Section */}
        <MotionDiv 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16 max-w-4xl"
        >
          <div className="flex justify-center items-center gap-3 mb-4">
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-2xl shadow-sm">
              <Globe2 className="text-emerald-700 w-8 h-8" />
            </div>
            <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight">
              ZARI<span className="text-emerald-600">.ai</span>
            </h1>
          </div>
          
          {/* Flip Title */}
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6 flex flex-col items-center gap-2">
            <FlipText 
              english="Autonomous agricultural intelligence." 
              urdu="خودمختار زرعی ذہانت۔" 
            />
          </h2>
          
          <p className="text-lg md:text-xl text-gray-600 mb-2">
            <FlipText 
              english="Upload a leaf scan for instant, edge-powered disease diagnostics and localized treatment protocols." 
              urdu="فوری، جدید بیماریوں کی تشخیص اور مقامی علاج کے لیے پتے کی تصویر اپ لوڈ کریں۔" 
            />
          </p>
          <p className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 inline-block px-3 py-1 rounded-full uppercase tracking-wider mt-4">
            [Hover text to translate to Urdu]
          </p>
        </MotionDiv>

        {/* Clean Diagnostic Zone */}
        <MotionDiv 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="w-full max-w-4xl"
        >
          <div className="bg-white border border-gray-200 rounded-3xl p-8 md:p-12 shadow-xl hover:shadow-2xl transition-shadow">
            <InferenceTester />
          </div>
        </MotionDiv>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20 w-full max-w-5xl">
          {[
            { title: "Computer Vision", desc: "Powered by EfficientNetV2-S for rapid, high-accuracy inference.", icon: <Activity className="w-6 h-6 text-emerald-700" /> },
            { title: "LLM Advisory", desc: "Actionable, localized treatment protocols generated via Llama-3.3.", icon: <Globe2 className="w-6 h-6 text-emerald-700" /> },
            { title: "Voice & Edge", desc: "Accessible globally via WhatsApp integration and Edge-TTS.", icon: <Leaf className="w-6 h-6 text-emerald-700" /> }
          ].map((feature, idx) => (
            <MotionDiv 
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 + (idx * 0.1) }}
              className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-emerald-300 transition-all"
            >
              <div className="bg-emerald-50 border border-emerald-200 w-12 h-12 rounded-xl flex items-center justify-center mb-4">
                {feature.icon}
              </div>
              <h3 className="text-gray-900 font-bold text-lg mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-600 leading-relaxed">{feature.desc}</p>
            </MotionDiv>
          ))}
        </div>

        {/* WhatsApp Section */}
        <MotionDiv
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-28 w-full max-w-5xl bg-emerald-900 text-white border border-emerald-800 rounded-3xl p-10 md:p-16 flex flex-col md:flex-row items-center gap-10 shadow-xl"
        >
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-white/10 p-3 rounded-full">
                <MessageCircle className="w-8 h-8 text-[#25D366]" />
              </div>
              <h2 className="text-3xl font-bold text-white">WhatsApp Integration</h2>
            </div>
            <h3 className="text-xl font-semibold text-emerald-100 mb-4">
              <FlipText 
                english="No internet? No web app? No problem." 
                urdu="انٹرنیٹ نہیں؟ ویب ایپ نہیں؟ کوئی مسئلہ نہیں۔" 
              />
            </h3>
            <p className="text-emerald-100/90 text-lg leading-relaxed mb-8">
              ZARI.ai runs a dedicated WhatsApp webhook node. Farmers directly in the field can simply take a photo of an infected crop and send it to our automated WhatsApp number. ZARI will reply instantly with voice notes detailing the exact diagnosis and cure in fluent Urdu.
            </p>
            <button className="bg-[#25D366] hover:bg-[#1EBE5A] text-gray-900 font-bold px-8 py-3.5 rounded-full flex items-center gap-2.5 transition-transform hover:scale-105 shadow-md">
              <MessageCircle className="w-5 h-5" />
              Message ZARI on WhatsApp
            </button>
          </div>
          
          {/* Mockup */}
          <div className="w-full md:w-[300px] h-[450px] bg-[#0B141A] rounded-3xl border-8 border-gray-800 shadow-2xl relative overflow-hidden flex flex-col">
            <div className="bg-[#202C33] p-4 flex items-center gap-3">
              <div className="w-10 h-10 bg-emerald-600 rounded-full flex items-center justify-center">
                <Leaf className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="text-white font-semibold text-sm">ZARI.ai Bot</h4>
                <p className="text-[#25D366] text-xs">online</p>
              </div>
            </div>
            <div className="flex-1 p-4 bg-[#0B141A] bg-[url('https://i.imgur.com/4p99V1D.png')] bg-cover bg-blend-overlay flex flex-col gap-3">
              <div className="self-end bg-[#005C4B] text-white p-2 rounded-lg rounded-tr-none max-w-[80%] text-sm">
                <div className="flex items-center justify-center w-full h-24 bg-black/30 rounded mb-1 border border-white/10">
                  <ScanLine className="w-6 h-6 text-white/50" />
                </div>
                What's wrong with my potato crop?
              </div>
              <div className="self-start bg-[#202C33] text-white p-3 rounded-lg rounded-tl-none max-w-[90%] text-sm border border-white/5">
                <span className="text-[#25D366] font-bold block mb-1">Diagnosis: Late Blight (98%)</span>
                یہ فنگس کا حملہ ہے۔ فوری طور پر مینکو زیب سپرے کریں۔ (Voice Note Attached)
              </div>
            </div>
          </div>
        </MotionDiv>
      </div>

      <DiagnosisShowcase />
      <CropCards />
      <Footer />
    </main>
  );
}
