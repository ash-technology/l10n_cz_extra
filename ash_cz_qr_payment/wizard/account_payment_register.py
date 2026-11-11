from odoo import api, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.depends("line_ids")
    def _compute_qr_code(self):
        # Pass the paid invoice to the CZK QR method
        # (res.partner.bank._get_qr_vals); a payment of several invoices has none.
        for wizard in self:
            move = wizard.line_ids.move_id
            move_id = move.id if len(move) == 1 else False
            super(
                AccountPaymentRegister, wizard.with_context(ash_cz_qr_move_id=move_id)
            )._compute_qr_code()
