export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6">
      {/* Hero Section */}
      <div className="text-center max-w-2xl mx-auto">
        <div className="mb-8">
          <span className="text-6xl">🌿</span>
        </div>

        <h1 className="font-display text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-zari-400 to-zari-600 bg-clip-text text-transparent">
          ZARI.ai
        </h1>

        <p className="text-lg md:text-xl text-zari-200/70 mb-2 font-light">
          فصل کی بیماری کی تشخیص اور مشاورت
        </p>

        <p className="text-sm md:text-base text-zari-200/50 mb-10">
          AI-Powered Crop Disease Diagnosis for Pakistani Farmers
        </p>

        {/* Upload Area */}
        <div className="border-2 border-dashed border-zari-700/50 rounded-2xl p-12 mb-8 hover:border-zari-500/50 transition-colors cursor-pointer bg-zari-950/30">
          <div className="text-4xl mb-4">📸</div>
          <p className="text-zari-300 font-medium mb-2">
            Upload a leaf photo for diagnosis
          </p>
          <p className="text-zari-400/60 text-sm">
            فصل کی پتی کی تصویر یہاں اپلوڈ کریں
          </p>
        </div>

        {/* Status Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-zari-900/50 border border-zari-800/50 text-sm text-zari-400">
          <span className="w-2 h-2 rounded-full bg-zari-500 animate-pulse"></span>
          System initializing — Backend integration pending
        </div>
      </div>
    </main>
  );
}
