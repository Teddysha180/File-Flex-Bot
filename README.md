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
DATABASE_URL=your-postgres-connection-string
DATA_DIR=./data
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

This repo is configured for a Docker-based Render deploy so system tools are available in production.

Included in the container:
- LibreOffice
- Ghostscript

That means these conversions can run on Render:
- Word -> PDF
- PowerPoint -> PDF
- Excel -> PDF
- HTML -> PDF
- PDF -> PDF/A

Recommended setup:
- Create a new Web Service from the GitHub repo
- Render will detect [render.yaml](./render.yaml)
- Set `BOT_TOKEN` in the Render dashboard
- Let Render build from the included [Dockerfile](./Dockerfile)

Persistence for admin-created stores:
- Shared file bundles are saved as Telegram `file_id` records in the database
- The included [render.yaml](./render.yaml) now provisions both:
- A Render Postgres database for permanent metadata storage
- A Render persistent disk mounted at `/data` for SQLite fallback and bot working data
- `REQUIRE_PERSISTENT_STORAGE=true` is enabled on Render so the bot won't silently run with ephemeral storage

Recommended production mode:
- Use `DATABASE_URL` from Render Postgres for the main persistent storage
- Keep `DATA_DIR=/data` so temporary files and any SQLite fallback live on the mounted disk instead of the app filesystem

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
- Docker deployment includes LibreOffice and Ghostscript for the Office/PDF conversions above
- Admin-created share links are durable when `DATABASE_URL` points to Postgres or when `DATA_DIR` is on a persistent disk

Redeploy verification note:
- If `System Status` shows `Storage location: /data/bot_database.db` and `Persistent storage: yes`, newly created shared bundles should survive future redeploys.
