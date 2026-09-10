"""Run the Discord Finance Bot summary formatter without credentials or network calls."""

import asyncio

from config import Config
from services.message_service import MessageService


async def main() -> None:
    service = MessageService(
        Config(
            discord_token="demo",
            channel_id=None,
            selected_stocks=["AAPL", "MSFT"],
            timezone="America/New_York",
        )
    )

    async def demo_sectors():
        return [
            {
                "plateName": "Technology",
                "changeRatio": "+2.5%",
                "stockName": "AAPL",
                "stockChangeRatio": "+3.2%",
                "priceRiseCount": 45,
                "priceSameCount": 3,
                "priceFallCount": 12,
            },
            {
                "plateName": "Healthcare",
                "changeRatio": "+1.8%",
                "stockName": "JNJ",
                "stockChangeRatio": "+2.1%",
                "priceRiseCount": 32,
                "priceSameCount": 8,
                "priceFallCount": 15,
            },
        ]

    async def demo_polymarket():
        return [
            {
                "date": "16",
                "time": "Post Market",
                "ticker": "AAPL",
                "eps_forecast": "EPS $2.10",
                "probability": "72%",
            }
        ]

    service.web_crawler_service.get_top_sectors_details_async = demo_sectors
    service.web_crawler_service.get_polymarket_earnings_async = demo_polymarket
    service.alpha_service.get_week_earnings_for_dates = lambda dates: [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "reportDate": "2025-01-16",
            "estimateEPS": "2.10",
            "estimateCurrency": "USD",
        }
    ]
    service.alpha_service.get_week_ipos_for_dates = lambda dates: []

    print(await service.generate_daily_summary_text_async())


if __name__ == "__main__":
    asyncio.run(main())
