"""
ZARI.ai ML Pipeline — Unified Taxonomy Builder
Maps all labels from PlantVillage, PlantDoc, PlantCity, and NWRD
into a single canonical JSON taxonomy to prevent label conflicts.

This is the single source of truth for class mappings across datasets.
"""

import json
import os

# ──────────────────────────────────────────────────────────────────────────────
# CANONICAL TAXONOMY
# ──────────────────────────────────────────────────────────────────────────────
# Every class_id is globally unique. Labels from each dataset are mapped here.
# `null` means that dataset does not contain this disease class.

TAXONOMY = {
    "version": "1.0.0",
    "description": "ZARI.ai unified crop disease taxonomy — maps PlantVillage, PlantDoc, PlantCity, and NWRD labels.",
    "crops": {
        # ── TOMATO ──
        "tomato": {
            "crop_id": 1,
            "diseases": {
                "bacterial_spot": {
                    "class_id": 0,
                    "display_name_en": "Tomato Bacterial Spot",
                    "display_name_ur": "ٹماٹر کا بیکٹیریل داغ",
                    "source_labels": {
                        "plantvillage": "Tomato___Bacterial_spot",
                        "plantdoc": "Tomato Bacterial Spot",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "early_blight": {
                    "class_id": 1,
                    "display_name_en": "Tomato Early Blight",
                    "display_name_ur": "ٹماٹر کا ابتدائی جھلسا",
                    "source_labels": {
                        "plantvillage": "Tomato___Early_blight",
                        "plantdoc": "Tomato Early Blight",
                        "plantcity": "tomato_early_blight",
                        "nwrd": None,
                    },
                },
                "late_blight": {
                    "class_id": 2,
                    "display_name_en": "Tomato Late Blight",
                    "display_name_ur": "ٹماٹر کا آخری جھلسا",
                    "source_labels": {
                        "plantvillage": "Tomato___Late_blight",
                        "plantdoc": "Tomato Late Blight",
                        "plantcity": "tomato_late_blight",
                        "nwrd": None,
                    },
                },
                "leaf_mold": {
                    "class_id": 3,
                    "display_name_en": "Tomato Leaf Mold",
                    "display_name_ur": "ٹماٹر کے پتے کی پھپھوندی",
                    "source_labels": {
                        "plantvillage": "Tomato___Leaf_Mold",
                        "plantdoc": "Tomato Leaf Mold",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "septoria_leaf_spot": {
                    "class_id": 4,
                    "display_name_en": "Tomato Septoria Leaf Spot",
                    "display_name_ur": "ٹماٹر سیپٹوریا پتی کا داغ",
                    "source_labels": {
                        "plantvillage": "Tomato___Septoria_leaf_spot",
                        "plantdoc": "Tomato Septoria Leaf Spot",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "spider_mites": {
                    "class_id": 5,
                    "display_name_en": "Tomato Spider Mites",
                    "display_name_ur": "ٹماٹر مکڑی کے کیڑے",
                    "source_labels": {
                        "plantvillage": "Tomato___Spider_mites_Two-spotted_spider_mite",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "target_spot": {
                    "class_id": 6,
                    "display_name_en": "Tomato Target Spot",
                    "display_name_ur": "ٹماٹر کا ہدف داغ",
                    "source_labels": {
                        "plantvillage": "Tomato___Target_Spot",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "yellow_leaf_curl_virus": {
                    "class_id": 7,
                    "display_name_en": "Tomato Yellow Leaf Curl Virus",
                    "display_name_ur": "ٹماٹر پیلے پتے کا وائرس",
                    "source_labels": {
                        "plantvillage": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
                        "plantdoc": "Tomato Yellow Leaf Curl Virus",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "mosaic_virus": {
                    "class_id": 8,
                    "display_name_en": "Tomato Mosaic Virus",
                    "display_name_ur": "ٹماٹر موزیک وائرس",
                    "source_labels": {
                        "plantvillage": "Tomato___Tomato_mosaic_virus",
                        "plantdoc": "Tomato Mosaic Virus",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 9,
                    "display_name_en": "Tomato Healthy",
                    "display_name_ur": "ٹماٹر صحت مند",
                    "source_labels": {
                        "plantvillage": "Tomato___healthy",
                        "plantdoc": "Tomato Healthy",
                        "plantcity": "tomato_healthy",
                        "nwrd": None,
                    },
                },
            },
        },

        # ── POTATO ──
        "potato": {
            "crop_id": 2,
            "diseases": {
                "early_blight": {
                    "class_id": 10,
                    "display_name_en": "Potato Early Blight",
                    "display_name_ur": "آلو کا ابتدائی جھلسا",
                    "source_labels": {
                        "plantvillage": "Potato___Early_blight",
                        "plantdoc": "Potato Early Blight",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "late_blight": {
                    "class_id": 11,
                    "display_name_en": "Potato Late Blight",
                    "display_name_ur": "آلو کا آخری جھلسا",
                    "source_labels": {
                        "plantvillage": "Potato___Late_blight",
                        "plantdoc": "Potato Late Blight",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 12,
                    "display_name_en": "Potato Healthy",
                    "display_name_ur": "آلو صحت مند",
                    "source_labels": {
                        "plantvillage": "Potato___healthy",
                        "plantdoc": "Potato Healthy",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
            },
        },

        # ── MAIZE / CORN ──
        "maize": {
            "crop_id": 3,
            "diseases": {
                "cercospora_gray_leaf_spot": {
                    "class_id": 13,
                    "display_name_en": "Maize Cercospora (Gray Leaf Spot)",
                    "display_name_ur": "مکئی سرکوسپورا (خاکستری پتی داغ)",
                    "source_labels": {
                        "plantvillage": "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "common_rust": {
                    "class_id": 14,
                    "display_name_en": "Maize Common Rust",
                    "display_name_ur": "مکئی کا عام زنگ",
                    "source_labels": {
                        "plantvillage": "Corn_(maize)___Common_rust_",
                        "plantdoc": "Corn Common Rust",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "northern_leaf_blight": {
                    "class_id": 15,
                    "display_name_en": "Maize Northern Leaf Blight",
                    "display_name_ur": "مکئی شمالی پتی جھلسا",
                    "source_labels": {
                        "plantvillage": "Corn_(maize)___Northern_Leaf_Blight",
                        "plantdoc": "Corn Northern Leaf Blight",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 16,
                    "display_name_en": "Maize Healthy",
                    "display_name_ur": "مکئی صحت مند",
                    "source_labels": {
                        "plantvillage": "Corn_(maize)___healthy",
                        "plantdoc": "Corn Healthy",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
            },
        },

        # ── APPLE ──
        "apple": {
            "crop_id": 4,
            "diseases": {
                "apple_scab": {
                    "class_id": 17,
                    "display_name_en": "Apple Scab",
                    "display_name_ur": "سیب کی ابری بیماری",
                    "source_labels": {
                        "plantvillage": "Apple___Apple_scab",
                        "plantdoc": "Apple Scab",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "black_rot": {
                    "class_id": 18,
                    "display_name_en": "Apple Black Rot",
                    "display_name_ur": "سیب کا کالا گلاؤ",
                    "source_labels": {
                        "plantvillage": "Apple___Black_rot",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "cedar_apple_rust": {
                    "class_id": 19,
                    "display_name_en": "Apple Cedar Rust",
                    "display_name_ur": "سیب دیودار زنگ",
                    "source_labels": {
                        "plantvillage": "Apple___Cedar_apple_rust",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 20,
                    "display_name_en": "Apple Healthy",
                    "display_name_ur": "سیب صحت مند",
                    "source_labels": {
                        "plantvillage": "Apple___healthy",
                        "plantdoc": "Apple Healthy",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
            },
        },

        # ── GRAPE ──
        "grape": {
            "crop_id": 5,
            "diseases": {
                "black_rot": {
                    "class_id": 21,
                    "display_name_en": "Grape Black Rot",
                    "display_name_ur": "انگور کا کالا گلاؤ",
                    "source_labels": {
                        "plantvillage": "Grape___Black_rot",
                        "plantdoc": "Grape Black Rot",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "esca_black_measles": {
                    "class_id": 22,
                    "display_name_en": "Grape Esca (Black Measles)",
                    "display_name_ur": "انگور ایسکا (کالا خسرہ)",
                    "source_labels": {
                        "plantvillage": "Grape___Esca_(Black_Measles)",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "leaf_blight": {
                    "class_id": 23,
                    "display_name_en": "Grape Leaf Blight",
                    "display_name_ur": "انگور پتی جھلسا",
                    "source_labels": {
                        "plantvillage": "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 24,
                    "display_name_en": "Grape Healthy",
                    "display_name_ur": "انگور صحت مند",
                    "source_labels": {
                        "plantvillage": "Grape___healthy",
                        "plantdoc": "Grape Healthy",
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
            },
        },

        # ── PEPPER ──
        "pepper": {
            "crop_id": 6,
            "diseases": {
                "bacterial_spot": {
                    "class_id": 25,
                    "display_name_en": "Pepper Bacterial Spot",
                    "display_name_ur": "مرچ کا بیکٹیریل داغ",
                    "source_labels": {
                        "plantvillage": "Pepper,_bell___Bacterial_spot",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 26,
                    "display_name_en": "Pepper Healthy",
                    "display_name_ur": "مرچ صحت مند",
                    "source_labels": {
                        "plantvillage": "Pepper,_bell___healthy",
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": None,
                    },
                },
            },
        },

        # ── WHEAT (Critical Cash Crop — NWRD + PlantCity) ──
        "wheat": {
            "crop_id": 7,
            "diseases": {
                "leaf_rust": {
                    "class_id": 27,
                    "display_name_en": "Wheat Leaf Rust",
                    "display_name_ur": "گندم کی پتی کا زنگ",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "wheat_leaf_rust",
                        "nwrd": "Leaf_Rust",
                    },
                },
                "stem_rust": {
                    "class_id": 28,
                    "display_name_en": "Wheat Stem Rust",
                    "display_name_ur": "گندم کے تنے کا زنگ",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": "Stem_Rust",
                    },
                },
                "stripe_rust": {
                    "class_id": 29,
                    "display_name_en": "Wheat Stripe Rust (Yellow Rust)",
                    "display_name_ur": "گندم کا پیلا زنگ",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": None,
                        "nwrd": "Stripe_Rust",
                    },
                },
                "healthy": {
                    "class_id": 30,
                    "display_name_en": "Wheat Healthy",
                    "display_name_ur": "گندم صحت مند",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "wheat_healthy",
                        "nwrd": "Healthy",
                    },
                },
            },
        },

        # ── RICE (PlantCity Pakistan crops) ──
        "rice": {
            "crop_id": 8,
            "diseases": {
                "brown_spot": {
                    "class_id": 31,
                    "display_name_en": "Rice Brown Spot",
                    "display_name_ur": "چاول کا بھورا داغ",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "rice_brown_spot",
                        "nwrd": None,
                    },
                },
                "leaf_blast": {
                    "class_id": 32,
                    "display_name_en": "Rice Leaf Blast",
                    "display_name_ur": "چاول کی پتی کا جھلسا",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "rice_leaf_blast",
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 33,
                    "display_name_en": "Rice Healthy",
                    "display_name_ur": "چاول صحت مند",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "rice_healthy",
                        "nwrd": None,
                    },
                },
            },
        },

        # ── SUGARCANE (PlantCity Pakistan crops) ──
        "sugarcane": {
            "crop_id": 9,
            "diseases": {
                "red_rot": {
                    "class_id": 34,
                    "display_name_en": "Sugarcane Red Rot",
                    "display_name_ur": "گنے کا لال گلاؤ",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "sugarcane_red_rot",
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 35,
                    "display_name_en": "Sugarcane Healthy",
                    "display_name_ur": "گنا صحت مند",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "sugarcane_healthy",
                        "nwrd": None,
                    },
                },
            },
        },

        # ── COTTON (PlantCity Pakistan crops) ──
        "cotton": {
            "crop_id": 10,
            "diseases": {
                "bacterial_blight": {
                    "class_id": 36,
                    "display_name_en": "Cotton Bacterial Blight",
                    "display_name_ur": "کپاس کا بیکٹیریل جھلسا",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "cotton_bacterial_blight",
                        "nwrd": None,
                    },
                },
                "curl_virus": {
                    "class_id": 37,
                    "display_name_en": "Cotton Leaf Curl Virus",
                    "display_name_ur": "کپاس پتی مروڑ وائرس",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "cotton_curl_virus",
                        "nwrd": None,
                    },
                },
                "healthy": {
                    "class_id": 38,
                    "display_name_en": "Cotton Healthy",
                    "display_name_ur": "کپاس صحت مند",
                    "source_labels": {
                        "plantvillage": None,
                        "plantdoc": None,
                        "plantcity": "cotton_healthy",
                        "nwrd": None,
                    },
                },
            },
        },
    },
}


def get_total_classes() -> int:
    """Count the total number of unique disease classes."""
    count = 0
    for crop_data in TAXONOMY["crops"].values():
        count += len(crop_data["diseases"])
    return count


def get_class_id_to_label() -> dict:
    """Build a mapping from class_id → canonical label string."""
    mapping = {}
    for crop_name, crop_data in TAXONOMY["crops"].items():
        for disease_name, disease_data in crop_data["diseases"].items():
            class_id = disease_data["class_id"]
            mapping[class_id] = f"{crop_name}_{disease_name}"
    return mapping


def get_source_label_to_class_id(source: str) -> dict:
    """
    Build a reverse mapping from a source dataset's label → class_id.

    Args:
        source: One of 'plantvillage', 'plantdoc', 'plantcity', 'nwrd'.

    Returns:
        dict mapping source-specific labels to canonical class_ids.
    """
    mapping = {}
    for crop_data in TAXONOMY["crops"].values():
        for disease_data in crop_data["diseases"].values():
            source_label = disease_data["source_labels"].get(source)
            if source_label is not None:
                mapping[source_label] = disease_data["class_id"]
    return mapping


def export_taxonomy_json(output_path: str):
    """Export the taxonomy to a JSON file."""
    taxonomy_export = {
        **TAXONOMY,
        "total_classes": get_total_classes(),
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy_export, f, indent=2, ensure_ascii=False)

    print(f"✅ Taxonomy exported to: {output_path}")
    print(f"   Total classes: {taxonomy_export['total_classes']}")
    print(f"   Total crops: {len(taxonomy_export['crops'])}")


def print_taxonomy_summary():
    """Print a human-readable summary of the taxonomy."""
    total = get_total_classes()
    print(f"\n{'='*60}")
    print(f"  ZARI.ai Unified Taxonomy — {total} classes")
    print(f"{'='*60}")

    for crop_name, crop_data in TAXONOMY["crops"].items():
        diseases = crop_data["diseases"]
        print(f"\n  🌱 {crop_name.upper()} (crop_id: {crop_data['crop_id']})")
        for disease_name, disease_data in diseases.items():
            sources = [
                src for src, label in disease_data["source_labels"].items()
                if label is not None
            ]
            print(
                f"     [{disease_data['class_id']:>2}] {disease_data['display_name_en']}"
                f"  ← {', '.join(sources)}"
            )

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Print summary
    print_taxonomy_summary()

    # Export to JSON
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, "data", "cleaned", "taxonomy.json")
    export_taxonomy_json(output_path)
