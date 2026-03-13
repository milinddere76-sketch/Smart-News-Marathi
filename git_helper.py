import os
import subprocess

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="d:\\Apps\\VARTAPRAVAH")
        return f"CMD: {cmd}\nOUT: {result.stdout}\nERR: {result.stderr}\nRC: {result.returncode}\n"
    except Exception as e:
        return f"CMD: {cmd}\nEXCEPTION: {str(e)}\n"

with open("git_diagnosis.txt", "w") as f:
    f.write("--- Git Diagnosis ---\n")
    f.write(run_cmd("git --version"))
    f.write(run_cmd("git init"))
    f.write(run_cmd("git remote add origin https://github.com/milinddere76-sketch/Smart-News-Marathi.git"))
    f.write(run_cmd("git branch -M main"))
    f.write(run_cmd("git status"))
    f.write(run_cmd("dir .git /A"))
