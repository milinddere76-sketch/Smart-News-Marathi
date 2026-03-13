import time
import os

log_path = r"D:\Apps\Smart News Marathi\heartbeat.txt"
print(f"Starting heartbeat at {log_path}")
count = 0
try:
    while count < 30: # Run for 60 seconds
        with open(log_path, "a") as f:
            f.write(f"Heartbeat {count} at {time.ctime()}\n")
        count += 1
        time.sleep(2)
except Exception as e:
    with open(log_path, "a") as f:
        f.write(f"ERROR: {str(e)}\n")
