"""Main routes — Homepage + static pages."""
from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

# ── Tool definitions for homepage cards ─────────────────────
TOOLS = [
    {
        "id": "image", "emoji": "📸", "name": "Image QR Code",
        "urdu": "تصویر والا QR کوڈ", "star": True,
        "desc": "Upload your logo or photo — get a branded QR code",
        "desc_ur": "اپنا لوگو یا تصویر اپ لوڈ کریں — برانڈڈ QR کوڈ بنائیں",
        "category": "image", "time": "60 sec",
        "url": "/qr/image",
    },
    {
        "id": "url", "emoji": "🌐", "name": "URL / Website QR",
        "urdu": "ویب سائٹ QR کوڈ",
        "desc": "Create QR code for any website link",
        "desc_ur": "کسی بھی ویب سائٹ لنک کا QR کوڈ بنائیں",
        "category": "personal", "time": "30 sec",
        "url": "/qr/url",
    },
    {
        "id": "wifi", "emoji": "📶", "name": "WiFi QR Code",
        "urdu": "وائی فائی QR کوڈ",
        "desc": "Scan to connect WiFi — no typing password",
        "desc_ur": "سکین کریں اور وائی فائی سے جڑ جائیں",
        "category": "business", "time": "30 sec",
        "url": "/qr/wifi",
    },
    {
        "id": "whatsapp", "emoji": "💬", "name": "WhatsApp QR Code",
        "urdu": "واٹس ایپ QR کوڈ",
        "desc": "Customers scan → WhatsApp chat opens instantly",
        "desc_ur": "سکین کریں → واٹس ایپ چیٹ فوراً کھلے",
        "category": "business", "time": "30 sec",
        "url": "/qr/whatsapp",
    },
    {
        "id": "vcard", "emoji": "📞", "name": "vCard / Contact QR",
        "urdu": "ڈیجیٹل وزیٹنگ کارڈ",
        "desc": "Digital business card — scan to save contact",
        "desc_ur": "ڈیجیٹل بزنس کارڈ — سکین کر کے رابطہ محفوظ کریں",
        "category": "personal", "time": "45 sec",
        "url": "/qr/vcard",
    },
    {
        "id": "restaurant", "emoji": "🍽️", "name": "Restaurant Menu QR",
        "urdu": "ریسٹورنٹ مینیو QR کوڈ",
        "desc": "QR on every table — customers scan for menu",
        "desc_ur": "ہر میز پر QR — گاہک مینیو دیکھیں",
        "category": "restaurant", "time": "30 sec",
        "url": "/qr/restaurant",
    },
    {
        "id": "payment", "emoji": "💳", "name": "Payment QR Code",
        "urdu": "ادائیگی QR کوڈ",
        "desc": "Easypaisa / JazzCash / UPI payment QR",
        "desc_ur": "ایزی پیسہ / جیز کیش / UPI ادائیگی QR",
        "category": "business", "time": "30 sec",
        "url": "/qr/payment",
    },
    {
        "id": "location", "emoji": "📍", "name": "Google Maps QR",
        "urdu": "گوگل میپس QR کوڈ",
        "desc": "Scan to open your shop/office location in Maps",
        "desc_ur": "سکین کریں — آپ کی دکان کا مقام میپس پر کھلے",
        "category": "business", "time": "30 sec",
        "url": "/qr/location",
    },
    {
        "id": "email", "emoji": "📧", "name": "Email QR Code",
        "urdu": "ای میل QR کوڈ",
        "desc": "Scan to compose an email with pre-filled info",
        "desc_ur": "سکین کریں — ای میل خودکار طور پر تیار ہو",
        "category": "personal", "time": "30 sec",
        "url": "/qr/email",
    },
    {
        "id": "app", "emoji": "📱", "name": "App Download QR",
        "urdu": "ایپ ڈاؤن لوڈ QR",
        "desc": "Link to Play Store or App Store download",
        "desc_ur": "پلے اسٹور یا ایپ اسٹور ڈاؤن لوڈ لنک",
        "category": "personal", "time": "30 sec",
        "url": "/qr/app",
    },
    {
        "id": "pdf", "emoji": "📄", "name": "PDF / File QR",
        "urdu": "فائل QR کوڈ",
        "desc": "Link to any PDF, Google Drive, or document",
        "desc_ur": "کسی بھی PDF، گوگل ڈرائیو، یا دستاویز کا لنک",
        "category": "personal", "time": "30 sec",
        "url": "/qr/pdf",
    },
    {
        "id": "text", "emoji": "📝", "name": "Plain Text QR",
        "urdu": "ٹیکسٹ QR کوڈ",
        "desc": "Encode any message or text as QR code",
        "desc_ur": "کوئی بھی پیغام یا ٹیکسٹ QR کوڈ میں بدلیں",
        "category": "personal", "time": "30 sec",
        "url": "/qr/text",
    },
]


@main_bp.route("/")
def home():
    return render_template("home/index.html",
                           tools=TOOLS,
                           page_title="Free QR Code Generator — Make QR Codes Online Free | QR Code Studio",
                           page_description="Create free QR codes instantly — URL, WiFi, WhatsApp, Image QR, vCard, Restaurant Menu, Payment & more. No signup. 100% free. Download in seconds.",
                           page_url="/")


@main_bp.route("/about")
def about():
    return render_template("pages/about.html",
                           page_title="About QR Code Studio — Free QR Code Generator",
                           page_description="QR Code Studio is a free online QR code generator. Create URL, WiFi, WhatsApp, Image, vCard, and 12+ QR code types. No signup required.",
                           page_url="/about")


@main_bp.route("/contact")
def contact():
    return render_template("pages/contact.html",
                           page_title="Contact Us — QR Code Studio",
                           page_description="Get in touch with QR Code Studio. We are here to help with any questions about our free QR code generator.",
                           page_url="/contact")


@main_bp.route("/privacy")
def privacy():
    return render_template("pages/privacy.html",
                           page_title="Privacy Policy — QR Code Studio",
                           page_description="Read the Privacy Policy of QR Code Studio. We respect your privacy. No data stored, no tracking beyond standard analytics.",
                           page_url="/privacy")


@main_bp.route("/disclaimer")
def disclaimer():
    return render_template("pages/disclaimer.html",
                           page_title="Disclaimer — QR Code Studio",
                           page_description="QR Code Studio disclaimer. QR codes are generated based on user input. We do not guarantee accuracy of encoded data.",
                           page_url="/disclaimer")


@main_bp.route("/history")
def history():
    return render_template("pages/history.html",
                           page_title="My QR Code History — QR Code Studio",
                           page_description="View your recently generated QR codes. Saved locally in your browser — no account needed.",
                           page_url="/history")
