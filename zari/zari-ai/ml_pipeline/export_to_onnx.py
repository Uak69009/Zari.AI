import os
import sys
import json
import torch
import warnings

# Ensure we can import from the ml_pipeline modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from models.model import build_model

DATA_DIR = os.path.join(BASE_DIR, "data")
TAXONOMY_PATH = os.path.join(DATA_DIR, "taxonomy.json")
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "saved_models")
WEIGHTS_PATH = os.path.join(SAVED_MODELS_DIR, "best_zari_model.pth")
ONNX_OUT_PATH = os.path.join(SAVED_MODELS_DIR, "zari_model.onnx")

def get_num_classes():
    """Dynamically determine the number of classes from taxonomy.json."""
    if not os.path.exists(TAXONOMY_PATH):
        raise FileNotFoundError(f"Taxonomy JSON not found at {TAXONOMY_PATH}")
        
    with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)
        
    classes = taxonomy.get("classes", {})
    return len(classes)

def export_onnx():
    # 1. Ensure directory exists
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    
    # 2. Determine class count
    num_classes = get_num_classes()
    print(f"Number of classes determined from taxonomy: {num_classes}")
    
    # 3. Instantiate model
    print("Instantiating PyTorch model...")
    model = build_model(num_classes=num_classes)
    
    # 4. Check for existing weights
    if os.path.exists(WEIGHTS_PATH):
        print(f"Loading trained weights from {WEIGHTS_PATH}...")
        model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
    else:
        warnings.warn(f"Trained weights not found at {WEIGHTS_PATH}. Proceeding with randomly initialized weights for validation.")
        
    # 5. Set model to eval mode
    model.eval()
    
    # 6. Create dummy input tensor
    print("Creating dummy input tensor of shape (1, 3, 224, 224)...")
    dummy_input = torch.randn(1, 3, 224, 224)
    
    # 7. Export to ONNX
    print(f"Exporting model to ONNX format -> {ONNX_OUT_PATH}")
    torch.onnx.export(
        model,
        dummy_input,
        ONNX_OUT_PATH,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    print(f"\n[OK] Model successfully exported to: {ONNX_OUT_PATH}")

if __name__ == "__main__":
    export_onnx()
