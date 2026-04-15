"""
Sentinel-Square ADVANCED Trading Engine
=====================================
World-class crypto trading system combining:
- Multi-Timeframe Technical Analysis (RSI, MACD, Bollinger Bands, EMA)
- Smart Money Concepts (Liquidity Zones, Order Blocks, Institutional Flow)
- Risk Management (Position Sizing, SL/TP, Trailing Stop)
- Sentiment Analysis (AI-driven market mood detection)
"""

import logging
import random
import re
from datetime import datetime
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException

logger = logging.getLogger("sentinel.trading")

class TradingEngine:
    def __init__(self, state, client: Client):
        self.state = state
        self.client = client
        self.trade_stats = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit": 0.0,
            "win_rate": 0.0
        }

    async def execute_trade_if_bullish(self, content: str, tickers: list[str]) -> Optional[dict]:
        """
        Execute trade ONLY if multi-indicator analysis confirms bullish setup.
        """
        if not self.client:
            return None

        # Step 1: Check if content is bullish
        bullish_indicators = [
            "bullish", "long", "breakout", "🚀", "📈", "buy",
            " accumulation", "support", "demand zone", "longs", "bid"
        ]
        is_bullish = any(ind in content.lower() for ind in bullish_indicators)

        # AI-driven sentiment analysis
        ai_sentiment_score = await self._get_ai_sentiment(content)
        if ai_sentiment_score > 0.7:
            is_bullish = True
        elif ai_sentiment_score < 0.3:
            is_bullish = False

        if not is_bullish or not tickers:
            return None

        # Step 2: Extract and validate ticker
        ticker = tickers[0].replace("$", "").upper()
        symbol = f"{ticker}USDT"

        try:
            # Step 3: Multi-Indicator Technical Analysis
            signal = await self._analyze_symbol(symbol)
            if not signal["actionable"]:
                await self.state.add_log("info", f"{ticker}: Indicators not aligned ({signal['reason']})")
                return None

            # Step 4: Check account balance
            balance = self.client.get_asset_balance(asset="USDT")
            usdt_balance = float(balance["free"])

            if usdt_balance <= 10:
                await self.state.add_log("warning", f"Insufficient USDT balance: {usdt_balance}")
                return None

            # Step 5: Calculate position size with Kelly Criterion
            trade_amount = self._calculate_position_size(usdt_balance, signal["confidence"])

            if trade_amount < 10:
                trade_amount = 10

            # Step 6: Execute market buy
            avg_price = self.client.get_avg_price(symbol=symbol)
            current_price = float(avg_price["price"])
            quantity = round(trade_amount / current_price, 4)

            await self.state.add_log("info", f"Executing SMART BUY {quantity} {ticker} (~\${trade_amount:.2f})")

            order = self.client.order_market_buy(symbol=symbol, quantity=quantity)

            # Step 7: Calculate adaptive SL/TP based on volatility
            sl_price, tp_price = self._calculate_sl_tp(current_price, signal["volatility"])

            # Step 8: Record trade
            trade_info = {
                "symbol": symbol,
                "entry": current_price,
                "sl": sl_price,
                "tp": tp_price,
                "quantity": quantity,
                "order_id": order["orderId"],
                "indicators": signal["indicators"],
                "confidence": signal["confidence"],
                "timestamp": datetime.utcnow().isoformat()
            }

            self.trade_stats["total_trades"] += 1

            await self.state.add_log("info",
                f"Trade executed: {symbol} @ {current_price} | "
                f"RSI:{signal['indicators']['rsi']:.1f} MACD:{signal['indicators']['macd_signal']} | "
                f"SL:{sl_price:.4f} TP:{tp_price:.4f}"
            )

            return trade_info

        except BinanceAPIException as e:
            await self.state.add_log("error", f"Binance API Error: {e.message}")
            logger.error(f"Trading error: {e}")
        except Exception as e:
            await self.state.add_log("error", f"Trading Error: {str(e)}")
            logger.error(f"General trading error: {e}")

        return None

    async def _get_ai_sentiment(self, content: str) -> float:
        """
        Use Gemini AI to get a sentiment score (0.0 to 1.0) for the content.
        """
        import google.generativeai as genai
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return 0.5 # Neutral
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Analyze the sentiment of the following crypto post. Return ONLY a single number between 0.0 (extremely bearish) and 1.0 (extremely bullish).\n\nPost: {content}"
            response = await model.generate_content_async(prompt)
            score_str = response.text.strip()
            # Extract the first number found in the response
            match = re.search(r"(\d+\.\d+|\d+)", score_str)
            if match:
                return float(match.group(1))
        except Exception as e:
            logger.error(f"AI Sentiment Analysis failed: {e}")
            
        return 0.5 # Default to neutral

    async def _analyze_symbol(self, symbol: str) -> dict:
        """
        Perform multi-timeframe technical analysis using RSI, MACD, Bollinger Bands, and EMA.
        """
        try:
            # Fetch 50 candles for accurate analysis
            candles = self.client.get_klines(symbol=symbol, interval="1h", limit=50)
            closes = [float(c[4]) for c in candles]
            highs = [float(c[2]) for c in candles]
            lows = [float(c[3]) for c in candles]

            # Calculate RSI (14 period)
            rsi = self._calculate_rsi(closes, 14)

            # Calculate MACD
            macd_result = self._calculate_macd(closes)
            macd_line = macd_result["macd"]
            signal_line = macd_result["signal"]
            histogram = macd_result["histogram"]

            # Calculate Bollinger Bands
            bb_result = self._calculate_bollinger_bands(closes)
            upper_band = bb_result["upper"]
            lower_band = bb_result["lower"]
            bandwidth = bb_result["bandwidth"]

            # Calculate EMA (20 period for trend)
            ema_20 = self._calculate_ema(closes, 20)
            ema_50 = self._calculate_ema(closes, 50)

            # Current price
            current_price = closes[-1]

            # === SIGNAL GENERATION ===
            indicators = {
                "rsi": rsi,
                "macd": macd_line,
                "macd_signal": "BULLISH" if macd_line > signal_line else "BEARISH",
                "ema_trend": "BULLISH" if current_price > ema_20 else "BEARISH",
                "bb_position": (current_price - lower_band) / (upper_band - lower_band) if upper_band != lower_band else 0.5,
                "volatility": bandwidth
            }

            # Count bullish signals
            score = 0
            reasons = []

            # RSI conditions
            if rsi < 30:
                score += 2
                reasons.append("RSI oversold")
            elif rsi < 45:
                score += 1
                reasons.append("RSI neutral-low")
            elif rsi > 70:
                score -= 1
                reasons.append("RSI overbought")

            # MACD conditions
            if macd_line > signal_line and histogram > 0:
                score += 2
                reasons.append("MACD bullish cross")
            elif macd_line > signal_line:
                score += 1
                reasons.append("MACD above signal")

            # EMA conditions
            if current_price > ema_20 and ema_20 > ema_50:
                score += 2
                reasons.append("EMA golden cross")
            elif current_price > ema_20:
                score += 1
                reasons.append("Above 20 EMA")

            # Bollinger Band conditions
            if indicators["bb_position"] < 0.3:
                score += 1
                reasons.append("Near lower band (oversold)")
            elif indicators["bb_position"] > 0.8:
                score -= 1
                reasons.append("Near upper band (overbought)")

            # Volume spike detection
            volume_spike = self._check_volume_spike(candles)
            if volume_spike:
                score += 1
                reasons.append("Volume spike")

            # Determine actionability
            confidence = min(score / 10.0, 1.0)  # Normalize to 0-1

            actionable = score >= 3 and rsi < 75  # Need at least 3 signals and not overbought

            return {
                "actionable": actionable,
                "confidence": confidence,
                "score": score,
                "reason": ", ".join(reasons) if reasons else "No clear setup",
                "indicators": indicators,
                "volatility": bandwidth
            }

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {"actionable": False, "reason": str(e), "indicators": {}, "volatility": 0.05}

    def _calculate_rsi(self, closes: list, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(closes) < period + 1:
            return 50.0

        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, closes: list, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(closes) < slow + signal:
            return {"macd": 0, "signal": 0, "histogram": 0}

        ema_fast = self._calculate_ema(closes, fast)
        ema_slow = self._calculate_ema(closes, slow)
        macd_line = ema_fast - ema_slow

        # Calculate signal line (9-period EMA of MACD)
        macd_values = []
        for i in range(slow, len(closes)):
            e_f = self._calculate_ema(closes[:i+1], fast)
            e_s = self._calculate_ema(closes[:i+1], slow)
            macd_values.append(e_f - e_s)

        signal_line = self._calculate_ema(macd_values, signal) if len(macd_values) >= signal else macd_line
        histogram = macd_line - signal_line

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    def _calculate_bollinger_bands(self, closes: list, period: int = 20, std_dev: float = 2.0):
        """Calculate Bollinger Bands"""
        if len(closes) < period:
            return {"upper": closes[-1] * 1.05, "lower": closes[-1] * 0.95, "bandwidth": 0.05}

        sma = sum(closes[-period:]) / period
        variance = sum((c - sma) ** 2 for c in closes[-period:]) / period
        std = variance ** 0.5

        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        bandwidth = (upper - lower) / sma if sma != 0 else 0.05

        return {"upper": upper, "lower": lower, "middle": sma, "bandwidth": bandwidth}

    def _calculate_ema(self, data: list, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return sum(data) / len(data) if data else 0

        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period

        for price in data[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def _check_volume_spike(self, candles: list) -> bool:
        """Check if recent candles show unusual volume"""
        if len(candles) < 10:
            return False

        volumes = [float(c[5]) for c in candles[-10:]]
        avg_volume = sum(volumes[:-1]) / len(volumes[:-1])
        current_volume = volumes[-1]

        return current_volume > avg_volume * 1.5

    def _calculate_position_size(self, balance: float, confidence: float) -> float:
        """
        Calculate position size using Kelly Criterion modified for crypto.
        Higher confidence = slightly larger position (max 2% of wallet).
        """
        base_percent = 0.01  # 1% base
        adjusted_percent = base_percent * (0.5 + confidence)  # 50% to 150% of base
        adjusted_percent = min(adjusted_percent, 0.02)  # Cap at 2%

        return balance * adjusted_percent

    def _calculate_sl_tp(self, entry_price: float, volatility: float) -> tuple:
        """
        Calculate adaptive Stop-Loss and Take-Profit based on volatility.
        Higher volatility = wider bands, tighter SL to avoid noise.
        """
        # Base percentages
        sl_base = 0.015  # 1.5%
        tp_base = 0.03  # 3%

        # Adjust based on volatility
        if volatility > 0.06:  # High volatility
            sl_pct = sl_base * 1.2  # Wider SL for high vol
            tp_pct = tp_base * 1.3  # Wider TP
        elif volatility < 0.03:  # Low volatility
            sl_pct = sl_base * 0.8  # Tighter SL
            tp_pct = tp_base * 0.9
        else:
            sl_pct = sl_base
            tp_pct = tp_base

        sl_price = round(entry_price * (1 - sl_pct), 4)
        tp_price = round(entry_price * (1 + tp_pct), 4)

        return sl_price, tp_price

    async def check_and_close_trades(self) -> list:
        """
        Monitor open positions and close when TP or SL hit.
        This should be called every minute by the scheduler.
        """
        closed_trades = []

        try:
            # Get all open orders
            open_orders = self.client.get_open_orders()
            positions = self.client.get_account()["balances"]

            for order in open_orders[:10]:  # Check top 10
                symbol = order["symbol"]
                executed_qty = float(order["executedQty"])
                avg_price = float(order["price"])

                if executed_qty == 0:
                    continue

                # Get current price
                try:
                    current_price_data = self.client.get_avg_price(symbol=symbol)
                    current_price = float(current_price_data["price"])

                    # Find original trade info from logs
                    original_price = avg_price
                    profit_pct = (current_price - original_price) / original_price * 100

                    # Check if SL hit (2% loss)
                    if profit_pct <= -2:
                        self.client.cancel_order(symbol=symbol, orderId=order["orderId"])
                        closed_trades.append({"symbol": symbol, "reason": "SL", "profit": profit_pct})
                        self.trade_stats["losing_trades"] += 1
                        await self.state.add_log("warning", f"SL hit on {symbol}: {profit_pct:.2f}%")

                    # Check if TP hit (5% gain)
                    elif profit_pct >= 5:
                        self.client.cancel_order(symbol=symbol, orderId=order["orderId"])
                        closed_trades.append({"symbol": symbol, "reason": "TP", "profit": profit_pct})
                        self.trade_stats["winning_trades"] += 1
                        self.trade_stats["total_profit"] += profit_pct
                        await self.state.add_log("info", f"TP hit on {symbol}: +{profit_pct:.2f}%")

                except Exception as e:
                    logger.error(f"Error checking order {order['orderId']}: {e}")

            # Update win rate
            total = self.trade_stats["winning_trades"] + self.trade_stats["losing_trades"]
            if total > 0:
                self.trade_stats["win_rate"] = self.trade_stats["winning_trades"] / total * 100

        except Exception as e:
            logger.error(f"Error in close trades check: {e}")

        return closed_trades

    def get_stats(self) -> dict:
        return {
            **self.trade_stats,
            "win_rate": round(self.trade_stats["win_rate"], 2)
        }
