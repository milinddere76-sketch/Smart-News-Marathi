import os
import shutil

# Target path
target_dir = r"D:\Apps\Smart News Marathi\backend\media\assets"
target_file = os.path.join(target_dir, "news_font.ttf")

os.makedirs(target_dir, exist_ok=True)

source_fonts = [
    r"C:\Windows\Fonts\Nirmala.ttf",
    r"C:\Windows\Fonts\arial.ttf"
]

print(f"Ensuring font at {target_file}")
found = False
for src in source_fonts:
    if os.path.exists(src):
        try:
            shutil.copy(src, target_file)
            print(f"SUCCESS: Copied {src} to {target_file}")
            found = True
            break
        except Exception as e:
            print(f"Error copying {src}: {e}")

if not found:
    print("WARNING: No suitable font found on system!")

if os.path.exists(target_file):
    print(f"File Size: {os.path.getsize(target_file)} bytes")
else:
    print("FAILED: Font file does not exist after copy attempt.")
