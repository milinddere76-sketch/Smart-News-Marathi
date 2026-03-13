import sys
import os

log_file = "startup_debug.log"

with open(log_file, "w") as f:
    f.write("Starting backend diagnostic...\n")
    try:
        f.write("Importing modules...\n")
        import main
        f.write("Successfully imported main.py\n")
        
        f.write("Importing uvicorn...\n")
        import uvicorn
        f.write("Successfully imported uvicorn\n")
        
        f.write("Starting uvicorn...\n")
        # Use a very short timeout or just try to initialize
        uvicorn.run(main.app, host="127.0.0.1", port=8001)
        
    except Exception as e:
        import traceback
        f.write(f"\nERROR: {str(e)}\n")
        f.write(traceback.format_exc())
        f.write("\n")
