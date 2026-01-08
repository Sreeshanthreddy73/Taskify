from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
@app.get("/api")
def read_root():
    return {"Hello": "World", "deployed": "on Vercel", "status": "SUCCESS"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "SupplyChain Sentinel"}

# IMPORTANT: This is what Vercel calls
handler = Mangum(app, lifespan="off")
