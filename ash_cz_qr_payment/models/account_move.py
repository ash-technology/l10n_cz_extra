import qrcode
import base64
import io
from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_cz_qr_code_base64(self):
        """ Returns Base64 PNG image for the invoice PDF """
        self.ensure_one()
        if self.currency_id.name != 'CZK':
            return False

        # Find bank: 1. Matching CZK, 2. No currency set (default)
        bank = self.company_id.partner_id.bank_ids.filtered(lambda b: b.currency_id == self.currency_id)[:1]
        if not bank:
            bank = self.company_id.partner_id.bank_ids.filtered(lambda b: not b.currency_id)[:1]
        
        if not bank or not bank.acc_number:
            return False

        # Build SPAYD string
        iban = self.cz_to_iban(bank.acc_number)
        amount = '%.2f' % self.amount_residual
        vs = ''.join(filter(str.isdigit, self.payment_reference or ''))[-10:]
        
        spayd = f"SPD*1.0*ACC:{iban}*AM:{amount}*CC:CZK*X-VS:{vs}"

        # Generate QR Image
        qr = qrcode.make(spayd)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def cz_to_iban(self, acc_number):
        """
        Converts '123-456/0800' or '456/0800' to a valid CZ IBAN.
        """
        if not acc_number:
            return ""
        
        # Clean the input
        clean_acc = acc_number.replace(" ", "")
        
        # If already an IBAN, return it
        if clean_acc.upper().startswith('CZ'):
            return clean_acc.upper()
    
        try:
            # Split into [prefix-main, bank_code]
            parts = clean_acc.split('/')
            if len(parts) != 2:
                return clean_acc # Fallback
                
            bank_code = parts[1]
            account_parts = parts[0].split('-')
            
            if len(account_parts) == 2:
                prefix = account_parts[0].zfill(6)
                main = account_parts[1].zfill(10)
            else:
                prefix = "000000"
                main = account_parts[0].zfill(10)
    
            # 1. Start with Bank Code + Prefix + Main + Country Number (CZ=12, 35=Z) + 00
            # Czech Republic code is 123500 (12 for C, 35 for Z)
            check_string = f"{bank_code}{prefix}{main}123500"
            
            # 2. Calculate checksum
            checksum = 98 - (int(check_string) % 97)
            checksum_str = str(checksum).zfill(2)
            
            return f"CZ{checksum_str}{bank_code}{prefix}{main}"
        except Exception:
            return clean_acc