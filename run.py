import subprocess
import sys
import time

backend_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "localhost", "--port", "8000", "--reload"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

time.sleep(2)

frontend_process = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py", 
     "--server.port", "5000", 
     "--server.address", "0.0.0.0",
     "--server.headless", "true",
     "--browser.gatherUsageStats", "false"],
)

try:
    frontend_process.wait()
except KeyboardInterrupt:
    backend_process.terminate()
    frontend_process.terminate()
