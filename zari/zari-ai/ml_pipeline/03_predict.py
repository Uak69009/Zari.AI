"""
=============================================================================
03_predict.py — Model Inference & Prediction Tester
=============================================================================
Run this script to test single-image prediction using your trained model checkpoint.
Usage: python 03_predict.py path/to/leaf_image.jpg
"""

import sys
import os
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models

MODEL_PATH = r"D:\New folder\zari\zari-ai\ml_pipeline\best_model.pth"
IMAGE_SIZE = (224, 224)

transform = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def predict_image(image_path):
    print("=" * 70)
    print("  ZARI.ai -- STEP 3: SINGLE IMAGE PREDICTION")
    print("=" * 70)

    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model weights file not found at {MODEL_PATH}")
        print("Please run 02_train.py first to train and save model weights.")
        return

    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load checkpoint
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    class_names = checkpoint['class_names']
    
    # Load model
    model = models.efficientnet_v2_s(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, len(class_names))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()

    # Preprocess image
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        outputs = model(tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        confidence, predicted_idx = torch.max(probabilities, dim=0)

    disease_name = class_names[predicted_idx.item()]
    conf_pct = confidence.item() * 100

    print(f"\nImage File  : {os.path.basename(image_path)}")
    print(f"Diagnosis   : {disease_name}")
    print(f"Confidence  : {conf_pct:.2f}%")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        # Example default path
        img_path = r"D:\New folder\zari\zari-ai\ml_pipeline\data\raw\plantvillage\raw\color\Apple___Apple_scab\0a5e9323-dbad-432d-9f58-28f9a286c0e8___FREC_Scab 3417.JPG"
    
    predict_image(img_path)
