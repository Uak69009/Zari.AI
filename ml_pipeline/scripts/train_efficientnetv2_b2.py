#!/usr/bin/env python3
"""
ZARI.ai — EfficientNetV2-B2 Plant Disease Classification Training Pipeline
===========================================================================
Single self-contained script for training, evaluation, and model export.

Model:      tf_efficientnetv2_b2 (ImageNet pretrained, timm)
Dataset:    142,596 images across 150 crop-disease classes
Split:      80/10/10 stratified
Loss:       CrossEntropy with sqrt-dampened inverse-frequency class weights
Optimizer:  AdamW + CosineAnnealingWarmRestarts + AMP (mixed precision)
GPU:        NVIDIA RTX 4090 (24 GB)
"""

import os
import sys
import json
import csv
import time
import random
import warnings
from datetime import datetime
from pathlib import Path
from collections import OrderedDict

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.amp import autocast, GradScaler
import torchvision.transforms as T
from PIL import Image, ImageFile

import timm
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, f1_score,
    precision_score, recall_score, accuracy_score, top_k_accuracy_score
)

# Allow truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True
warnings.filterwarnings('ignore', category=UserWarning)

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────
CONFIG = {
    # Paths
    'csv_path': '/home/hammad/Desktop/project zari - experimental/ml_pipeline/ANALYSIS_COMPLETE/dataset_clean_final.csv',
    'output_base': '/home/hammad/Desktop/project zari/ml_pipeline/scripts/runs',

    # Model
    'model_name': 'tf_efficientnetv2_b2',
    'pretrained': True,
    'input_size': 260,           # Upscaled from default 208 for better accuracy
    'min_class_samples': 20,     # Remove classes with fewer images

    # Training
    'batch_size': 64,
    'epochs': 30,
    'lr': 1e-3,
    'weight_decay': 1e-4,
    'label_smoothing': 0.1,
    'gradient_clip': 1.0,
    'num_workers': 8,

    # Scheduler
    'scheduler_T0': 5,
    'scheduler_Tmult': 2,

    # Early stopping
    'patience': 7,

    # Split
    'train_ratio': 0.80,
    'val_ratio': 0.10,
    'test_ratio': 0.10,

    # Reproducibility
    'seed': 42,

    # ImageNet normalization
    'mean': (0.485, 0.456, 0.406),
    'std': (0.229, 0.224, 0.225),
}


def set_seed(seed):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True  # Faster on fixed input sizes


# ─────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────
class PlantDiseaseDataset(Dataset):
    """PyTorch Dataset for plant disease image classification."""

    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        try:
            img = Image.open(img_path).convert('RGB')
        except Exception:
            # Return a blank image on error (rare)
            img = Image.new('RGB', (CONFIG['input_size'], CONFIG['input_size']), (0, 0, 0))

        if self.transform:
            img = self.transform(img)

        return img, label


def get_transforms(split='train'):
    """Get data transforms for train/val/test."""
    input_size = CONFIG['input_size']
    mean = CONFIG['mean']
    std = CONFIG['std']

    if split == 'train':
        return T.Compose([
            T.RandomResizedCrop(input_size, scale=(0.7, 1.0), interpolation=T.InterpolationMode.BICUBIC),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.3),
            T.RandomRotation(15),
            T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.05),
            T.RandAugment(num_ops=2, magnitude=9),
            T.ToTensor(),
            T.Normalize(mean=mean, std=std),
            T.RandomErasing(p=0.1, scale=(0.02, 0.15)),
        ])
    else:
        # Val & Test: deterministic resize + center crop
        resize_size = int(input_size / 0.89)  # ~292 for crop_pct=0.89
        return T.Compose([
            T.Resize(resize_size, interpolation=T.InterpolationMode.BICUBIC),
            T.CenterCrop(input_size),
            T.ToTensor(),
            T.Normalize(mean=mean, std=std),
        ])


# ─────────────────────────────────────────────────────────────
# Data Loading & Splitting
# ─────────────────────────────────────────────────────────────
def load_and_split_data(config):
    """Load CSV, filter classes, create stratified 80/10/10 split."""
    print("=" * 70)
    print("STEP 1: Loading & Splitting Dataset")
    print("=" * 70)

    df = pd.read_csv(config['csv_path'])
    print(f"  Loaded CSV: {len(df):,} rows, {df['class_name'].nunique()} classes")

    # Filter classes below minimum threshold
    class_counts = df['class_name'].value_counts()
    valid_classes = class_counts[class_counts >= config['min_class_samples']].index
    removed_classes = class_counts[class_counts < config['min_class_samples']]
    df = df[df['class_name'].isin(valid_classes)].reset_index(drop=True)

    if len(removed_classes) > 0:
        print(f"  Removed {len(removed_classes)} classes with < {config['min_class_samples']} samples:")
        for name, cnt in removed_classes.items():
            print(f"    - {name}: {cnt} samples")
    else:
        print(f"  All classes have >= {config['min_class_samples']} samples. No classes removed.")

    # Create label encoding
    unique_classes = sorted(df['class_name'].unique())
    num_classes = len(unique_classes)
    class_to_idx = {name: idx for idx, name in enumerate(unique_classes)}
    idx_to_class = {idx: name for name, idx in class_to_idx.items()}
    df['label'] = df['class_name'].map(class_to_idx)

    print(f"  Final dataset: {len(df):,} samples, {num_classes} classes")

    # Stratified 80/10/10 split
    # First split: 80% train, 20% temp
    train_df, temp_df = train_test_split(
        df, test_size=(1 - config['train_ratio']),
        stratify=df['label'], random_state=config['seed']
    )
    # Second split: 50/50 of temp → 10% val, 10% test
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5,
        stratify=temp_df['label'], random_state=config['seed']
    )

    print(f"  Split: Train={len(train_df):,} ({len(train_df)/len(df)*100:.1f}%) | "
          f"Val={len(val_df):,} ({len(val_df)/len(df)*100:.1f}%) | "
          f"Test={len(test_df):,} ({len(test_df)/len(df)*100:.1f}%)")

    return train_df, val_df, test_df, class_to_idx, idx_to_class, num_classes


def compute_class_weights(train_df, num_classes, device):
    """Compute sqrt-dampened inverse frequency class weights."""
    class_counts = train_df['label'].value_counts().sort_index()
    total = len(train_df)

    # Inverse frequency with sqrt dampening
    weights = []
    for i in range(num_classes):
        count = class_counts.get(i, 1)
        w = np.sqrt(total / (num_classes * count))
        weights.append(w)

    weights = torch.FloatTensor(weights).to(device)
    # Normalize so mean weight = 1.0
    weights = weights / weights.mean()

    print(f"  Class weights: min={weights.min():.3f}, max={weights.max():.3f}, "
          f"mean={weights.mean():.3f}, std={weights.std():.3f}")

    return weights


# ─────────────────────────────────────────────────────────────
# Model Creation
# ─────────────────────────────────────────────────────────────
def create_model(num_classes, config, device):
    """Create EfficientNetV2-B2 model with ImageNet pretrained weights."""
    print("\n" + "=" * 70)
    print("STEP 2: Creating Model")
    print("=" * 70)

    model = timm.create_model(
        config['model_name'],
        pretrained=config['pretrained'],
        num_classes=num_classes,
        drop_rate=0.3,
        drop_path_rate=0.2,
    )

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Model: {config['model_name']}")
    print(f"  Pretrained: {config['pretrained']} (ImageNet)")
    print(f"  Total params: {total_params:,}")
    print(f"  Trainable params: {trainable_params:,}")
    print(f"  Input size: {config['input_size']}×{config['input_size']}")
    print(f"  Num classes: {num_classes}")

    model = model.to(device)
    return model


# ─────────────────────────────────────────────────────────────
# Training Engine
# ─────────────────────────────────────────────────────────────
def train_one_epoch(model, loader, criterion, optimizer, scaler, device, epoch, total_epochs):
    """Train for one epoch with AMP mixed precision."""
    model.train()
    running_loss = 0.0
    all_preds = []
    all_labels = []
    num_batches = len(loader)

    for batch_idx, (images, labels) in enumerate(loader):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        with autocast(device_type='cuda'):
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), CONFIG['gradient_clip'])
        scaler.step(optimizer)
        scaler.update()

        running_loss += loss.item()
        preds = outputs.argmax(dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

        # Progress every 50 batches
        if (batch_idx + 1) % 50 == 0 or (batch_idx + 1) == num_batches:
            current_loss = running_loss / (batch_idx + 1)
            print(f"    Batch [{batch_idx+1}/{num_batches}] Loss: {current_loss:.4f}", flush=True)

    epoch_loss = running_loss / num_batches
    epoch_acc = accuracy_score(all_labels, all_preds)
    epoch_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)

    return epoch_loss, epoch_acc, epoch_f1


@torch.no_grad()
def validate(model, loader, criterion, device):
    """Validate the model."""
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_labels = []
    all_probs = []

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        with autocast(device_type='cuda'):
            outputs = model(images)
            loss = criterion(outputs, labels)

        running_loss += loss.item()
        probs = torch.softmax(outputs.float(), dim=1)
        preds = probs.argmax(dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())

    epoch_loss = running_loss / len(loader)
    epoch_acc = accuracy_score(all_labels, all_preds)
    epoch_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)

    return epoch_loss, epoch_acc, epoch_f1, np.array(all_preds), np.array(all_labels), np.array(all_probs)


def train(model, train_loader, val_loader, criterion, optimizer, scheduler, device, config, run_dir):
    """Full training loop with early stopping and checkpointing."""
    print("\n" + "=" * 70)
    print("STEP 3: Training")
    print("=" * 70)
    print(f"  Epochs: {config['epochs']}")
    print(f"  Batch size: {config['batch_size']}")
    print(f"  Learning rate: {config['lr']}")
    print(f"  Early stopping patience: {config['patience']}")
    print(f"  Device: {device}")
    print()

    scaler = GradScaler('cuda')

    best_val_f1 = 0.0
    best_epoch = 0
    patience_counter = 0
    history = []

    log_path = os.path.join(run_dir, 'training_log.csv')
    with open(log_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['epoch', 'train_loss', 'train_acc', 'train_f1',
                         'val_loss', 'val_acc', 'val_f1', 'lr', 'time_sec'])

    total_start = time.time()

    for epoch in range(1, config['epochs'] + 1):
        epoch_start = time.time()
        current_lr = optimizer.param_groups[0]['lr']

        print(f"  Epoch [{epoch}/{config['epochs']}] lr={current_lr:.6f}")

        # Train
        train_loss, train_acc, train_f1 = train_one_epoch(
            model, train_loader, criterion, optimizer, scaler, device, epoch, config['epochs']
        )

        # Validate
        val_loss, val_acc, val_f1, _, _, _ = validate(model, val_loader, criterion, device)

        # Step scheduler
        scheduler.step()

        epoch_time = time.time() - epoch_start

        print(f"  ─── Train Loss: {train_loss:.4f} | Acc: {train_acc:.4f} | F1: {train_f1:.4f}")
        print(f"  ─── Val   Loss: {val_loss:.4f} | Acc: {val_acc:.4f} | F1: {val_f1:.4f}")
        print(f"  ─── Time: {epoch_time:.1f}s")

        # Log
        history.append({
            'epoch': epoch,
            'train_loss': train_loss, 'train_acc': train_acc, 'train_f1': train_f1,
            'val_loss': val_loss, 'val_acc': val_acc, 'val_f1': val_f1,
            'lr': current_lr, 'time_sec': epoch_time
        })

        with open(log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([epoch, f"{train_loss:.6f}", f"{train_acc:.6f}", f"{train_f1:.6f}",
                             f"{val_loss:.6f}", f"{val_acc:.6f}", f"{val_f1:.6f}",
                             f"{current_lr:.8f}", f"{epoch_time:.2f}"])

        # Checkpoint best model
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch
            patience_counter = 0
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'val_f1': val_f1,
                'val_acc': val_acc,
                'val_loss': val_loss,
            }, os.path.join(run_dir, 'best_model.pth'))
            print(f"  ★ New best model saved! (Val F1: {val_f1:.4f})")
        else:
            patience_counter += 1
            print(f"  No improvement ({patience_counter}/{config['patience']})")

        print()

        # Early stopping
        if patience_counter >= config['patience']:
            print(f"  ⚠ Early stopping triggered at epoch {epoch}. Best epoch: {best_epoch}")
            break

    total_time = time.time() - total_start
    print(f"  Training completed in {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"  Best validation F1: {best_val_f1:.4f} at epoch {best_epoch}")

    # Save final model
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
    }, os.path.join(run_dir, 'final_model.pth'))

    return history, best_epoch, best_val_f1


# ─────────────────────────────────────────────────────────────
# Evaluation & Visualization
# ─────────────────────────────────────────────────────────────
def evaluate_and_visualize(model, test_loader, criterion, device, idx_to_class, run_dir, history):
    """Full evaluation suite on the test set."""
    print("\n" + "=" * 70)
    print("STEP 4: Evaluation on Test Set")
    print("=" * 70)

    eval_dir = os.path.join(run_dir, 'evaluation')
    os.makedirs(eval_dir, exist_ok=True)

    # Load best model
    ckpt = torch.load(os.path.join(run_dir, 'best_model.pth'), map_location=device, weights_only=True)
    model.load_state_dict(ckpt['model_state_dict'])

    # Run evaluation
    test_loss, test_acc, test_f1, all_preds, all_labels, all_probs = validate(
        model, test_loader, criterion, device
    )

    print(f"  Test Loss: {test_loss:.4f}")
    print(f"  Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
    print(f"  Test Macro-F1: {test_f1:.4f}")

    # Weighted F1
    weighted_f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    macro_precision = precision_score(all_labels, all_preds, average='macro', zero_division=0)
    macro_recall = recall_score(all_labels, all_preds, average='macro', zero_division=0)
    print(f"  Test Weighted-F1: {weighted_f1:.4f}")
    print(f"  Test Macro-Precision: {macro_precision:.4f}")
    print(f"  Test Macro-Recall: {macro_recall:.4f}")

    # Top-5 accuracy
    try:
        top5_acc = top_k_accuracy_score(all_labels, all_probs, k=5)
        print(f"  Test Top-5 Accuracy: {top5_acc:.4f} ({top5_acc*100:.2f}%)")
    except Exception:
        top5_acc = None

    # Classification report
    class_names = [idx_to_class[i] for i in range(len(idx_to_class))]
    report = classification_report(all_labels, all_preds, target_names=class_names, zero_division=0)
    print("\n  Classification Report (first 60 lines):")
    for line in report.split('\n')[:60]:
        print(f"    {line}")

    with open(os.path.join(eval_dir, 'classification_report.txt'), 'w') as f:
        f.write(report)

    # Save evaluation summary
    summary = {
        'test_loss': round(test_loss, 6),
        'test_accuracy': round(test_acc, 6),
        'test_macro_f1': round(test_f1, 6),
        'test_weighted_f1': round(weighted_f1, 6),
        'test_macro_precision': round(macro_precision, 6),
        'test_macro_recall': round(macro_recall, 6),
        'test_top5_accuracy': round(top5_acc, 6) if top5_acc else None,
        'best_epoch': int(ckpt['epoch']),
        'num_classes': len(idx_to_class),
        'test_samples': len(all_labels),
    }
    with open(os.path.join(eval_dir, 'evaluation_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    # ── Visualization: Training Curves ──
    plot_training_curves(history, eval_dir)

    # ── Visualization: Confusion Matrix (Top 20 confused pairs) ──
    plot_confusion_matrix(all_labels, all_preds, idx_to_class, eval_dir)

    # ── Visualization: Per-Class F1 Scores ──
    plot_per_class_f1(all_labels, all_preds, idx_to_class, eval_dir)

    # ── Visualization: Confidence Distribution ──
    plot_confidence_distribution(all_preds, all_labels, all_probs, eval_dir)

    return summary


def plot_training_curves(history, eval_dir):
    """Plot training and validation loss, accuracy, and F1 over epochs."""
    epochs = [h['epoch'] for h in history]
    train_loss = [h['train_loss'] for h in history]
    val_loss = [h['val_loss'] for h in history]
    train_acc = [h['train_acc'] for h in history]
    val_acc = [h['val_acc'] for h in history]
    train_f1 = [h['train_f1'] for h in history]
    val_f1 = [h['val_f1'] for h in history]
    lrs = [h['lr'] for h in history]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=200)

    # Loss
    axes[0, 0].plot(epochs, train_loss, 'o-', color='#2563eb', linewidth=2, label='Train Loss', markersize=4)
    axes[0, 0].plot(epochs, val_loss, 's-', color='#dc2626', linewidth=2, label='Val Loss', markersize=4)
    axes[0, 0].set_title('Loss Curves', fontsize=13, fontweight='bold')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].legend(fontsize=10)
    axes[0, 0].grid(True, alpha=0.3)

    # Accuracy
    axes[0, 1].plot(epochs, train_acc, 'o-', color='#2563eb', linewidth=2, label='Train Acc', markersize=4)
    axes[0, 1].plot(epochs, val_acc, 's-', color='#dc2626', linewidth=2, label='Val Acc', markersize=4)
    axes[0, 1].set_title('Accuracy Curves', fontsize=13, fontweight='bold')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Accuracy')
    axes[0, 1].legend(fontsize=10)
    axes[0, 1].grid(True, alpha=0.3)

    # F1
    axes[1, 0].plot(epochs, train_f1, 'o-', color='#2563eb', linewidth=2, label='Train Macro-F1', markersize=4)
    axes[1, 0].plot(epochs, val_f1, 's-', color='#dc2626', linewidth=2, label='Val Macro-F1', markersize=4)
    axes[1, 0].set_title('Macro-F1 Curves', fontsize=13, fontweight='bold')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('F1 Score')
    axes[1, 0].legend(fontsize=10)
    axes[1, 0].grid(True, alpha=0.3)

    # Learning Rate
    axes[1, 1].plot(epochs, lrs, 'o-', color='#7c3aed', linewidth=2, markersize=4)
    axes[1, 1].set_title('Learning Rate Schedule', fontsize=13, fontweight='bold')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('LR')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(eval_dir, 'training_curves.png'), bbox_inches='tight')
    plt.close()
    print("  ✓ Saved training_curves.png")


def plot_confusion_matrix(all_labels, all_preds, idx_to_class, eval_dir):
    """Plot confusion matrix showing top-20 most confused class pairs."""
    cm = confusion_matrix(all_labels, all_preds)
    num_classes = cm.shape[0]

    # Find top-20 most confused pairs (off-diagonal)
    confused_pairs = []
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j and cm[i, j] > 0:
                confused_pairs.append((i, j, cm[i, j]))

    confused_pairs.sort(key=lambda x: x[2], reverse=True)
    top_confused = confused_pairs[:20]

    # Get unique classes involved
    involved = set()
    for i, j, _ in top_confused:
        involved.add(i)
        involved.add(j)
    involved = sorted(involved)[:25]  # Cap at 25 for readability

    # Extract sub-matrix
    sub_cm = cm[np.ix_(involved, involved)]
    sub_names = [idx_to_class[i][:25] for i in involved]

    fig, ax = plt.subplots(figsize=(16, 14), dpi=200)
    sns.heatmap(sub_cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=sub_names, yticklabels=sub_names, ax=ax,
                linewidths=0.5, linecolor='#e2e8f0',
                cbar_kws={'label': 'Prediction Count'})
    ax.set_title('Confusion Matrix — Top 25 Most Confused Classes', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('True', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(eval_dir, 'confusion_matrix_top25.png'), bbox_inches='tight')
    plt.close()
    print("  ✓ Saved confusion_matrix_top25.png")


def plot_per_class_f1(all_labels, all_preds, idx_to_class, eval_dir):
    """Plot per-class F1 score bar chart."""
    num_classes = len(idx_to_class)
    per_class_f1 = f1_score(all_labels, all_preds, average=None, zero_division=0)
    class_names = [idx_to_class[i] for i in range(num_classes)]

    # Sort by F1 ascending
    sorted_indices = np.argsort(per_class_f1)

    # Plot bottom 30 and top 30
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 12), dpi=200)

    # Bottom 30 (worst performing)
    bottom = sorted_indices[:30]
    ax1.barh([class_names[i][:30] for i in bottom], [per_class_f1[i] for i in bottom], color='#ef4444', alpha=0.8)
    ax1.set_title('Bottom 30 Classes by F1 Score', fontsize=13, fontweight='bold')
    ax1.set_xlabel('F1 Score', fontsize=11)
    ax1.set_xlim(0, 1.0)
    ax1.grid(True, axis='x', alpha=0.3)

    # Top 30 (best performing)
    top = sorted_indices[-30:]
    ax2.barh([class_names[i][:30] for i in top], [per_class_f1[i] for i in top], color='#10b981', alpha=0.8)
    ax2.set_title('Top 30 Classes by F1 Score', fontsize=13, fontweight='bold')
    ax2.set_xlabel('F1 Score', fontsize=11)
    ax2.set_xlim(0, 1.05)
    ax2.grid(True, axis='x', alpha=0.3)

    plt.suptitle(f'Per-Class F1 Distribution (Macro-F1 = {per_class_f1.mean():.4f})', fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(eval_dir, 'per_class_f1.png'), bbox_inches='tight')
    plt.close()
    print("  ✓ Saved per_class_f1.png")

    # Also save F1 histogram
    fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
    ax.hist(per_class_f1, bins=30, color='#3b82f6', edgecolor='#1e293b', alpha=0.8)
    ax.axvline(per_class_f1.mean(), color='#dc2626', linestyle='--', linewidth=2, label=f'Mean = {per_class_f1.mean():.4f}')
    ax.axvline(np.median(per_class_f1), color='#f59e0b', linestyle='--', linewidth=2, label=f'Median = {np.median(per_class_f1):.4f}')
    ax.set_title('F1 Score Distribution Across All 150 Classes', fontsize=13, fontweight='bold')
    ax.set_xlabel('F1 Score', fontsize=11)
    ax.set_ylabel('Number of Classes', fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(eval_dir, 'f1_histogram.png'), bbox_inches='tight')
    plt.close()
    print("  ✓ Saved f1_histogram.png")


def plot_confidence_distribution(all_preds, all_labels, all_probs, eval_dir):
    """Plot confidence score distribution for correct vs incorrect predictions."""
    max_probs = all_probs.max(axis=1)
    correct_mask = all_preds == all_labels
    correct_conf = max_probs[correct_mask]
    incorrect_conf = max_probs[~correct_mask]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=200)

    # Overall confidence histogram
    ax1.hist(correct_conf, bins=50, alpha=0.7, color='#10b981', label=f'Correct (n={len(correct_conf):,})', edgecolor='#064e3b')
    ax1.hist(incorrect_conf, bins=50, alpha=0.7, color='#ef4444', label=f'Incorrect (n={len(incorrect_conf):,})', edgecolor='#7f1d1d')
    ax1.set_title('Confidence Score Distribution', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Max Softmax Probability', fontsize=11)
    ax1.set_ylabel('Count', fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Reliability / Calibration curve
    bins = np.linspace(0, 1, 11)
    bin_indices = np.digitize(max_probs, bins) - 1
    bin_accuracies = []
    bin_confidences = []
    bin_counts = []
    for i in range(len(bins) - 1):
        mask = bin_indices == i
        if mask.sum() > 0:
            bin_accuracies.append(correct_mask[mask].mean())
            bin_confidences.append(max_probs[mask].mean())
            bin_counts.append(mask.sum())
        else:
            bin_accuracies.append(0)
            bin_confidences.append((bins[i] + bins[i+1]) / 2)
            bin_counts.append(0)

    ax2.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Perfect Calibration')
    ax2.bar([(bins[i] + bins[i+1])/2 for i in range(len(bins)-1)], bin_accuracies,
            width=0.09, color='#3b82f6', alpha=0.7, edgecolor='#1e293b', label='Model Accuracy')
    ax2.set_title('Calibration Plot (Reliability Diagram)', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Mean Predicted Confidence', fontsize=11)
    ax2.set_ylabel('Fraction of Positives (Accuracy)', fontsize=11)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(os.path.join(eval_dir, 'confidence_distribution.png'), bbox_inches='tight')
    plt.close()
    print("  ✓ Saved confidence_distribution.png")


# ─────────────────────────────────────────────────────────────
# Model Export
# ─────────────────────────────────────────────────────────────
def export_model(model, run_dir, config, idx_to_class, num_classes, summary):
    """Export model artifacts for deployment."""
    print("\n" + "=" * 70)
    print("STEP 5: Model Export")
    print("=" * 70)

    # Load best weights
    ckpt = torch.load(os.path.join(run_dir, 'best_model.pth'), map_location='cpu', weights_only=True)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()
    model.cpu()

    # Save class labels
    labels_path = os.path.join(run_dir, 'class_labels.json')
    with open(labels_path, 'w') as f:
        json.dump({str(k): v for k, v in idx_to_class.items()}, f, indent=2)
    print(f"  ✓ Saved class_labels.json ({num_classes} classes)")

    # Save training config
    config_path = os.path.join(run_dir, 'training_config.json')
    export_config = {**config, **summary, 'timestamp': datetime.now().isoformat()}
    with open(config_path, 'w') as f:
        json.dump(export_config, f, indent=2, default=str)
    print(f"  ✓ Saved training_config.json")

    # TorchScript export
    try:
        example_input = torch.randn(1, 3, config['input_size'], config['input_size'])
        scripted = torch.jit.trace(model, example_input)
        scripted_path = os.path.join(run_dir, 'model_scripted.pt')
        scripted.save(scripted_path)
        print(f"  ✓ Saved model_scripted.pt (TorchScript)")
    except Exception as e:
        print(f"  ⚠ TorchScript export failed: {e}")

    print(f"\n  All artifacts saved to: {run_dir}")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    print("╔" + "═" * 68 + "╗")
    print("║  ZARI.ai — EfficientNetV2-B2 Plant Disease Classifier Training     ║")
    print("╚" + "═" * 68 + "╝")
    print()

    set_seed(CONFIG['seed'])

    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if device.type == 'cuda':
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("  WARNING: No GPU found. Training on CPU will be extremely slow.")
    print()

    # Create run directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = os.path.join(CONFIG['output_base'], f'efficientnetv2_b2_{timestamp}')
    splits_dir = os.path.join(run_dir, 'splits')
    os.makedirs(splits_dir, exist_ok=True)

    # Step 1: Load & Split
    train_df, val_df, test_df, class_to_idx, idx_to_class, num_classes = load_and_split_data(CONFIG)

    # Save splits
    train_df.to_csv(os.path.join(splits_dir, 'train.csv'), index=False)
    val_df.to_csv(os.path.join(splits_dir, 'val.csv'), index=False)
    test_df.to_csv(os.path.join(splits_dir, 'test.csv'), index=False)
    print(f"  Saved split CSVs to {splits_dir}")

    # Class weights
    class_weights = compute_class_weights(train_df, num_classes, device)

    # Datasets & DataLoaders
    train_dataset = PlantDiseaseDataset(
        train_df['image_path'].values, train_df['label'].values, get_transforms('train')
    )
    val_dataset = PlantDiseaseDataset(
        val_df['image_path'].values, val_df['label'].values, get_transforms('val')
    )
    test_dataset = PlantDiseaseDataset(
        test_df['image_path'].values, test_df['label'].values, get_transforms('test')
    )

    train_loader = DataLoader(
        train_dataset, batch_size=CONFIG['batch_size'], shuffle=True,
        num_workers=CONFIG['num_workers'], pin_memory=True,
        persistent_workers=True, drop_last=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=CONFIG['batch_size'] * 2, shuffle=False,
        num_workers=CONFIG['num_workers'], pin_memory=True,
        persistent_workers=True
    )
    test_loader = DataLoader(
        test_dataset, batch_size=CONFIG['batch_size'] * 2, shuffle=False,
        num_workers=CONFIG['num_workers'], pin_memory=True,
        persistent_workers=True
    )

    print(f"  DataLoaders ready: Train={len(train_loader)} batches, "
          f"Val={len(val_loader)} batches, Test={len(test_loader)} batches")

    # Step 2: Model
    model = create_model(num_classes, CONFIG, device)

    # Step 3: Loss, Optimizer, Scheduler
    criterion = nn.CrossEntropyLoss(
        weight=class_weights,
        label_smoothing=CONFIG['label_smoothing']
    )

    optimizer = optim.AdamW(
        model.parameters(),
        lr=CONFIG['lr'],
        weight_decay=CONFIG['weight_decay'],
        betas=(0.9, 0.999)
    )

    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer,
        T_0=CONFIG['scheduler_T0'],
        T_mult=CONFIG['scheduler_Tmult'],
        eta_min=1e-6
    )

    # Train
    history, best_epoch, best_val_f1 = train(
        model, train_loader, val_loader, criterion, optimizer, scheduler, device, CONFIG, run_dir
    )

    # Step 4: Evaluate
    # Use unweighted CE for test evaluation (fair metric)
    test_criterion = nn.CrossEntropyLoss()
    summary = evaluate_and_visualize(model, test_loader, test_criterion, device, idx_to_class, run_dir, history)

    # Step 5: Export
    export_model(model, run_dir, CONFIG, idx_to_class, num_classes, summary)

    print("\n" + "=" * 70)
    print("TRAINING COMPLETE — Final Results Summary")
    print("=" * 70)
    print(f"  Test Accuracy:        {summary['test_accuracy']*100:.2f}%")
    print(f"  Test Macro-F1:        {summary['test_macro_f1']:.4f}")
    print(f"  Test Weighted-F1:     {summary['test_weighted_f1']:.4f}")
    print(f"  Test Macro-Precision: {summary['test_macro_precision']:.4f}")
    print(f"  Test Macro-Recall:    {summary['test_macro_recall']:.4f}")
    if summary.get('test_top5_accuracy'):
        print(f"  Test Top-5 Accuracy:  {summary['test_top5_accuracy']*100:.2f}%")
    print(f"  Best Epoch:           {summary['best_epoch']}")
    print(f"  Artifacts:            {run_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()
