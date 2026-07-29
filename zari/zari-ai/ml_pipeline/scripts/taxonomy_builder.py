"""
ZARI.ai ML Pipeline — Unified Taxonomy Builder
Maps all labels from PlantVillage, PlantDoc, PlantCity, and NWRD
into a single canonical JSON taxonomy to prevent label conflicts.

This is the single source of truth for class mappings across datasets.
Run this script directly to regenerate taxonomy.json from the master definition.
"""

import os
import json

# ──────────────────────────────────────────────────────────────────────────────
# PATH CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TAXONOMY_OUT_PATH = os.path.join(DATA_DIR, "taxonomy.json")

# ──────────────────────────────────────────────────────────────────────────────
# 1. CANONICAL MASTER CLASS LIST
# ──────────────────────────────────────────────────────────────────────────────
# Continuous integer IDs 0–7 for PyTorch CrossEntropyLoss compatibility.
# Each ID is globally unique across all dataset sources.

CANONICAL_CLASSES = {
    0: {"name": "Wheat_Healthy",        "urdu": "صحت مند گندم"},
    1: {"name": "Wheat_Leaf_Rust",      "urdu": "گندم کا پتوں کا زنگ"},
    2: {"name": "Wheat_Loose_Smut",     "urdu": "گندم کی کانگیاری"},
    3: {"name": "Wheat_Crown_Root_Rot", "urdu": "گندم کی جڑ کا سڑنا"},
    4: {"name": "Tomato_Healthy",       "urdu": "صحت مند ٹماٹر"},
    5: {"name": "Tomato_Early_Blight",  "urdu": "ٹماٹر کا اگیتا جھلساؤ"},
    6: {"name": "Maize_Healthy",        "urdu": "صحت مند مکئی"},
    7: {"name": "Maize_Fall_Armyworm",  "urdu": "مکئی کا فال آرمی ورم"},
}

# ──────────────────────────────────────────────────────────────────────────────
# 2. DATASET ROUTING MAP
# ──────────────────────────────────────────────────────────────────────────────
# Maps every raw folder/label name from each dataset → canonical class_id.
# These are the exact folder names produced by each dataset's directory layout.

RAW_TO_CANONICAL_MAP = {
    "nwrd": {
        "healthy":           0,
        "leaf_rust":         1,
        "loose_smut":        2,
        "crown_and_root_rot": 3,
    },
    "plantvillage": {
        "Tomato___healthy":        4,
        "Tomato___Early_blight":   5,
        "Corn_(maize)___healthy":  6,
    },
    "plantcity": {
        "Tomato_Healthy":        4,
        "Tomato_Early_Blight":   5,
        "Maize_Healthy_Leaf":    6,
        "Maize_Armyworm_Damage": 7,
    },
    "plantdoc": {
        "wheat leaf":              0,
        "wheat leaf rust":         1,
        "tomato leaf":             4,
        "tomato early blight leaf": 5,
        "corn leaf":               6,
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def get_class_id_to_name() -> dict:
    """Return mapping: class_id (int) → canonical name string."""
    return {cid: meta["name"] for cid, meta in CANONICAL_CLASSES.items()}


def get_source_label_to_class_id(source: str) -> dict:
    """
    Build a reverse lookup for a specific dataset source.

    Args:
        source: One of 'nwrd', 'plantvillage', 'plantcity', 'plantdoc'.

    Returns:
        dict mapping raw folder/label strings → canonical class_id (int).

    Raises:
        KeyError: If the source name is not registered in RAW_TO_CANONICAL_MAP.
    """
    if source not in RAW_TO_CANONICAL_MAP:
        raise KeyError(
            f"Unknown dataset source '{source}'. "
            f"Valid sources: {list(RAW_TO_CANONICAL_MAP.keys())}"
        )
    return dict(RAW_TO_CANONICAL_MAP[source])


def get_all_class_ids() -> list:
    """Return sorted list of all canonical class IDs."""
    return sorted(CANONICAL_CLASSES.keys())


def get_num_classes() -> int:
    """Return total number of canonical classes (for model head sizing)."""
    return len(CANONICAL_CLASSES)


# ──────────────────────────────────────────────────────────────────────────────
# TAXONOMY BUILD + EXPORT
# ──────────────────────────────────────────────────────────────────────────────

def build_taxonomy() -> dict:
    """
    Assemble the final taxonomy dictionary by joining CANONICAL_CLASSES
    with their source provenance derived from RAW_TO_CANONICAL_MAP.

    Returns:
        dict: The complete taxonomy ready for JSON serialisation.
    """
    print("Building unified ZARI.ai taxonomy...")

    final_taxonomy = {
        "classes": {},
        "dataset_mapping": RAW_TO_CANONICAL_MAP,
    }

    for class_id, metadata in CANONICAL_CLASSES.items():
        # Determine which datasets contain this class
        sources = [
            dataset_name
            for dataset_name, mapping in RAW_TO_CANONICAL_MAP.items()
            if class_id in mapping.values()
        ]

        final_taxonomy["classes"][str(class_id)] = {
            "canonical_name": metadata["name"],
            "urdu_name":      metadata["urdu"],
            "sources":        sources,
        }

    return final_taxonomy


def export_taxonomy(output_path: str | None = None) -> None:
    """
    Build the taxonomy and write it to a JSON file.

    Args:
        output_path: Destination path for taxonomy.json.
                     Defaults to TAXONOMY_OUT_PATH.
    """
    if output_path is None:
        output_path = TAXONOMY_OUT_PATH

    taxonomy = build_taxonomy()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=4, ensure_ascii=False)

    print(f"[OK] Taxonomy saved  -> {output_path}")
    print(f"     Total canonical classes : {get_num_classes()}")
    print(f"     Datasets registered     : {list(RAW_TO_CANONICAL_MAP.keys())}")


def print_taxonomy_summary() -> None:
    """Print a human-readable summary of class→source mappings."""
    total = get_num_classes()
    print(f"\n{'=' * 62}")
    print(f"  ZARI.ai Canonical Taxonomy  —  {total} classes")
    print(f"{'=' * 62}")
    for cid in get_all_class_ids():
        meta = CANONICAL_CLASSES[cid]
        sources = [
            ds for ds, mapping in RAW_TO_CANONICAL_MAP.items()
            if cid in mapping.values()
        ]
        print(f"  [{cid}]  {meta['name']:<28} <- {', '.join(sources)}")
    print(f"{'=' * 62}\n")


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print_taxonomy_summary()
    export_taxonomy()
