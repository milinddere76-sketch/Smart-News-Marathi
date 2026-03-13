import os
import sys

try:
    import librosa
    lib_ver = librosa.__version__
except Exception as e:
    lib_ver = f"ERROR: {e}"

try:
    import numpy as np
    np_ver = np.__version__
except Exception as e:
    np_ver = f"ERROR: {e}"

try:
    import numba
    nb_ver = numba.__version__
except Exception as e:
    nb_ver = f"ERROR: {e}"

try:
    import cv2
    cv_ver = cv2.__version__
except Exception as e:
    cv_ver = f"ERROR: {e}"

res = f"librosa: {lib_ver}\nnumpy: {np_ver}\nnumba: {nb_ver}\ncv2: {cv_ver}\n"
res += f"Python: {sys.version}\n"

with open("env_check_final.txt", "w") as f:
    f.write(res)
print("Done")
