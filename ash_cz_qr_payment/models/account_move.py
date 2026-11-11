from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _generate_qr_code(self, silent_errors=False):
        # Pass the invoice to the CZK QR method (res.partner.bank._get_qr_vals)
        return super(
            AccountMove, self.with_context(ash_cz_qr_move_id=self.id)
        )._generate_qr_code(silent_errors=silent_errors)
