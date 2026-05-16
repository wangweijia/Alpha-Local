from __future__ import annotations

from typing import Any


class EmQuantClientError(RuntimeError):
    pass


def mainCallback(quantdata: Any) -> None:
    print(f"EmQuant mainCallback: {quantdata}")


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
        if self.connected:
            return True

        self._ensure_sdk_imported()
        
        import os
        phone_number = os.getenv("EMQUANT_PHONE_NUMBER", "")
        
        # 默认尝试使用 userInfo 令牌自动登录
        start_options = "ForceLogin=1"
        
        # 如果提供了手机号，则采用方式三：上行短信登录验证
        if phone_number:
            start_options = f"LoginMode=SXDL,PhoneNumber={phone_number}"

        # 尝试登录
        loginResult = self._sdk.start(start_options, "", mainCallback)
        if loginResult.ErrorCode != 0:
            raise EmQuantClientError(f"EmQuant SDK 登录失败: {loginResult.ErrorMsg} (Code: {loginResult.ErrorCode})")

        self.connected = True
        return self.connected

    def fetch_positions(self) -> list[dict[str, Any]]:
        self.connect()

        # 我们指定一个默认的股票组合池来获取实时数据
        # 实际业务中这里可以是用户的自选股或者真实券商持仓，在此使用固定的代码作为示例
        symbols = "600519.SH,000001.SZ,300059.SZ,000858.SZ,300750.SZ"
        
        # 使用 css 获取最新快照数据 (NAME: 股票名称, NOW: 最新价)
        data = self._sdk.css(symbols, "NAME,NOW", "Ispandas=0")
        
        if data.ErrorCode != 0:
            raise EmQuantClientError(f"EmQuant SDK 获取数据失败: {data.ErrorMsg}")

        results = []
        for code in data.Codes:
            indicator_values = data.Data.get(code, [])
            
            name = str(indicator_values[0]) if len(indicator_values) > 0 else code
            try:
                last_price = float(indicator_values[1])
            except (ValueError, TypeError, IndexError):
                last_price = 0.0

            # 构建虚拟的持仓数据
            results.append({
                "symbol": code,
                "name": name,
                "quantity": 100,
                "average_cost": round(last_price * 0.95, 2),  # 假设浮盈 5%
                "last_price": last_price,
                "portfolio_tag": "自动同步组合",
                "strategy_description": "API 自动拉取股票",
                "expected_action": "观察趋势"
            })

        return results

    def _ensure_sdk_imported(self) -> None:
        if self._sdk is None:
            message = "EmQuant SDK 不可用：未安装或导入失败。"
            if self._sdk_import_error is not None:
                message = f"{message} 原因: {self._sdk_import_error}"
            raise EmQuantClientError(message)
