"""
ZARI.ai Backend — API Routes
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from api import cv_inference, llm_advisory

router = APIRouter()

@router.post("/diagnose")
async def diagnose_crop_disease(
    file: UploadFile = File(...),
    language: Optional[str] = "ur",
):
    """
    Diagnose crop disease from uploaded leaf image bytes.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Please upload JPEG, PNG, or WebP.",
        )

    image_bytes = await file.read()
    result = cv_inference.predict(image_bytes)

    advisory_text = llm_advisory.generate_advisory(result)

    return JSONResponse(
        status_code=200,
        content={
            "status": result.get("status", "success"),
            "disease_label": result.get("class_name"),
            "confidence": result.get("confidence"),
            "crop": result.get("crop"),
            "disease": result.get("disease"),
            "top3": result.get("top3", []),
            "advisory": advisory_text,
            "is_confident": result.get("is_confident", True)
        },
    )

@router.get("/taxonomy")
async def get_taxonomy():
    """Return available class labels."""
    _, class_labels, _ = cv_inference.load_model_and_labels()
    return {"total_classes": len(class_labels), "classes": class_labels}
