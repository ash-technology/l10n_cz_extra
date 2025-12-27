import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AresPartnerWizard(models.TransientModel):
    _name = 'l10n_cz.ares.wizard'
    _description = 'Wizard to create Partner from ARES'

    ico = fields.Char(string="IČO", required=True, help="Enter the 8-digit Company ID")

    def action_fetch_and_create(self):
        self.ensure_one()
        ico = self.ico.strip()

        # Call the centralized logic
        data = self.env['l10n_cz.ares.connector'].fetch_ares_data(self.ico)
        
        if not data:
            raise UserError("ICO not found in ARES.")

        # 2. Parse Data
        address = data.get('sidlo', {})
        street = address.get('nazevUlice', '')
        house_num = address.get('cisloDomovni', '')
        orient_num = address.get('cisloOrientacni', '')
            
        full_street = f"{street} {house_num}"
        if orient_num:
            full_street += f"/{orient_num}"

            # Safe lookup for Country
        cz_country = self.env.ref('base.cz', raise_if_not_found=False)
        
        active_id = self.env.context.get('active_id')
        if active_id and self.env.context.get('active_model') == 'res.partner':
            partner = self.env['res.partner'].browse(active_id)
            partner.write({
                'name': data.get('obchodniJmeno'),
                'company_registry': ico,
                'street': full_street.strip(),
                'city': address.get('nazevObce'),
                'zip': str(address.get('psc', '')),
                'country_id': cz_country.id if cz_country else False,
                'vat': "CZ" + ico, # Assuming VAT payer based on IČO, or check ARES DPH
                'is_company': True,
            })
            return {'type': 'ir.actions.client', 'tag': 'reload'} # Just refresh the page
        else:    
            # 3. Create the Partner Record
            # We create it directly. Since we provide the Name, no validation error occurs.
            new_partner = self.env['res.partner'].create({
                'name': data.get('obchodniJmeno') or f"Company {ico}",
                'company_registry': ico,
                'street': full_street.strip(),
                'city': address.get('nazevObce'),
                'zip': str(address.get('psc', '')),
                'country_id': cz_country.id if cz_country else False,
                'vat': "CZ" + ico, # Assuming VAT payer based on IČO, or check ARES DPH
                'is_company': True,
            })
        
            # 4. Return Action to Open the New Record
            # This redirects the user's screen to the form view of the created partner
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'res_id': new_partner.id,
                'target': 'current',
            }