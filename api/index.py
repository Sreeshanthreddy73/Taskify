from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum

# Create app
app = FastAPI(title="SupplyChain Sentinel API")

# Root route
@app.get("/")
async def root():
    return JSONResponse({
        "message": "SupplyChain Sentinel API",
        "status": "online",
        "deployed_on": "Vercel",
        "endpoints": {
            "health": "/api/health",
            "docs": "/docs"
        }
    })

# API routes
@app.get("/api")
async def api_root():
    return {"message": "API is working", "version": "1.0"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "SupplyChain Sentinel"}

# Vercel serverless handler - MUST be named 'handler'
handler = Mangum(app, lifespan="off")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
