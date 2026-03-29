from transmission_rpc import Client
import config

def get_client():
    try:
        return Client(host=config.TR_HOST, port=config.TR_PORT)
    except:
        return None

def add_magnet(link):
    client = get_client()
    if client:
        try:
            client.add_torrent(link)
            return True
        except Exception:
            return False
    return False

def get_torrents():
    client = get_client()
    if client:
        try:
            return client.get_torrents()
        except Exception:
            return []
    return None

def remove_torrent(torrent_id, delete_data=False):
    client = get_client()
    if client:
        try:
            client.remove_torrent(torrent_id, delete_data=delete_data)
            return True
        except Exception:
            return False
    return False