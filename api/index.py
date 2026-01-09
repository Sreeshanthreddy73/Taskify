from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel!", "status": "working"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

handler = Mangum(app, lifespan="off")
