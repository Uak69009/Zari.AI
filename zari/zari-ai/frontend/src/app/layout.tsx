import type { Metadata } from "next";
import "./globals.css";
import Navbar from "./components/Navbar";

export const metadata: Metadata = {
  title: "ZARI.ai — Crop Disease Diagnosis",
  description: "ZARI.ai is a multi-modal agricultural crop disease diagnosis and advisory platform for Pakistani farmers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
      </head>
      <body style={{ backgroundColor: "#0A1A10", color: "#E5E7EB", fontFamily: "Inter, system-ui, sans-serif" }}>
        <Navbar />
        <main className="w-full">
          {children}
        </main>
      </body>
    </html>
  );
}
