import urllib.request
import os
import sys

def download_file(url, filename):
    print(f"Downloading {url} to {filename}...")
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request) as response:
            total_size = int(response.info().get('Content-Length', 0))
            downloaded = 0
            block_size = 1024 * 64 # 64KB
            
            with open(filename, 'wb') as out_file:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    out_file.write(buffer)
                    if total_size > 0:
                        percent = downloaded * 100 / total_size
                        if (downloaded // block_size) % 100 == 0:
                            print(f"Progress: {percent:.1f}% ({downloaded}/{total_size})")

        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"\nError: {e}")
        return False

if __name__ == "__main__":
    # Huggingface resolve URL
    target_url = "https://huggingface.co/rippertnt/wav2lip/resolve/main/checkpoints/wav2lip_gan.pth?download=true"
    target_path = r"D:\Wav2Lip_Windows_GUI-main\src\Wav2Lip\checkpoints\wav2lip_gan.pth"
    
    success = download_file(target_url, target_path)
    if success and os.path.exists(target_path) and os.path.getsize(target_path) > 1000000:
        print("Verification successful!")
        sys.exit(0)
    else:
        print("Verification failed!")
        sys.exit(1)
