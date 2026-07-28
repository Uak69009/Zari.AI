import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ZARI.ai — Crop Disease Diagnosis",
  description:
    "Multi-modal agricultural crop disease diagnosis and advisory platform for Pakistani farmers. Powered by AI.",
  keywords: [
    "crop disease",
    "agriculture",
    "AI",
    "Pakistan",
    "farming",
    "plant disease",
    "ZARI",
  ],
  authors: [{ name: "Umair Amjad Khan" }],
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
  themeColor: "#16a34a",
  manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ur" dir="ltr">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
