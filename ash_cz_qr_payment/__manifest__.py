{
    "name": "Czech QR Payment (SPAYD)",
    "version": "19.0.1.0.0",
    "depends": ["account", "base", "l10n_cz"],
    "countries": ["cz"],
    "category": "Accounting",
    "summary": "Add Czech standard QR codes for payment to your invoices.",
    "author": "Ash technology s.r.o.",
    "website": "https://github.com/ash-technology/l10n_cz_extra",
    "license": "LGPL-3",
    "external_dependencies": {
        "python": ["qrcode"],
    },
    "data": [
        "views/report_invoice.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    "images": ["static/description/qr_payment_main_screenshot.png"],
}
