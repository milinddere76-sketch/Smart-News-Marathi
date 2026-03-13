import subprocess
import os
import sys

# Try to find the venv python
venv_python = os.path.join("backend", "venv", "Scripts", "python.exe")
if not os.path.exists(venv_python):
    venv_python = "python" # Fallback

try:
    # Run pip list
    output = subprocess.check_output([venv_python, "-m", "pip", "list"], text=True, stderr=subprocess.STDOUT)
    with open("pip_list_final.txt", "w", encoding="utf-8") as f:
        f.write(output)
    
    # Also check versions directly
    ver_check = """
import sys
try: import librosa; l_v = librosa.__version__
except: l_v = "N/A"
try: import numpy; n_v = numpy.__version__
except: n_v = "N/A"
print(f"librosa: {l_v}")
print(f"numpy: {n_v}")
"""
    output2 = subprocess.check_output([venv_python, "-c", ver_check], text=True, stderr=subprocess.STDOUT)
    with open("versions_direct.txt", "w", encoding="utf-8") as f:
        f.write(output2)

except Exception as e:
    with open("pip_list_final.txt", "w", encoding="utf-8") as f:
        f.write(f"FATAL ERROR: {e}")

print("Diagnostic script finished.")
