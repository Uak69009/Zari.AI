"use client";

import { useState } from "react";
import Link from "next/link";
import { Leaf, Menu, X } from "lucide-react";

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const navLinks = [
    { name: "Home", href: "/" },
    { name: "Diagnostics", href: "#diagnostics" },
    { name: "About ZARI", href: "#about" },
    { name: "Contact", href: "#contact" },
  ];

  return (
    <header className="w-full bg-white/90 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 border border-emerald-200 flex items-center justify-center group-hover:bg-emerald-600 transition-colors">
            <Leaf className="text-emerald-700 group-hover:text-white w-6 h-6 transition-colors" />
          </div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            ZARI<span className="text-emerald-600">.ai</span>
          </h1>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link 
              key={link.name} 
              href={link.href} 
              className="text-sm font-semibold text-gray-700 hover:text-emerald-700 transition-colors"
            >
              {link.name}
            </Link>
          ))}
        </nav>

        {/* Mobile Menu Button */}
        <button 
          onClick={toggleMenu}
          className="md:hidden text-gray-700 hover:text-emerald-700 transition-colors focus:outline-none"
        >
          {isMobileMenuOpen ? <X size={28} /> : <Menu size={28} />}
        </button>
      </div>

      {/* Mobile Navigation Dropdown */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-gray-200 overflow-hidden shadow-lg">
          <div className="flex flex-col px-6 py-4 space-y-4">
            {navLinks.map((link) => (
              <Link 
                key={link.name} 
                href={link.href} 
                onClick={() => setIsMobileMenuOpen(false)}
                className="text-base font-semibold text-gray-700 hover:text-emerald-700 transition-colors block border-b border-gray-100 pb-2"
              >
                {link.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
