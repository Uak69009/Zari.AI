"use client";

import React from "react";
import { Leaf, Code2, Globe } from "lucide-react";

export default function Footer() {
  return (
    <footer className="w-full bg-white border-t border-gray-200 text-gray-600 py-10">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-100 border border-emerald-200 flex items-center justify-center">
            <Leaf className="w-5 h-5 text-emerald-700" />
          </div>
          <div>
            <span className="text-gray-900 font-bold text-lg tracking-tight">
              ZARI<span className="text-emerald-600">.ai</span>
            </span>
            <p className="text-xs text-gray-500">
              Autonomous Agricultural Intelligence Platform for Pakistan
            </p>
          </div>
        </div>

        {/* Center/Right: Developer Attribution - Subtle & Non-Flashy */}
        <div className="flex items-center gap-4 text-xs text-gray-600 bg-gray-50 border border-gray-200 px-4 py-2 rounded-full shadow-sm">
          <div className="flex items-center gap-1.5">
            <Code2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Developed by</span>
            <span className="text-gray-900 font-semibold tracking-wide">icloude studios</span>
          </div>
          <span className="text-gray-300">|</span>
          <div className="flex items-center gap-1 text-gray-500 hover:text-emerald-700 transition-colors cursor-pointer">
            <Globe className="w-3.5 h-3.5" />
            <span>All Rights Reserved &copy; {new Date().getFullYear()}</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
