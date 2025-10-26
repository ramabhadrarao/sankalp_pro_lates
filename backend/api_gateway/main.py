from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

from common.config import (
    AUTH_SERVICE_URL,
    USER_SERVICE_URL,
    SUBSCRIPTION_SERVICE_URL,
    PAYMENT_SERVICE_URL,
    CALCULATION_SERVICE_URL,
    REPORT_SERVICE_URL,
    FORM_SERVICE_URL,
    AFFILIATE_SERVICE_URL,
    ADMIN_SERVICE_URL,
    NOTIFICATION_SERVICE_URL,
    STORAGE_SERVICE_URL,
    I18N_SERVICE_URL,
    PRO_SERVICE_URL,
)

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

@app.api_route("/api/v1/calculate/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_calculate(path: str, request: Request):
    return await proxy(request, CALCULATION_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/reports/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_reports(path: str, request: Request):
    return await proxy(request, REPORT_SERVICE_URL, f"api/v1/{path}")

# Newly added proxies for remaining services
@app.api_route("/api/v1/forms/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_forms(path: str, request: Request):
    return await proxy(request, FORM_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/affiliates/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_affiliates(path: str, request: Request):
    return await proxy(request, AFFILIATE_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/admin/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_admin(path: str, request: Request):
    return await proxy(request, ADMIN_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_notifications(path: str, request: Request):
    return await proxy(request, NOTIFICATION_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/storage/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_storage(path: str, request: Request):
    return await proxy(request, STORAGE_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/i18n/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_i18n(path: str, request: Request):
    return await proxy(request, I18N_SERVICE_URL, f"api/v1/{path}")

@app.api_route("/api/v1/pro/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_pro(path: str, request: Request):
    return await proxy(request, PRO_SERVICE_URL, f"api/v1/{path}")