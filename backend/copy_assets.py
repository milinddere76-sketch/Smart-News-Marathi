import shutil
import os

src_male = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14\anchor_male_1773086847808.png"
src_female = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14\anchor_female_1773086862527.png"

dst_male = r"d:\Apps\Smart News Marathi\backend\media\assets\anchor_male.jpg"
dst_female = r"d:\Apps\Smart News Marathi\backend\media\assets\anchor_female.jpg"

def copy_f(src, dst):
    try:
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"Copied {src} to {dst}")
        else:
            print(f"Source not found: {src}")
    except Exception as e:
        print(f"Error copying {src}: {e}")

if __name__ == "__main__":
    copy_f(src_male, dst_male)
    copy_f(src_female, dst_female)
