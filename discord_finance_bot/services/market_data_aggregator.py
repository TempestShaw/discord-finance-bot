"""
Market Data Aggregator - Unified interface for all market data sources.

This service orchestrates data from:
1. Yahoo Finance (stocks, prices)
2. Polymarket (earnings predictions)
3. Alpha Vantage (IPOs, official earnings)
4. Moomoo (sector data)

Single responsibility: Aggregate and normalize market data from multiple sources.
"""

import asyncio
from typing import Dict, List, Optional
from services.finance.yahoo_finance_service import YahooFinanceService
from services.finance.sector_chart_service import SectorChartService
from services.web_crawler_service import WebCrawlerService
from services.alphavantage_service import AlphaVantageService
from utils.logger import get_logger
import datetime as dt
from zoneinfo import ZoneInfo


class MarketDataAggregator:
    """Aggregate market data from multiple sources."""

    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)

        # Initialize all data source services
        self.yahoo_finance = YahooFinanceService()
        self.sector_chart = SectorChartService()
        self.web_crawler = WebCrawlerService(config)
        self.alpha_vantage = AlphaVantageService(config)

    async def get_polymarket_earnings(self) -> List[Dict]:
        """Get earnings predictions from Polymarket."""
        try:
            return await self.web_crawler.get_polymarket_earnings_async()
        except Exception as e:
            self.logger.error(f"Error fetching Polymarket data: {e}")
            return []

    async def get_sector_data(self) -> List[Dict]:
        """Get sector performance data from Moomoo."""
        try:
            return await self.web_crawler.get_top_sectors_details_async(limit=10)
        except Exception as e:
            self.logger.error(f"Error fetching sector data: {e}")
            return []

    async def get_ipos(self) -> List[Dict]:
        """Get IPO calendar from Alpha Vantage."""
        try:
            # AlphaVantageService only has sync methods
            # Get dates and call sync method
            today = dt.datetime.now(ZoneInfo(self.config.timezone)).date()
            dates = [today, today + dt.timedelta(days=1), today + dt.timedelta(days=2)]
            return self.alpha_vantage.get_week_ipos_for_dates(dates)
        except Exception as e:
            self.logger.error(f"Error fetching IPO data: {e}")
            return []

    async def get_daily_market_summary(self) -> Dict:
        """
        Complete daily market summary from all sources.

        Returns:
            Dict with all market data normalized
        """
        self.logger.info("Generating daily market summary...")

        # Fetch data from all sources in parallel
        polymarket_data = await self.get_polymarket_earnings()
        sector_data = await self.get_sector_data()
        ipo_data = await self.get_ipos()

        # Get current date
        today = dt.datetime.now(ZoneInfo(self.config.timezone)).date()
        dates = [today, today + dt.timedelta(days=1), today + dt.timedelta(days=2)]

        # Compile summary
        summary = {
            'polymarket_earnings': polymarket_data,
            'top_sectors_details': sector_data,
            'ipos': ipo_data,
            'dates': [d.isoformat() for d in dates]
        }

        self.logger.info("Daily market summary generated")
        return summary

    async def get_stock_data(self, ticker: str, period: str = "3mo"):
        return await asyncio.to_thread(self._get_stock_data_sync, ticker, period)

    def _get_stock_data_sync(self, ticker: str, period: str = "3mo"):
        # Fetch stock data
        data = self.yahoo_finance.fetch_stock_data(ticker, period=period)

        # Return error immediately if it's an error response
        if isinstance(data, dict) and "type" in data:
            return data

        # Extract stock info from data
        info = self.yahoo_finance.extract_stock_info(ticker, data)
        if not info:
            return {
                "type": "not_found",
                "message": f"No info found for {ticker}"
            }

        chart = self.yahoo_finance.create_candlestick_chart(data, ticker, period=period)

        return {
            "info": info,
            "data": data,
            "chart": chart
        }


    def generate_sector_chart(self, sector_data: List[Dict]) -> Optional[bytes]:
        """
        Generate sector performance chart.

        Args:
            sector_data: List of sector dictionaries

        Returns:
            PNG chart as bytes or None if error
        """
        try:
            return self.sector_chart.generate_sector_performance_chart(sector_data)
        except Exception as e:
            self.logger.error(f"Error generating sector chart: {e}")
            return None
