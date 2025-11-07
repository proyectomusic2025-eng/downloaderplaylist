#!/usr/bin/env python3
import requests, sys
from pathlib import Path
def get_hwid():
    import uuid, platform, hashlib
    s = f"{uuid.getnode()}-{platform.system()}-{platform.machine()}"
    return hashlib.sha256(s.encode()).hexdigest()
def activate(server_url, key):
    hwid = get_hwid()
    r = requests.post(server_url + '/webhook/kofi/' if '/webhook/kofi/' in server_url else server_url + '/api/activate/', data={'key': key, 'hwid': hwid})
    if r.status_code == 200:
        license_str = r.json().get('license')
        p = Path.home() / '.musicdown'
        p.mkdir(parents=True, exist_ok=True)
        (p / 'license.lic').write_text(license_str)
        print('Activación exitosa. License guardada en', p / 'license.lic')
    else:
        print('Error:', r.status_code, r.text)
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: activate_cli.py <server_url> <key>')
        sys.exit(1)
    activate(sys.argv[1], sys.argv[2])
