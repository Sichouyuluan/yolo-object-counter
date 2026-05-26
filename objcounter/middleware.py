"""中间件 — API Key 认证 + 限速 + 设备追踪 + 扫描防护"""
import time
import secrets

from fastapi import Header, HTTPException, Request
from fastapi.responses import JSONResponse

from objcounter.config import get_config
from objcounter.guard import get_guard
from objcounter.i18n import t
from objcounter.state import app_state


async def verify_api_key(authorization: str = Header(None)):
    if not get_config("require_api_key", True):
        return
    if not authorization:
        raise HTTPException(status_code=401, detail={"error": True, "message": t("api_key_required"), "code": 401})
    token = authorization.replace("Bearer ", "").strip()
    if not secrets.compare_digest(token, app_state.api_key):
        raise HTTPException(status_code=403, detail={"error": True, "message": t("api_key_invalid"), "code": 403})


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    path = request.url.path

    # 0. 扫描保护检查（单次 get_stats 避免 TOCTOU）
    guard = get_guard()
    if guard:
        gs = guard.get_stats()
        if gs["is_protected"]:
            return JSONResponse(
                status_code=503,
                content={"error": t("protection_mode", seconds=gs['remaining_seconds'])},
            )

    # 1. 踢出检查
    dt = app_state.device_tracker
    if path not in ("/api/online-devices", "/api/kick-device") and dt.is_kicked(client_ip):
        return JSONResponse(status_code=403, content={"error": t("kicked")})

    # 2. 限速 + 封禁
    general_limiter = app_state.rate_limiter
    detect_limiter = app_state.detect_rate_limiter
    if path not in ("/api/ping", "/api/online-devices", "/api/kick-device"):
        if general_limiter.is_banned(client_ip):
            return JSONResponse(
                status_code=403,
                content={"error": t("banned")},
            )
        if path == "/api/detect":
            if not detect_limiter.is_allowed(client_ip):
                general_limiter.record_rejection(client_ip)
                return JSONResponse(status_code=429, content={"error": t("rate_limited")})
        else:
            if not general_limiter.is_allowed(client_ip):
                general_limiter.record_rejection(client_ip)
                return JSONResponse(status_code=429, content={"error": t("rate_limited")})

    # 3. 设备追踪（跳过 localhost）
    if client_ip not in ("127.0.0.1", "::1"):
        ua = request.headers.get("user-agent", "")
        dt.update_activity(client_ip, ua)

    response = await call_next(request)

    # 记录到扫描防护
    if guard:
        guard.check_and_record(client_ip, response.status_code, path)

    # 检测请求计数
    if path == "/api/detect" and client_ip not in ("127.0.0.1", "::1"):
        dt.increment_detect(client_ip)

    return response
