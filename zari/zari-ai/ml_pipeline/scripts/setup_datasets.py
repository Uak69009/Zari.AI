"""
ZARI.ai ML Pipeline — Dataset Download & Setup Script
Automates the creation of data folders and downloads the four core datasets.

Prerequisites:
  - Kaggle CLI installed: pip install kaggle
  - Kaggle API token: ~/.kaggle/kaggle.json
  - Git installed and accessible from PATH

Usage:
  python ml_pipeline/scripts/setup_datasets.py
"""

import os
import subprocess
import sys


# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")

# Define target folders for each dataset
DATASET_PATHS = {
    "plantcity": os.path.join(RAW_DIR, "plantcity"),
    "nwrd": os.path.join(RAW_DIR, "nwrd"),
    "plantvillage": os.path.join(RAW_DIR, "plantvillage"),
    "plantdoc": os.path.join(RAW_DIR, "plantdoc"),
}

# Dataset source URLs
DATASET_SOURCES = {
    "plantcity": {
        "type": "kaggle",
        "slug": "codewithsk/plantcity-a-comprehensive-images-multicrop-leaves",
    },
    "nwrd": {
        "type": "git",
        "url": "https://github.com/dll-ncai/NUST-Wheat-Rust-Disease-NWRD.git",
    },
    "plantvillage": {
        "type": "git",
        "url": "https://github.com/spMohanty/PlantVillage-Dataset.git",
    },
    "plantdoc": {
        "type": "git",
        "url": "https://github.com/pratikkayal/PlantDoc-Dataset.git",
    },
}


def create_folders():
    """Create the data directory structure."""
    print("📁 Creating folder structure...")
    os.makedirs(CLEANED_DIR, exist_ok=True)
    for name, path in DATASET_PATHS.items():
        os.makedirs(path, exist_ok=True)
        print(f"   ✓ {name}: {path}")
    print(f"\n✅ Data directories created at: {DATA_DIR}\n")


def _is_dir_populated(path: str) -> bool:
    """Check if a directory has contents (skip re-download)."""
    if not os.path.exists(path):
        return False
    contents = os.listdir(path)
    # Filter out hidden files like .gitkeep
    contents = [c for c in contents if not c.startswith(".")]
    return len(contents) > 0


def download_datasets():
    """Download all four datasets into their respective raw/ subdirectories."""
    print("⬇️  Beginning dataset downloads...\n")

    for name, source in DATASET_SOURCES.items():
        target_path = DATASET_PATHS[name]

        if _is_dir_populated(target_path):
            print(f"⏭️  {name}: Already populated, skipping.\n")
            continue

        if source["type"] == "kaggle":
            _download_kaggle(name, source["slug"], target_path)
        elif source["type"] == "git":
            _download_git(name, source["url"], target_path)

    print("\n🎉 All downloads completed! Raw data is ready for taxonomy mapping.")


def _download_kaggle(name: str, slug: str, target_path: str):
    """Download a dataset from Kaggle."""
    print(f"📦 Downloading {name} from Kaggle: {slug}")
    try:
        subprocess.run(
            [
                "kaggle", "datasets", "download", "-d",
                slug,
                "-p", target_path,
                "--unzip",
            ],
            check=True,
        )
        print(f"   ✅ {name} downloaded successfully.\n")
    except FileNotFoundError:
        print(
            f"   ❌ Kaggle CLI not found. Install it with: pip install kaggle\n"
            f"      Then place your kaggle.json in ~/.kaggle/\n"
        )
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to download {name}. Error: {e}\n")


def _download_git(name: str, url: str, target_path: str):
    """Clone a dataset from GitHub."""
    print(f"📦 Cloning {name} from GitHub: {url}")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, target_path],
            check=True,
        )
        print(f"   ✅ {name} cloned successfully.\n")
    except FileNotFoundError:
        print(f"   ❌ Git not found. Please install Git.\n")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to clone {name}. Error: {e}\n")


def print_summary():
    """Print a summary of the data directory status."""
    print(f"\n{'='*60}")
    print(f"  ZARI.ai Data Directory Status")
    print(f"{'='*60}")

    for name, path in DATASET_PATHS.items():
        if _is_dir_populated(path):
            count = len([
                f for f in os.listdir(path)
                if not f.startswith(".")
            ])
            print(f"  ✅ {name:15s} — {count} items")
        else:
            print(f"  ⬜ {name:15s} — empty / not downloaded")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("\n🌿 ZARI.ai Dataset Setup Script")
    print("=" * 40 + "\n")

    create_folders()
    download_datasets()
    print_summary()
