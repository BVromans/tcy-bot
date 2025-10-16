# TCY Bot v5.7
# Portfolio-waarde-gestuurde papertrading bot met configureerbare cooldown

import asyncio
import aiohttp
import logging
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env configuration
load_dotenv()

# Logging setup
logging.basicConfig(
    filename="tcy_bot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("tcy_bot_v5.7")

API_BASE = "https://api.rujira.network/api"

# Environment settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "thor1n7y5j4swnq3ufqf6ywzk65mu7stdtwv45dc3gy")

PAIR = os.getenv("PAIR", "TCY_USDC")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))
TRADE_COOLDOWN = int(os.getenv("TRADE_COOLDOWN", "60"))

# Convert helper
def _to_float(value, default):
    try:
        return float(value)
    except:
        return default

# Portfolio logic settings
INITIAL_TCY = _to_float(os.getenv("INITIAL_TCY"), 33187.0)
INITIAL_PORTFOLIO_VALUE = _to_float(os.getenv("INITIAL_PORTFOLIO_VALUE"), 5700.0)
BASE_VALUE = _to_float(os.getenv("BASE_VALUE"), INITIAL_PORTFOLIO_VALUE)
SELL_DELTA = _to_float(os.getenv("SELL_DELTA"), 0.036)  # +3.6%
BUY_DELTA = _to_float(os.getenv("BUY_DELTA"), -0.032)   # -3.2%
BASE_INCREMENT = _to_float(os.getenv("BASE_INCREMENT"), 25.0)

# Starting balances (calculated from initial portfolio)
TCY_START_PRICE = INITIAL_PORTFOLIO_VALUE / INITIAL_TCY
TCY_BALANCE = INITIAL_TCY
USDC_BALANCE = 0.0

TRADES_FILE = "trades.csv"

def init_csv():
    if not os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "action", "tcy_price", "portfolio_value", "base_value", "trade_value", "new_base_value", "tcy_balance", "usdc_balance"])

def log_trade(action, tcy_price, portfolio_value, base_value, trade_value, new_base_value, tcy_balance, usdc_balance):
    with open(TRADES_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            action,
            f"{tcy_price:.6f}",
            f"{portfolio_value:.2f}",
            f"{base_value:.2f}",
            f"{trade_value:.2f}",
            f"{new_base_value:.2f}",
            f"{tcy_balance:.4f}",
            f"{usdc_balance:.2f}"
        ])

async def send_telegram(msg: str):
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID":
        logger.info(f"[Telegram Simulated] {msg}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        async with aiohttp.ClientSession() as sess:
            await sess.post(url, json=payload)
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

async def get_midprice(ticker_id=PAIR):
    url = f"{API_BASE}/trade/orderbook?ticker_id={ticker_id}&depth=1"
    async with aiohttp.ClientSession() as sess:
        try:
            resp = await sess.get(url)
            if resp.status != 200:
                logger.error(f"Failed to fetch orderbook: {resp.status}")
                return None
            obj = await resp.json()
            bids, asks = obj.get("bids", []), obj.get("asks", [])
            if not bids or not asks:
                return None
            best_bid, best_ask = float(bids[0][0]), float(asks[0][0])
            return (best_bid + best_ask) / 2.0
        except Exception as e:
            logger.error(f"Error fetching midprice: {e}")
            return None

async def run_cycle():
    global BASE_VALUE, TCY_BALANCE, USDC_BALANCE

    tcy_price = await get_midprice(PAIR)
    if not tcy_price:
        logger.warning("No live price available; skipping cycle.")
        return

    portfolio_value = (TCY_BALANCE * tcy_price) + USDC_BALANCE
    sell_threshold = BASE_VALUE * (1 + SELL_DELTA)
    buy_threshold = BASE_VALUE * (1 + BUY_DELTA)

    logger.info(f"[Cycle] Price={tcy_price:.6f}, Portfolio={portfolio_value:.2f}, Base={BASE_VALUE:.2f}, Sell≥{sell_threshold:.2f}, Buy≤{buy_threshold:.2f}")

    # SELL
    if portfolio_value >= sell_threshold:
        trade_value = BASE_VALUE * SELL_DELTA
        USDC_BALANCE += trade_value
        TCY_BALANCE -= trade_value / tcy_price
        BASE_VALUE += BASE_INCREMENT
        logger.info(f"[SELL] Sold TCY worth {trade_value:.2f} at {tcy_price:.6f}. New base={BASE_VALUE:.2f}")
        await send_telegram(f"💰 SELL | +{SELL_DELTA*100:.1f}% | ${trade_value:.2f} | New base=${BASE_VALUE:.2f} | TCY={TCY_BALANCE:.2f}")
        log_trade("SELL", tcy_price, portfolio_value, BASE_VALUE - BASE_INCREMENT, trade_value, BASE_VALUE, TCY_BALANCE, USDC_BALANCE)
        await asyncio.sleep(TRADE_COOLDOWN)

    # BUY
    elif portfolio_value <= buy_threshold:
        trade_value = BASE_VALUE * abs(BUY_DELTA)
        USDC_BALANCE -= trade_value
        TCY_BALANCE += trade_value / tcy_price
        logger.info(f"[BUY] Bought TCY worth {trade_value:.2f} at {tcy_price:.6f}. Base unchanged={BASE_VALUE:.2f}")
        await send_telegram(f"🛒 BUY | {BUY_DELTA*100:.1f}% | ${trade_value:.2f} | Base=${BASE_VALUE:.2f} | TCY={TCY_BALANCE:.2f}")
        log_trade("BUY", tcy_price, portfolio_value, BASE_VALUE, trade_value, BASE_VALUE, TCY_BALANCE, USDC_BALANCE)
        await asyncio.sleep(TRADE_COOLDOWN)

    else:
        logger.info("No trade condition met.")

async def main():
    init_csv()
    await send_telegram(f"🚀 TCY Bot v5.7 started | Base=${BASE_VALUE:.2f} | TCY={TCY_BALANCE:.0f} | Δ+{SELL_DELTA*100:.2f}% / {BUY_DELTA*100:.2f}% | Cooldown={TRADE_COOLDOWN}s")
    while True:
        try:
            await run_cycle()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await send_telegram(f"⚠️ Error: {e}")
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())