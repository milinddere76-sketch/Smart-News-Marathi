import basicsr.data.degradations as deg
import os
print(f"File: {deg.__file__}")
with open(deg.__file__, 'r') as f:
    lines = f.readlines()
    print(f"Line 8: {lines[7].strip()}")
