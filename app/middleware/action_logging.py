import asyncio
import json
import os
import re
import time
from typing import Optional

import requests
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


ACTION_LOG_URL = os.getenv(
    "ACTION_LOG_URL",
    "http://localhost:8082/api/internal/action-logs",
)
ID_PATTERN = re.compile(r"^(?:\d+|[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,})$")
PREFIXES = {"api", "admin", "student", "internal"}
SENSITIVE_MODULES = {"users", "roles", "permissions", "tests", "questions", "classrooms", "subjects", "categories"}

SKIP_EXACT = {"/", "/health", "/docs", "/openapi.json", "/redoc"}
SKIP_PREFIXES = (
    "/docs",
    "/openapi",
    "/internal",
)

# Segment path (không dùng contains — tránh "shared-with-me" khớp "share")
GET_LOG_SEGMENTS = {"export", "download", "logout"}
ACTION_SEGMENTS = {
    "export": "EXPORT",
    "download": "EXPORT",
    "upload": "UPLOAD",
    "save": "SAVE",
    "generate": "GENERATE",
    "translate": "TRANSLATE",
    "convert": "CONVERT",
    "check": "CHECK",
    "extract": "EXTRACT",
    "join": "JOIN",
    "submit": "SUBMIT",
    "password": "CHANGE_PASSWORD",
}


class ActionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started_at = time.perf_counter()
        response = None
        error: Optional[Exception] = None
        try:
            response = await call_next(request)
            return response
        except Exception as exception:
            error = exception
            raise
        finally:
            if should_log(request):
                status_code = response.status_code if response is not None else 500
                payload = build_payload(request, status_code, started_at, error)
                asyncio.create_task(asyncio.to_thread(send_log, payload))


def should_log(request: Request) -> bool:
    if request.method == "OPTIONS":
        return False
    # Gateway hoặc service Java nội bộ đã ghi log → bỏ qua
    if request.headers.get("X-Action-Logged-By-Gateway") == "true":
        return False
    if request.headers.get("X-Internal-Service") == "true":
        return False

    path = request.url.path
    normalized = path.lower()
    if normalized in SKIP_EXACT:
        return False
    if any(normalized.startswith(prefix) for prefix in SKIP_PREFIXES):
        return False
    # Gọi nội bộ từ Spring (không có token) — đã log ở Gateway
    if not request.headers.get("Authorization") and (
        normalized.startswith("/api/pronunciation")
        or normalized.startswith("/api/tts")
    ):
        return False
    # Dịch từng đoạn / file trung gian — không ghi log (log ở bước tạo bài giảng)
    if normalized.startswith("/api/translate"):
        return False

    method = request.method.upper()
    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        return True

    if method == "GET":
        segments = {part for part in normalized.split("/") if part}
        # Không log browse/list (kể cả /images/{userId}). Chỉ export/download/logout.
        return bool(segments & GET_LOG_SEGMENTS)

    return False


def path_segments(path: str) -> set[str]:
    return {part.lower() for part in path.split("/") if part}


def build_payload(request: Request, status_code: int, started_at: float, error: Optional[Exception]) -> dict:
    path = request.url.path
    module = resolve_module(path)
    resource_id = resolve_resource_id(path)
    action = resolve_action(request.method, path, module, resource_id)
    failed = error is not None or status_code >= 400
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent", "")
    description = {
        "statusCode": status_code,
        "durationMs": round((time.perf_counter() - started_at) * 1000),
        "source": "fastapi-direct",
    }
    if error is not None:
        description["error"] = type(error).__name__

    return {
        "authToken": request.headers.get("Authorization"),
        "clientIdentifier": f"guest_{ip_address}" if ip_address else f"unknown_{user_agent[:220] or 'client'}",
        "action": action,
        "module": module,
        "resourceId": resource_id,
        "httpMethod": request.method,
        "endpoint": path,
        "severity": resolve_severity(request.method, path, module),
        "status": "FAILED" if failed else "SUCCESS",
        "description": json.dumps(description, ensure_ascii=False),
        "ipAddress": ip_address,
    }


def resolve_module(path: str) -> str:
    for part in (item for item in path.split("/") if item):
        lowered = part.lower()
        if lowered not in PREFIXES and not ID_PATTERN.fullmatch(lowered):
            return lowered.replace("-", "_")
    return "system"


def resolve_resource_id(path: str) -> Optional[str]:
    for part in reversed([item for item in path.split("/") if item]):
        if ID_PATTERN.fullmatch(part):
            return part
    return None


def resolve_action(method: str, path: str, module: str, resource_id: Optional[str]) -> str:
    upper_module = module.upper()
    segments = path_segments(path)
    if "login" in segments or "oauth2" in path.lower():
        return "LOGIN"
    if "logout" in segments:
        return "LOGOUT"
    if "classroom-shares" in segments:
        return f"SHARE_{upper_module}_CLASS"
    if "shares" in segments or "share" in segments:
        return f"SHARE_{upper_module}"
    for segment, verb in ACTION_SEGMENTS.items():
        if segment in segments:
            if verb == "CHANGE_PASSWORD":
                return "CHANGE_PASSWORD"
            return f"{verb}_{upper_module}"
    if method == "GET":
        return f"VIEW_{upper_module}_{'DETAIL' if resource_id else 'LIST'}"
    if method == "POST":
        return f"CREATE_{upper_module}"
    if method in {"PUT", "PATCH"}:
        return f"UPDATE_{upper_module}"
    if method == "DELETE":
        return f"DELETE_{upper_module}"
    return f"{method}_{upper_module}"


def resolve_severity(method: str, path: str, module: str) -> str:
    normalized = path.lower()
    if method == "DELETE" or "permission" in normalized or "role" in normalized:
        return "ALERT"
    if method in {"PUT", "PATCH"} and (module in SENSITIVE_MODULES or "password" in normalized):
        return "DANGER"
    if method in {"POST", "PUT", "PATCH"}:
        return "WARNING"
    return "INFO"


def send_log(payload: dict) -> None:
    try:
        requests.post(ACTION_LOG_URL, json=payload, timeout=2)
    except requests.RequestException:
        # Ghi log không được làm gián đoạn nghiệp vụ chính.
        pass
