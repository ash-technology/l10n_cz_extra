{
    'name': 'Czech QR Payment (SPAYD)',
    'version': '19.0.1.0.0',
    'depends': ['account', 'base', 'l10n_cz'],
    'countries': ['cz'],
    'category': 'Accounting',
    'summary': 'Add Czech standard QR codes (SPAYD) to your invoices with automatic IBAN conversion.',
    'description': """

Czech QR Payment Generator
==========================
Allow to generate czech banks compliant QR code for payment on the invoice, if the invoice currency is "CZK"

Key Features:
-------------
* **Standard SPAYD Support:** Fully compatible with all major Czech banking apps.
* **Smart IBAN Conversion:** Automatically converts local account numbers (e.g. 123-456/0800) to IBAN format.
* **Integration:** Works with standard Odoo invoice templates.
    """,
    'author': 'Ash technology s.r.o.',
    'website': 'https://github.com/ash-technology/l10n_cz_extra',
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['qrcode'],
    },
    'data': [
        'views/report_invoice.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['images/qr_payment_main_screenshot.png'],
}