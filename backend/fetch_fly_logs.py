import subprocess
import traceback

try:
    with open("fly_backend_logs.txt", "w", encoding="utf-8") as f:
        res = subprocess.run(
            [r"C:\Users\Priyansh Dere\.fly\bin\flyctl.exe", "logs", "-n", "100", "-a", "snm-be-priyansh-dere"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15
        )
        f.write(res.stdout)
        f.write("\n\nSTDERR:\n")
        f.write(res.stderr)
except Exception as e:
    with open("fly_backend_logs.txt", "w", encoding="utf-8") as f:
        f.write(f"Error: {e}\n{traceback.format_exc()}")
