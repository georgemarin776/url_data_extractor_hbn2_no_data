import requests

def get_shopify_json(url):
    try:
        r = requests.get(url, timeout=1)
    except:
        return None
    if r.status_code != 200:
        return None
    # try return json, otherwise return None
    try:
        return r.json()
    except:
        return None
