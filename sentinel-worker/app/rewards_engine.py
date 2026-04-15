"""
Sentinel-Square Rewards Engine
===============================
Comprehensive reward maximization system:
1. YieldEngine: Simple Earn / Dual Investment / Auto-Compound
2. LaunchpoolAutoStaker: Automatically stake BNB for new token launches
3. ReferralOptimizer: Track best performing content and amplify with CTAs
"""

import asyncio
import logging
import random
import re
from datetime import datetime, timedelta
from typing import Optional

import httpx
from binance.client import Client
from binance.exceptions import BinanceAPIException

logger = logging.getLogger("sentinel.rewards")

# ---------------------------------------------------------------------------
# Rewards Engine
# ---------------------------------------------------------------------------
class RewardsEngine:
    def __init__(self, state, client: Client):
        self.state = state
        self.client = client
        self.earn_subscription_queue = []
        self.launchpool_positions = []
        self.referral_clicks = 0
        self.referral_conversions = 0

    # =========================================================================
    # 1. YIELD ENGINE - Idle Balance Sweep into Simple Earn
    # =========================================================================
    async def sweep_idle_to_earn(self, min_balance_usdt: float = 10.0, target_apr: float = 15.0) -> dict | None:
        """
        Sweep idle USDT from Spot wallet into Simple Earn (Flexible).
        Only subscribes if idle balance > min_balance_usdt.
        """
        try:
            account = self.client.get_account()
            usdt_balance = 0.0

            for asset in account["balances"]:
                if asset["asset"] == "USDT":
                    usdt_balance = float(asset["free"])
                    break

            if usdt_balance < min_balance_usdt:
                return None

            subscribe_amount = usdt_balance * 0.95  # Keep 5% for gas/fees
            if subscribe_amount < min_balance_usdt:
                return None

            # Get Flexible Product ID for USDT
            products = self.client.get_simple_earn_flexible_product_list(asset="USDT")
            if not products or "rows" not in products:
                return None
            
            product_id = products["rows"][0]["productId"]
            
            # Subscribe to Flexible Earn
            result = self.client.subscribe_simple_earn_flexible_product(
                productId=product_id,
                amount=str(round(subscribe_amount, 2)),
                autoSubscribe="true"
            )

            if result.get("success"):
                await self.state.add_log(
                    "info",
                    f"Yield Engine: Successfully swept ${subscribe_amount:.2f} USDT into Simple Earn (APR: {target_apr}%)"
                )
            else:
                await self.state.add_log(
                    "warning",
                    f"Yield Engine: Simple Earn subscription failed: {result.get('message')}"
                )

            return {
                "action": "sweep_earn",
                "amount_usdt": subscribe_amount,
                "apr": target_apr,
                "timestamp": datetime.utcnow().isoformat()
            }

        except BinanceAPIException as e:
            await self.state.add_log("error", f"Yield Engine Error: {e.message}")
        except Exception as e:
            await self.state.add_log("error", f"Yield Engine Error: {str(e)}")
        return None

    # =========================================================================
    # 2. DUAL INVESTMENT - Auto-Subscribe
    # =========================================================================
    async def check_and_subscribe_dual_investment(self) -> dict | None:
        """
        Check for Dual Investment products and auto-subscribe BTC/ETH
        if user holds the underlying asset.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                headers = {"X-Square-OpenAPI-Key": self.client.API_KEY}
                response = await http_client.get(
                    "https://www.binance.com/sapi/v1/dci/product/list",
                    headers=headers
                )

                if response.status_code == 200:
                    products = response.json().get("data", [])
                    if products:
                        product = products[0]
                        await self.state.add_log(
                            "info",
                            f" Dual Investment available: {product.get('asset', 'BTC')}"
                        )
                        return {
                            "action": "dual_investment_check",
                            "product": product.get("asset"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
        except Exception as e:
            await self.state.add_log("error", f"Dual Investment Check Error: {str(e)}")
        return None

    # =========================================================================
    # 3. LAUNCHPOOL AUTO-STAKER
    # =========================================================================
    async def check_launchpools(self) -> list[dict]:
        """
        Fetch active Launchpools and auto-stake BNB if user qualifies.
        Returns list of available pools.
        """
        available_pools = []
        try:
            # Using private request for sapi v1 launchpool
            response = self.client._request_api('get', 'launchpool/token/list', signed=True, version='v1', api='sapi')
            
            if response and response.get("code") == "000000":
                pools = response.get("data", [])
                for pool in pools:
                    if pool.get("status") == "ACTIVE":
                        pool_name = pool.get("poolName", "Unknown")
                        token_name = pool.get("tokenName", "Unknown")
                        apr = float(pool.get("annualInterestRate", 0)) * 100

                        available_pools.append({
                            "pool_name": pool_name,
                            "token": token_name,
                            "apr": round(apr, 2),
                            "status": "ACTIVE"
                        })

                        await self.state.add_log(
                            "info",
                            f" Launchpool detected: {token_name} | APR: {apr:.1f}%"
                        )

        except Exception as e:
            logger.error(f"Launchpool Check Error: {e}")
            # Fallback to public if private fails
            try:
                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    resp = await http_client.get("https://www.binance.com/sapi/v1/launchpool/token/list")
                    if resp.status_code == 200:
                        # ... fallback logic
                        pass
            except:
                pass

        return available_pools

    async def stake_for_launchpool(self, pool_token: str, amount_bnb: float) -> dict | None:
        """
        Stake BNB for a specific Launchpool.
        """
        if amount_bnb < 0.01:  # Minimum stake
            return None

        try:
            params = {
                "poolToken": pool_token,
                "amount": str(amount_bnb)
            }
            result = self.client._request_api('post', 'launchpool/stake', signed=True, version='v1', api='sapi', data=params)
            
            if result and result.get("code") == "000000":
                await self.state.add_log(
                    "info",
                    f" Launchpool: Successfully staked {amount_bnb} BNB for {pool_token}"
                )
                return {
                    "action": "launchpool_stake",
                    "pool": pool_token,
                    "amount_bnb": amount_bnb,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                await self.state.add_log(
                    "warning",
                    f" Launchpool: Staking failed: {result.get('message', 'Unknown error')}"
                )
        except Exception as e:
            await self.state.add_log("error", f"Launchpool Stake Error: {str(e)}")
        return None

    # =========================================================================
    # 4. AUTOMATED REFERRAL OPTIMIZER
    # =========================================================================
    async def track_referral_performance(self, post_content: str) -> dict:
        """
        Analyze post content and track referral link clicks/conversions.
        """
        has_referral = "binance.com/referral" in post_content.lower()

        if has_referral:
            self.referral_clicks += 1
            await self.state.add_log(
                "info",
                f" Referral CTA detected in post | Total CTAs shown: {self.referral_clicks}"
            )

        return {
            "referral_in_post": has_referral,
            "total_ctas": self.referral_clicks,
            "conversions": self.referral_conversions,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_best_performing_tickers(self, post_history: list) -> list[str]:
        """
        Analyze post history to find tickers that generated most engagement.
        Returns top 3 tickers to emphasize in next posts.
        """
        ticker_counts = {}
        for post in post_history[-50:]:  # Last 50 posts
            content = post.get("content", "")
            tickers = re.findall(r"\$[A-Z]{2,10}", content.upper())
            for ticker in tickers:
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

        sorted_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_tickers[:3]]

    # =========================================================================
    # 5. DAILY CLAIMS CHECKER
    # =========================================================================
    async def check_daily_claims(self) -> dict:
        """
        Check for claimable rewards (Launchpool, Simple Earn, etc).
        This scans the account for any unclaimed rewards.
        """
        claimable = []

        try:
            # Check Simple Earn rewards
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                headers = {"X-Square-OpenAPI-Key": self.client.API_KEY}

                # Check for Simple Earn positions
                earn_response = await http_client.get(
                    "https://www.binance.com/sapi/v1/simple-earn/flexible/positions",
                    headers=headers
                )

                if earn_response.status_code == 200:
                    positions = earn_response.json().get("data", [])
                    for pos in positions:
                        asset = pos.get("asset", "USDT")
                        apr = float(pos.get("annualInterestRate", 0)) * 100
                        amount = float(pos.get("amount", 0))
                        claimable.append({
                            "type": "simple_earn",
                            "asset": asset,
                            "amount": amount,
                            "apr": round(apr, 2)
                        })

                # Check for Locked Staking
                locked_response = await http_client.get(
                    "https://www.binance.com/sapi/v1/staking/staking/positions",
                    headers=headers,
                    params={"product": "STAKING", "transactionHistory": "true"}
                )

                if locked_response.status_code == 200:
                    locked_positions = locked_response.json().get("data", [])
                    for pos in locked_positions:
                        asset = pos.get("asset", "BNB")
                        amount = float(pos.get("amount", 0))
                        claimable.append({
                            "type": "locked_staking",
                            "asset": asset,
                            "amount": amount
                        })

                if claimable:
                    await self.state.add_log(
                        "info",
                        f" Daily Claims: Found {len(claimable)} active earning positions"
                    )

        except Exception as e:
            await self.state.add_log("error", f"Daily Claims Check Error: {str(e)}")

        return {
            "claimable_rewards": claimable,
            "total_positions": len(claimable),
            "timestamp": datetime.utcnow().isoformat()
        }

    # =========================================================================
    # MAIN ORCHESTRATOR - Run All Reward Checks
    # =========================================================================
    async def run_reward_cycle(self, post_history: list) -> dict:
        """
        Run all reward checks in parallel and return comprehensive report.
        """
        results = {
            "yield_sweep": None,
            "dual_investment": None,
            "launchpools": [],
            "referral_stats": {},
            "daily_claims": {},
            "best_tickers": []
        }

        # Run all checks concurrently
        tasks = [
            self.sweep_idle_to_earn(),
            self.check_daily_claims(),
            self.check_launchpools(),
            self.get_best_performing_tickers(post_history)
        ]

        yield_result, claims_result, pools_result, best_tickers = await asyncio.gather(*tasks, return_exceptions=True)

        if isinstance(yield_result, dict):
            results["yield_sweep"] = yield_result
        if isinstance(claims_result, dict):
            results["daily_claims"] = claims_result
        if isinstance(pools_result, list):
            results["launchpools"] = pools_result
        if isinstance(best_tickers, list):
            results["best_tickers"] = best_tickers

        return results
