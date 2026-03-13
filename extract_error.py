import os

log_path = r"backend\app.log"
if not os.path.exists(log_path):
    print(f"Log file not found: {log_path}")
    sys.exit(1)

with open(log_path, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()
    
# Find the last "Traceback"
last_traceback_index = -1
for i in range(len(lines) - 1, -1, -1):
    if "Traceback (most recent call last):" in lines[i]:
        last_traceback_index = i
        break

if last_traceback_index != -1:
    print("--- LAST TRACEBACK DETECTED ---")
    # Print from traceback until next timestamp or end of file
    for line in lines[last_traceback_index:last_traceback_index + 30]:
        print(line.strip())
else:
    print("No Traceback found in the last 1000 lines of app.log")
    print("--- LAST 20 LINES OF LOG ---")
    for line in lines[-20:]:
        print(line.strip())
