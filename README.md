<h1 align="center">TeleFlash</h1>

<p align="center">
  <img src="teleflash-logo.png" alt="TeleFlash Logo" width="160">
</p>

## ⚡ Telegram News Scraper & Summarizer

Simple tool to fetch Telegram channel posts, save to PostgreSQL, pick Finland-related items, summarize with OpenAI, and post to Slack.

---

## 🔥 Features

- 📥 Fetch channel info & posts daily
- 🗄️ Store data with SQLAlchemy & PostgreSQL
- 🇫🇮 **Smart Finland-topic search:** Finds messages about Finland by scanning for country names, place names, and related keywords in English, Russian, and Ukrainian
- 🤖 AI summaries in English & Finnish
- 💬 Post reports automatically to Slack
- ⏰ Scheduler runs daily at 06:00

---

## ⚙️ Installation

1. Clone this repo  
2. Create a `.env` file & fill in credentials (see below)  
3. `pip install -r requirements.txt`  

---

## 🛠️ Configuration

Add a `.env` file like this:

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

---

## 🚀 Usage

- `channel_content.py` – Scrape channels & save posts to DB  
- `teleflash.py` – Find Finland topics, summarize & post to Slack  
- `scheduler.py` – Run both scripts every day at 06:00  

**Manual run:**
```
python channel_content.py
python teleflash.py
```

**Or start the scheduler (recommended):**
```
python scheduler.py
```

---

## 📁 File Overview

- `init.py` – Telethon connection & helpers
- `channel_content.py` – Scrape & save posts
- `teleflash.py` – Filter, summarize & Slack
- `scheduler.py` – Daily runner
- `models.py` – Database models
- `requirements.txt` – Dependencies

---

## 🤝 Funded by Media-alan tutkimussäätiö


## 👥 Our Team

<table>
  <tr>
    <td><b>Vasileios Maltezos</b><br><a href="mailto:vasileios.maltezos@helsinki.fi">vasileios.maltezos@helsinki.fi</a></td>
  </tr>
  <tr>
    <td><b>Roman Kyrychenko</b><br><a href="mailto:roman.kyrychenko@helsinki.fi">roman.kyrychenko@helsinki.fi</a></td>
  </tr>
  <tr>
    <td><b>Aleksi Knuutila</b><br><a href="mailto:aleksi.knuutila@helsinki.fi">aleksi.knuutila@helsinki.fi</a></td>
  </tr>
</table>
