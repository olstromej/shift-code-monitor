# 🎮 Shift Code Monitor


Never miss a SHiFT code or Golden Key! Monitor Twitter accounts and automatically post new codes to Discord.

---

## 🚀 Features

- Monitors multiple Twitter accounts:  
  - `GearboxOfficial`, `Borderlands`, `BorderlandsGame`, `ShiftCodesTK`, `DuvalMagic`
- Detects keywords: `"shift code"`, `"golden key"`, `"redeem code"`
- Sends detected codes to **Discord** automatically via webhooks
- Keeps a **log of seen tweets** to avoid duplicates
- Can run **locally** or via **GitHub Actions**
- Gracefully handles **Twitter API rate limits**

---

## 🖥️ Demo

**Example Discord notification:**  

![Discord Demo](docs/discord_demo.png)  
*(Replace with your actual screenshot if you want)*

---

## 🛠️ Setup

1. **Clone the repo:**

```bash
git clone https://github.com/yourusername/shift-code-monitor.git
cd shift-code-monitor


TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
DISCORD_WEBHOOK_URL=your_discord_webhook_here


python3 -m pip install --upgrade pip
pip install tweepy requests python-dotenv



python3 twitter_shift_scraper.py


⏰ GitHub Actions

Run daily at 8 AM EST with .github/workflows/monitor.yml

Saves seen tweets and logs as GitHub artifacts

⚡ Notes

Rate Limits: Free Twitter API has limited requests per 15-min window

Custom Accounts: Edit ACCOUNTS in twitter_shift_scraper.py

Keyword Matching: Case-insensitive, configurable in KEYWORDS


🖖 Contributing

Add new accounts

Enhance keyword detection

Improve logging or notifications




