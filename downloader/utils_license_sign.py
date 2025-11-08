import os
import base64
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def load_private_key():
    """Carga la clave privada desde el archivo secreto"""
    # ⬇️ ¡Asegúrate de que esta línea es correcta!
    private_key_path = settings.LICENSE_PRIVATE_KEY_PATH
    
    if not os.path.exists(private_key_path):
        # Esto debería lanzar un error si Render no montó el archivo.
        raise FileNotFoundError(f"Private key not found at {private_key_path}")

    with open(private_key_path, "rb") as key_file:
        private_key_data = key_file.read()
        return serialization.load_pem_private_key(
            private_key_data,
            password=None,
        )


def sign_license_payload(payload: dict) -> str:
    """Firma digitalmente un diccionario JSON (licencia) con la clave privada"""
    private_key = load_private_key()
    payload_json = json.dumps(payload, sort_keys=True).encode("utf-8")

    signature = private_key.sign(
        payload_json,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    signed_data = {
        "payload": payload,
        "signature": base64.b64encode(signature).decode("utf-8"),
    }

    return base64.b64encode(json.dumps(signed_data).encode("utf-8")).decode("utf-8")


def verify_license_signature(public_key_path: str, signed_license: str) -> bool:
    """Verifica una licencia firmada usando la clave pública"""
    signed_data = json.loads(base64.b64decode(signed_license.encode("utf-8")))
    payload = signed_data["payload"]
    signature = base64.b64decode(signed_data["signature"])

    with open(public_key_path, "rb") as key_file:
        public_key_data = key_file.read()
        public_key = serialization.load_pem_public_key(public_key_data)

    payload_json = json.dumps(payload, sort_keys=True).encode("utf-8")

    try:
        public_key.verify(
            signature,
            payload_json,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
