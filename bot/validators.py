from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or not s.isalpha():
        raise ValueError(f"'{symbol}' doesn't look like a valid symbol. Try something like BTCUSDT.")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValueError(f"Side must be BUY or SELL, got '{side}'.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be one of {sorted(VALID_ORDER_TYPES)}, got '{order_type}'.")
    return t


def validate_quantity(quantity: str | float) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Quantity must be a number, got '{quantity}'.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {qty}.")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    if order_type == "LIMIT":
        if price is None or str(price).strip() == "":
            raise ValueError("--price is required for LIMIT orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Price must be a number, got '{price}'.")
        if p <= 0:
            raise ValueError(f"Price must be greater than zero, got {p}.")
        return p
    return None


def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    if order_type == "STOP_MARKET":
        if stop_price is None or str(stop_price).strip() == "":
            raise ValueError("--stop-price is required for STOP_MARKET orders.")
        try:
            sp = float(stop_price)
        except (ValueError, TypeError):
            raise ValueError(f"Stop price must be a number, got '{stop_price}'.")
        if sp <= 0:
            raise ValueError(f"Stop price must be greater than zero, got {sp}.")
        return sp
    return None