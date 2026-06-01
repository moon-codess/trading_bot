# Binance Futures Testnet Trading Bot

A command-line trading bot for placing orders on Binance Futures Testnet (USDT-M).
No third-party Binance SDK — just Python's `requests` library and the standard library.

## Project Structure

```
trading_bot/
├── bot/
│   ├── client.py          # REST client: request signing, HTTP, error handling
│   ├── orders.py          # one function per order type
│   ├── validators.py      # validates all user input before hitting the API
│   └── logging_config.py  # sets up file + console logging
├── cli.py                 # entry point — run this
├── requirements.txt
└── logs/                  # auto-created; one log file per day
```

## Setup

### 1. Get testnet credentials

Go to [testnet.binancefuture.com](https://testnet.binancefuture.com), sign in with GitHub,
then find the API Key section on the dashboard and click Generate.

### 2. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/trading_bot.git
cd trading_bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set credentials

```bash
# Windows (PowerShell)
$env:BINANCE_API_KEY="your_key_here"
$env:BINANCE_API_SECRET="your_secret_here"

# Linux/Mac
export BINANCE_API_KEY="your_key_here"
export BINANCE_API_SECRET="your_secret_here"
```

## Usage

```bash
# Market order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

# Limit order
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3200

# Stop-Market order (bonus order type)
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 58000

# Pass credentials directly instead of env vars
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 \
  --api-key YOUR_KEY --api-secret YOUR_SECRET
```

## All flags

| Flag | Required | Description |
|---|---|---|
| `--symbol` | Yes | Trading pair e.g. `BTCUSDT` |
| `--side` | Yes | `BUY` or `SELL` |
| `--type` | Yes | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--quantity` | Yes | Positive number e.g. `0.01` |
| `--price` | LIMIT only | Limit price |
| `--stop-price` | STOP_MARKET only | Trigger price |
| `--api-key` | If env not set | Binance API key |
| `--api-secret` | If env not set | Binance API secret |
| `--log-dir` | No | Log folder, default `./logs` |

## Logs

All orders and API activity are logged to `logs/trading_bot_YYYYMMDD.log`.
The terminal shows INFO and above only; the log file captures full DEBUG detail
including raw request parameters and API responses.

## Assumptions

- Targets Binance Futures Testnet only. To use in production, update `TESTNET_BASE_URL`
  in `bot/client.py` and handle symbol-specific quantity precision via `/fapi/v1/exchangeInfo`.
- `timeInForce` defaults to `GTC` (Good Till Cancelled) for all limit orders.
- Quantity precision: the testnet is lenient; production has strict `LOT_SIZE` filters per symbol.