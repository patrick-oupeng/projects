import requests

'''
Use the tdx API to get metro data.
I actually don't think I need this since I can just hit the 'get station timetable' API
and get all the info downloaded once.
'''

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
BASE_URL = "https://tdx.transportdata.tw/api/basic/v2"
RAIL_SYSTEM = "TRTC" # Taipei

# uses id + secret 
def login(client_id, client_secret):
    # token lasts 86400 s; cache it. endpoint allows 20 calls/min.
    r = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",   # authenticates the app, not a user
        "client_id": client_id, "client_secret": client_secret})
    r.raise_for_status()
    return r.json()["access_token"]

def tdx_get(path, token, **params):
    params.setdefault("$format", "JSON")      # OData: also $filter, $select, $top
    r = requests.get(f"{BASE}/{path}", headers={"Authorization": f"Bearer {token}"}, params=params)
    r.raise_for_status()
    return r.json()


