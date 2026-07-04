import json
import os
import urllib.error
import urllib.request
from typing import Any


class RegisterApiClient:
    def __init__(self, base_url: str | None = None, timeout: float = 30):
        self.base_url = (base_url or os.getenv("API_BASE_URL") or "http://127.0.0.1:9212").rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        body = None
        headers = {"Accept": "application/json"}

        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"

        request = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = response.read().decode("utf-8")
                return json.loads(data) if data else {}
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(detail).get("message", detail)
            except json.JSONDecodeError:
                message = detail or error.reason
            raise RuntimeError(f"HTTP {error.code}: {message}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"无法连接服务 {self.base_url}: {error.reason}") from error

    def info(self) -> dict[str, Any]:
        return self._request("GET", "/api")

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/api/health")

    def generate(
        self,
        machine_code: str,
        sn: str,
        key: str | None = None,
        md5_length: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "machine_code": machine_code,
            "sn": sn,
        }
        if key is not None:
            payload["key"] = key
        if md5_length is not None:
            payload["md5_length"] = md5_length
        return self._request("POST", "/api/generate", payload=payload)

    def machine_md5(
        self,
        machine_code: str,
        md5_length: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"machine_code": machine_code}
        if md5_length is not None:
            payload["md5_length"] = md5_length
        return self._request("POST", "/api/machine-md5", payload=payload)

    def register_code(
        self,
        sn: str,
        key: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"sn": sn}
        if key is not None:
            payload["key"] = key
        return self._request("POST", "/api/register-code", payload=payload)
