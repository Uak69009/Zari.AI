import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim

# Ensure we can import from the ml_pipeline modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from data.dataset import build_dataloaders
from models.model import build_model

DATA_DIR = os.path.join(BASE_DIR, "data")
TAXONOMY_PATH = os.path.join(DATA_DIR, "taxonomy.json")
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "saved_models")

def get_num_classes():
    """Dynamically determine the number of classes from taxonomy.json."""
    if not os.path.exists(TAXONOMY_PATH):
        raise FileNotFoundError(f"Taxonomy JSON not found at {TAXONOMY_PATH}")
        
    with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)
        
    classes = taxonomy.get("classes", {})
    return len(classes)

def train_model(epochs=10):
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    best_model_path = os.path.join(SAVED_MODELS_DIR, "best_zari_model.pth")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # 1. Load Data
    print("Building DataLoaders...")
    train_loader, val_loader = build_dataloaders(batch_size=32, num_workers=4)
    
    if len(train_loader) == 0:
        print("Warning: No training data found. Make sure the dataset is downloaded in data/raw.")
        return
        
    # 2. Setup Model
    num_classes = get_num_classes()
    print(f"Number of classes determined from taxonomy: {num_classes}")
    
    print("Building Model (EfficientNetV2-S)...")
    # Utilizing freeze_backbone for phase 2 fine-tuning potential
    model = build_model(num_classes=num_classes, freeze_backbone=False)
    model = model.to(device)
    
    # 3. Setup Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3)
    
    best_val_acc = 0.0
    
    # 4. Training Loop
    print("\nStarting Training Loop...")
    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 25)
        
        # --- Training Phase ---
        model.train()
        running_loss = 0.0
        
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            # Zero the parameter gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            
            if (batch_idx + 1) % 10 == 0 or (batch_idx + 1) == len(train_loader):
                print(f"  [Train] Batch {batch_idx+1}/{len(train_loader)} - Loss: {loss.item():.4f}")
            
        epoch_loss = running_loss / len(train_loader.dataset)
        
        # --- Validation Phase ---
        model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                # Forward pass
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
        epoch_acc = correct / total if total > 0 else 0.0
        
        print(f"-> Epoch Summary | Train Loss: {epoch_loss:.4f} | Val Accuracy: {epoch_acc:.4f}")
        
        # Save best model
        if epoch_acc >= best_val_acc and total > 0:
            best_val_acc = epoch_acc
            print(f"-> Validation accuracy improved to {best_val_acc:.4f}. Saving model to {best_model_path}...")
            torch.save(model.state_dict(), best_model_path)
            
    print(f"\nTraining complete. Best Validation Accuracy: {best_val_acc:.4f}")

if __name__ == "__main__":
    train_model(epochs=10)
