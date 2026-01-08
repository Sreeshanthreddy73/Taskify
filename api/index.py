"""
Minimal FastAPI test for Vercel
"""
from fastapi import FastAPI
from mangum import Mangum

# Create minimal app
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from Vercel!", "status": "working"}

@app.get("/api/test")
def test():
    return {"test": "API endpoint working"}

# Vercel handler
handler = Mangum(app, lifespan="off")
