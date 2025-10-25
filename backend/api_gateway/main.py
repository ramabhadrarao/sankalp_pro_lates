from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

from common.config import AUTH_SERVICE_URL, USER_SERVICE_URL, SUBSCRIPTION_SERVICE_URL, PAYMENT_SERVICE_URL

app = FastAPI(title="API Gateway", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "ok", "gateway": True}

async def proxy(request: Request, target_base: str, path: str):
    url = f"{target_base}/{path}"
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    async with httpx.AsyncClient() as client:
        content = await request.body()
        resp = await client.request(method, url, headers=headers, content=content, params=request.query_params)
        return JSONResponse(status_code=resp.status_code, content=resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text})

@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_auth(path: str, request: Request):
    return await proxy(request, AUTH_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_users(path: str, request: Request):
    return await proxy(request, USER_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/subscription/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_subscription(path: str, request: Request):
    return await proxy(request, SUBSCRIPTION_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/payments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_payments(path: str, request: Request):
    return await proxy(request, PAYMENT_SERVICE_URL, f"api/v1/{path}")