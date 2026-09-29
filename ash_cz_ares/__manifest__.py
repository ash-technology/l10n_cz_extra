{
    "name": "Connector to czech public registers (VAT, ARES)",
    "version": "19.0.1.1.0",
    "category": "Localization",
    "countries": ["cz"],
    "summary": 'Partner creation via "IČ" and VAT reliability check (ARES/DPH)',
    "author": "Ash technology s.r.o.",
    "website": "https://github.com/ash-technology/l10n_cz_extra",
    "license": "LGPL-3",
    "depends": ["base", "account", "contacts", "l10n_cz"],
    "external_dependencies": {
        "python": ["requests"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "wizard/ares_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ash_cz_ares/static/src/**/*",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "images": ["static/description/ares_cz_main_screenshot.png"],
}
