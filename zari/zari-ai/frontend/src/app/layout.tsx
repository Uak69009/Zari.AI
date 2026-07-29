import type { Metadata } from "next";
import "./globals.css";
import Navbar from "./components/Navbar";

export const metadata: Metadata = {
  title: "ZARI.ai - Agricultural Intelligence",
  description: "ZARI.ai is a multi-modal agricultural crop disease diagnosis and advisory platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-[#0A1A10] text-gray-200 antialiased">
        
        {/* Responsive Client-Side Navigation Bar */}
        <Navbar />

        {/* Full-width Main Content Container */}
        <main className="w-full">
          {children}
        </main>
      </body>
    </html>
  );
}
