from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
app = FastAPI();

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")