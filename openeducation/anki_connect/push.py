import requests

ANKI_CONNECT_URL = "http://localhost:8765"


def request(action: str, **params) -> dict:
    payload = {"action": action, "version": 6, "params": params}
    r = requests.post(ANKI_CONNECT_URL, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def import_package(path: str) -> dict:
    return request("importPackage", path=path)
