from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import HTTPException


DEFAULT_CONTROL_API_BASE_URL = "http://127.0.0.1:8001"
DEFAULT_CONTROL_API_KEY = "MakeThisBetter.txt"


def get_control_api_base_url() -> str:
    return os.getenv("CONTROL_API_BASE_URL", DEFAULT_CONTROL_API_BASE_URL).rstrip("/")


def get_control_api_key() -> str:
    return os.getenv("CONTROL_API_API_KEY", DEFAULT_CONTROL_API_KEY)


async def forward_to_control_api(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: Any = None,
    headers: dict[str, str] | None = None,
) -> Any:
    base_url = get_control_api_base_url()
    request_headers = dict(headers or {})
    request_headers.setdefault("Authorization", f"Bearer {get_control_api_key()}")

    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=15.0) as client:
            response = await client.request(
                method,
                path,
                params=params,
                json=json_body,
                headers=request_headers,
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Control API unreachable at {base_url}: {exc}",
        ) from exc

    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body: Any = response.json()
        except ValueError:
            body = {"detail": response.text}
    else:
        body = {"detail": response.text}

    if response.is_success:
        return body

    raise HTTPException(status_code=response.status_code, detail=body)