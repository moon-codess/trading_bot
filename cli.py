#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import textwrap

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logger
from bot.orders import place_limit_order, place_market_order, place_stop_market_order
from bot.validators import (
    validate_order_type, validate_price, validate_quantity,
    validate_side, validate_stop_price, validate_symbol,
)

logger = setup_logger()
LINE = "─" * 58


def print_summary(args):
    print(f"\n{LINE}")
    print("  ORDER SUMMARY")
    print(LINE)
    print(f"  Symbol     : {args.symbol}")
    print(f"  Side       : {args.side}")
    print(f"  Type       : {args.order_type}")
    print(f"  Quantity   : {args.quantity}")
    if args.order_type == "LIMIT":
        print(f"  Price      : {args.price}")
    if args.order_type == "STOP_MARKET":
        print(f"  Stop Price : {args.stop_price}")
    print(LINE)


def print_result(result):
    print(f"\n{LINE}")
    print("  ORDER RESPONSE")
    print(LINE)
    print(f"  Order ID      : {result['orderId']}")
    print(f"  Symbol        : {result['symbol']}")
    print(f"  Side          : {result['side']}")
    print(f"  Type          : {result['type']}")
    print(f"  Status        : {result['status']}")
    print(f"  Orig Qty      : {result['origQty']}")
    print(f"  Executed Qty  : {result['executedQty']}")
    print(f"  Avg Price     : {result['avgPrice']}")
    if result["type"] == "LIMIT":
        print(f"  Limit Price   : {result['price']}")
        print(f"  Time In Force : {result['timeInForce']}")
    if result["type"] == "STOP_MARKET":
        print(f"  Stop Price    : {result['stopPrice']}")
    print(LINE)
    print(f"\n  ✓ Order placed! ID: {result['orderId']}\n")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.01
              python cli.py --symbol ETHUSDT --side SELL --type LIMIT  --quantity 0.1 --price 3200
              python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 58000
        """),
    )
    parser.add_argument("--symbol",     required=True)
    parser.add_argument("--side",       required=True)
    parser.add_argument("--type",       required=True, dest="order_type")
    parser.add_argument("--quantity",   required=True)
    parser.add_argument("--price",      default=None)
    parser.add_argument("--stop-price", default=None, dest="stop_price")
    parser.add_argument("--api-key",    default=os.getenv("BINANCE_API_KEY"))
    parser.add_argument("--api-secret", default=os.getenv("BINANCE_API_SECRET"))
    parser.add_argument("--log-dir",    default="logs")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    setup_logger(log_dir=args.log_dir)

    if not args.api_key or not args.api_secret:
        parser.error(
            "Credentials missing. Pass --api-key/--api-secret or "
            "set BINANCE_API_KEY and BINANCE_API_SECRET."
        )

    try:
        args.symbol     = validate_symbol(args.symbol)
        args.side       = validate_side(args.side)
        args.order_type = validate_order_type(args.order_type)
        args.quantity   = validate_quantity(args.quantity)
        args.price      = validate_price(args.price, args.order_type)
        args.stop_price = validate_stop_price(args.stop_price, args.order_type)
    except ValueError as exc:
        print(f"\n[Validation Error] {exc}\n")
        sys.exit(1)

    print_summary(args)
    client = BinanceClient(api_key=args.api_key, api_secret=args.api_secret)

    try:
        if args.order_type == "MARKET":
            result = place_market_order(client, args.symbol, args.side, args.quantity)
        elif args.order_type == "LIMIT":
            result = place_limit_order(client, args.symbol, args.side, args.quantity, args.price)
        elif args.order_type == "STOP_MARKET":
            result = place_stop_market_order(client, args.symbol, args.side, args.quantity, args.stop_price)
    except BinanceAPIError as exc:
        print(f"\n[API Error] {exc.message}  (code: {exc.code})\n")
        sys.exit(1)
    except ConnectionError as exc:
        print(f"\n[Network Error] {exc}\n")
        sys.exit(1)
    except TimeoutError as exc:
        print(f"\n[Timeout] {exc}\n")
        sys.exit(1)
    except Exception as exc:
        print(f"\n[Unexpected Error] {exc}\n")
        logger.exception("Unexpected error")
        sys.exit(1)

    print_result(result)


if __name__ == "__main__":
    main()