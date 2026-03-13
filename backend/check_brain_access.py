import os
path = r"C:\Users\Priyansh Dere\.gemini\antigravity\brain\4c6ecebf-949b-4e1b-8a17-265d9ccfda14\anchor_male_1773086847808.png"
if os.path.exists(path):
    print(f"I CAN see it! Size: {os.path.getsize(path)}")
else:
    print("I CANNOT see it from Python process.")
