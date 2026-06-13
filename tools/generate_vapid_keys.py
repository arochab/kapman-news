"""
Run once to generate VAPID keys.
Copy the output into Render environment variables:
  VAPID_PRIVATE_KEY=...
  VAPID_PUBLIC_KEY=...
And replace REPLACE_WITH_YOUR_VAPID_PUBLIC_KEY in issues/09/index.html
"""
from py_vapid import Vapid

v = Vapid()
v.generate_keys()

private_key = v.private_pem().decode().strip()
public_key  = v.public_key

print("=== VAPID KEYS ===")
print(f"\nVAPID_PRIVATE_KEY (Render env var):\n{private_key}\n")
print(f"VAPID_PUBLIC_KEY (Render env var + index.html):\n{public_key}\n")
print("=== DONE ===")
