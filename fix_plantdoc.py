import urllib.request
import zipfile
import os
import shutil

ZIP_URL = "https://github.com/pratikkayal/PlantDoc-Dataset/archive/refs/heads/master.zip"
ZIP_PATH = "plantdoc_temp.zip"
FINAL_DIR = "ml_pipeline/data/raw/plantdoc"

print("Downloading PlantDoc ZIP directly...")
urllib.request.urlretrieve(ZIP_URL, ZIP_PATH)

print("Extracting and sanitizing files for Windows...")
os.makedirs(FINAL_DIR, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    for member in zip_ref.infolist():
        # Sanitize the filename to avoid Windows OS crashes
        original_filename = member.filename
        sanitized_filename = original_filename.replace('?', '_').replace(':', '_').replace('*', '_')
        
        if member.is_dir():
            continue
            
        # Strip the top-level repository folder name
        parts = sanitized_filename.split('/', 1)
        if len(parts) > 1:
            dir_name, base_name = os.path.split(parts[1])
            # Truncate base name to avoid Windows MAX_PATH (260 char) errors
            if len(base_name) > 100:
                name, ext = os.path.splitext(base_name)
                base_name = name[:100] + ext
                
            target_path = os.path.normpath(os.path.join(FINAL_DIR, dir_name, base_name))
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Read from zip and write to the sanitized path
            source = zip_ref.read(member)
            with open(target_path, "wb") as f:
                f.write(source)

# Cleanup the temp zip
os.remove(ZIP_PATH)
print("PlantDoc successfully sanitized and extracted into data/raw/plantdoc!")
