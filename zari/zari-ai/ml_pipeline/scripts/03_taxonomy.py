import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split

METADATA_PATH = "ml_pipeline/dataset_metadata.csv"
TAXONOMY_PATH = "ml_pipeline/taxonomy.json"
SPLITS_DIR = "ml_pipeline/splits"

os.makedirs(SPLITS_DIR, exist_ok=True)

def generate_taxonomy(df):
    print("Generating class taxonomy mapping...")
    unique_classes = sorted(df['class_name'].unique().tolist())
    
    taxonomy = {}
    for idx, class_name in enumerate(unique_classes):
        # We replace underscores with spaces and capitalize for a clean english name
        english_name = class_name.replace("_", " ").title()
        
        # Placeholder for Urdu translation (this will be handled natively by Groq API LLM at runtime)
        urdu_translation = f"اردو تشخیص: {english_name}"
        
        taxonomy[idx] = {
            "folder_name": class_name,
            "english_name": english_name,
            "urdu_translation": urdu_translation
        }
        
    with open(TAXONOMY_PATH, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, ensure_ascii=False, indent=4)
        
    print(f"Taxonomy mapping saved to {TAXONOMY_PATH} for {len(unique_classes)} classes.")
    return taxonomy, unique_classes

def generate_splits(df, taxonomy):
    print("Performing 80/10/10 Stratified Split...")
    
    # Map class index to dataframe
    class_to_idx = {v['folder_name']: k for k, v in taxonomy.items()}
    df['class_index'] = df['class_name'].map(class_to_idx)
    
    # Some classes in PlantDoc or wild datasets might only have 1 or 2 images.
    # Stratified split requires at least 3 items per class (to split into 3 sets).
    # We will filter out classes with less than 3 samples.
    class_counts = df['class_index'].value_counts()
    valid_classes = class_counts[class_counts >= 3].index
    
    dropped_rows = len(df) - len(df[df['class_index'].isin(valid_classes)])
    if dropped_rows > 0:
        print(f"WARNING: Dropping {dropped_rows} images because their classes have fewer than 3 samples (cannot stratify).")
        df = df[df['class_index'].isin(valid_classes)]
        
    # First split: 80% train, 20% temp (val + test)
    train_df, temp_df = train_test_split(
        df, test_size=0.2, stratify=df['class_index'], random_state=42
    )
    
    # Second split: 50% val, 50% test of the 20% temp (so 10% / 10% overall)
    # Re-verify stratify requirement for temp_df (requires at least 2 samples per class in temp_df)
    # To bypass strict stratification errors on extremely small classes in temp_df, we drop stratify for the val/test split.
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42
    )
    
    train_df.to_csv(os.path.join(SPLITS_DIR, "train.csv"), index=False)
    val_df.to_csv(os.path.join(SPLITS_DIR, "val.csv"), index=False)
    test_df.to_csv(os.path.join(SPLITS_DIR, "test.csv"), index=False)
    
    print(f"Splits completed successfully:")
    print(f" - Train: {len(train_df)} images")
    print(f" - Val:   {len(val_df)} images")
    print(f" - Test:  {len(test_df)} images")

def main():
    print("Initiating Phase 3: Taxonomy & Splits...")
    if not os.path.exists(METADATA_PATH):
        print(f"ERROR: {METADATA_PATH} not found. Did Phase 2 run?")
        return
        
    df = pd.read_csv(METADATA_PATH)
    taxonomy, _ = generate_taxonomy(df)
    generate_splits(df, taxonomy)
    
    print("Phase 3 Complete!")

if __name__ == "__main__":
    main()
