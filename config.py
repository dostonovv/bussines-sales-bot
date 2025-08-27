
import os
BOT_TOKEN = ""


DB_NAME = "database.sqlite3"


IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Admin ID (Telegram user_id)
ADMINS = [6585387011 , 5817141157]
