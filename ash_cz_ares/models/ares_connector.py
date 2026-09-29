import re

import requests
from lxml import etree

from odoo import api, models
from odoo.exceptions import UserError

ARES_URL = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/{ico}"
MFCR_SOAP_URL = (
    "https://adisrws.mfcr.cz/dpr/axis2/services/rozhraniCRPDPH.rozhraniCRPDPHSOAP"
)
MFCR_NAMESPACE = "http://adis.mfcr.cz/rozhraniCRPDPH/"
MFCR_RELIABILITY = {
    "ANO": "unreliable",
    "NE": "reliable",
    # MFCR answers NENALEZEN for any DIC missing from the VAT payer registry
    "NENALEZEN": "not_vat_payer",
}


class AresConnector(models.AbstractModel):
    _name = "l10n_cz.ares.connector"
    _description = "Centralized ARES API Logic"

    @api.model
    def fetch_ares_data(self, ico):
        try:
            response = requests.get(ARES_URL.format(ico=ico), timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise UserError(
                self.env._("ARES Connection Error: %(error)s", error=str(e))
            ) from e
        return response.json()

    @api.model
    def _prepare_partner_values(self, ico, current_vat):
        ico = (ico or "").replace(" ", "")
        if not re.fullmatch(r"\d{1,8}", ico):
            raise UserError(self.env._("IČ must consist of 1 to 8 digits."))
        ico = ico.zfill(8)
        data = self.fetch_ares_data(ico)
        if not data:
            raise UserError(self.env._("IČ %(ico)s was not found in ARES.", ico=ico))
        if not data.get("obchodniJmeno"):
            raise UserError(
                self.env._("ARES returned no business name for IČ %(ico)s.", ico=ico)
            )

        address = data.get("sidlo", {})
        full_street = (
            f"{address.get('nazevUlice', '')} {address.get('cisloDomovni', '')}"
        )
        if address.get("cisloOrientacni"):
            full_street += f"/{address['cisloOrientacni']}"
        cz_country = self.env.ref("base.cz")
        values = {
            "name": data["obchodniJmeno"],
            "company_registry": ico,
            "street": full_street.strip(),
            "city": address.get("nazevObce"),
            "zip": str(address.get("psc", "")),
            "country_id": cz_country.id,
            "is_company": True,
        }
        # A VAT group member keeps its own DIC in ARES with an ended registration,
        # only the group DIC is valid for VAT
        registrations = data.get("seznamRegistraci", {})
        dic = False
        if registrations.get("stavZdrojeSkDph") == "AKTIVNI":
            dic = data.get("dicSkDph")
        elif registrations.get("stavZdrojeDph") == "AKTIVNI":
            dic = data.get("dic")
        warning = False
        if not dic:
            values["is_unreliable_payer"] = "not_vat_payer"
            return values, warning

        values["vat"] = dic
        try:
            values["is_unreliable_payer"] = self._get_vat_reliability(dic)
        except UserError as e:
            # Deliberate fallback: keep the ARES data so the user can re-run the check;
            # an unchanged DIC keeps its previous result (e.g. unreliable).
            warning = self.env._(
                "VAT payer reliability could not be verified, verify it later "
                "manually: %(error)s",
                error=str(e),
            )
            if dic != current_vat:
                values["is_unreliable_payer"] = "not_checked"
        return values, warning

    @api.model
    def _get_vat_reliability(self, vat):
        match = re.fullmatch(r"(?:CZ)?(\d{8,10})", vat.replace(" ", "").upper())
        if not match:
            return "not_checked"

        soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:roz="{MFCR_NAMESPACE}">
    <soapenv:Header/>
    <soapenv:Body>
        <roz:StatusNespolehlivyPlatceRequest>
            <roz:dic>{match.group(1)}</roz:dic>
        </roz:StatusNespolehlivyPlatceRequest>
    </soapenv:Body>
</soapenv:Envelope>"""
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f"{MFCR_NAMESPACE}getStatusNespolehlivyPlatce",
        }
        try:
            response = requests.post(
                MFCR_SOAP_URL,
                data=soap_envelope.encode("utf-8"),
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise UserError(
                self.env._(
                    "VAT registry (MFČR) Connection Error: %(error)s", error=str(e)
                )
            ) from e

        root = etree.fromstring(response.content)
        namespaces = {"r": MFCR_NAMESPACE}
        status = root.find(".//r:status", namespaces)
        if status is None or status.get("statusCode") != "0":
            raise UserError(
                self.env._(
                    "VAT registry (MFČR) returned an error: %(error)s",
                    error=status.get("statusText") if status is not None else "",
                )
            )
        payer = root.find(".//r:statusPlatceDPH", namespaces)
        value = payer.get("nespolehlivyPlatce") if payer is not None else None
        if value not in MFCR_RELIABILITY:
            raise UserError(
                self.env._(
                    "VAT registry (MFČR) returned an unknown status: %(status)s",
                    status=value,
                )
            )
        return MFCR_RELIABILITY[value]
