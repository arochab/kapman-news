"""
Génère le QR code d'abonnement pour la newsletter.
Output : pwa/qr.png
"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from pathlib import Path

SUBSCRIBE_URL = "https://arochab.github.io/kapman-news/"

qr = qrcode.QRCode(
    version=2,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=8,
    border=2,
)
qr.add_data(SUBSCRIBE_URL)
qr.make(fit=True)

img = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    back_color="#0D0D0D",
    fill_color="#F5F0E8",
)

out = Path(__file__).parent.parent / "pwa" / "qr.png"
img.save(out)
print(f"QR code saved → {out}")
print(f"URL: {SUBSCRIBE_URL}")
