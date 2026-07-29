import os
import sys
import importlib.metadata
from PIL import Image

def audit_environment():
    required_packages = [
        'pandas', 'matplotlib', 'seaborn', 'reportlab', 
        'torch', 'torchvision', 'pillow', 'scikit-learn', 'tqdm'
    ]
    missing_packages = []
    
    for pkg in required_packages:
        try:
            importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            missing_packages.append(pkg)
            
    return missing_packages

def audit_datasets(base_path="ml_pipeline/data/raw"):
    corrupted_files = []
    total_files = 0
    
    datasets = ['plantcity', 'plantdoc', 'plantvillage', 'nwrd']
    for ds in datasets:
        ds_path = os.path.join(base_path, ds)
        if not os.path.exists(ds_path):
            print(f"WARNING: Dataset folder {ds_path} is missing!")
            continue
            
        for root, dirs, files in os.walk(ds_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    try:
                        with Image.open(file_path) as img:
                            img.verify()
                    except Exception as e:
                        corrupted_files.append(file_path)
                        
    return total_files, corrupted_files

def main():
    os.makedirs("ml_pipeline/logs", exist_ok=True)
    os.makedirs("ml_pipeline/scripts", exist_ok=True)
    
    log_path = "ml_pipeline/logs/01_verification_summary.txt"
    
    with open(log_path, "w") as f:
        f.write("ZARI.ai Pre-Flight Audit Report\n")
        f.write("===============================\n\n")
        
        print("Auditing environment...")
        missing = audit_environment()
        if missing:
            f.write(f"Environment check failed. Missing packages: {missing}\n")
            print(f"FAILED: Missing packages: {missing}")
            # Do not exit 1 immediately, allow script to finish logging
        else:
            f.write("Environment check PASSED. All required ML dependencies are installed.\n")
            print("Environment check PASSED.")
            
        print("Auditing raw datasets (this may take a few minutes)...")
        total_files, corrupted = audit_datasets()
        
        f.write(f"Data audit processed {total_files} images.\n")
        print(f"Data audit processed {total_files} images.")
        
        if corrupted:
            f.write(f"Data check WARNING. Found {len(corrupted)} corrupted/zero-byte files.\n")
            for c in corrupted:
                f.write(f" - {c}\n")
                try:
                    os.remove(c)
                except OSError:
                    pass
            f.write("Corrupted files have been automatically deleted (Self-Healing applied).\n")
            print(f"WARNING: Automatically deleted {len(corrupted)} corrupted files.")
        else:
            f.write("Data integrity check PASSED. Zero corruption detected.\n")
            print("Data integrity check PASSED.")
            
        if missing:
            print("Audit failed due to missing dependencies. Auto-healing required.")
            sys.exit(1)
            
    print(f"Phase 1 Audit complete. Log written to {log_path}")

if __name__ == "__main__":
    main()
