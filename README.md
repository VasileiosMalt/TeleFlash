# TeleFlash
## ⚡ Telegram News Scraper & Summarizer

![teleflash-logo](teleflash-logo.png)

Simple tool to fetch Telegram channel posts, save to PostgreSQL, pick Finland-related items, summarize with OpenAI, and post to Slack.

## 🔥 Features
- 📥 Daily fetch of channel info & posts  
- 🗄️ Store data with SQLAlchemy/PostgreSQL  
- 🔍 Regex filter for Finland keywords  
- 🤖 AI summaries in English & Finnish  
- 💬 Post reports to Slack  
- ⏰ Scheduler runs daily at 06:00  

## ⚙️ Installation
1. git clone …  
2. copy `teleflash-logo.png` to repo root  
3. `cp .env.example .env` & fill in creds  
4. `pip install -r requirements.txt`  

## 🛠️ Configuration
In `.env`:
```
API_ID=…
API_HASH=…
PHONE=…
SESSION_FILE=session.session
DB_USER=…
DB_PASSWORD=…
DB_HOST=…
DB_NAME=…
OPENAI_API_KEY=…
SLACK_BOT_TOKEN=…
SLACK_CHANNEL_ID=…
```

## 🚀 Usage
- `channel_content.py` – scrape channels & save to DB  
- `teleflash.py` – filter, summarize & post to Slack  
- `scheduler.py` – run both daily at 06:00  

Run manually:
```
python channel_content.py
python teleflash.py
```

Or start scheduler:
```
python scheduler.py
```

## 📁 File Overview
- init.py – Telethon setup & helpers  
- channel_content.py – scrape & save posts  
- teleflash.py – filter, summarize & Slack  
- scheduler.py – daily runner  
- models.py – ORM models  
- requirements.txt – deps  

## 🤝 Funded by Media-alan tutkimussäätiö

## 👥 Team
- Vasileios Maltezos ‹vasileios.maltezos@helsinki.fi›  
- Roman Kyrychenko ‹roman.kyrychenko@helsinki.fi›  
- Aleksi Knuutila ‹aleksi.knuutila@helsinki.fi›  
