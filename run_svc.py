import subprocess
import os
import time

def run_service():
    print("Starting services...")
    # 1. Start Backend
    backend_log = open("backend_boot.log", "w")
    backend_proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=r"d:\Apps\Smart News Marathi\backend",
        stdout=backend_log,
        stderr=backend_log,
        text=True
    )
    print(f"Backend started with PID {backend_proc.pid}")

    # 2. Wait a bit for backend to initialize
    time.sleep(10)

    # 3. Start Streaming a test video (manually)
    stream_log = open("stream_boot.log", "w")
    ffmpeg_path = r"D:\ffmpeg\bin\ffmpeg.exe"
    video_path = r"D:\Apps\Smart News Marathi\backend\media\video\final_0829b5f793b3423091de63b02c389a21.mp4"
    stream_key = "zcbg-54rm-p1ue-fuk7-6pys"
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    
    ffmpeg_cmd = [
        ffmpeg_path, "-re", "-stream_loop", "-1", "-i", video_path,
        "-c:v", "copy", "-c:a", copy, "-f", "flv", rtmp_url
    ]
    # Note: I used 'copy' as a variable above by mistake, fixing it to "copy"
    ffmpeg_cmd = [
        ffmpeg_path, "-re", "-stream_loop", "-1", "-i", video_path,
        "-c:v", "copy", "-c:a", "copy", "-f", "flv", rtmp_url
    ]

    stream_proc = subprocess.Popen(
        ffmpeg_cmd,
        stdout=stream_log,
        stderr=stream_log,
        text=True
    )
    print(f"Stream started with PID {stream_proc.pid}")

    # Keep script alive
    while True:
        if backend_proc.poll() is not None:
             print("Backend DIED")
        if stream_proc.poll() is not None:
             print("Stream DIED")
        time.sleep(60)

if __name__ == "__main__":
    run_service()
