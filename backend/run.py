
import uvicorn
import os
import sys

# Ensure we are in the correct directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

if __name__ == "__main__":
    print("🚀 Starting SupplyChain Sentinel...")
    print("👉 Open your browser at: http://localhost:8000")
    print("❌ Press Ctrl+C to stop the server")
    
    # Run Uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
