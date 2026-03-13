"""QR Code generation routes — 12 tool pages + designer + API endpoints."""
import os, io
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from services import qr_generator
from services.image_qr import generate_image_qr
from services.shape_qr import generate_modern_qr, generate_modern_qr_svg

qr_bp = Blueprint("qr", __name__)


# ═══════════════════════════════════════════════════════════════
#  SEO meta data for each tool page
# ═══════════════════════════════════════════════════════════════
TOOL_META = {
    "image": {
        "title": "Free Image QR Code Generator — Upload Logo & Create Branded QR | QR Code Studio",
        "description": "Upload your logo, shop photo, or any image and create a stunning Image QR Code for free. 3 styles: center overlay, background, color blend. Download PNG & PDF instantly.",
        "h1": "Image QR Code Maker",
        "h1_ur": "تصویر والا QR کوڈ بنائیں",
        "keyword": "image qr code generator free",
    },
    "url": {
        "title": "Free QR Code Generator for URL & Website Link | QR Code Studio",
        "description": "Generate a free QR code for any website URL. Paste your link, customize colors, download PNG or PDF. No signup required.",
        "h1": "URL / Website QR Code Generator",
        "h1_ur": "ویب سائٹ لنک کا QR کوڈ بنائیں",
        "keyword": "free qr code generator for url",
    },
    "wifi": {
        "title": "Free WiFi QR Code Generator — Scan to Connect WiFi | QR Code Studio",
        "description": "Create a WiFi QR code free. Customers scan and connect to your WiFi instantly — no password typing. Perfect for cafes, offices, homes.",
        "h1": "WiFi QR Code Generator",
        "h1_ur": "وائی فائی QR کوڈ بنائیں",
        "keyword": "wifi qr code generator free",
    },
    "whatsapp": {
        "title": "Free WhatsApp QR Code Generator — Scan to Chat | QR Code Studio",
        "description": "Create a WhatsApp QR code for your business. Customers scan and WhatsApp chat opens instantly with your number. Perfect for shops in Pakistan.",
        "h1": "WhatsApp QR Code Generator",
        "h1_ur": "واٹس ایپ QR کوڈ بنائیں",
        "keyword": "whatsapp qr code maker free",
    },
    "vcard": {
        "title": "Free Digital Business Card QR Code — vCard QR Generator | QR Code Studio",
        "description": "Create a digital visiting card QR code. Scan to save name, phone, email, company — one tap. Perfect for business cards and networking.",
        "h1": "vCard / Digital Business Card QR",
        "h1_ur": "ڈیجیٹل وزیٹنگ کارڈ QR بنائیں",
        "keyword": "digital business card qr code free",
    },
    "restaurant": {
        "title": "Free Restaurant Menu QR Code Generator — Table QR | QR Code Studio",
        "description": "Create a menu QR code for your restaurant or cafe. Print and put on every table. Customers scan to see your digital menu. 100% free.",
        "h1": "Restaurant Menu QR Code",
        "h1_ur": "ریسٹورنٹ مینیو QR کوڈ بنائیں",
        "keyword": "restaurant menu qr code free",
    },
    "payment": {
        "title": "Free Payment QR Code Generator — Easypaisa JazzCash UPI | QR Code Studio",
        "description": "Create a payment QR code for Easypaisa, JazzCash, or UPI. Customers scan to pay directly. No payment gateway needed. 100% free.",
        "h1": "Payment QR Code Generator",
        "h1_ur": "ادائیگی QR کوڈ بنائیں",
        "keyword": "easypaisa jazzcash qr code generator",
    },
    "location": {
        "title": "Free Google Maps Location QR Code Generator | QR Code Studio",
        "description": "Create a Google Maps QR code for your shop, office, or home. Customers scan to open exact location in Maps. No API keys needed.",
        "h1": "Google Maps Location QR Code",
        "h1_ur": "گوگل میپس لوکیشن QR بنائیں",
        "keyword": "google maps qr code generator free",
    },
    "email": {
        "title": "Free Email QR Code Generator — Scan to Send Email | QR Code Studio",
        "description": "Create an email QR code with pre-filled recipient, subject, and message. Scan to compose email instantly. Perfect for professionals.",
        "h1": "Email QR Code Generator",
        "h1_ur": "ای میل QR کوڈ بنائیں",
        "keyword": "email qr code generator free",
    },
    "app": {
        "title": "Free App Download QR Code Generator — Play Store & App Store | QR Code Studio",
        "description": "Create a QR code that links to your app on Play Store or App Store. Users scan to download. Perfect for app developers and startups.",
        "h1": "App Download QR Code",
        "h1_ur": "ایپ ڈاؤن لوڈ QR کوڈ بنائیں",
        "keyword": "app download qr code generator",
    },
    "pdf": {
        "title": "Free PDF / File QR Code Generator — Link Any Document | QR Code Studio",
        "description": "Create a QR code for any PDF, Google Drive file, or document. Scan to open or download. Perfect for menus, price lists, and brochures.",
        "h1": "PDF / File QR Code Generator",
        "h1_ur": "PDF / فائل QR کوڈ بنائیں",
        "keyword": "pdf qr code generator online free",
    },
    "text": {
        "title": "Free Text to QR Code Generator — Encode Any Message | QR Code Studio",
        "description": "Convert any text, message, or information into a QR code for free. Type your text, generate, and download. No signup required.",
        "h1": "Plain Text QR Code Generator",
        "h1_ur": "ٹیکسٹ QR کوڈ بنائیں",
        "keyword": "text to qr code generator free",
    },
}

# FAQ for each tool (helps SEO with structured data)
TOOL_FAQS = {
    "image": [
        ("What is an Image QR Code?", "An Image QR Code embeds your logo or photo inside the QR code. It still scans perfectly thanks to high error correction. Great for branding."),
        ("Is the Image QR Code free?", "Yes! 100% free. No signup, no payment. Upload your image, generate, and download."),
        ("Will the Image QR Code still scan?", "Yes. We use the highest error correction level (H) which can handle up to 30% of the QR being covered by an image."),
        ("What image formats are supported?", "JPG, PNG, and WEBP. Maximum file size is 5MB."),
        ("Can I use this for my business logo?", "Absolutely! Upload your business logo to create branded QR codes for marketing materials, business cards, and packaging."),
    ],
    "url": [
        ("How do I create a QR code for a website?", "Paste your website URL, customize colors if you want, and click Generate. Download your QR code as PNG or PDF."),
        ("Is this URL QR code generator free?", "Yes, completely free. No signup required. Generate unlimited QR codes."),
        ("Does the QR code expire?", "No. QR codes generated here never expire. They encode the URL directly."),
    ],
    "wifi": [
        ("How does WiFi QR code work?", "The QR code contains your WiFi name and password in a special format. When scanned, the phone connects automatically."),
        ("Is my WiFi password safe?", "The password is encoded in the QR image. We don't store it on any server. Everything is processed and deleted immediately."),
        ("Which phones can scan WiFi QR?", "All modern Android phones and iPhones (iOS 11+) can scan WiFi QR codes using the built-in camera."),
    ],
    "whatsapp": [
        ("How does WhatsApp QR work?", "The QR contains a wa.me link with your number. When scanned, WhatsApp opens with a chat to your number."),
        ("Can I add a pre-filled message?", "Yes! Add an optional message that will appear pre-typed when the customer scans."),
        ("Does it work in Pakistan?", "Yes! Use your number with country code +92. Works worldwide."),
    ],
}

# Default FAQ for tools without specific ones
DEFAULT_FAQ = [
    ("Is this tool free?", "Yes, 100% free. No signup, no payment, no hidden fees."),
    ("Do I need to create an account?", "No account needed. Just open the tool, enter your details, and generate your QR code."),
    ("Can I download the QR code?", "Yes, download as PNG for digital use or PDF for printing. Both are free."),
]


# ═══════════════════════════════════════════════════════════════
#  TOOL PAGE ROUTES (GET)
# ═══════════════════════════════════════════════════════════════

@qr_bp.route("/qr/image")
def image_qr_page():
    meta = TOOL_META["image"]
    faqs = TOOL_FAQS.get("image", DEFAULT_FAQ)
    return render_template("tools/image_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/image")

@qr_bp.route("/qr/url")
def url_qr_page():
    meta = TOOL_META["url"]
    faqs = TOOL_FAQS.get("url", DEFAULT_FAQ)
    return render_template("tools/url_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/url")

@qr_bp.route("/qr/wifi")
def wifi_qr_page():
    meta = TOOL_META["wifi"]
    faqs = TOOL_FAQS.get("wifi", DEFAULT_FAQ)
    return render_template("tools/wifi_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/wifi")

@qr_bp.route("/qr/whatsapp")
def whatsapp_qr_page():
    meta = TOOL_META["whatsapp"]
    faqs = TOOL_FAQS.get("whatsapp", DEFAULT_FAQ)
    return render_template("tools/whatsapp_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/whatsapp")

@qr_bp.route("/qr/vcard")
def vcard_qr_page():
    meta = TOOL_META["vcard"]
    faqs = TOOL_FAQS.get("vcard", DEFAULT_FAQ)
    return render_template("tools/vcard_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/vcard")

@qr_bp.route("/qr/restaurant")
def restaurant_qr_page():
    meta = TOOL_META["restaurant"]
    faqs = TOOL_FAQS.get("restaurant", DEFAULT_FAQ)
    return render_template("tools/restaurant_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/restaurant")

@qr_bp.route("/qr/payment")
def payment_qr_page():
    meta = TOOL_META["payment"]
    faqs = TOOL_FAQS.get("payment", DEFAULT_FAQ)
    return render_template("tools/payment_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/payment")

@qr_bp.route("/qr/location")
def location_qr_page():
    meta = TOOL_META["location"]
    faqs = TOOL_FAQS.get("location", DEFAULT_FAQ)
    return render_template("tools/location_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/location")

@qr_bp.route("/qr/email")
def email_qr_page():
    meta = TOOL_META["email"]
    faqs = TOOL_FAQS.get("email", DEFAULT_FAQ)
    return render_template("tools/email_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/email")

@qr_bp.route("/qr/app")
def app_qr_page():
    meta = TOOL_META["app"]
    faqs = TOOL_FAQS.get("app", DEFAULT_FAQ)
    return render_template("tools/app_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/app")

@qr_bp.route("/qr/pdf")
def pdf_qr_page():
    meta = TOOL_META["pdf"]
    faqs = TOOL_FAQS.get("pdf", DEFAULT_FAQ)
    return render_template("tools/pdf_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/pdf")

@qr_bp.route("/qr/text")
def text_qr_page():
    meta = TOOL_META["text"]
    faqs = TOOL_FAQS.get("text", DEFAULT_FAQ)
    return render_template("tools/text_qr.html", meta=meta, faqs=faqs,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/text")


# ═══════════════════════════════════════════════════════════════
#  API ENDPOINTS (POST — return JSON with base64 image)
# ═══════════════════════════════════════════════════════════════

@qr_bp.route("/generate-image-qr", methods=["POST"])
def api_image_qr():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400
    f = request.files["image"]
    qr_data = request.form.get("qr_data", "")
    if not qr_data:
        return jsonify({"success": False, "error": "QR data is required"}), 400
    style = request.form.get("style", "center")
    fg = request.form.get("fg_color", "#000000")
    bg = request.form.get("bg_color", "#FFFFFF")
    result = generate_image_qr(f.stream, qr_data, style, fg, bg)
    return jsonify(result)


@qr_bp.route("/generate-url-qr", methods=["POST"])
def api_url_qr():
    data = request.get_json() or request.form
    url = data.get("url", "")
    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400
    result = qr_generator.generate_url_qr(
        url, data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-wifi-qr", methods=["POST"])
def api_wifi_qr():
    data = request.get_json() or request.form
    ssid = data.get("ssid", "")
    password = data.get("password", "")
    if not ssid:
        return jsonify({"success": False, "error": "WiFi name is required"}), 400
    result = qr_generator.generate_wifi_qr(
        ssid, password, data.get("security", "WPA"),
        data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-whatsapp-qr", methods=["POST"])
def api_whatsapp_qr():
    data = request.get_json() or request.form
    phone = data.get("phone", "")
    if not phone:
        return jsonify({"success": False, "error": "Phone number is required"}), 400
    result = qr_generator.generate_whatsapp_qr(
        phone, data.get("message", ""),
        data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-vcard-qr", methods=["POST"])
def api_vcard_qr():
    data = request.get_json() or request.form
    name = data.get("name", "")
    if not name:
        return jsonify({"success": False, "error": "Name is required"}), 400
    result = qr_generator.generate_vcard_qr(
        name, data.get("phone", ""), data.get("email", ""),
        data.get("company", ""), data.get("job_title", ""), data.get("website", ""),
        data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-restaurant-qr", methods=["POST"])
def api_restaurant_qr():
    data = request.get_json() or request.form
    menu_url = data.get("menu_url", "")
    if not menu_url:
        return jsonify({"success": False, "error": "Menu URL is required"}), 400
    result = qr_generator.generate_restaurant_qr(
        menu_url, data.get("restaurant_name", ""),
        data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-payment-qr", methods=["POST"])
def api_payment_qr():
    data = request.get_json() or request.form
    pid = data.get("payment_id", "")
    if not pid:
        return jsonify({"success": False, "error": "Payment ID / Account number is required"}), 400
    result = qr_generator.generate_payment_qr(
        pid, data.get("provider", "generic"), data.get("name", ""),
        data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-location-qr", methods=["POST"])
def api_location_qr():
    data = request.get_json() or request.form
    lat = data.get("latitude", "")
    lng = data.get("longitude", "")
    if not lat or not lng:
        return jsonify({"success": False, "error": "Latitude and longitude are required"}), 400
    result = qr_generator.generate_location_qr(
        lat, lng, data.get("label", ""),
        data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-email-qr", methods=["POST"])
def api_email_qr():
    data = request.get_json() or request.form
    email = data.get("email", "")
    if not email:
        return jsonify({"success": False, "error": "Email address is required"}), 400
    result = qr_generator.generate_email_qr(
        email, data.get("subject", ""), data.get("body", ""),
        data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-app-qr", methods=["POST"])
def api_app_qr():
    data = request.get_json() or request.form
    app_url = data.get("app_url", "")
    if not app_url:
        return jsonify({"success": False, "error": "App URL is required"}), 400
    result = qr_generator.generate_app_qr(
        app_url, data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-pdf-qr", methods=["POST"])
def api_pdf_qr():
    data = request.get_json() or request.form
    file_url = data.get("file_url", "")
    if not file_url:
        return jsonify({"success": False, "error": "File URL is required"}), 400
    result = qr_generator.generate_pdf_qr(
        file_url, data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


@qr_bp.route("/generate-text-qr", methods=["POST"])
def api_text_qr():
    data = request.get_json() or request.form
    text = data.get("text", "")
    if not text:
        return jsonify({"success": False, "error": "Text is required"}), 400
    result = qr_generator.generate_text_qr(
        text, data.get("fg_color", "#000000"), data.get("bg_color", "#FFFFFF"),
        data.get("dot_shape", "square"))
    return jsonify(result)


# ═══════════════════════════════════════════════════════════════
#  MODERN DESIGNER QR — Star feature
# ═══════════════════════════════════════════════════════════════

DESIGNER_META = {
    "title": "Modern QR Code Designer — Dots, Shapes, Logo & Art QR | QR Code Studio",
    "description": "Create stunning modern QR codes with dot styles, shape masks (pizza, car, coffee), image art, gradient colors, and custom logos. 100% free with SVG export.",
    "h1": "Modern QR Code Designer",
    "h1_ur": "جدید QR کوڈ ڈیزائنر",
    "keyword": "modern qr code designer free",
}

DESIGNER_FAQS = [
    ("What is a Modern QR Code?", "A modern QR code replaces boring black squares with dots, lines, shapes, or even images — while staying 100% scannable."),
    ("Will these designed QR codes still scan?", "Yes! We use Error Correction Level H (highest) which allows up to 30% of modules to be modified. Finder patterns (corner squares) are always protected."),
    ("What shapes are available?", "Circle/Pizza, Heart, Car, Coffee Cup, Camera, Shopping Bag, Star, and Diamond — all generated automatically."),
    ("Can I use my own image?", "Yes! Upload any logo or photo. Or pick a business category and we'll use a fitting default image."),
    ("What is the SVG format?", "SVG is a vector format that scales infinitely without losing quality. Perfect for large print banners and signage."),
    ("Is this really free?", "Yes, 100% free. No signup, no watermark, no hidden fees."),
]

# Business category defaults for users who don't want to upload
BUSINESS_CATEGORIES = {
    "car_wash": {"name": "Car Wash", "name_ur": "کار واش", "emoji": "🚗", "shape": "car", "fg": "#1a73e8", "bg": "#ffffff"},
    "mobile_shop": {"name": "Mobile Shop", "name_ur": "موبائل شاپ", "emoji": "📱", "shape": "diamond", "fg": "#6a0572", "bg": "#ffffff"},
    "computer_shop": {"name": "Computer Shop", "name_ur": "کمپیوٹر شاپ", "emoji": "💻", "shape": "diamond", "fg": "#264653", "bg": "#ffffff"},
    "medical_shop": {"name": "Medical / Pharmacy", "name_ur": "میڈیکل اسٹور", "emoji": "💊", "shape": "heart", "fg": "#e63946", "bg": "#ffffff"},
    "restaurant": {"name": "Restaurant", "name_ur": "ریسٹورنٹ", "emoji": "🍽️", "shape": "circle", "fg": "#d62828", "bg": "#fff3e0"},
    "cafe": {"name": "Café / Coffee Shop", "name_ur": "کیفے", "emoji": "☕", "shape": "coffee", "fg": "#5d4037", "bg": "#fff8e1"},
    "bakery": {"name": "Bakery / Sweets", "name_ur": "بیکری", "emoji": "🧁", "shape": "circle", "fg": "#d81b60", "bg": "#fce4ec"},
    "salon": {"name": "Salon / Beauty", "name_ur": "سیلون", "emoji": "💇", "shape": "star", "fg": "#ad1457", "bg": "#fce4ec"},
    "gym": {"name": "Gym / Fitness", "name_ur": "جم", "emoji": "🏋️", "shape": "diamond", "fg": "#1b5e20", "bg": "#e8f5e9"},
    "real_estate": {"name": "Real Estate", "name_ur": "رئیل اسٹیٹ", "emoji": "🏠", "shape": "diamond", "fg": "#0d47a1", "bg": "#e3f2fd"},
    "education": {"name": "School / Education", "name_ur": "اسکول / تعلیم", "emoji": "🎓", "shape": "star", "fg": "#ff6f00", "bg": "#fff3e0"},
    "grocery": {"name": "Grocery Store", "name_ur": "کریانہ اسٹور", "emoji": "🛒", "shape": "shopping_bag", "fg": "#2e7d32", "bg": "#ffffff"},
    "photography": {"name": "Photography", "name_ur": "فوٹوگرافی", "emoji": "📷", "shape": "camera", "fg": "#37474f", "bg": "#ffffff"},
    "pizza": {"name": "Pizza Shop", "name_ur": "پیزا شاپ", "emoji": "🍕", "shape": "circle", "fg": "#e65100", "bg": "#fff3e0"},
}


@qr_bp.route("/qr/designer")
def designer_qr_page():
    meta = DESIGNER_META
    faqs = DESIGNER_FAQS
    return render_template("tools/designer_qr.html", meta=meta, faqs=faqs,
                           categories=BUSINESS_CATEGORIES,
                           page_title=meta["title"], page_description=meta["description"],
                           page_url="/qr/designer")


@qr_bp.route("/generate-designer-qr", methods=["POST"])
def api_designer_qr():
    """Modern designer QR generation — supports form data with optional file uploads."""
    qr_data = request.form.get("qr_data", "")
    if not qr_data:
        return jsonify({"success": False, "error": "Enter the URL or data for QR code"}), 400

    style = request.form.get("style", "dots")
    shape = request.form.get("shape", "none")
    fg_color = request.form.get("fg_color", "#000000")
    bg_color = request.form.get("bg_color", "#FFFFFF")
    gradient_color = request.form.get("gradient_color", "")
    gradient_type = request.form.get("gradient_type", "linear")
    frame_text = request.form.get("frame_text", "")
    image_style = request.form.get("image_style", "overlay")
    category = request.form.get("category", "")

    # Handle logo upload
    logo_file = None
    if "logo" in request.files and request.files["logo"].filename:
        logo_file = request.files["logo"].stream

    # Handle image upload OR category default
    image_file = None
    if "image" in request.files and request.files["image"].filename:
        image_file = request.files["image"].stream
    elif category and category in BUSINESS_CATEGORIES:
        # Use category defaults
        cat = BUSINESS_CATEGORIES[category]
        if not shape or shape == "none":
            shape = cat["shape"]
        if fg_color == "#000000":
            fg_color = cat["fg"]
        if bg_color == "#FFFFFF":
            bg_color = cat["bg"]
        if not frame_text:
            frame_text = cat["name"]
            
        # Optional: attempt to load the default image if not manually uploaded
        cat_img_path = os.path.join(current_app.static_folder, "category_images", f"{category}.png")
        if os.path.exists(cat_img_path):
            image_file = open(cat_img_path, "rb")

    result = generate_modern_qr(
        data=qr_data,
        style=style,
        shape=shape,
        fg_color=fg_color,
        bg_color=bg_color,
        gradient_color=gradient_color,
        gradient_type=gradient_type,
        frame_text=frame_text,
        logo_file=logo_file,
        image_file=image_file,
        image_style=image_style,
    )
    return jsonify(result)


@qr_bp.route("/generate-designer-svg", methods=["POST"])
def api_designer_svg():
    """SVG export for modern QR codes."""
    data = request.get_json() or request.form
    qr_data = data.get("qr_data", "")
    if not qr_data:
        return jsonify({"success": False, "error": "QR data required"}), 400

    result = generate_modern_qr_svg(
        data=qr_data,
        style=data.get("style", "dots"),
        fg_color=data.get("fg_color", "#000000"),
        bg_color=data.get("bg_color", "#FFFFFF"),
        shape=data.get("shape", "none"),
    )
    if result["success"]:
        return result["svg"], 200, {"Content-Type": "image/svg+xml",
                                     "Content-Disposition": "attachment; filename=qr-code.svg"}
    return jsonify(result), 400


@qr_bp.route("/scan-qr", methods=["POST"])
def api_scan_qr():
    """Reads an uploaded QR code image and returns its decoded text."""
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400
    
    file = request.files["image"]
    if not file.filename:
        return jsonify({"success": False, "error": "Empty file"}), 400
        
    try:
        # Read the image via PIL first to handle various formats
        img = Image.open(file.stream).convert('RGB')
        
        # Try decoding with pyzbar first
        decoded_objects = decode(img)
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode('utf-8')
            return jsonify({"success": True, "data": qr_data})
            
        # Fallback to OpenCV if pyzbar fails
        np_img = np.array(img)
        # Convert RGB to BGR for OpenCV
        cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        
        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(cv_img)
        
        if data:
            return jsonify({"success": True, "data": data})
            
        return jsonify({"success": False, "error": "Could not detect a valid QR code in the image. Please try a clearer image."}), 400
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error scanning image: {str(e)}"}), 500

