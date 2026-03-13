import os
import sys

def sanity_check():
    print("--- SANITY CHECK ---")
    
    # 1. Check BasicsSR match
    try:
        import basicsr
        from basicsr.data.degradations import rgb_to_grayscale
        print("[SUCCESS] BasicsSR import worked (patched)!")
    except Exception as e:
        print(f"[FAIL] BasicsSR import error: {e}")
        # Let's see what's actually in there
        try:
            import basicsr.data.degradations as deg
            print(f"File path: {deg.__file__}")
        except:
            pass

    # 2. Check Anchor Photos
    assets_dir = r"d:\Apps\Smart News Marathi\backend\media\assets"
    for f in ["anchor_male.jpg", "anchor_female.jpg"]:
        path = os.path.join(assets_dir, f)
        if os.path.exists(path):
            print(f"[SUCCESS] {f} exists. Size: {os.path.getsize(path)}")
        else:
            print(f"[FAIL] {f} is missing.")

if __name__ == "__main__":
    sanity_check()
