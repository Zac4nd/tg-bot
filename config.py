from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WHITELIST = [int(i) for i in os.getenv("WHITELIST", "").split(",")]
MK_HOST = os.getenv("MK_HOST", "172.16.0.1")
MK_USER = os.getenv("MK_USER", "tg-bot")
MK_PASS = os.getenv("MK_PASS")
TR_HOST = os.getenv("TR_HOST", "transmission")
DB_FILE = "/app/notified_torrents.json"