"""
ZARI.ai ML Pipeline — Two-Phase EfficientNetV2-S Training Script
Implements the domain-shift-aware training strategy:
  Phase 1: PlantVillage + PlantDoc (lab → noisy bridge)
  Phase 2: PlantCity + NWRD (Pakistani field fine-tuning)

Usage:
  python ml_pipeline/scripts/train_efficientnet_v2.py --phase 1 --epochs 30
  python ml_pipeline/scripts/train_efficientnet_v2.py --phase 2 --epochs 20 --checkpoint <path>
"""

import argparse
import json
import os
import sys
from pathlib import Path

import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import transforms
import timm
from PIL import Image
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEANED_DIR = DATA_DIR / "cleaned"
TAXONOMY_PATH = CLEANED_DIR / "taxonomy.json"

INPUT_SIZE = 384
BATCH_SIZE = 32
NUM_WORKERS = 4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ──────────────────────────────────────────────────────────────────────────────
# AUGMENTATION PIPELINES
# ──────────────────────────────────────────────────────────────────────────────

def get_phase1_transforms(is_train: bool = True):
    """Phase 1 augmentations: moderate — lab data with mild noise."""
    if is_train:
        return A.Compose([
            A.RandomResizedCrop(height=INPUT_SIZE, width=INPUT_SIZE, scale=(0.8, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.Rotate(limit=15, p=0.4),
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.4),
            A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=15, p=0.3),
            A.GaussNoise(var_limit=(5.0, 25.0), p=0.2),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])
    else:
        return A.Compose([
            A.Resize(INPUT_SIZE, INPUT_SIZE),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])


def get_phase2_transforms(is_train: bool = True):
    """Phase 2 augmentations: aggressive — simulate Pakistani field conditions."""
    if is_train:
        return A.Compose([
            # Geometric
            A.RandomResizedCrop(height=INPUT_SIZE, width=INPUT_SIZE, scale=(0.7, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.2),
            A.Rotate(limit=30, p=0.5),

            # Simulated field conditions
            A.MotionBlur(blur_limit=7, p=0.3),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.RandomSunFlare(src_radius=100, p=0.15),
            A.RandomShadow(p=0.2),
            A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.3, p=0.1),

            # Color/Contrast shifts
            A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.5),
            A.HueSaturationValue(
                hue_shift_limit=15, sat_shift_limit=30, val_shift_limit=20, p=0.4
            ),
            A.CLAHE(clip_limit=4.0, p=0.3),

            # Normalization
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])
    else:
        return A.Compose([
            A.Resize(INPUT_SIZE, INPUT_SIZE),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])


# ──────────────────────────────────────────────────────────────────────────────
# DATASET
# ──────────────────────────────────────────────────────────────────────────────

class CropDiseaseDataset(Dataset):
    """
    PyTorch Dataset for unified crop disease images.

    Expects a list of (image_path, class_id) tuples.
    Uses Albumentations for augmentation.
    """

    def __init__(self, samples: list, transform=None):
        self.samples = samples  # List of (path, class_id)
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, class_id = self.samples[idx]

        # Load image
        image = np.array(Image.open(img_path).convert("RGB"))

        # Apply augmentations
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented["image"]

        return image, class_id


# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADING HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def load_taxonomy() -> dict:
    """Load the canonical taxonomy JSON."""
    if not TAXONOMY_PATH.exists():
        print("⚠️  Taxonomy not found. Run taxonomy_builder.py first.")
        sys.exit(1)

    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_phase1_samples(taxonomy: dict) -> list:
    """
    Collect samples from PlantVillage + PlantDoc for Phase 1 training.

    Returns:
        List of (image_path, class_id) tuples.
    """
    samples = []

    # Build reverse label → class_id maps
    from taxonomy_builder import get_source_label_to_class_id

    pv_map = get_source_label_to_class_id("plantvillage")
    pd_map = get_source_label_to_class_id("plantdoc")

    # PlantVillage: folder-per-class structure
    pv_dir = RAW_DIR / "plantvillage"
    if pv_dir.exists():
        # Navigate into the dataset's image directory
        for color_dir in ["color", "segmented", "grayscale"]:
            img_dir = pv_dir / "PlantVillage-Dataset" / "raw" / color_dir
            if not img_dir.exists():
                img_dir = pv_dir / color_dir
            if img_dir.exists() and color_dir == "color":
                for class_folder in img_dir.iterdir():
                    if class_folder.is_dir():
                        folder_name = class_folder.name
                        if folder_name in pv_map:
                            class_id = pv_map[folder_name]
                            for img_file in class_folder.glob("*.*"):
                                if img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                                    samples.append((str(img_file), class_id))

    # PlantDoc: similar folder structure
    pd_dir = RAW_DIR / "plantdoc"
    if pd_dir.exists():
        for root_name in ["train", "test"]:
            split_dir = pd_dir / "PlantDoc-Dataset" / root_name
            if not split_dir.exists():
                split_dir = pd_dir / root_name
            if split_dir.exists():
                for class_folder in split_dir.iterdir():
                    if class_folder.is_dir():
                        folder_name = class_folder.name
                        if folder_name in pd_map:
                            class_id = pd_map[folder_name]
                            for img_file in class_folder.glob("*.*"):
                                if img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                                    samples.append((str(img_file), class_id))

    print(f"📊 Phase 1 samples collected: {len(samples)}")
    return samples


def collect_phase2_samples(taxonomy: dict) -> list:
    """
    Collect samples from PlantCity + NWRD for Phase 2 fine-tuning.

    Returns:
        List of (image_path, class_id) tuples.
    """
    samples = []

    from taxonomy_builder import get_source_label_to_class_id

    pc_map = get_source_label_to_class_id("plantcity")
    nwrd_map = get_source_label_to_class_id("nwrd")

    # PlantCity
    pc_dir = RAW_DIR / "plantcity"
    if pc_dir.exists():
        for class_folder in pc_dir.rglob("*"):
            if class_folder.is_dir():
                folder_name = class_folder.name
                if folder_name in pc_map:
                    class_id = pc_map[folder_name]
                    for img_file in class_folder.glob("*.*"):
                        if img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                            samples.append((str(img_file), class_id))

    # NWRD
    nwrd_dir = RAW_DIR / "nwrd"
    if nwrd_dir.exists():
        for class_folder in nwrd_dir.rglob("*"):
            if class_folder.is_dir():
                folder_name = class_folder.name
                if folder_name in nwrd_map:
                    class_id = nwrd_map[folder_name]
                    for img_file in class_folder.glob("*.*"):
                        if img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                            samples.append((str(img_file), class_id))

    print(f"📊 Phase 2 samples collected: {len(samples)}")
    return samples


# ──────────────────────────────────────────────────────────────────────────────
# MODEL
# ──────────────────────────────────────────────────────────────────────────────

def create_model(num_classes: int, pretrained: bool = True) -> nn.Module:
    """Create EfficientNetV2-S model with custom classification head."""
    model = timm.create_model(
        "tf_efficientnetv2_s",
        pretrained=pretrained,
        num_classes=num_classes,
    )
    return model


def freeze_base_layers(model: nn.Module):
    """Freeze all layers except the classification head (for Phase 2)."""
    for name, param in model.named_parameters():
        if "classifier" not in name and "head" not in name:
            param.requires_grad = False

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"🧊 Frozen: {total - trainable:,} params | Trainable: {trainable:,} params")


# ──────────────────────────────────────────────────────────────────────────────
# TRAINING LOOP
# ──────────────────────────────────────────────────────────────────────────────

def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
    epoch: int,
) -> float:
    """Train for one epoch. Returns average loss."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(dataloader, desc=f"Epoch {epoch}")
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        pbar.set_postfix({
            "loss": f"{loss.item():.4f}",
            "acc": f"{100. * correct / total:.2f}%",
        })

    epoch_loss = running_loss / total
    epoch_acc = 100. * correct / total
    return epoch_loss, epoch_acc


def validate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple:
    """Validate the model. Returns (loss, accuracy)."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Validating"):
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    val_loss = running_loss / total
    val_acc = 100. * correct / total
    return val_loss, val_acc


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main(args):
    print(f"\n🌿 ZARI.ai — Phase {args.phase} Training")
    print(f"   Device: {DEVICE}")
    print(f"   Epochs: {args.epochs}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Input size: {INPUT_SIZE}×{INPUT_SIZE}\n")

    # Load taxonomy
    taxonomy = load_taxonomy()
    num_classes = taxonomy.get("total_classes", 39)
    print(f"   Classes: {num_classes}\n")

    # Collect samples
    if args.phase == 1:
        samples = collect_phase1_samples(taxonomy)
        train_transform = get_phase1_transforms(is_train=True)
        val_transform = get_phase1_transforms(is_train=False)
    else:
        samples = collect_phase2_samples(taxonomy)
        train_transform = get_phase2_transforms(is_train=True)
        val_transform = get_phase2_transforms(is_train=False)

    if len(samples) == 0:
        print("❌ No samples found. Run setup_datasets.py first.")
        sys.exit(1)

    # Split: Train 80% / Val 10% / Test 10%
    labels = [s[1] for s in samples]
    train_samples, temp_samples = train_test_split(
        samples, test_size=0.2, stratify=labels, random_state=42
    )
    temp_labels = [s[1] for s in temp_samples]
    val_samples, test_samples = train_test_split(
        temp_samples, test_size=0.5, stratify=temp_labels, random_state=42
    )

    print(f"   Train: {len(train_samples)} | Val: {len(val_samples)} | Test: {len(test_samples)}")

    # Create datasets and dataloaders
    train_dataset = CropDiseaseDataset(train_samples, transform=train_transform)
    val_dataset = CropDiseaseDataset(val_samples, transform=val_transform)

    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True,
        num_workers=NUM_WORKERS, pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=NUM_WORKERS, pin_memory=True,
    )

    # Create model
    model = create_model(num_classes, pretrained=(args.phase == 1))

    if args.checkpoint and args.phase == 2:
        print(f"📥 Loading Phase 1 checkpoint: {args.checkpoint}")
        checkpoint = torch.load(args.checkpoint, map_location=DEVICE)
        model.load_state_dict(checkpoint["model_state_dict"])
        freeze_base_layers(model)

    model = model.to(DEVICE)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    if args.phase == 1:
        optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    else:
        # Only optimize unfrozen parameters in Phase 2
        trainable_params = [p for p in model.parameters() if p.requires_grad]
        optimizer = optim.AdamW(trainable_params, lr=5e-5, weight_decay=1e-4)

    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # Training loop
    best_val_acc = 0.0
    save_dir = BASE_DIR / "checkpoints"
    save_dir.mkdir(exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, DEVICE, epoch
        )
        val_loss, val_acc = validate(model, val_loader, criterion, DEVICE)
        scheduler.step()

        print(
            f"  Epoch {epoch}/{args.epochs} — "
            f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
            f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%"
        )

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_path = save_dir / f"phase{args.phase}_best.pth"
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": val_acc,
                "val_loss": val_loss,
                "num_classes": num_classes,
            }, save_path)
            print(f"  💾 Best model saved: {save_path} (Val Acc: {val_acc:.2f}%)")

    print(f"\n✅ Phase {args.phase} training complete. Best Val Acc: {best_val_acc:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ZARI.ai Two-Phase Training")
    parser.add_argument(
        "--phase", type=int, required=True, choices=[1, 2],
        help="Training phase (1: lab baseline, 2: field fine-tuning)",
    )
    parser.add_argument(
        "--epochs", type=int, default=30,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--checkpoint", type=str, default=None,
        help="Path to Phase 1 checkpoint (required for Phase 2)",
    )

    args = parser.parse_args()
    main(args)
