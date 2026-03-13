import shutil
import os

files = {
    r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14\anchor_male_new_jpg_1773134214222.png": r"d:\Apps\Smart News Marathi\backend\media\assets\anchor_male.jpg",
    r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14\anchor_female_new_jpg_1773134231371.png": r"d:\Apps\Smart News Marathi\backend\media\assets\anchor_female.jpg"
}

def do_copy():
    os.makedirs(r"d:\Apps\Smart News Marathi\backend\media\assets", exist_ok=True)
    for src, dst in files.items():
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                print(f"SUCCESS: {os.path.basename(src)} -> {dst}")
            except Exception as e:
                print(f"FAIL: {src} -> {e}")
        else:
            print(f"NOT FOUND: {src}")

if __name__ == "__main__":
    do_copy()
