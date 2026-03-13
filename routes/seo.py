"""SEO routes — sitemap.xml, robots.txt, ads.txt"""
from flask import Blueprint, Response, current_app

seo_bp = Blueprint("seo", __name__)

PAGES = [
    ("/", 1.0, "daily"),
    ("/qr/image", 0.9, "weekly"),
    ("/qr/url", 0.8, "weekly"),
    ("/qr/wifi", 0.8, "weekly"),
    ("/qr/whatsapp", 0.8, "weekly"),
    ("/qr/vcard", 0.8, "weekly"),
    ("/qr/restaurant", 0.8, "weekly"),
    ("/qr/payment", 0.8, "weekly"),
    ("/qr/location", 0.8, "weekly"),
    ("/qr/email", 0.8, "weekly"),
    ("/qr/app", 0.8, "weekly"),
    ("/qr/pdf", 0.8, "weekly"),
    ("/qr/text", 0.8, "weekly"),
    ("/qr/designer", 0.9, "daily"),
    ("/history", 0.5, "monthly"),
    ("/about", 0.4, "monthly"),
    ("/contact", 0.4, "monthly"),
    ("/privacy", 0.3, "monthly"),
    ("/disclaimer", 0.3, "monthly"),
]


@seo_bp.route("/sitemap.xml")
def sitemap():
    domain = current_app.config["SITE_DOMAIN"].rstrip("/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path, priority, freq in PAGES:
        xml += "  <url>\n"
        xml += f"    <loc>{domain}{path}</loc>\n"
        xml += f"    <changefreq>{freq}</changefreq>\n"
        xml += f"    <priority>{priority}</priority>\n"
        xml += "  </url>\n"
    xml += "</urlset>"
    return Response(xml, mimetype="application/xml")


@seo_bp.route("/robots.txt")
def robots():
    domain = current_app.config["SITE_DOMAIN"].rstrip("/")
    txt = f"""User-agent: *
Allow: /
Disallow: /static/uploads/

Sitemap: {domain}/sitemap.xml
"""
    return Response(txt, mimetype="text/plain")


@seo_bp.route("/ads.txt")
def ads_txt():
    adsense_id = current_app.config.get("ADSENSE_ID", "")
    if adsense_id:
        pub_id = adsense_id.replace("ca-pub-", "")
        txt = f"google.com, pub-{pub_id}, DIRECT, f08c47fec0942fa0"
    else:
        txt = "# AdSense not yet configured. Add ADSENSE_ID to .env after approval."
    return Response(txt, mimetype="text/plain")
