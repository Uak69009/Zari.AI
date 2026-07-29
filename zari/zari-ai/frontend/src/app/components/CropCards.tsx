"use client";

import React from "react";
import { Sprout, ShieldAlert, ChevronRight } from "lucide-react";

interface CropInfo {
  id: string;
  name: string;
  urduName: string;
  category: string;
  description: string;
  diseases: { name: string; urdu: string; severity: "High" | "Medium" }[];
  iconBg: string;
  imageUrl: string;
}

const cropData: CropInfo[] = [
  {
    id: "wheat",
    name: "Wheat (گندم)",
    urduName: "گندم",
    category: "Staple Food Crop",
    description: "Pakistan's primary staple crop, cultivated extensively across Punjab and Sindh during the Rabi season.",
    diseases: [
      { name: "Leaf Rust (Stripe/Yellow)", urdu: "پتوں کی زنگ", severity: "High" },
      { name: "Powdery Mildew", urdu: "سفوفی پھپھوندی", severity: "Medium" },
      { name: "Loose Smut", urdu: "سرمئی کُنگیا", severity: "Medium" }
    ],
    iconBg: "from-amber-500/20 to-yellow-600/10",
    imageUrl: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "cotton",
    name: "Cotton (کپاس)",
    urduName: "کپاس",
    category: "Cash Crop (White Gold)",
    description: "The backbone of Pakistan's textile industry, highly susceptible to viral and sucking pest complexes.",
    diseases: [
      { name: "Cotton Leaf Curl Virus (CLCuV)", urdu: "کپاس کے پتوں کا مڑاؤ وائرس", severity: "High" },
      { name: "Bacterial Blight", urdu: "بیکٹیریل بلائٹ", severity: "High" },
      { name: "Fusarium Wilt", urdu: "مرجھاؤ", severity: "Medium" }
    ],
    iconBg: "from-emerald-500/20 to-teal-600/10",
    imageUrl: "https://images.unsplash.com/photo-1595126730719-197941786877?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "rice",
    name: "Rice (چاول)",
    urduName: "چاول",
    category: "Major Export Grain",
    description: "Basmati and IRRI varieties grown in monsoon flooded paddies across Kalar tract and lower Sindh.",
    diseases: [
      { name: "Bacterial Leaf Blight (BLB)", urdu: "پتوں کا جھلساؤ", severity: "High" },
      { name: "Rice Blast", urdu: "چاول کا بلاسٹ", severity: "High" },
      { name: "Sheath Blight", urdu: "غلاف کا جھلساؤ", severity: "Medium" }
    ],
    iconBg: "from-[#00FFA3]/20 to-emerald-800/10",
    imageUrl: "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "potato",
    name: "Potato (آلو)",
    urduName: "آلو",
    category: "High-Yield Horticulture",
    description: "Vital tuber crop in Okara, Sahiwal, and northern valleys, vulnerable to sudden fungal epidemics.",
    diseases: [
      { name: "Late Blight (Phytophthora)", urdu: "پچھلا جھلساؤ", severity: "High" },
      { name: "Early Blight (Alternaria)", urdu: "اگلا جھلساؤ", severity: "Medium" },
      { name: "Blackleg & Soft Rot", urdu: "کالی ٹانگ اور نرم گلنا", severity: "High" }
    ],
    iconBg: "from-amber-700/20 to-orange-900/10",
    imageUrl: "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "tomato",
    name: "Tomato (ٹماٹر)",
    urduName: "ٹماٹر",
    category: "Vegetable Cash Crop",
    description: "Cultivated nationwide; highly prone to whitefly-transmitted geminiviruses and fungal leaf spots.",
    diseases: [
      { name: "Tomato Yellow Leaf Curl Virus", urdu: "پیلا مڑاؤ وائرس", severity: "High" },
      { name: "Septoria Leaf Spot", urdu: "سیپٹوریا دھبے", severity: "Medium" },
      { name: "Target Spot", urdu: "ٹارگٹ دھبے", severity: "Medium" }
    ],
    iconBg: "from-red-500/20 to-rose-700/10",
    imageUrl: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80"
  },
  {
    id: "sugarcane",
    name: "Sugarcane (گنا)",
    urduName: "گنا",
    category: "Perennial Industrial Crop",
    description: "Long-duration crop feeding Pakistan's sugar mills, heavily impacted by soil-borne fungal rots.",
    diseases: [
      { name: "Red Rot (Sugarcane Cancer)", urdu: "سرخ سڑاند", severity: "High" },
      { name: "Sugarcane Mosaic Virus", urdu: "موزیک وائرس", severity: "Medium" },
      { name: "Whip Smut", urdu: "کوڑا کُنگیا", severity: "Medium" }
    ],
    iconBg: "from-lime-500/20 to-green-700/10",
    imageUrl: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=600&q=80"
  }
];

export default function CropCards() {
  return (
    <section className="w-full py-20 bg-[#0A1A10] text-gray-200 border-t border-white/10">
      <div className="max-w-7xl mx-auto px-6">
        
        {/* Header Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-14 gap-4">
          <div>
            <div className="flex items-center gap-2 text-[#00FFA3] text-base font-semibold tracking-wider uppercase mb-2">
              <Sprout className="w-5 h-5" />
              <span>Pakistani Agricultural Profile</span>
            </div>
            <h2 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight">
              Major Crops & Frequent Diseases
            </h2>
            <p className="text-gray-400 text-base md:text-lg mt-2">
              Common pathological threats affecting Pakistani agriculture detected by ZARI.ai.
            </p>
          </div>
          <span className="text-sm text-gray-400 font-mono bg-black/40 border border-white/10 px-3 py-1.5 rounded-lg">
            6 Key Agronomic Targets
          </span>
        </div>

        {/* Cards Grid - Increased Image Size & Text Scale */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {cropData.map((crop) => (
            <div
              key={crop.id}
              className="group bg-[#0E2417]/80 hover:bg-[#122B1C] border border-white/15 hover:border-[#00FFA3]/50 rounded-2xl p-7 transition-all duration-300 flex flex-col justify-between shadow-xl hover:shadow-[0_0_30px_rgba(0,255,163,0.15)] relative overflow-hidden"
            >
              <div>
                {/* Card Top: Title Left, Substantially Larger Crop Image Right */}
                <div className="flex items-start justify-between gap-5 mb-5">
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-white group-hover:text-[#00FFA3] transition-colors leading-snug">
                      {crop.name}
                    </h3>
                    <span className="inline-block mt-2 text-xs md:text-sm font-semibold text-[#00FFA3] bg-[#00FFA3]/15 border border-[#00FFA3]/30 px-3 py-1 rounded-full">
                      {crop.category}
                    </span>
                  </div>
                  
                  {/* Larger Crop Image Thumbnail (w-24 h-24 / 96px x 96px) */}
                  <div className="w-24 h-24 md:w-28 md:h-28 rounded-2xl overflow-hidden border-2 border-white/20 flex-shrink-0 bg-black/60 shadow-lg group-hover:border-[#00FFA3]/50 transition-colors">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={crop.imageUrl}
                      alt={crop.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                  </div>
                </div>

                {/* Info Description - Slightly Larger Font */}
                <p className="text-sm md:text-base text-gray-300 leading-relaxed mb-6 border-b border-white/10 pb-5">
                  {crop.description}
                </p>

                {/* Frequent Diseases List - Increased Font Sizes */}
                <div className="space-y-2.5 mb-6">
                  <div className="flex items-center gap-2 text-sm font-bold text-gray-200 mb-3">
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                    <span>Frequent Pathogens in Pakistan:</span>
                  </div>
                  {crop.diseases.map((dis, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between text-xs md:text-sm bg-black/40 px-3.5 py-2.5 rounded-xl border border-white/10"
                    >
                      <div className="flex items-center gap-2.5">
                        <span className={`w-2 h-2 rounded-full ${dis.severity === "High" ? "bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.6)]" : "bg-amber-400"}`} />
                        <span className="text-gray-100 font-medium">{dis.name}</span>
                      </div>
                      <span className="text-gray-300 text-xs md:text-sm font-serif" dir="rtl">
                        {dis.urdu}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Card Footer Action */}
              <div className="pt-4 border-t border-white/10 flex items-center justify-between text-sm text-[#00FFA3]/80 group-hover:text-[#00FFA3] font-bold transition-colors">
                <span>AI Diagnostic Ready</span>
                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
