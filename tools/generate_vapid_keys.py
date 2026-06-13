"""
Run once to generate VAPID keys.
Copy the output into Render environment variables:
  VAPID_PRIVATE_KEY=...
  VAPID_PUBLIC_KEY=...
And replace REPLACE_WITH_YOUR_VAPID_PUBLIC_KEY in issues/09/index.html
"""
from py_vapid import Vapid
import base64
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

v = Vapid()
v.generate_keys()

private_key = v.private_pem().decode().strip()

# Clé publique en format URL-safe base64 non paddé (format navigateur)
pub_bytes = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
public_key = base64.urlsafe_b64encode(pub_bytes).decode().rstrip('=')

print("=== VAPID KEYS ===")
print(f"\nVAPID_PRIVATE_KEY (Render + .env):\n{private_key}\n")
print(f"VAPID_PUBLIC_KEY (Render + .env):\n{public_key}\n")
print("=== DONE ===")
