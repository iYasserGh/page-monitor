# Page Monitor

Simple website change monitor.
It checks a page on a schedule, compares content hashes, and sends Telegram screenshots when a change is detected.

## Requirements

- Python 3.11+
- Google Chrome/Chromium installed
- Telegram bot token and chat ID

## Setup

Create a `.env` file in the project root with the following content:

```env
BOT_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
URL_TO_MONITOR=your_url_to_monitor_here
CHECK_INTERVAL=60  # Time in seconds between checks
RISK_MODE=False  # Set to True to disable random sleep (may increase risk of IP blocking)
```

then, You have two ways to set up and run the monitor:

### Simple way

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the monitor:

```bash
python3 monitor.py
```

### Docker way

Build and run the Docker container:

```bash
docker build -t page-monitor .
docker run --rm \
	-e BOT_TOKEN="$BOT_TOKEN" \
	-e CHAT_ID="$CHAT_ID" \
	-e URL_TO_MONITOR="$URL_TO_MONITOR" \
	-e CHECK_INTERVAL="300" \
	-e RISK_MODE="False" \
	page-monitor
```
