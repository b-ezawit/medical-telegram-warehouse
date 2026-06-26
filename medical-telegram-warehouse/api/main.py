from fastapi import FastAPI

app = FastAPI(title="Medical Telegram Warehouse API")

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "API is operational"}