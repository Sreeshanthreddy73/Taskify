"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_path)

# Now we can import from backend
from main import app
from mangum import Mangum

# Create the handler for Vercel
handler = Mangum(app, lifespan="off")

# Also export app directly for compatibility
__all__ = ['handler', 'app']
