from odoo import fields, models


class AresPartnerWizard(models.TransientModel):
    _name = "l10n_cz.ares.wizard"
    _description = "Wizard to create Partner from ARES"

    ico = fields.Char(string="IČ", required=True, help="Enter the IČ (up to 8 digits)")

    def action_fetch_and_create(self):
        self.ensure_one()
        values, warning = self.env["l10n_cz.ares.connector"]._prepare_partner_values(
            self.ico, False
        )
        partner = self.env["res.partner"].create(values)
        action = {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "res_id": partner.id,
            "target": "current",
        }
        if not warning:
            return action
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": warning,
                "type": "warning",
                "sticky": True,
                "next": action,
            },
        }
