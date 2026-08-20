from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uuid
import os
from typing import Optional

from api import cv_inference, llm_advisory, tts_engine
from api.routes import router as api_router
from api.whatsapp import router as whatsapp_router

app = FastAPI(
    title="ZARI.ai Autonomous Agricultural Intelligence API",
    description="Backend API for EfficientNetV2-B2 Plant Disease Diagnostics & Urdu Advisory System",
    version="2.0.0"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audio temp folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_AUDIO_DIR = os.path.join(BASE_DIR, "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
app.mount("/temp_audio", StaticFiles(directory=TEMP_AUDIO_DIR), name="temp_audio")

# Mount API routers
app.include_router(api_router, prefix="/api")
app.include_router(whatsapp_router)

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": "ZARI.ai Agricultural Intelligence Backend",
        "model": "EfficientNetV2-B2 (150 Classes)",
        "device": str(cv_inference._DEVICE) if hasattr(cv_inference, "_DEVICE") else "PyTorch CUDA"
    }

@app.post("/predict")
async def web_predict(file: UploadFile = File(...)):
    """
    Main web application prediction endpoint.
    Processes leaf image -> EfficientNetV2-B2 inference -> Urdu advisory.
    """
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file uploaded.")

        # 1. Computer Vision Inference
        cv_result = cv_inference.predict(image_bytes)

        if cv_result.get("status") == "error":
            return JSONResponse(status_code=500, content=cv_result)

        # 2. Expert Urdu Advisory Generation
        advisory_text = llm_advisory.generate_advisory(cv_result)

        # 3. Text-to-Speech Audio (Optional generation)
        message_id = f"web_{uuid.uuid4().hex[:8]}"
        audio_url = None
        try:
            audio_path = await tts_engine.generate_audio(advisory_text, message_id)
            if audio_path and os.path.exists(audio_path):
                audio_url = f"http://localhost:8000/temp_audio/{os.path.basename(audio_path)}"
        except Exception as tts_err:
            print(f"TTS Generation optional skip: {tts_err}")

        class_name = cv_result.get("data", {}).get("canonical_name", cv_result.get("class_name", "Unknown"))

        return {
            "status": cv_result.get("status", "success"),
            "confidence": cv_result.get("confidence", 0.0),
            "class_name": class_name,
            "crop": cv_result.get("crop", "Unknown"),
            "disease": cv_result.get("disease", "Unknown"),
            "top3": cv_result.get("top3", []),
            "advisory": advisory_text,
            "audio_url": audio_url,
            "is_confident": cv_result.get("is_confident", True)
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
