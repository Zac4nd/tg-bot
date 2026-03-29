import routeros_api
import config # Usiamo le tue credenziali del .env

def check_raw_containers():
    print(f"--- DEBUG RAW CONTAINERS (SSL 8729) ---")
    connection = None
    try:
        connection = routeros_api.RouterOsApiPool(
            config.MK_HOST,
            username=config.MK_USER,
            password=config.MK_PASS,
            port=config.MK_PORT,
            use_ssl=config.MK_SSL,
            ssl_verify=False,
            plaintext_login=True
        )
        api = connection.get_api()
        conts = api.get_resource('/container').get()
        
        if not conts:
            print("ℹ️ Nessun container trovato.")
            return

        for i, c in enumerate(conts):
            print(f"\n📦 CONTAINER #{i} DATI COMPLETI:")
            for key, value in c.items():
                print(f"   {key}: {value}")
            print("-" * 30)

    except Exception as e:
        print(f"❌ Errore durante il debug: {e}")
    finally:
        if connection:
            connection.disconnect()

if __name__ == "__main__":
    check_raw_containers()