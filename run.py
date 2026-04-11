import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Starting API server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"API Documentation: http://localhost:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)