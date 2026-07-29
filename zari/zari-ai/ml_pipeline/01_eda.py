"""
=============================================================================
01_eda.py — Dataset Exploratory Data Analysis (EDA)
=============================================================================
Run this script to inspect your plant disease dataset, check total images,
verify all class names, and analyze class imbalance ratio.
"""

import os
from collections import Counter
import pandas as pd

# Path to dataset root directory (where class folders live)
DATASET_PATH = r"D:\New folder\zari\zari-ai\ml_pipeline\data\raw\plantvillage\raw\color"

def run_eda(data_dir):
    print("=" * 70)
    print("  ZARI.ai -- STEP 1: EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 70)

    if not os.path.exists(data_dir):
        print(f"Error: Dataset directory not found at:\n   {data_dir}")
        print("Please verify your data path.")
        return

    class_counts = Counter()
    total_images = 0
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')

    # Scan each class directory
    for class_name in sorted(os.listdir(data_dir)):
        class_path = os.path.join(data_dir, class_name)
        if os.path.isdir(class_path):
            images = [f for f in os.listdir(class_path) if f.lower().endswith(valid_extensions)]
            count = len(images)
            class_counts[class_name] = count
            total_images += count

    if not class_counts:
        print("No class folders found in directory!")
        return

    # Create summary table
    df = pd.DataFrame(class_counts.items(), columns=["Class Name", "Image Count"])
    df["Percentage (%)"] = (df["Image Count"] / total_images * 100).round(2)
    df = df.sort_values(by="Image Count", ascending=False).reset_index(drop=True)

    print(f"\nDATASET SUMMARY")
    print(f"   Total Images  : {total_images:,}")
    print(f"   Total Classes : {len(df)}")
    print("-" * 70)
    print(df.to_string(index=True))
    print("=" * 70)

    # Imbalance Metrics
    max_count = int(df["Image Count"].max())
    min_count = int(df["Image Count"].min())
    imbalance_ratio = max_count / min_count if min_count > 0 else float("inf")

    top_class = df.iloc[0]["Class Name"]
    bot_class = df.iloc[-1]["Class Name"]

    print("\nCLASS BALANCE ANALYSIS")
    print(f"   Highest Class : {top_class} ({max_count:,} images)")
    print(f"   Lowest Class  : {bot_class} ({min_count:,} images)")
    print(f"   Imbalance Ratio: {imbalance_ratio:.2f} : 1")

    if imbalance_ratio > 5.0:
        print("\nWARNING: Significant Class Imbalance (>5:1 ratio).")
        print("   Recommendation: Use weighted CrossEntropyLoss in step 2 (02_train.py).")
    else:
        print("\nDataset balance looks reasonable (<5:1 ratio).")

if __name__ == "__main__":
    run_eda(DATASET_PATH)
