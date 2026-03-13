import subprocess
import sys

try:
    result = subprocess.run([r"C:\Users\Priyansh Dere\.fly\bin\flyctl.exe", "status", "-a", "snm-be-priyansh-dere"], capture_output=True, text=True, check=False)
    with open("fly_status_py.txt", "w", encoding="utf-8") as f:
        f.write("STDOUT:\n" + result.stdout + "\n")
        f.write("STDERR:\n" + result.stderr + "\n")
except Exception as e:
    with open("fly_status_py.txt", "w", encoding="utf-8") as f:
        f.write("ERROR:\n" + str(e) + "\n")
