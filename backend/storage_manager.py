import os
import time
import shutil
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger("storage_manager")

class StorageManager:
    def __init__(self, video_dir="media/video", log_file="storage_cleanup.log"):
        self.video_dir = video_dir
        self.log_file = log_file
        os.makedirs(self.video_dir, exist_ok=True)
        
        # Setup specific logger for cleanup
        self.cleanup_logger = logging.getLogger("cleanup_history")
        self.cleanup_logger.setLevel(logging.INFO)
        fh = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(message)s'))
        self.cleanup_logger.addHandler(fh)

    def log_deletion(self, filename, reason):
        """Records a deletion in the system log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        log_entry = f"[{timestamp}]\nDeleted File: {filename}\nReason: {reason}\n"
        self.cleanup_logger.info(log_entry)
        logger.info(f"Cleanup: Deleted {filename} - {reason}")

    def get_disk_usage_percent(self):
        """Returns the current disk usage percentage of the drive containing video_dir."""
        total, used, free = shutil.disk_usage(self.video_dir)
        return (used / total) * 100

    def run_cleanup(self, current_playing_file=None):
        """
        Main cleanup routine.
        1. Run a cleanup check every 30 minutes (handled by caller).
        2. Identify all videos older than 6 hours.
        3. Automatically delete those old videos.
        4. Never delete the newest 10 videos in the folder.
        5. Never delete the video currently used in the live broadcast.
        6. Always keep enough videos available for continuous streaming.
        """
        try:
            # Step 1: Scan directory
            files = [f for f in os.listdir(self.video_dir) if f.endswith(".mp4") and f != "placeholder_loop.mp4"]
            if not files:
                return

            # Step 2: Sort files by creation time
            file_stats = []
            for f in files:
                path = os.path.join(self.video_dir, f)
                ctime = os.path.getctime(path)
                file_stats.append({
                    "name": str(f),
                    "path": str(path),
                    "ctime": float(ctime),
                    "age_hours": float((time.time() - ctime) / 3600)
                })
            
            # Sort oldest first for deletion consideration
            file_stats.sort(key=lambda x: x["ctime"])
            
            # Identification of "Keepers"
            # 1. Newest 10 videos (Explicitly using a slice from a list)
            newest_stats = sorted(file_stats, key=lambda x: x["ctime"], reverse=True)
            newest_10 = []
            max_keep = 10
            for i in range(len(newest_stats)):
                if i >= max_keep:
                    break
                newest_10.append(str(newest_stats[i]["name"]))
            
            # 2. Currently playing
            protected_files = set(newest_10)
            if current_playing_file:
                protected_files.add(os.path.basename(current_playing_file))

            # Rules logic
            disk_usage = self.get_disk_usage_percent()
            is_critical = disk_usage > 80.0
            
            retention_limit = 6.0 # Default 6 hours
            if is_critical:
                retention_limit = 3.0 # Critical 3 hours
                logger.warning(f"CRITICAL: Storage at {disk_usage:.1f}%. Reducing retention to 3h.")

            deleted_count = 0
            
            # Step 3 & 4 & 5: Process for deletion
            for f_info in file_stats:
                filename = str(f_info["name"])
                age_hours = float(f_info["age_hours"])
                file_path = str(f_info["path"])
                
                # Rule: Never delete protected files
                if filename in protected_files:
                    continue
                
                # Rule: Check age
                should_delete = False
                reason = ""
                
                if age_hours > retention_limit:
                    should_delete = True
                    reason = f"Expired (older than {retention_limit} hours)"
                
                if should_delete:
                    try:
                        os.remove(file_path)
                        self.log_deletion(filename, reason)
                        deleted_count += 1
                        
                        # Check disk again if in critical mode
                        if is_critical:
                            current_usage = self.get_disk_usage_percent()
                            if current_usage < 60.0:
                                logger.info(f"Storage back to safe level: {current_usage:.1f}%")
                                is_critical = False # Stop aggressive deletion
                    except Exception as e:
                        logger.error(f"Failed to delete {filename}: {e}")

            return deleted_count

        except Exception as e:
            logger.error(f"Error in StorageManager.run_cleanup: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0

if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    sm = StorageManager(video_dir="media/video")
    print(f"Current Disk Usage: {sm.get_disk_usage_percent():.2f}%")
    count = sm.run_cleanup()
    print(f"Cleanup finished. Deleted {count} files.")
