@echo off
echo "BATCH_EXECUTION_SUCCESS" > batch_out.txt
echo "Current Dir: %cd%" >> batch_out.txt
echo "User: %USERNAME%" >> batch_out.txt
dir >> batch_out.txt
