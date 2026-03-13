import subprocess

try:
    with open("fly_logs.txt", "w", encoding="utf-8") as f:
        subprocess.run(
            [r"C:\Users\Priyansh Dere\.fly\bin\flyctl.exe", "logs", "-a", "snm-be-priyansh-dere"],
            stdout=f,
            stderr=subprocess.STDOUT,
            timeout=10
        )
except subprocess.TimeoutExpired:
    pass
except Exception as e:
    with open("fly_logs.txt", "w", encoding="utf-8") as f:
        f.write(str(e))
