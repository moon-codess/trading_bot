from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

TESTNET_BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logger()


class BinanceAPIError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        if not api_key or not api_secret:
            raise ValueError("API key and secret are both required.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        sig = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = sig
        return params

    def _request(self, method: str, path: str, params: dict | None = None) -> Any:
        params = params or {}
        params = self._sign(params)
        url = f"{self.base_url}{path}"

        logger.debug("→ %s %s  params=%s", method.upper(), url,
                     {k: v for k, v in params.items() if k != "signature"})

        try:
            resp = self.session.request(method, url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError("Could not reach Binance testnet. Check your connection.") from exc
        except requests.exceptions.Timeout:
            logger.error("Request timed out.")
            raise TimeoutError("Request timed out.")

        logger.debug("← HTTP %s  body=%s", resp.status_code, resp.text[:600])

        try:
            data = resp.json()
        except ValueError:
            raise BinanceAPIError(-1, f"Non-JSON response (HTTP {resp.status_code})")

        if not resp.ok:
            code = data.get("code", resp.status_code)
            msg = data.get("msg", resp.text)
            logger.error("API error — code=%s msg=%s", code, msg)
            raise BinanceAPIError(code, msg)

        return data

    def place_order(self, **kwargs) -> dict:
        return self._request("POST", "/fapi/v1/order", params=kwargs)