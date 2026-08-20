"""
ZARI.ai Backend — Computer Vision Inference Module
=================================================
Loads the trained EfficientNetV2-B2 model (PyTorch / TorchScript)
and runs GPU/CPU inference with confidence quality gate.
"""

import os
import io
import json
import warnings
import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNS_DIR = os.path.join(BASE_DIR, "ml_pipeline", "scripts", "runs")
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "ml_pipeline", "saved_models")

# Global Cache
_MODEL = None
_CLASS_LABELS = None
_DEVICE = None

def get_latest_run_dir():
    """Find the latest model run directory."""
    if os.path.exists(RUNS_DIR):
        runs = [os.path.join(RUNS_DIR, d) for d in os.listdir(RUNS_DIR) if d.startswith("efficientnetv2_b2")]
        if runs:
            runs.sort(key=os.path.getmtime, reverse=True)
            return runs[0]
    return None

def load_model_and_labels():
    """Lazy-load PyTorch model and class labels mapping."""
    global _MODEL, _CLASS_LABELS, _DEVICE
    if _MODEL is not None and _CLASS_LABELS is not None:
        return _MODEL, _CLASS_LABELS, _DEVICE

    _DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Locate run dir
    run_dir = get_latest_run_dir()
    
    # Check model path priority
    model_path = None
    labels_path = None

    if run_dir:
        bp = os.path.join(run_dir, "best_model.pth")
        lp = os.path.join(run_dir, "class_labels.json")
        if os.path.exists(bp) and os.path.exists(lp):
            model_path = bp
            labels_path = lp

    if not model_path:
        bp = os.path.join(SAVED_MODELS_DIR, "best_model.pth")
        lp = os.path.join(SAVED_MODELS_DIR, "class_labels.json")
        if os.path.exists(bp) and os.path.exists(lp):
            model_path = bp
            labels_path = lp

    if not model_path or not os.path.exists(model_path):
        raise FileNotFoundError("Trained EfficientNetV2-B2 model checkpoint not found!")

    # Load class labels
    with open(labels_path, "r", encoding="utf-8") as f:
        _CLASS_LABELS = json.load(f)

    num_classes = len(_CLASS_LABELS)

    # Load model
    import timm
    _MODEL = timm.create_model('tf_efficientnetv2_b2', pretrained=False, num_classes=num_classes)
    checkpoint = torch.load(model_path, map_location=_DEVICE, weights_only=True)
    if "model_state_dict" in checkpoint:
        _MODEL.load_state_dict(checkpoint["model_state_dict"])
    else:
        _MODEL.load_state_dict(checkpoint)

    _MODEL.to(_DEVICE)
    _MODEL.eval()

    print(f"Loaded EfficientNetV2-B2 model ({num_classes} classes) on {_DEVICE}")
    return _MODEL, _CLASS_LABELS, _DEVICE


def transform_image(image_bytes: bytes):
    """Preprocess image bytes for EfficientNetV2-B2 model."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    transform = T.Compose([
        T.Resize((292), interpolation=T.InterpolationMode.BICUBIC),
        T.CenterCrop(260),
        T.ToTensor(),
        T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
    ])
    return transform(image).unsqueeze(0)


def predict(image_bytes: bytes, confidence_threshold: float = 0.50) -> dict:
    """
    Run inference on leaf image bytes and return diagnosis dictionary.
    """
    try:
        model, class_labels, device = load_model_and_labels()
        tensor = transform_image(image_bytes).to(device)

        with torch.no_grad():
            output = model(tensor)
            probabilities = torch.softmax(output, dim=1)[0]
            top_prob, top_idx = torch.topk(probabilities, k=3)

        pred_idx = str(top_idx[0].item())
        confidence = float(top_prob[0].item())
        predicted_label = class_labels.get(pred_idx, f"Class_{pred_idx}")

        # Extract top 3 predictions
        top3 = []
        for i in range(3):
            idx_str = str(top_idx[i].item())
            top3.append({
                "class_name": class_labels.get(idx_str, f"Class_{idx_str}"),
                "confidence": round(float(top_prob[i].item()), 4)
            })

        # Format clean display names
        crop = predicted_label.split("_")[0] if "_" in predicted_label else "Crop"
        disease = "_".join(predicted_label.split("_")[1:]) if "_" in predicted_label else predicted_label

        is_confident = confidence >= confidence_threshold

        return {
            "status": "success" if is_confident else "low_confidence",
            "confidence": round(confidence, 4),
            "class_id": int(pred_idx),
            "class_name": predicted_label,
            "canonical_name": predicted_label.replace("_", " "),
            "crop": crop,
            "disease": disease.replace("_", " "),
            "is_confident": is_confident,
            "top3": top3,
            "data": {
                "canonical_name": predicted_label.replace("_", " "),
                "crop": crop,
                "disease": disease.replace("_", " ")
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"CV Inference failed: {str(e)}",
            "confidence": 0.0,
            "class_name": "Unknown",
            "data": {"canonical_name": "Unknown"}
        }
