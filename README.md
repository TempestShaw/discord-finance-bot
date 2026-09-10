<p align="center">
  <img src="assets/discord-finance-bot.png" alt="Discord Finance Bot logo" width="240">
</p>

<h1 align="center">Discord Finance Bot</h1>

<p align="center">Daily market summaries and stock research inside Discord.</p>

<p align="center">
  <a href="#offline-demo">Offline demo</a> ·
  <a href="#live-bot">Live bot</a> ·
  <a href="#architecture">Architecture</a>
</p>

Discord Finance Bot collects market data from provider adapters and turns it into Discord commands, Markdown summaries, JSON payloads, and scheduled messages. It supports Yahoo Finance charts, earnings, IPOs, sector data, and prediction-market signals.

## Start with the offline demo

Run the message pipeline with fixture data. No Discord token, API key, browser, or network call is required:

```bash
python discord_finance_bot/demo.py
```

The demo prints the same Markdown summary shape used by the live `!today` command.

## Why use it?

- **Inspect the output first.** The offline demo makes the user-visible summary reproducible.
- **Use one command surface.** `!stock`, `!today`, and `!today_json` expose charts, readable summaries, and structured data.
- **Keep providers replaceable.** External data access lives behind repository and service modules.
- **Keep unavailable data visible.** Provider failures produce empty sections or explicit errors instead of fabricated values.

## Live bot

Requires Python, the dependencies in `discord_finance_bot/requirements.txt`, and a Chromium installation for the browser-backed providers.

```bash
cd discord_finance_bot
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Set environment variables before starting:

```bash
export DISCORD_TOKEN="your-discord-bot-token"
export DISCORD_CHANNEL_ID="123456789012345678"
export SELECTED_STOCKS="AAPL,MSFT,GOOGL"
export TIMEZONE="America/New_York"
export ALPHAVANTAGE_API_KEY="optional-api-key"
python main.py
```

## Commands

| Command | Result |
| --- | --- |
| `!stock AAPL` | Fetch a stock chart and latest price summary. |
| `!s AAPL 3mo` | Same chart command with an explicit period. |
| `!today` | Generate a readable daily market summary. |
| `!today_json` | Return the structured summary payload. |

## What is included?

| Capability | Implementation |
| --- | --- |
| Stock charts | Yahoo Finance and `mplfinance` |
| Earnings and IPOs | Alpha Vantage adapter |
| Prediction-market data | Polymarket scraper |
| Sector data | Browser-backed sector provider |
| Scheduling | APScheduler |
| Discord delivery | `discord.py` embeds and file attachments |

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

## Test

```bash
cd discord_finance_bot
python -m pytest tests -q
```

The tests mock external providers. Keep tokens and API keys in environment variables; never commit `.env` files or credentials.

This project is for research and automation. It does not provide investment advice or recommendations to buy or sell securities.
