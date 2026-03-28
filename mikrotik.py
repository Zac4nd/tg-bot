import routeros_api
import logging
import config

def get_api_pool():
    return routeros_api.RouterOsApiPool(
        config.MK_HOST, username=config.MK_USER, password=config.MK_PASS, plaintext_login=True
    )

def get_system_report():
    try:
        connection = get_api_pool()
        api = connection.get_api()
        
        # Risorse, Temp, Dischi, Container (tutta la tua logica originale)
        res = api.get_resource('/system/resource').get()[0]
        health = api.get_resource('/system/health').get()
        temp = next((i.get('value') for i in health if "temp" in i.get('name', '').lower()), "--")
        
        disks = api.get_resource('/disk').get()
        usb_ok = any("usb-esterna" in d.get('slot', '') and d.get('mounted') == 'true' for d in disks)
        
        conts = api.get_resource('/container').get()
        c_status = []
        for c in conts:
            name = c.get('comment') or c.get('name') or f"ID-{c.get('.id')}"
            icon = "🟢" if c.get('running') == 'true' else "🔴"
            c_status.append(f"{icon} {name}")
            
        connection.disconnect()
        return {
            "cpu": res.get('cpu-load'),
            "ram": int(res.get('free-memory')) // 1048576,
            "temp": temp,
            "disk": "✅ Montato" if usb_ok else "❌ SCOLLEGATO",
            "conts": "\n".join(c_status)
        }
    except Exception as e:
        logging.error(f"Errore MikroTik API: {e}")
        return None

def run_fix_script():
    try:
        connection = get_api_pool()
        api = connection.get_api()
        api.get_binary_resource('/system/script').call('run', {'number': 'check-containers-auto'})
        connection.disconnect()
        return True
    except Exception as e:
        logging.error(f"Errore script fix: {e}")
        return False