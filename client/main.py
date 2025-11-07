#!/usr/bin/env python3
import sys
from pathlib import Path
import json, base64, hashlib, platform, uuid, datetime
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
def load_public_key():
    data = Path(__file__).resolve().parent.joinpath('public.pem').read_bytes()
    return serialization.load_pem_public_key(data)
def verify_license(signed_license):
    try:
        payload_b64, sig_b64 = signed_license.split('.')
        payload = base64.b64decode(payload_b64)
        sig = base64.b64decode(sig_b64)
        pub = load_public_key()
        pub.verify(sig, payload, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        data = json.loads(payload.decode('utf-8'))
        return True, data
    except Exception as e:
        return False, str(e)
def get_hwid():
    mac = uuid.getnode()
    s = f"{mac}-{platform.system()}-{platform.machine()}"
    return hashlib.sha256(s.encode()).hexdigest()
def load_local_license():
    p = Path.home() / '.musicdown' / 'license.lic'
    if not p.exists():
        print('No license found. Please purchase at https://ko-fi.com/downloaderplaylist and follow instructions.')
        sys.exit(1)
    return p.read_text()
def main():
    signed = load_local_license()
    ok, info = verify_license(signed)
    if not ok:
        print('Invalid license:', info); sys.exit(1)
    # check hwid and expiry
    if info.get('expires_at'):
        exp = datetime.datetime.fromisoformat(info['expires_at'].replace('Z','+00:00')) if 'Z' in info['expires_at'] else datetime.datetime.fromisoformat(info['expires_at'])
        if datetime.datetime.utcnow() > exp.replace(tzinfo=None):
            print('License expired'); sys.exit(1)
    hwids = info.get('hwids') or []
    hwid = get_hwid()
    if hwids and hwid not in hwids:
        print('HWID mismatch'); sys.exit(1)
    print('License valid. Running app...')
    # TODO: invoke packaged downloader functionality
if __name__ == '__main__':
    main()
