import shutil
import os

# New generated files from previous steps
src_male = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14\anchor_male_new_jpg_1773134214222.png"
src_female = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14\anchor_female_new_jpg_1773134231371.png"

dst_male = r"d:\Apps\Smart News Marathi\backend\media\assets\anchor_male.jpg"
dst_female = r"d:\Apps\Smart News Marathi\backend\media\assets\anchor_female.jpg"

def force_copy(src, dst):
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"SUCCESS: Copied to {dst}")
        else:
            print(f"ERROR: Source file not found at {src}")
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")

if __name__ == "__main__":
    force_copy(src_male, dst_male)
    force_copy(src_female, dst_female)
