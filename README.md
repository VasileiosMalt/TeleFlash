<h1 align="center">TeleFlash</h1>

<p align="center">
  <img src="teleflash-logo.png" alt="TeleFlash Logo" width="140">
</p>

## ⚡ Telegram News Scraper & Summarizer

Simple tool to fetch Telegram channel posts, save to PostgreSQL, find Finland-related items, summarize with OpenAI, and post results to Slack.

---

## 🔥 Features

- 📥 **Automatic Daily Fetch:** Collects channel info and latest posts every morning.
- 🗄️ **Robust Storage:** Saves all data using SQLAlchemy and PostgreSQL.
- 🇫🇮 **Smart Finland-topic Detection:** Finds posts mentioning Finland by searching for keywords and place names in English, Russian, and Ukrainian (e.g. "Finland", "Suomi", "Финляндия", etc).
- 🤖 **AI Summaries:** Uses OpenAI to summarize findings in both English and Finnish.
- 💬 **Slack Reporting:** Posts structured summaries and message stats to Slack.
- ⏰ **Hands-free Operation:** Scheduler runs the process automatically every day at 06:00.

---

## ⚙️ Installation

1. Clone this repository  
2. Create a `.env` file and add your credentials (see below)  
3. Install dependencies:  
pip install -r requirements.txt

text

---

## 🛠️ Configuration

Create a `.env` file with the following variables:

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

text

---

## 🚀 Usage

- `channel_content.py` – Scrape Telegram channels and save posts to the database  
- `teleflash.py` – Filter, summarize Finland-related messages & post summaries to Slack  
- `scheduler.py` – Runs both scripts every day at 06:00  

**To run manually:**
python channel_content.py
python teleflash.py

text

**Or start the automatic scheduler:**
python scheduler.py

text

---

## 📁 File Overview

- `init.py` – Telethon connection & helpers  
- `channel_content.py` – Scraping and DB save logic  
- `teleflash.py` – Filtering, summarizing, and posting to Slack  
- `scheduler.py` – Daily runner script  
- `models.py` – SQLAlchemy ORM models  
- `requirements.txt` – Dependencies

---

## 🤝 Funded by Media-alan tutkimussäätiö

---

## 👥 Our Team

<table>
  <tr>
    <td align="center"><b>Vasileios Maltezos</b><br>
      <a href="mailto:vasileios.maltezos@helsinki.fi">vasileios.maltezos@helsinki.fi</a>
    </td>
  </tr>
  <tr>
    <td align="center"><b>Roman Kyrychenko</b><br>
      <a href="mailto:roman.kyrychenko@helsinki.fi">roman.kyrychenko@helsinki.fi</a>
    </td>
  </tr>
  <tr>
    <td align="center"><b>Aleksi Knuutila</b><br>
      <a href="mailto:aleksi.knuutila@helsinki.fi">aleksi.knuutila@helsinki.fi</a>
    </td>
  </tr>
</table>
