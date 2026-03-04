"""Core QR Code Generator — supports all 12 QR types using FREE libraries."""
import io
import base64
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
)
from PIL import Image, ImageDraw


# ── Module drawer map ──────────────────────────────────────
DRAWERS = {
    "square": SquareModuleDrawer,
    "gapped": GappedSquareModuleDrawer,
    "circle": CircleModuleDrawer,
}


def _make_qr(data, fg_color="#000000", bg_color="#FFFFFF", dot_shape="square",
             error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10):
    """Generate a base QR code image (PIL) from data string."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    drawer_cls = DRAWERS.get(dot_shape, SquareModuleDrawer)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer_cls(),
        fill_color=fg_color,
        back_color=bg_color,
    )
    return img.convert("RGBA")


def _img_to_base64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _img_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────────────────────
#  1. URL QR
# ─────────────────────────────────────────────────────────────
def generate_url_qr(url, fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    img = _make_qr(url, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
#  2. WiFi QR
# ─────────────────────────────────────────────────────────────
def generate_wifi_qr(ssid, password, security="WPA",
                     fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    data = f"WIFI:T:{security};S:{ssid};P:{password};;"
    img = _make_qr(data, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
#  3. WhatsApp QR
# ─────────────────────────────────────────────────────────────
def generate_whatsapp_qr(phone, message="",
                         fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    phone = phone.replace(" ", "").replace("-", "").replace("+", "")
    from urllib.parse import quote
    data = f"https://wa.me/{phone}"
    if message:
        data += f"?text={quote(message)}"
    img = _make_qr(data, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
#  4. vCard QR
# ─────────────────────────────────────────────────────────────
def generate_vcard_qr(name, phone="", email="", company="",
                      job_title="", website="",
                      fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
ORG:{company}
TITLE:{job_title}
TEL:{phone}
EMAIL:{email}
URL:{website}
END:VCARD"""
    img = _make_qr(vcard.strip(), fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
#  5. Email QR
# ─────────────────────────────────────────────────────────────
def generate_email_qr(email, subject="", body="",
                      fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    data = f"mailto:{email}"
    params = []
    if subject:
        params.append(f"subject={subject}")
    if body:
        params.append(f"body={body}")
    if params:
        data += "?" + "&".join(params)
    img = _make_qr(data, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
#  6. Phone QR
# ─────────────────────────────────────────────────────────────
def generate_phone_qr(phone,
                      fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    data = f"tel:{phone}"
    img = _make_qr(data, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
#  7. Location / Google Maps QR
# ─────────────────────────────────────────────────────────────
def generate_location_qr(latitude, longitude, label="",
                         fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    if label:
        data = f"geo:{latitude},{longitude}?q={latitude},{longitude}({label})"
    else:
        data = f"geo:{latitude},{longitude}"
    img = _make_qr(data, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
#  8. Restaurant Menu QR
# ─────────────────────────────────────────────────────────────
def generate_restaurant_qr(menu_url, restaurant_name="",
                           fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    if not menu_url.startswith(("http://", "https://")):
        menu_url = "https://" + menu_url
    img = _make_qr(menu_url, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
#  9. Payment QR (Easypaisa / JazzCash / UPI)
# ─────────────────────────────────────────────────────────────
def generate_payment_qr(payment_id, provider="generic", name="",
                        fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    if provider == "upi":
        data = f"upi://pay?pa={payment_id}&pn={name}"
    else:
        # Generic: just encode the payment info as text
        data = f"Pay to: {name}\nAccount: {payment_id}\nProvider: {provider}"
    img = _make_qr(data, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
# 10. App Download QR
# ─────────────────────────────────────────────────────────────
def generate_app_qr(app_url,
                    fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    if not app_url.startswith(("http://", "https://")):
        app_url = "https://" + app_url
    img = _make_qr(app_url, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
# 11. PDF / File QR
# ─────────────────────────────────────────────────────────────
def generate_pdf_qr(file_url,
                    fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    if not file_url.startswith(("http://", "https://")):
        file_url = "https://" + file_url
    img = _make_qr(file_url, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}


# ─────────────────────────────────────────────────────────────
# 12. Plain Text QR
# ─────────────────────────────────────────────────────────────
def generate_text_qr(text,
                     fg_color="#000000", bg_color="#FFFFFF", dot_shape="square"):
    img = _make_qr(text, fg_color, bg_color, dot_shape)
    return {"image": _img_to_base64(img), "success": True}
