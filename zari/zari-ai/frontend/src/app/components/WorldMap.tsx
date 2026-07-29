"use client";

import React from "react";
import dynamic from "next/dynamic";

const MotionDiv = dynamic(() => import("framer-motion").then((mod) => mod.motion.div), { ssr: false }) as any;

export default function WorldMap() {
  return (
    <div className="absolute top-0 left-0 w-full h-[650px] pointer-events-none overflow-hidden z-0 flex items-center justify-center">
      {/* High-Contrast, High-Visibility Vector World Map Container */}
      <div className="relative w-full max-w-6xl h-full flex items-center justify-center px-4">
        
        {/* World Map SVG with crisp slate-300 continent shapes */}
        <svg
          viewBox="0 0 1000 500"
          className="w-full h-full text-slate-300 opacity-60"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Detailed North America */}
          <path
            d="M120,60 L180,40 L240,50 L280,80 L320,110 L290,160 L240,210 L180,230 L160,190 L120,150 L100,100 Z"
            fill="#CBD5E1"
            stroke="#94A3B8"
            strokeWidth="1.5"
          />
          {/* Greenland */}
          <path
            d="M320,30 L380,25 L400,60 L360,80 L310,60 Z"
            fill="#CBD5E1"
            stroke="#94A3B8"
            strokeWidth="1.5"
          />
          {/* South America */}
          <path
            d="M240,240 L310,260 L340,320 L310,400 L270,440 L250,380 L230,300 Z"
            fill="#CBD5E1"
            stroke="#94A3B8"
            strokeWidth="1.5"
          />
          {/* Europe */}
          <path
            d="M460,80 L540,70 L580,100 L540,150 L480,140 L450,110 Z"
            fill="#CBD5E1"
            stroke="#94A3B8"
            strokeWidth="1.5"
          />
          {/* Africa */}
          <path
            d="M450,160 L560,160 L600,230 L560,350 L500,380 L460,300 L440,220 Z"
            fill="#CBD5E1"
            stroke="#94A3B8"
            strokeWidth="1.5"
          />
          {/* Asia & Eurasia */}
          <path
            d="M580,60 L780,50 L880,90 L900,160 L820,200 L720,170 L600,140 Z"
            fill="#CBD5E1"
            stroke="#94A3B8"
            strokeWidth="1.5"
          />
          
          {/* PAKISTAN REGION - HIGHLY PROMINENT EMERALD GREEN HIGHLIGHT */}
          <path
            d="M660,155 L705,160 L695,200 L655,190 Z"
            fill="#10B981"
            stroke="#047857"
            strokeWidth="2.5"
            className="animate-pulse"
          />

          {/* Australia */}
          <path
            d="M780,310 L870,310 L890,370 L830,400 L760,370 Z"
            fill="#CBD5E1"
            stroke="#94A3B8"
            strokeWidth="1.5"
          />
        </svg>

        {/* PROMINENT PAKISTAN NODE BADGE & PIN */}
        <div className="absolute top-[33%] left-[65%] md:left-[66%] flex items-center gap-3 z-30 pointer-events-auto">
          <MotionDiv
            className="relative flex items-center justify-center"
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          >
            <div className="w-8 h-8 bg-emerald-500/40 rounded-full animate-ping absolute" />
            <div className="w-5 h-5 bg-emerald-600 rounded-full border-2 border-white shadow-xl relative" />
          </MotionDiv>
          
          <div className="bg-white border-2 border-emerald-600 text-emerald-950 text-xs md:text-sm font-extrabold px-3.5 py-1.5 rounded-full shadow-lg flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-pulse" />
            <span>Pakistan Node Active</span>
          </div>
        </div>

      </div>

      {/* Background Radial Glow */}
      <div className="absolute top-10 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-emerald-100/60 rounded-full blur-[90px] pointer-events-none -z-10" />
    </div>
  );
}
