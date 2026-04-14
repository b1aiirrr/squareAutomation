import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import (
    TRADING_API_KEY,
    TRADING_API_SECRET,
    TRADE_PERCENT_OF_WALLET,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
)

logger = logging.getLogger("sentinel.trading")

class TradingEngine:
    def __init__(self, state):
        self.state = state
        self.client = None
        if TRADING_API_KEY and TRADING_API_SECRET:
            try:
                self.client = Client(TRADING_API_KEY, TRADING_API_SECRET)
                logger.info("Trading engine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize trading engine: {e}")
        else:
            logger.warning("Trading API keys missing. Trading engine disabled.")

    async def execute_trade_if_bullish(self, content, tickers):
        if not self.client:
            return None

        bullish_indicators = ["bullish", "long", "breakout", "🚀", "📈", "buy", "target"]
        is_bullish = any(indicator in content.lower() for indicator in bullish_indicators)

        if not is_bullish or not tickers:
            return None

        ticker = tickers[0].replace("$", "").upper()
        symbol = f"{ticker}USDT"

        try:
            balance = self.client.get_asset_balance(asset='USDT')
            usdt_balance = float(balance['free'])

            if usdt_balance <= 10:
                await self.state.add_log("warning", f"Insufficient USDT balance: {usdt_balance}")
                return None

            trade_amount_usdt = usdt_balance * TRADE_PERCENT_OF_WALLET
            if trade_amount_usdt < 10:
                trade_amount_usdt = 10

            avg_price = self.client.get_avg_price(symbol=symbol)
            current_price = float(avg_price['price'])

            quantity = trade_amount_usdt / current_price
            quantity = round(quantity, 4)

            await self.state.add_log("info", f"Executing market BUY for {quantity} {ticker} (~${trade_amount_usdt:.2f})")

            order = self.client.order_market_buy(symbol=symbol, quantity=quantity)

            sl_price = current_price * (1 - STOP_LOSS_PCT)
            tp_price = current_price * (1 + TAKE_PROFIT_PCT)

            trade_info = {
                "symbol": symbol,
                "entry": current_price,
                "sl": sl_price,
                "tp": tp_price,
                "quantity": quantity,
                "order_id": order['orderId']
            }

            await self.state.add_log("info", f"Trade executed: {symbol} at {current_price}. SL: {sl_price:.2f}, TP: {tp_price:.2f}")

            return trade_info

        except BinanceAPIException as e:
            await self.state.add_log("error", f"Binance Trading Error: {e.message}")
            logger.error(f"Trading error: {e}")
        except Exception as e:
            await self.state.add_log("error", f"Trading Engine Error: {str(e)}")
            logger.error(f"General trading error: {e}")

        return None
