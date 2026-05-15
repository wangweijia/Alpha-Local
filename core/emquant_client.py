from __future__ import annotations

from typing import Any


class EmQuantClientError(RuntimeError):
    pass


class EmQuantClient:
    def __init__(self) -> None:
        self._sdk = None
        self._sdk_import_error: Exception | None = None
        self.connected = False
        try:
            from EmQuantAPI import c  # type: ignore

            self._sdk = c
        except ImportError as exc:
            self._sdk = None
            self._sdk_import_error = exc

    @property
    def sdk_available(self) -> bool:
        return self._sdk is not None

    def connect(self) -> bool:
        self._ensure_sdk_ready()
        self.connected = True
        return self.connected

    def fetch_positions(self) -> list[dict[str, Any]]:
        self._ensure_sdk_ready()
        query_method = getattr(self._sdk, "get_positions")
        response = query_method()
        if not isinstance(response, list):
            raise EmQuantClientError("EmQuant SDK get_positions() 返回值必须是 list。")
        return response

    def _ensure_sdk_ready(self) -> None:
        if self._sdk is None:
            message = "EmQuant SDK 不可用：未安装或导入失败。"
            if self._sdk_import_error is not None:
                message = f"{message} 原因: {self._sdk_import_error}"
            raise EmQuantClientError(message)
        query_method = getattr(self._sdk, "get_positions", None)
        if not callable(query_method):
            raise EmQuantClientError("EmQuant SDK 不可用：缺少 get_positions() 方法。")
