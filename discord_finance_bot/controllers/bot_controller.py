import json
import discord
from discord.ext import commands
import io
from services.message_service import MessageService
from services.market_data_aggregator import MarketDataAggregator
from utils.logger import get_logger
from typing import Optional


class BotController(commands.Bot):
    """Discord bot controller - coordinates all bot functionality.

    Responsibilities:
    - Initialize all services
    - Handle lifecycle events (on_ready)
    - Handle commands ($stock, !today, !today_json)
    - Coordinate with SchedulerController for scheduled tasks

    This controller delegates to MarketDataAggregator for all data operations.
    """

    def __init__(self, config):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix='!',
            intents=intents,
            case_insensitive=True  # Make commands case-insensitive
        )

        self.config = config
        self.message_service = MessageService(config)
        self.market_data = MarketDataAggregator(config)
        self.logger = get_logger(__name__)
        self._scheduler: Optional[object] = None

        # Create command implementations as local functions (no self parameter)
        async def stock_cmd(ctx, ticker: str, period: Optional[str] = None):
            ticker = ticker.upper().strip()

            # Validate and set period
            if period:
                period = period.upper().strip()
                # Remove trailing slashes if present
                if period.endswith('/'):
                    period = period[:-1]

                # Validate period format
                valid_periods = ['1D', '5D', '1MO', '3MO', '6MO', '1Y', '2Y', '5Y', '10Y']
                if period not in valid_periods:
                    await ctx.send(
                        f"❌ Invalid period: **{period}**\n"
                        f"Valid periods: {', '.join(valid_periods)}\n"
                        f"Example: `!s {ticker} 3mo` or `!s {ticker} 1y`"
                    )
                    return
            else:
                period = "3mo"  # Default period

            try:
                # Send initial response
                await ctx.send(f"📊 Fetching {ticker} data...")

                # Get complete stock data from aggregator
                stock_data = await self.market_data.get_stock_data(ticker, period=period)

                if isinstance(stock_data, dict) and "type" in stock_data:
                    error_type = stock_data["type"]

                    if error_type == "rate_limit":
                        await ctx.send(
                            "⏳ **Yahoo Finance is rate limiting requests.**\n"
                            "Please wait a minute and try again."
                        )
                        return

                    if error_type == "not_found":
                        await ctx.send(f"❌ No data found for ticker **{ticker}**")
                        return

                    await ctx.send(f"❌ Error fetching **{ticker}**: {stock_data['message']}")
                    return

                # Extract data
                info = stock_data['info']
                chart_bytes = stock_data['chart']

                # Create Discord embed - keep title consistent
                embed = discord.Embed(
                    title=f"{ticker} Stock Chart",
                    color=0x26a69a  # Teal color
                )

                # Add stock info fields
                change_emoji = "🟢" if info['change'] >= 0 else "🔴"
                embed.add_field(
                    name="Latest Price",
                    value=f"${info['price']:.2f}",
                    inline=True
                )
                embed.add_field(
                    name=f"Last Day {change_emoji} Change",
                    value=f"{info['change']:+.2f} ({info['change_percent']:+.2f}%)",
                    inline=True
                )
                embed.add_field(
                    name="Volume",
                    value=f"{info['volume']:,}",
                    inline=True
                )

                embed.set_footer(text="Data from Yahoo Finance")

                # Send embed with chart attachment
                chart_file = discord.File(io.BytesIO(chart_bytes), filename=f"{ticker}_chart.png")
                embed.set_image(url=f"attachment://{ticker}_chart.png")

                await ctx.send(embed=embed, files=[chart_file])

                self.logger.info(f"Sent stock chart for {ticker} (period={period}) to channel {ctx.channel.id}")

            except Exception as e:
                self.logger.error(f"Error handling stock command for {ticker}: {e}")
                await ctx.send(
                    f"❌ Unable to fetch data for **{ticker}**. Check the bot logs for details."
                )

        async def today_cmd(ctx):
            try:
                text = await self.message_service.generate_daily_summary_text_async()
                await ctx.send(text)
            except Exception as e:
                self.logger.error(f"Error handling today command: {e}")
                await ctx.send("❌ Unable to generate the summary. Check the bot logs for details.")

        async def today_json_cmd(ctx):
            try:
                payload = await self.message_service.generate_daily_summary_json_async()
                await ctx.send(
                    f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
                )
            except Exception as e:
                self.logger.error(f"Error handling today_json command: {e}")
                await ctx.send("❌ Unable to generate the JSON payload. Check the bot logs for details.")

        # Register commands
        self._stock_cmd = self.command(name='stock', aliases=['s'])(stock_cmd)
        self._today_cmd = self.command(name='today')(today_cmd)
        self._today_json_cmd = self.command(name='today_json')(today_json_cmd)

    def attach_scheduler(self, scheduler) -> None:
        """Attach a scheduler instance to be started when bot is ready."""
        self._scheduler = scheduler

    async def on_ready(self):
        """Bot is ready - start scheduler."""
        self.logger.info(f"Logged in as {self.user}")
        self.logger.info(f"Bot is ready! Commands available: {list(self.commands)}")

        if self._scheduler:
            self._scheduler.start()

    async def on_message(self, message: discord.Message):
        """Handle incoming Discord messages."""
        # Ignore bot's own messages
        if message.author == self.user:
            return

        # Process commands
        await self.process_commands(message)
