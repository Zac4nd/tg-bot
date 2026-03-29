import routeros_api

# Parametri definiti
host = "192.168.88.1"
user = "tg-bot"
password = "5gTuau8hZXksT0gQx4Fa"

print(f"--- TENTATIVO CONNESSIONE SSL (Porta 8729) ---")

try:
    connection = routeros_api.RouterOsApiPool(
        host,
        username=user,
        password=password,
        port=8729,
        use_ssl=True,
        ssl_verify=False,    # Obbligatorio: il tuo PC non conosce la "myCA" del router
        plaintext_login=True # Obbligatorio per RouterOS v7 / RB5009
    )
    api = connection.get_api()
    print("✅ BOOM! Connesso in SSL con successo!")
    
    # Prova di lettura
    res = api.get_resource('/system/identity').get()
    print(f"🤖 Risposta dal router: {res[0]['name']}")
    
    connection.disconnect()
except Exception as e:
    print(f"❌ Errore: {e}")