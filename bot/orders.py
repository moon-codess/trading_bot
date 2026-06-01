from __future__ import annotations

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logger

logger = setup_logger()


def _extract(response: dict) -> dict:
    avg = response.get("avgPrice") or response.get("price") or "N/A"
    if avg in ("0", "0.00000000"):
        avg = "N/A (not filled yet)"
    return {
        "orderId":     response.get("orderId", "N/A"),
        "symbol":      response.get("symbol", "N/A"),
        "side":        response.get("side", "N/A"),
        "type":        response.get("type", "N/A"),
        "status":      response.get("status", "N/A"),
        "origQty":     response.get("origQty", "N/A"),
        "executedQty": response.get("executedQty", "N/A"),
        "avgPrice":    avg,
        "price":       response.get("price", "N/A"),
        "timeInForce": response.get("timeInForce", "N/A"),
        "stopPrice":   response.get("stopPrice", "N/A"),
        "updateTime":  response.get("updateTime", "N/A"),
    }


def place_market_order(client: BinanceClient, symbol: str, side: str, quantity: float) -> dict:
    logger.info("Placing MARKET %s — symbol=%s qty=%s", side, symbol, quantity)
    try:
        raw = client.place_order(symbol=symbol, side=side, type="MARKET", quantity=quantity)
    except BinanceAPIError:
        raise
    result = _extract(raw)
    logger.info("MARKET order done — orderId=%s status=%s executedQty=%s avgPrice=%s",
                result["orderId"], result["status"], result["executedQty"], result["avgPrice"])
    return result


def place_limit_order(
    client: BinanceClient, symbol: str, side: str,
    quantity: float, price: float, time_in_force: str = "GTC"
) -> dict:
    logger.info("Placing LIMIT %s — symbol=%s qty=%s price=%s", side, symbol, quantity, price)
    try:
        raw = client.place_order(
            symbol=symbol, side=side, type="LIMIT",
            quantity=quantity, price=price, timeInForce=time_in_force,
        )
    except BinanceAPIError:
        raise
    result = _extract(raw)
    logger.info("LIMIT order done — orderId=%s status=%s", result["orderId"], result["status"])
    return result


def place_stop_market_order(
    client: BinanceClient, symbol: str, side: str,
    quantity: float, stop_price: float
) -> dict:
    logger.info("Placing STOP_MARKET %s — symbol=%s qty=%s stopPrice=%s", side, symbol, quantity, stop_price)
    try:
        raw = client.place_order(
            symbol=symbol, side=side, type="STOP_MARKET",
            quantity=quantity, stopPrice=stop_price,
        )
    except BinanceAPIError:
        raise
    result = _extract(raw)
    logger.info("STOP_MARKET order done — orderId=%s status=%s", result["orderId"], result["status"])
    return result