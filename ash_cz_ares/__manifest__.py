
{
    'name': 'Connector to czech public registers (VAT, ARES)',
    'version': '19.0.1.0.0',
    'category': 'Localization',
    'countries': ['cz'],
    'summary': 'Partner creation via "IČO" and  VAT reliability check (ARES/DPH)',
    'description': """
This module automates the creation of partners and ensures their VAT reliability.

Key Features:
-------------
* **ARES Lookup:** Create partners by entering their "IČO", fill its name and address into appropriate fields in Odoo.
* **VAT Reliability Check**
* **Status Badges & Ribbons:** Clear visual warnings (Red Ribbon) for unreliable payers.
* **Batch Processing:** Verify the reliability of selected partners at once from the list view.
    """,
    'author': 'Ash technology s.r.o.',
    'website': 'https://github.com/ash-technology/l10n_cz_extra',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'contacts', 'l10n_cz'],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/ares_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/ares_cz_main_screenshot.png'],

}