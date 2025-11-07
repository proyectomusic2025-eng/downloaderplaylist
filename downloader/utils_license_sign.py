import json, base64, os
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
PRIVATE_KEY_PATH = os.environ.get('LICENSE_PRIVATE_KEY_PATH', '/run/secrets/license_private.pem')
def load_private_key():
    p = Path(PRIVATE_KEY_PATH)
    if not p.exists():
        raise FileNotFoundError(f'Private key not found at {PRIVATE_KEY_PATH} - generate it and set LICENSE_PRIVATE_KEY_PATH')
    data = p.read_bytes()
    return serialization.load_pem_private_key(data, password=None)
def sign_license_payload(payload_dict):
    payload_json = json.dumps(payload_dict, separators=(',',':')).encode('utf-8')
    priv = load_private_key()
    signature = priv.sign(
        payload_json,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return base64.b64encode(payload_json).decode() + '.' + base64.b64encode(signature).decode()
