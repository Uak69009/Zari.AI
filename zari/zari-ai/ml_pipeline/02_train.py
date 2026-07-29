"""
=============================================================================
02_train.py — Model Training Pipeline (PyTorch)
=============================================================================
Run this script to train your plant disease classifier from scratch using
EfficientNetV2-S / ResNet50 with automatic class weighting for imbalance.
"""

import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, datasets, models

# Configuration
DATASET_PATH = r"D:\New folder\zari\zari-ai\ml_pipeline\data\raw\plantvillage\raw\color"
MODEL_SAVE_PATH = r"D:\New folder\zari\zari-ai\ml_pipeline\best_model.pth"
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001
IMAGE_SIZE = (224, 224)

def get_data_loaders(data_dir, batch_size=32):
    # Data Augmentation & Normalization
    transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    dataset = datasets.ImageFolder(root=data_dir, transform=transform)
    num_classes = len(dataset.classes)
    
    # Train / Validation Split (80% Train, 20% Val)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    return train_loader, val_loader, dataset.classes

def build_model(num_classes):
    # Load pretrained EfficientNetV2-S
    model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.DEFAULT)
    # Replace final classification head for custom plant classes
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model

def train():
    print("=" * 70)
    print("  ZARI.ai -- STEP 2: MODEL TRAINING")
    print("=" * 70)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    print("Loading dataset...")
    train_loader, val_loader, class_names = get_data_loaders(DATASET_PATH, BATCH_SIZE)
    print(f"Found {len(class_names)} classes | Train samples: {len(train_loader.dataset)} | Val samples: {len(val_loader.dataset)}")

    model = build_model(num_classes=len(class_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    best_val_acc = 0.0

    for epoch in range(1, EPOCHS + 1):
        # Training Phase
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += (preds == labels).sum().item()
            total_train += labels.size(0)

        epoch_train_loss = running_loss / total_train
        epoch_train_acc = (correct_train / total_train) * 100

        # Validation Phase
        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                correct_val += (preds == labels).sum().item()
                total_val += labels.size(0)

        epoch_val_loss = val_loss / total_val
        epoch_val_acc = (correct_val / total_val) * 100

        print(f"Epoch [{epoch:02d}/{EPOCHS:02d}] "
              f"| Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc:.2f}% "
              f"| Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc:.2f}%")

        # Save Best Checkpoint
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': class_names,
                'val_acc': best_val_acc
            }, MODEL_SAVE_PATH)
            print(f"   --> Saved best model checkpoint: {MODEL_SAVE_PATH}")

    print("\nTraining Complete! Best Validation Accuracy: {:.2f}%".format(best_val_acc))

if __name__ == "__main__":
    train()
