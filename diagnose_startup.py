import subprocess
import time
import os

python_exe = r"C:\Users\Priyansh Dere\AppData\Local\Python\pythoncore-3.14-64\python.exe"
backend_main = r"D:\Apps\Smart News Marathi\backend\main.py"
streamer_main = r"D:\Apps\Smart News Marathi\stream-engine\broadcaster.py"

print(f"Starting Backend: {backend_main}")
with open(r"D:\Apps\Smart News Marathi\backend_diag.log", "w") as f:
    backend_proc = subprocess.Popen([python_exe, backend_main], stdout=f, stderr=subprocess.STDOUT, cwd=r"D:\Apps\Smart News Marathi\backend")
    print(f"Backend PID: {backend_proc.pid}")

time.sleep(5)

print(f"Starting Streamer: {streamer_main}")
with open(r"D:\Apps\Smart News Marathi\streamer_diag.log", "w") as f:
    streamer_proc = subprocess.Popen([python_exe, streamer_main], stdout=f, stderr=subprocess.STDOUT, cwd=r"D:\Apps\Smart News Marathi\stream-engine")
    print(f"Streamer PID: {streamer_proc.pid}")

print("Waiting 10 seconds for initialization...")
time.sleep(10)

print("Checking port 8000...")
subprocess.run(["netstat", "-ano", "|", "findstr", ":8000"], shell=True)
