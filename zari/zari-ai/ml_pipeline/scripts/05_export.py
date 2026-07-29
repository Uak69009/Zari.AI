import os
import json
import logging
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

CHECKPOINT_PATH = "ml_pipeline/checkpoints/best_model.pth"
EXPORT_PATH = "ml_pipeline/checkpoints/best_model_jit.pt"
TAXONOMY_PATH = "ml_pipeline/taxonomy.json"

def build_model(num_classes):
    logging.info("Building EfficientNetV2-S for Export...")
    model = models.efficientnet_v2_s(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, num_classes)
    )
    return model

def main():
    logging.info("Initiating Phase 5: Export & Inference Parity Testing")
    
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)
    num_classes = len(taxonomy)
    
    device = torch.device("cpu") # Exporting on CPU to ensure backend compatibility
    
    model = build_model(num_classes)
    model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=device))
    model.to(device)
    model.eval()
    
    # 1. Export to TorchScript (JIT) as a replacement for ONNX
    logging.info("Tracing model with TorchScript (JIT)...")
    dummy_input = torch.randn(1, 3, 224, 224, device=device)
    
    try:
        traced_model = torch.jit.trace(model, dummy_input)
        traced_model.save(EXPORT_PATH)
        logging.info(f"Model successfully traced and exported to {EXPORT_PATH}")
    except Exception as e:
        logging.error(f"Failed to export TorchScript: {e}")
        return

    # 2. Basic Inference Parity Test
    logging.info("Running inference parity test on traced model...")
    with torch.no_grad():
        raw_output = model(dummy_input)
        traced_output = traced_model(dummy_input)
        
    diff = (raw_output - traced_output).abs().max().item()
    logging.info(f"Max absolute difference between raw PyTorch and JIT Traced: {diff:.6f}")
    
    if diff < 1e-4:
        logging.info("Parity Test PASSED. Model is identical.")
    else:
        logging.warning("Parity Test WARNING. Slight differences detected.")
        
    logging.info("Phase 5 Complete!")

if __name__ == "__main__":
    main()
