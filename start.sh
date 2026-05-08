# start.sh
#!/bin/bash

# Start FastAPI in the background on port 8000 (adjust if needed, but 8000 is common)
uvicorn main:app --host 0.0.0.0 --port 8001 &

# Start Streamlit in the foreground (Replit will show this in the web view)
streamlit run app.py --server.port 8081 --server.address 0.0.0.0