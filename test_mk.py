import routeros_api
import config

print(f"--- TENTATIVO CONNESSIONE SSL (Porta {config.MK_PORT}) ---")

try:
    connection = routeros_api.RouterOsApiPool(
        config.MK_HOST,
        username=config.MK_USER,
        password=config.MK_PASS,
        port=config.MK_PORT,
        use_ssl=config.MK_USE_SSL,
        ssl_verify=config.MK_SSL_VERIFY,
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