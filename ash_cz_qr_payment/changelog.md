## 19.0.3.0.0 — 2026-11-11
- The variable symbol is the payment reference of the invoice, without changes, instead of the digits of the invoice number. On vendor bills, the QR code in the payment dialog had the digits of the internal bill number as the variable symbol and the vendor's variable symbol as the message.
- The message is the invoice number, on vendor bills and customer credit notes the bill reference (the vendor's invoice number).
- The QR code takes the due date and the other data from the invoice being paid; previously the invoice was searched by the payment reference and could be another invoice with the same reference.
- This differs from Odoo 20, whose Czech localization keeps the previous behavior.
- Upgrade note: set the Communication Standard of the sales journals to "Numbers only" and correct the payment reference of unpaid invoices that is not made of digits; see "Upgrading to version 19.0.3.x" in the README.

## 19.0.2.1.0 — 2026-11-01
- For a Czech IBAN, the invoice prints the account number in the Czech format (e.g. 19-2000145399/0800) and the IBAN on the next line, so that customers can pay by hand also in banking apps that do not accept an IBAN. Odoo 20 prints only the IBAN, so this line disappears when the module is uninstalled.
- Upgrade guide: added the step to enable the "QR Codes" setting, which version 19.0.1.x did not need.
- Documentation: how to fix copies of the invoice report (e.g. made in Studio), which module updates don't reach: the Czech account number, and what to change before uninstalling the module.

## 19.0.2.0.0 — 2026-10-01
- The QR Platba code is now a standard Odoo payment QR method ("CZK QR"), identical to the one built into Odoo 20. It is shown in the usual place of the invoice PDF and the customer portal and can be selected in the "Payment QR-code" field of the invoice.
- The QR code follows the company's "QR Codes" setting and is no longer shown on credit notes and paid invoices. It always pays to the invoice's Recipient Bank, the same account that is printed on the invoice (on vendor bills the vendor's account, no longer your own).
- The code now also contains the due date, the payment reference as message and the recipient name; the variable symbol is made of the digits of the invoice number.
- Upgrade note: read "Upgrading from version 19.0.1.x" in the README first. The company bank account must be an IBAN (the Czech format 123-456/0800 is no longer converted), trusted ("Send Money") and, with several accounts, have its currency set; invoice report copies made with 19.0.1.x (e.g. in Studio) must be fixed; the variable symbol now comes from the invoice number. Upgrade the module right after replacing its files (Apps › Upgrade or `-u ash_cz_qr_payment`); until then printing invoices fails. Version 19.0.1.0.0 stays available as the tag `ash_cz_qr_payment-19.0.1.0.0`.

## 19.0.1.0.0
- First release: SPAYD QR codes on CZK invoices.
