import os
log_file = r'backend\app.log'
out_file = 'log_tail_final.txt'
try:
    if os.path.exists(log_file):
        with open(log_file, 'rb') as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 50000)) # 50KB
            data = f.read()
            # Decode carefully
            text = data.decode('utf-8', errors='replace')
            with open(out_file, 'w', encoding='utf-8') as out:
                out.write(text)
        print("Tail written to log_tail_final.txt")
    else:
        print("Log file missing.")
except Exception as e:
    print(f"Error: {e}")
