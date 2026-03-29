import os
from dotenv import load_dotenv

# Forza il caricamento del file .env dalla cartella corrente
load_dotenv()

# --- TELEGRAM ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
# Puliamo la whitelist: rimuove spazi e converte in numeri interi
raw_whitelist = os.getenv("TELEGRAM_WHITELIST", "")
WHITELIST = [int(x.strip()) for x in raw_whitelist.split(",") if x.strip()]

# --- MIKROTIK ---
MK_HOST = os.getenv("MK_HOST")
MK_USER = os.getenv("MK_USER")
MK_PASS = os.getenv("MK_PASS")
MK_PORT = int(os.getenv("MK_PORT"))
MK_USE_SSL = os.getenv("MK_USE_SSL", "True").lower() == "true"
MK_SSL_VERIFY = os.getenv("MK_SSL_VERIFY", "False").lower() == "true"

# --- TRANSMISSION ---
TR_HOST = os.getenv("TR_HOST")
TR_PORT = int(os.getenv("TR_PORT", 9091))