# Discord Finance Bot

A Python Discord bot for daily market summaries, stock charts, earnings, IPOs, sector data, and prediction-market signals.

The bot can run against live providers, but it also includes a credential-free demo so the message pipeline can be inspected without a Discord token, API keys, or browser automation.

## What works

- `!stock AAPL` or `!s AAPL 3mo` — fetch a Yahoo Finance chart and summary.
- `!today` — generate a Markdown daily market summary.
- `!today_json` — return the structured summary payload.
- Scheduled daily summaries through the Discord bot scheduler.
- Provider adapters for Yahoo Finance, Alpha Vantage, Polymarket, and sector scraping.

Live provider coverage depends on credentials, provider availability, and the local Playwright browser installation. Missing data is returned as an empty section rather than invented values.

## Run the offline demo

The demo uses fixture data and makes no network calls:

```bash
cd discord_finance_bot
python demo.py
```

It prints the same Markdown summary shape used by the `!today` command.

## Run the bot

```bash
cd discord_finance_bot
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Set the required environment variables before starting:

```bash
export DISCORD_TOKEN="your-discord-bot-token"
export DISCORD_CHANNEL_ID="123456789012345678"
export SELECTED_STOCKS="AAPL,MSFT,GOOGL"
export TIMEZONE="America/New_York"
export ALPHAVANTAGE_API_KEY="optional-api-key"
python main.py
```

Keep tokens and API keys in environment variables. Never commit `.env` files or credentials.

## Test

```bash
cd discord_finance_bot
python -m pytest tests -q
```

The tests mock external providers. The offline demo is the fastest smoke test for the user-visible summary format.

## Architecture

```text
Discord commands / scheduler
            ↓
      MessageService
            ↓
  provider repositories/services
            ↓
 Yahoo Finance · Alpha Vantage · Polymarket · sector data
```

This project is for research and automation. It does not provide investment advice or recommendations to buy or sell securities.
