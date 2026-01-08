"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
