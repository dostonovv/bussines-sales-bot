# 🤖 Telegram Business Bot

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) 
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange?logo=telegram&logoColor=white) 
![Build](https://img.shields.io/badge/Build-Passing-brightgreen) 
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white) 
![License](https://img.shields.io/badge/License-Proprietary-red)

> A **modular, production-ready** Telegram bot built for real businesses.  
> Designed with **scalability, maintainability, and authorship protection** in mind.  

---

## ✨ Demo

<p align="center">
  <img src="assets/demo.gif" alt="Bot Demo" width="500"/>
</p>

*(Optional: Add GIF or screenshot from your bot in action)*

---

## 🚀 Features

- 🛍 **Product catalog** with category navigation  
- 📦 **Order creation** with FSM-based workflows  
- 📞 Phone number capture via **contact request**  
- 🧑‍💼 **Admin panel** with product management  
- 🧾 Order tracking & cancellation  
- 🔐 **Authorship protection** with hidden `/creator` command  
- 📢 Broadcast-ready structure for future marketing  
- 🧠 **Clean architecture** powered by SQLAlchemy ORM  
- 🧩 Rich UX with inline & reply keyboards  

---

## 🧠 Tech Stack

| Layer        | Technology        |
|--------------|-------------------|
| Bot Engine   | [Aiogram 3.x](https://docs.aiogram.dev/) |
| Database     | PostgreSQL / SQLite (SQLAlchemy ORM) |
| FSM          | Aiogram FSMContext |
| Deployment   | Python 3.11+, Docker-ready |
| Structure    | Modular routers, states, keyboards |

---

## 📁 Project Structure

kaibot/
├── database/
│ ├── models.py
│ ├── db.py
├── handlers/
│ ├── user.py
│ ├── admin.py
├── keyboards/
│ ├── user_kb.py
│ ├── inline_kb.py
├── states/
│ ├── phone_states.py
├── utils/
│ ├── creator.py
├── main.py
└── config.py

yaml
Копировать код

---

## 🔐 Authorship Protection

This bot includes a **hidden `/creator` command** that always displays the original developer’s name, regardless of code edits.  

> 👨‍💻 Built by **Dostonov Zoirjon**  
> 🧬 Code signature embedded via `utils/creator.py`

---

## 🛠 Setup Instructions

1. Clone the repo  
   ```bash
   git clone https://github.com/yourusername/kaibot.git
   cd kaibot
Install dependencies

bash
Копировать код
pip install -r requirements.txt
Configure .env or config.py

env
Копировать код
BOT_TOKEN=your_token_here
DATABASE_URL=sqlite+aiosqlite:///bot.db
ADMIN_IDS=123456789
Run the bot

bash
Копировать код
python main.py
👨‍💻 Contribution
Want to improve this bot? Follow these steps:

Fork the repo

Create your feature branch: git checkout -b feature/amazing-feature

Commit changes: git commit -m 'Add amazing feature'

Push to branch: git push origin feature/amazing-feature

Create a Pull Request

📬 Contact
For business inquiries or support:

Telegram: @zoirjon_dev

Email: yourname@example.com

🧠 License
This project is proprietary.
Redistribution or modification without explicit permission is prohibited.

<p align="center"> Made with ❤️ by <b>Dostonov Zoirjon</b> </p> ```
