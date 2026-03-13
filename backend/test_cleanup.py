import os
import time

def test_cleanup_logic():
    test_dir = "media/test_cleanup"
    log_file = "cleanup_test_log.txt"
    os.makedirs(test_dir, exist_ok=True)
    
    with open(log_file, "w") as log:
        log.write("--- Cleanup Test Start ---\n")
        
        # Create an "old" file
        old_file = os.path.join(test_dir, "old_test.txt")
        with open(old_file, "w") as f:
            f.write("test")
        
        # Manually set high access/mod time (approx 7 hours ago)
        past_time = time.time() - (7 * 3600)
        os.utime(old_file, (past_time, past_time))
        
        # Create a "new" file
        new_file = os.path.join(test_dir, "new_test.txt")
        with open(new_file, "w") as f:
            f.write("test")
            
        log.write(f"Created {old_file} (7h old) and {new_file} (new)\n")
        
        # Cleanup logic (copied from main.py)
        max_age_seconds = 6 * 3600
        now = time.time()
        
        for f in os.listdir(test_dir):
            fp = os.path.join(test_dir, f)
            age = now - os.path.getmtime(fp)
            log.write(f"Checking {f}: age={age/3600:.2f}h\n")
            if age > max_age_seconds:
                log.write(f"Deleting {f}...\n")
                os.remove(fp)
                
        # Verify
        if not os.path.exists(old_file) and os.path.exists(new_file):
            log.write("✅ SUCCESS: Old file deleted, new file preserved.\n")
        else:
            log.write("❌ FAILURE: Cleanup logic did not work as expected.\n")
            
        # Cleanup test dir
        if os.path.exists(new_file): os.remove(new_file)
        os.rmdir(test_dir)
        log.write("--- Cleanup Test End ---\n")

if __name__ == "__main__":
    test_cleanup_logic()
