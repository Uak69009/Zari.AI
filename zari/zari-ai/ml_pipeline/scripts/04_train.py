import os
import json
import logging
import argparse
import pandas as pd
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_class_weight

# Configure Logging
os.makedirs("ml_pipeline/logs", exist_ok=True)
os.makedirs("ml_pipeline/checkpoints", exist_ok=True)

logging.basicConfig(
    filename="ml_pipeline/logs/03_training_run.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

class CropDataset(Dataset):
    def __init__(self, df, transform=None):
        self.df = df
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row['file_path']
        label = int(row['class_index'])
        
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            # Fallback for corrupted images during training
            image = Image.new('RGB', (224, 224), color='black')
            
        if self.transform:
            image = self.transform(image)
            
        return image, label

def get_transforms():
    train_transforms = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    val_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    return train_transforms, val_transforms

def build_model(num_classes):
    logging.info("Building EfficientNetV2-S architecture...")
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.DEFAULT)
    
    # Replace classifier head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, num_classes)
    )
    return model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-run', action='store_true', help='Run a fast 1-epoch subset for pipeline validation')
    args = parser.parse_args()

    logging.info("Initiating Phase 4: Model Training")
    
    # Load data
    train_df = pd.read_csv("ml_pipeline/splits/train.csv")
    val_df = pd.read_csv("ml_pipeline/splits/val.csv")
    
    # Determine num_classes correctly before subsetting to prevent IndexErrors
    num_classes = train_df['class_index'].max() + 1
    
    if args.test_run:
        logging.info("TEST RUN MODE ENABLED. Subsetting data to 1%...")
        train_df = train_df.sample(frac=0.01, random_state=42)
        val_df = val_df.sample(frac=0.01, random_state=42)
        epochs = 1
    else:
        epochs = 50
    
    # Compute Class Weights to handle imbalance
    logging.info("Computing class weights...")
    classes = np.unique(train_df['class_index'])
    y = train_df['class_index'].values
    computed_weights = compute_class_weight('balanced', classes=classes, y=y)
    
    # Map computed weights to full num_classes array (default 1.0 for missing classes in subset)
    weights = np.ones(num_classes, dtype=np.float32)
    for c, w in zip(classes, computed_weights):
        weights[c] = w
        
    class_weights = torch.tensor(weights, dtype=torch.float)
    
    # Setup DataLoaders
    train_transform, val_transform = get_transforms()
    train_ds = CropDataset(train_df, transform=train_transform)
    val_ds = CropDataset(val_df, transform=val_transform)
    
    batch_size = 32
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")
    
    model = build_model(num_classes).to(device)
    class_weights = class_weights.to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
    
    best_val_loss = float('inf')
    patience_counter = 0
    early_stopping_patience = 7
    history = []
    
    for epoch in range(epochs):
        logging.info(f"Epoch {epoch+1}/{epochs}")
        model.train()
        
        train_loss = 0.0
        for i, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
            if (i+1) % 50 == 0:
                logging.info(f" Batch {i+1}/{len(train_loader)} - Loss: {loss.item():.4f}")
                
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                _, preds = torch.max(outputs, 1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
        val_loss /= len(val_loader)
        scheduler.step(val_loss)
        
        # Metrics
        acc = accuracy_score(all_labels, all_preds)
        prec, rec, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='weighted', zero_division=0)
        
        logging.info(f" Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {acc:.4f} | F1: {f1:.4f}")
        
        history.append({
            "epoch": epoch + 1,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_accuracy": acc,
            "val_f1": f1
        })
        
        # Early Stopping & Checkpointing
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), "ml_pipeline/checkpoints/best_model.pth")
            logging.info(" -> Checkpoint saved (val_loss improved).")
        else:
            patience_counter += 1
            logging.info(f" -> No improvement. Patience: {patience_counter}/{early_stopping_patience}")
            if patience_counter >= early_stopping_patience:
                logging.info("EARLY STOPPING TRIGGERED.")
                break
                
    # Save History
    with open("ml_pipeline/logs/training_history.json", "w") as f:
        json.dump(history, f, indent=4)
        
    logging.info("Phase 4 Complete!")

if __name__ == "__main__":
    main()
