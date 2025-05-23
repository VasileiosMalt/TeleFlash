<p align="center">
  <img src="teleflash-logo.png" alt="TeleFlash Logo" width="300">
</p>

<p align="center">
  <strong>A Telegram News Scraper & Summarizer (Functioning Prototype)</strong><br>
  Monitor specific channels and fetch Telegram channel posts, store them in PostgreSQL, identify Finland-related content, summarize with OpenAI, and share results on Slack.
</p>

---

## ⚡ Features

- **📥 Automatic Daily Fetch**: Scrapes channel info and posts every morning at 06:00.
- **🗄️ Robust Storage**: Saves data securely using SQLAlchemy and PostgreSQL.
- **🇫🇮 Smart Detection**: Identifies posts mentioning Finland using keywords in English, Russian, and Ukrainian (e.g., "Finland", "Suomi", "Финляндия", ...).
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

## 📢 Current List of Channels

The scraper currently monitors **the following Telegram channels** (usernames):

<details>
<summary>Click to expand</summary>

`severnygorod`, `agapov_fi`, `karaulny`, `rusbrief`, `octgnews`, `tass_agency`, `baltnews`, `fontankaspb`, `dprunews`, `sp_1703`, `glavmedia`, `houseofcardseurope`, `good78news`, `rian_ru`, `belta_telegramm`, `radiogovoritmsk`, `bbbreaking`, `paperpaper_ru`, `nevnov`, `swodki`, `vzglyad_ru`, `parstodayrussian`, `ukraina_ru`, `solovievlive`, `rossiyaneevropa`, `online47news`, `riafan`, `radiomirby`, `dirtytatarstan`, `rgrunews`, `inosmichannel`, `sputnikby`, `rbc_news`, `ssigny`, `boyart777`, `lentadnya`, `radiosvoboda`, `kommersant`, `topspb_tv`, `allnews47`, `rt_russian`, `absatzmedia`, `match_tv`, `truekpru`, `bbcrussian`, `houseofcardsrussia`, `OdessaRussi`, `Novoeizdanie`, `rus_demiurge`, `stranaua`, `rbc_brief`, `aifonline`, `ostashkonews`, `dimsmirnov175`, `ateobreaking`, `infantmilitario`, `UAnotRU`, `smotri_media`, `thehandofthekremlin`, `leningrad_guide`, `izvestia`, `meduzalive`, `highlylikely20`, `rentv_news`, `znua_live`, `atn_btrc`, `vestiru24`, `chvkmedia`, `espresotb`, `kshulika`, `orientsouthrus`, `dwglavnoe`, `ZOVcrimea`, `Belarus_VPO`, `readovkanews`, `ranarod`, `gazetaru`, `nexta_live`, `ntvnews`, `uniannet`, `lady_north`, `fuckyouthatswhy`, `nstarikovru`, `new_militarycolumnist`, `mk_ru`, `lab365`, `go338`, `postovo`, `asphaltt`, `politkraina`, `rlz_the_kraken`, `ru2ch`, `bfmnews`, `russtrat`, `tv360`, `radio_sputnik`, `minut30`, `pluanews`, `rtvinews`, `interfaxonline`, `istorijaoruzijaz`, `currenttime`, `sputniklive`, `newsgrpua`, `srochnow`, `ukrpravda_news`, `first_political`, `oldlentach`, `RUSanctions`, `Pravda_Gerashchenko`, `warhistoryalconafter`, `ivan_utenkov13`, `TCH_channel`, `the_moscow_post`, `UkraineNow`, `openukraine`, `ukr_shvydko`, `lentachold`, `huyovy_kharkiv`, `kontext_channel`, `russica2`, `tvrain`, `operativnozsu`, `rus_now_news`, `voynareal`, `lachentyt`, `russianonwars`, `dmytrogordon_official`, `banksta`, `TolkoPoDely`, `rybar`, `rhymestg`, `ragnarockkyiv`, `ukraina24tv`, `bankrollo`, `truexanewsua`, `sheyhtamir1974`, `aleksandrsemchenko`, `tsaplienko`, `varlamov_news`, `DavydovIn`, `boris_rozhin`, `RVvoenkor`, `redacted6`, `zerkalo_io`, `voenacher`, `Mikle1On`, `UaOnlii`, `vchkogpu`, `kaktovottak`, `novosti_efir`, `shot_shot`, `insiderUKR`, `slavaded1337`, `bloodysx`, `breakingmash`, `readovkaru`, `ostorozhno_novosti`, `okoo_ukr`, `Cbpub`, `warfakes`, `montyan2`, `moscowmap`, `asupersharij`, `nevzorovtv`, `V_Zelenskiy_official`, `yurasumy`

</details>

---

### ✏️ How to Change This List

1. **Open `channel_content.py` and `teleflash.py`:**
   - The channel list is defined as a Python list named `channels` or `channels_list` near the top of each file.

2. **Edit the List:**  
   - Add or remove channel usernames as needed – just like editing a Python array.
   - Example:
     ```
     channels = [
         'severnygorod', 'agapov_fi', 'karaulny',  # etc.
         # 'channel_to_remove',
         'some_new_channel'
     ]
     ```

3. **Save and Restart:**  
   - Save your changes.
   - The next time you run the scripts (or the daily scheduler runs), your updated channel list will be used!

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
| **Roman Kyrychenko**   | [GitHub account](https://github.com/RomanKyrychenko)     |
| **Aleksi Knuutila**    | [GitHub account](https://github.com/AleksiKnuutila)       |
