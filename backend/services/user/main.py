from fastapi import FastAPI

app = FastAPI(title="SalahkaarPro User Service")

@app.get("/health")
def health():
    return {"status": "ok"}