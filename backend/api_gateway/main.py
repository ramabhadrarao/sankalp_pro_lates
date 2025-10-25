from fastapi import FastAPI, Request
import httpx
from common.config import AUTH_SERVICE_URL

app = FastAPI(title="SalahkaarPro API Gateway")

@app.get("/health")
def health():
    return {"status": "ok", "gateway": True}

# Proxy for /api/v1/auth/* routes
@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_auth(path: str, request: Request):
    target_url = f"{AUTH_SERVICE_URL}/api/v1/auth/{path}"
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient() as client:
        body = await request.body()
        resp = await client.request(request.method, target_url, headers=headers, content=body)
    return app.response_class(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type", "application/json"))