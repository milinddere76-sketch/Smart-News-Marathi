import sys
import os

target = r"D:\Apps\Smart News Marathi\backend\write_test.txt"
with open(target, "w") as f:
    f.write(f"Python: {sys.version}\n")
    f.write(f"Executable: {sys.executable}\n")
    f.write("Write test successful.\n")
print(f"Done writing to {target}")
