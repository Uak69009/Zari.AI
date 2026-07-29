"use client";

import React from "react";
import { Leaf, Code2, Globe } from "lucide-react";

export default function Footer() {
  return (
    <footer className="w-full bg-[#050D08] border-t border-white/10 text-gray-400 py-10">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-3">
          <Leaf className="w-6 h-6 text-[#00FFA3]" />
          <div>
            <span className="text-white font-bold text-lg tracking-tight">
              ZARI<span className="text-[#00FFA3]">.ai</span>
            </span>
            <p className="text-xs text-gray-500">
              Autonomous Agricultural Intelligence Platform for Pakistan
            </p>
          </div>
        </div>

        {/* Center/Right: Developer Attribution - Subtle & Non-Flashy */}
        <div className="flex items-center gap-4 text-xs text-gray-400 bg-white/5 border border-white/10 px-4 py-2 rounded-full">
          <div className="flex items-center gap-1.5">
            <Code2 className="w-3.5 h-3.5 text-[#00FFA3]" />
            <span>Developed by</span>
            <span className="text-white font-semibold tracking-wide">icloude studios</span>
          </div>
          <span className="text-gray-600">|</span>
          <div className="flex items-center gap-1 text-gray-400 hover:text-[#00FFA3] transition-colors cursor-pointer">
            <Globe className="w-3.5 h-3.5" />
            <span>All Rights Reserved &copy; {new Date().getFullYear()}</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
