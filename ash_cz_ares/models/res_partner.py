import requests
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # is_unreliable_payer = fields.Boolean(string="Nespolehlivý plátce", default=False)

    is_unreliable_payer = fields.Selection([
        ('not_checked', 'Not Checked'),
        ('reliable', 'Reliable'),
        ('unreliable', 'Unreliable')
    ], string="VAT Reliability", default='not_checked')

    def action_check_unreliable_vat_payer(self):
        connector = self.env['l10n_cz.ares.connector']

        for record in self:
            if not record.vat:
                record.is_unreliable_payer = 'not_checked'
                continue
        
            is_unreliable = connector.check_unreliable_payer(record.vat)

            # Mapping the API result to our three states
            if is_unreliable is True:
                self.is_unreliable_payer = 'unreliable'
            elif is_unreliable is False:
                self.is_unreliable_payer = 'reliable'
            else:
                self.is_unreliable_payer = 'not_checked'
        
        # This line tells Odoo to refresh the current screen if the 
        # method is called just for one record (so probaly inside a form)
        if len(self) == 1:
            return {'type': 'ir.actions.client', 'tag': 'reload'}
     

    def action_open_ares_wizard(self):
        self.ensure_one()
        return {
            'name': 'Refresh from ARES',
            'type': 'ir.actions.act_window',
            'res_model': 'l10n_cz.ares.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ico': self.company_registry or '',
            }
        }
