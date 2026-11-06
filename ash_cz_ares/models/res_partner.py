from odoo import api, fields, models
from odoo.tools import split_every

from .ares_connector import MFCR_BATCH_SIZE


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_unreliable_payer = fields.Selection(
        [
            ("not_checked", "Not Checked"),
            ("reliable", "Reliable"),
            ("unreliable", "Unreliable"),
            ("not_vat_payer", "Not a VAT Payer"),
        ],
        string="VAT Reliability",
        default="not_checked",
    )

    def action_check_unreliable_vat_payer(self):
        connector = self.env["l10n_cz.ares.connector"]
        for partners in split_every(
            MFCR_BATCH_SIZE, self.filtered("vat").ids, self.browse
        ):
            statuses = connector._get_vat_reliability(partners.mapped("vat"))
            for partner in partners:
                if partner.vat in statuses:
                    partner.is_unreliable_payer = statuses[partner.vat]

    @api.model
    def ares_get_partner_values(self, ico, current_vat):
        """RPC entry point of the "Load from ARES" button of the partner form."""
        values, warning = self.env["l10n_cz.ares.connector"]._prepare_partner_values(
            ico, current_vat
        )
        country = self.env["res.country"].browse(values["country_id"])
        values["country_id"] = {"id": country.id, "display_name": country.display_name}
        return {"values": values, "warning": warning}
