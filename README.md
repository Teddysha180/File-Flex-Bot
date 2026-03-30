# File Flex Bot

Simple Telegram file tools bot built with Python and `python-telegram-bot`.

## Main Tools

- Extract ZIP
- Compress Image
- Convert Files
- Rename File
- Merge PDF
- Split PDF

## Convert Files

- JPG -> PDF
- Word -> PDF
- PowerPoint -> PDF
- Excel -> PDF
- HTML -> PDF
- PDF -> JPG
- PDF -> Word
- PDF -> PowerPoint
- PDF -> Excel
- PDF -> PDF/A
- JPG -> PNG
- PNG -> JPG

## Local Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create `.env` from `.env.example` and set:

```env
BOT_TOKEN=your-telegram-bot-token
```

3. Start the bot:

```bash
python bot.py
```

## GitHub

1. Create a new GitHub repository.
2. In the project folder run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Render

This repo now includes [render.yaml](./render.yaml) so Render can deploy it directly from GitHub.

Recommended setup:
- Create a new Web Service from the GitHub repo
- Render will detect `render.yaml`
- Set `BOT_TOKEN` in Render dashboard

Render commands:
- Build: `pip install -r requirements.txt`
- Start: `python bot.py`

The bot also starts a tiny health endpoint on Render using the `PORT` environment variable:
- `/`
- `/health`
- `/healthz`

## UptimeRobot

Because the bot now exposes a health URL on Render, you can monitor it with UptimeRobot.

Recommended monitor:
- Type: `HTTP(s)`
- URL: `https://YOUR-RENDER-SERVICE.onrender.com/healthz`
- Interval: your preferred interval

## Notes

- Files are stored temporarily in `downloads/` and cleaned up after processing
- Polling is used, so no Telegram webhook setup is required
- Some conversions still depend on local system tools:
  - LibreOffice for Office -> PDF
  - Ghostscript for PDF -> PDF/A
