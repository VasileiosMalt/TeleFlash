# TeleFlash

<p align="center">
  <img src="teleflash-logo.png" alt="TeleFlash Logo" width="400">
</p>

<p align="center">
  <strong>A Telegram News Scraper & Summarizer</strong><br>
  Fetch Telegram channel posts, store them in PostgreSQL, identify Finland-related content, summarize with OpenAI, and share results on Slack.
</p>

---

## ⚡ Features

- **📥 Automatic Daily Fetch**: Scrapes channel info and posts every morning at 06:00.
- **🗄️ Robust Storage**: Saves data securely using SQLAlchemy and PostgreSQL.
- **🇫🇮 Smart Finland Detection**: Identifies posts mentioning Finland using keywords in English, Russian, and Ukrainian (e.g., "Finland", "Suomi", "Финляндия", ...).
- **🤖 AI-Powered Summaries**: Generates summaries in English and Finnish using OpenAI.
- **💬 Slack Integration**: Posts structured summaries and message statistics to Slack.
- **⏰ Hands-Free Operation**: Scheduler automates the process daily.

---

## ⚙️ Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd teleflash
   ```

2. **Set Up Environment**:
   Create a `.env` file in the project root with the following variables:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   PHONE=your_phone_number
   SESSION_FILE=session.session
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_NAME=your_db_name
   OPENAI_API_KEY=your_openai_api_key
   SLACK_BOT_TOKEN=your_slack_bot_token
   SLACK_CHANNEL_ID=your_slack_channel_id
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

### Scripts
- **`channel_content.py`**: Scrapes Telegram channels and stores posts in the database.
- **`teleflash.py`**: Filters Finland-related posts, summarizes them, and posts to Slack.
- **`scheduler.py`**: Runs both scripts daily at 06:00.

### Manual Execution
Run the scripts individually:
```bash
python channel_content.py
python teleflash.py
```

### Automatic Execution
Start the scheduler for automated daily runs:
```bash
python scheduler.py
```

---

## 📁 File Overview

| File                  | Description                              |
|-----------------------|------------------------------------------|
| `init.py`             | Telethon connection and helper functions |
| `channel_content.py`  | Logic for scraping and saving to DB      |
| `teleflash.py`        | Filtering, summarizing, and Slack posting|
| `scheduler.py`        | Daily automation script                  |
| `models.py`           | SQLAlchemy ORM models                    |
| `requirements.txt`    | Project dependencies                     |

---

## 🤝 Funding

This project is proudly funded by **Media-alan tutkimussäätiö**.

---

## 👥 Our Team

| Name                  | Contact                                  |
|-----------------------|------------------------------------------|
| **Vasileios Maltezos** | [vasileios.maltezos@helsinki.fi](mailto:vasileios.maltezos@helsinki.fi) |
| **Roman Kyrychenko**   | [roman.kyrychenko@helsinki.fi](mailto:roman.kyrychenko@helsinki.fi)     |
| **Aleksi Knuutila**    | [aleksi.knuutila@helsinki.fi](mailto:aleksi.knuutila@helsinki.fi)       |
