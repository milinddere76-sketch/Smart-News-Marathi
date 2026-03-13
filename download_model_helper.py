import urllib.request
import os
import sys

def download_file(url, filename):
    print(f"Downloading {url} to {filename}...")
    try:
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = downloaded * 100 / total_size
                if block_num % 1000 == 0:
                    print(f"Progress: {percent:.2f}% ({downloaded}/{total_size} bytes)")
            else:
                if block_num % 1000 == 0:
                    print(f"Downloaded {downloaded} bytes")

        urllib.request.urlretrieve(url, filename, reporthook=progress)
        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"\nError: {e}")
        return False

if __name__ == "__main__":
    target_url = "https://huggingface.co/numz/wav2lip_studio/resolve/main/Wav2lip/wav2lip_gan.pth"
    target_path = r"D:\Wav2Lip_Windows_GUI-main\src\Wav2Lip\checkpoints\wav2lip_gan.pth"
    
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    success = download_file(target_url, target_path)
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
