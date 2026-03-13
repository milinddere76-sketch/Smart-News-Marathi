import shutil
import os
import sys

source_dir = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14"
dest_dir = r"d:\Apps\Smart News Marathi\backend\media\assets"

files = {
    "anchor_male_1773086847808.png": "anchor_male.jpg",
    "anchor_female_1773086862527.png": "anchor_female.jpg",
    "bg_breaking_1773086956279.png": "bg_Breaking News.jpg",
    "bg_tech_1773086971821.png": "bg_Technology.jpg",
    "bg_india_1773086989515.png": "bg_India.jpg"
}

with open(r"d:\Apps\Smart News Marathi\copy_log.txt", "w") as log:
    log.write(f"Source dir exists: {os.path.exists(source_dir)}\n")
    log.write(f"Dest dir exists: {os.path.exists(dest_dir)}\n")
    
    for src_name, dst_name in files.items():
        src_path = os.path.join(source_dir, src_name)
        dst_path = os.path.join(dest_dir, dst_name)
        log.write(f"Trying to copy {src_path} to {dst_path}\n")
        try:
            if os.path.exists(src_path):
                shutil.copy(src_path, dst_path)
                log.write(f"SUCCESS: {dst_name}\n")
            else:
                log.write(f"ERROR: Source not found: {src_path}\n")
        except Exception as e:
            log.write(f"EXCEPTION: {str(e)}\n")

print("FINISHED COPY ATTEMPT")
