import os
import re

def patch_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Patterns to replace
    # .astype(np.float) -> .astype(float)
    # .astype(np.int) -> .astype(int)
    # .astype(np.bool) -> .astype(bool)
    # But NOT .astype(np.float32), .astype(np.int64), etc.
    
    new_content = re.sub(r'\.astype\(np\.float\)', '.astype(float)', content)
    new_content = re.sub(r'\.astype\(np\.int\)', '.astype(int)', new_content)
    new_content = re.sub(r'\.astype\(np\.bool\)', '.astype(bool)', new_content)
    
    # Also handle np.float, np.int, np.bool literal usage if any (rare in astype)
    
    if content != new_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def patch_dir(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                if patch_file(os.path.join(root, file)):
                    count += 1
    print(f"Patched {count} files.")

if __name__ == "__main__":
    patch_dir(r"d:\Apps\Smart News Marathi\backend\SadTalker\src")
