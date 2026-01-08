from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World", "deployed": "on Vercel"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}
