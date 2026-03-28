from transmission_rpc import Client
import config

def get_client():
    try:
        return Client(host=config.TR_HOST, port=9091)
    except:
        return None

def add_magnet(link):
    client = get_client()
    if client:
        client.add_torrent(link)
        return True
    return False