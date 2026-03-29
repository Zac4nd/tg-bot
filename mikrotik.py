import routeros_api
import logging
import config

def get_api_pool():
    # Qui aggiungiamo i parametri fondamentali per la connessione sicura al RB5009
    return routeros_api.RouterOsApiPool(
        config.MK_HOST, 
        username=config.MK_USER, 
        password=config.MK_PASS, 
        port=8729,            # Forza la porta SSL
        use_ssl=True,         # Attiva la crittografia
        ssl_verify=False,     # Ignora il certificato auto-firmato (come nel test)
        plaintext_login=True  # Fondamentale per RouterOS v7
    )

def get_system_report():
    connection = None
    try:
        connection = get_api_pool()
        api = connection.get_api()
        
        # --- RISORSE DI SISTEMA ---
        res = api.get_resource('/system/resource').get()[0]
        
        # --- SALUTE E TEMPERATURE ---
        # RouterOS v7 a volte cambia il percorso della temperatura, 
        # cerchiamo sia in health che altrove se necessario
        health = api.get_resource('/system/health').get()
        temp = "--"
        for i in health:
            name = i.get('name', '').lower()
            if "temperature" in name or "temp" in name:
                temp = i.get('value')
                break
        
        # --- DISCHI (USB ESTERNA) ---
        disks = api.get_resource('/disk').get()
        # Verifichiamo se l'USB è montata correttamente
        usb_ok = any(("usb" in d.get('slot', '').lower() or "disk" in d.get('name', '').lower()) 
                     and d.get('disabled') == 'false' for d in disks)
        
        # --- STATO CONTAINERS ---
        conts = api.get_resource('/container').get()
        c_status = []
        for c in conts:
            # Nome: Usiamo 'comment' (es. PiHole, ClientTorrent)
            name = c.get('comment') or c.get('name') or f"ID-{c.get('.id')}"
            
            # Stato: Se 'running' esiste ed è 'true' (stringa) o True (booleano)
            is_running = str(c.get('running', '')).lower() == 'true'
            
            icon = "🟢" if is_running else "🔴"
            c_status.append(f"{icon} {name}")
            
        if not c_status:
            c_status = ["ℹ️ Nessun container configurato"]
            
        return {
            "cpu": res.get('cpu-load'),
            "ram": int(res.get('free-memory')) // 1048576, # Conversione in MB
            "temp": temp,
            "disk": "✅ Montato" if usb_ok else "❌ SCOLLEGATO",
            "conts": "\n".join(c_status)
        }
    except Exception as e:
        logging.error(f"Errore MikroTik API (Report): {e}")
        return None
    finally:
        if connection:
            connection.disconnect()

def run_fix_script():
    connection = None
    try:
        connection = get_api_pool()
        api = connection.get_api()
        resource = api.get_binary_resource('/system/script')
        # Esecuzione in sequenza degli script di monitoraggio richiesti
        resource.call('run', {'number': 'monitor-disk'})
        resource.call('run', {'number': 'monitor-containers'})
        return True
    except Exception as e:
        logging.error(f"Errore script fix: {e}")
        return False
    finally:
        if connection:
            connection.disconnect()