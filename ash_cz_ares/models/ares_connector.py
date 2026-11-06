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
# MFCR answers only the first 100 DICs of a request
MFCR_BATCH_SIZE = 100
MFCR_RELIABILITY = {
    "ANO": "unreliable",
    "NE": "reliable",
    # MFCR answers NENALEZEN for any DIC missing from the VAT payer registry
    "NENALEZEN": "not_vat_payer",
}


class AresConnector(models.AbstractModel):
    _name = "l10n_cz.ares.connector"
    _description = "Czech Public Registers Connector (ARES, MFČR)"

    @api.model
    def _fetch_ares_data(self, ico):
        try:
            response = requests.get(ARES_URL.format(ico=ico), timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        # requests < 2.27 raises a plain ValueError on invalid JSON
        except (requests.exceptions.RequestException, ValueError) as e:
            raise UserError(
                self.env._("ARES Connection Error: %(error)s", error=str(e))
            ) from e

    @api.model
    def _prepare_partner_values(self, ico, current_vat):
        ico = (ico or "").replace(" ", "")
        if not re.fullmatch(r"\d{1,8}", ico):
            raise UserError(self.env._("IČ must consist of 1 to 8 digits."))
        ico = ico.zfill(8)
        data = self._fetch_ares_data(ico)
        if not data:
            raise UserError(self.env._("IČ %(ico)s was not found in ARES.", ico=ico))
        if not data.get("obchodniJmeno"):
            raise UserError(
                self.env._("ARES returned no business name for IČ %(ico)s.", ico=ico)
            )

        address = data.get("sidlo") or {}
        full_street = (
            f"{address.get('nazevUlice') or ''} {address.get('cisloDomovni') or ''}"
        )
        if address.get("cisloOrientacni"):
            full_street += f"/{address['cisloOrientacni']}"
            full_street += address.get("cisloOrientacniPismeno") or ""
        values = {
            "name": data["obchodniJmeno"],
            "company_registry": ico,
            "street": full_street.strip(),
            "city": address.get("nazevObce"),
            "zip": str(address.get("psc") or ""),
            "country_id": self.env.ref("base.cz").id,
            "is_company": True,
        }
        # A VAT group member keeps its own DIC in ARES with an ended registration,
        # only the group DIC is valid for VAT
        registrations = data.get("seznamRegistraci") or {}
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
            values["is_unreliable_payer"] = self._get_vat_reliability([dic])[dic]
        except UserError as e:
            # Deliberate fallback: keep the ARES data so the user can re-run the check;
            # an unchanged DIC keeps its previous result (e.g. unreliable).
            warning = self.env._(
                "VAT payer reliability could not be verified, verify it later "
                "manually: %(error)s",
                error=str(e),
            )
            if dic != (current_vat or "").replace(" ", "").upper():
                values["is_unreliable_payer"] = "not_checked"
        return values, warning

    @api.model
    def _get_vat_reliability(self, vats):
        """Return {vat: status} for the Czech DICs among at most MFCR_BATCH_SIZE
        VAT numbers; other VAT numbers are left out."""
        vat_dics = {}
        for vat in vats:
            match = re.fullmatch(r"(?:CZ)?(\d{8,10})", vat.replace(" ", "").upper())
            if match:
                vat_dics[vat] = match.group(1)
        if not vat_dics:
            return {}

        dic_elements = "".join(
            f"<roz:dic>{dic}</roz:dic>" for dic in dict.fromkeys(vat_dics.values())
        )
        soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:roz="{MFCR_NAMESPACE}">
    <soapenv:Header/>
    <soapenv:Body>
        <roz:StatusNespolehlivyPlatceRequest>{dic_elements}</roz:StatusNespolehlivyPlatceRequest>
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
            root = etree.fromstring(response.content)
        except (requests.exceptions.RequestException, etree.XMLSyntaxError) as e:
            raise UserError(
                self.env._(
                    "VAT registry (MFČR) Connection Error: %(error)s", error=str(e)
                )
            ) from e

        namespaces = {"r": MFCR_NAMESPACE}
        status = root.find(".//r:status", namespaces)
        if status is None or status.get("statusCode") != "0":
            raise UserError(
                self.env._(
                    "VAT registry (MFČR) returned an error: %(error)s",
                    error=status.get("statusText") if status is not None else "",
                )
            )
        payers = {
            payer.get("dic"): payer.get("nespolehlivyPlatce")
            for payer in root.iterfind(".//r:statusPlatceDPH", namespaces)
        }
        result = {}
        for vat, dic in vat_dics.items():
            value = payers.get(dic)
            if value not in MFCR_RELIABILITY:
                raise UserError(
                    self.env._(
                        "VAT registry (MFČR) returned an unknown status: %(status)s",
                        status=value,
                    )
                )
            result[vat] = MFCR_RELIABILITY[value]
        return result
