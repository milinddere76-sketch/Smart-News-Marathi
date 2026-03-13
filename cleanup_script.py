import os
import shutil
import glob

paths_to_clean = [
    r'd:\Apps\VARTAPRAVAH\backend\media\video\final_*.mp4',
    r'd:\Apps\VARTAPRAVAH\backend\media\audio\news_*.mp3',
    r'd:\Apps\VARTAPRAVAH\backend\media\anchor\anchor_*.mp4',
    r'd:\Apps\VARTAPRAVAH\media\video\final_*.mp4',
    r'd:\Apps\VARTAPRAVAH\media\audio\news_*.mp3',
    r'd:\Apps\VARTAPRAVAH\media\anchor\anchor_*.mp4',
    r'd:\Apps\VARTAPRAVAH\backend\app.log',
    r'd:\Apps\VARTAPRAVAH\backend\execution_log.txt',
    r'd:\Apps\VARTAPRAVAH\stream-engine\stream_engine.log',
    r'd:\Apps\VARTAPRAVAH\stream-engine\broadcaster_ffmpeg.log',
    r'd:\Apps\VARTAPRAVAH\recent_logs.txt',
    r'd:\Apps\VARTAPRAVAH\recent_logs2.txt',
    r'd:\Apps\VARTAPRAVAH\temp_backend_logs.txt',
    r'd:\Apps\VARTAPRAVAH\temp_streamer_logs.txt',
    r'd:\Apps\VARTAPRAVAH\streamer_test_logs.txt'
]

dirs_to_remove = [
    r'd:\Apps\VARTAPRAVAH\backend\media\anchor\debug_out',
    r'd:\Apps\VARTAPRAVAH\backend\media\anchor\sadtalker_tmp'
]

print("Starting cleanup...")

for pattern in paths_to_clean:
    files = glob.glob(pattern)
    print(f"Pattern: {pattern} -> Found {len(files)} files")
    for f in files:
        try:
            os.chmod(f, 0o777)
            os.remove(f)
            print(f"Deleted: {f}")
        except Exception as e:
            print(f"Error deleting {f}: {e}")

for d in dirs_to_remove:
    if os.path.exists(d):
        try:
            shutil.rmtree(d)
            print(f"Removed directory: {d}")
        except Exception as e:
            print(f"Error removing directory {d}: {e}")

print("Cleanup finished.")
