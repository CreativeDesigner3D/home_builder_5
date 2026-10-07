#!/usr/bin/env python3
import os
import zipfile

def build_zip():
    zip_filename = "caffmob_draw.zip"
    source_dir = "caffmob_draw"

    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    print(f"Packaging {source_dir}/ into {zip_filename}...")

    # Remove existing zip if it exists
    if os.path.exists(zip_filename):
        os.remove(zip_filename)

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip python cache directories
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")

            for file in files:
                file_path = os.path.join(root, file)
                # Keep file path relative to source directory (root of zip)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"Successfully created '{zip_filename}'!")

if __name__ == "__main__":
    build_zip()
