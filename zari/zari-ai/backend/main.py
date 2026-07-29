from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.whatsapp import router as whatsapp_router
from api import cv_inference, llm_advisory, tts_engine
import uuid
import os

app = FastAPI(
    title="ZARI.ai API"
)

# Add CORS Middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure temp directory exists and mount it for audio playback
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_AUDIO_DIR = os.path.join(BASE_DIR, "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
app.mount("/temp_audio", StaticFiles(directory=TEMP_AUDIO_DIR), name="temp_audio")

@app.get("/health")
async def health_check():
    return {"status": "ZARI.ai Backend is running"}

@app.post("/predict")
async def web_predict(file: UploadFile = File(...)):
    """Web interface endpoint for the full ZARI inference pipeline."""
    try:
        image_bytes = await file.read()
        
        # 1. Computer Vision
        cv_result = cv_inference.predict(image_bytes)
        
        if cv_result.get("status") != "success":
            return {
                "status": cv_result.get("status"),
                "confidence": cv_result.get("confidence", 0),
                "class_name": "Low Confidence",
                "advisory": cv_result.get("message")
            }
            
        # 2. LLM Advisory
        advisory_text = llm_advisory.generate_advisory(cv_result)
        
        # 3. TTS Audio
        message_id = f"web_{uuid.uuid4().hex[:8]}"
        await tts_engine.generate_audio(advisory_text, message_id)
        
        return {
            "status": "success",
            "confidence": cv_result.get("confidence"),
            "class_name": cv_result.get("data", {}).get("canonical_name", "Unknown"),
            "advisory": advisory_text,
            "audio_url": f"http://localhost:8000/temp_audio/{message_id}.mp3"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Wire the WhatsApp webhook router
app.include_router(whatsapp_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
