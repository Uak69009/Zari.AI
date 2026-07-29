"use client";

import React from "react";
import dynamic from "next/dynamic";

const MotionDiv = dynamic(() => import("framer-motion").then((mod) => mod.motion.div), { ssr: false }) as any;

export default function WorldMap() {
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden z-0 flex items-center justify-center">
      {/* Crisp, High-Reliability Clean World Map Vector SVG */}
      <div className="relative w-full max-w-5xl h-[500px] flex items-center justify-center opacity-30">
        <svg
          viewBox="0 0 1000 500"
          className="w-full h-full text-slate-400 fill-current"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* North America */}
          <path d="M150,120 Q180,100 220,110 T280,150 T220,220 T150,180 Z" opacity="0.7" />
          <path d="M120,80 Q160,50 200,70 T180,100 Z" opacity="0.6" />
          {/* South America */}
          <path d="M260,250 Q310,260 320,320 T280,420 T250,350 T240,280 Z" opacity="0.7" />
          {/* Europe */}
          <path d="M480,100 Q540,90 560,130 T500,160 T460,130 Z" opacity="0.7" />
          {/* Africa */}
          <path d="M470,180 Q540,180 570,240 T540,340 T480,320 T450,230 Z" opacity="0.7" />
          {/* Asia & Middle East */}
          <path d="M580,100 Q680,80 800,110 T850,200 T750,240 T620,180 Z" opacity="0.7" />
          {/* South Asia / Indian Subcontinent / Pakistan region */}
          <path d="M640,180 L700,190 L680,260 L630,220 Z" opacity="0.8" />
          {/* Australia & Oceania */}
          <path d="M780,300 Q840,300 860,350 T800,400 T750,360 Z" opacity="0.7" />
        </svg>

        {/* Highlighted Pakistan Node Pin */}
        <div className="absolute top-[38%] left-[65%] md:left-[64%] flex items-center gap-2 z-20">
          <MotionDiv
            className="relative flex items-center justify-center"
            animate={{ scale: [1, 1.25, 1] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          >
            <div className="w-6 h-6 bg-emerald-500 rounded-full opacity-40 animate-ping absolute" />
            <div className="w-4 h-4 bg-emerald-600 rounded-full border-2 border-white shadow-lg relative" />
          </MotionDiv>
          
          <div className="bg-white border-2 border-emerald-500 text-emerald-900 text-xs font-extrabold px-3 py-1 rounded-full shadow-md flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span>Pakistan Node Active</span>
          </div>
        </div>
      </div>

      {/* Subtle Light Accent Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-emerald-100/50 rounded-full blur-[100px] pointer-events-none" />
    </div>
  );
}
