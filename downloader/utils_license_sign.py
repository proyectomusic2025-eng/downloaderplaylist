import os
from cryptography.hazmat.primitives import serialization

def load_private_key():
    private_key_path = os.getenv("LICENSE_PRIVATE_KEY_PATH", "/etc/secrets/license_private.pem")
    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Private key not found at {private_key_path}")

    with open(private_key_path, "rb") as key_file:
        private_key_data = key_file.read()
        return serialization.load_pem_private_key(
            private_key_data,
            password=None,
        )
