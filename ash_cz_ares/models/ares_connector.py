import requests
from odoo import models, api, _
from odoo.exceptions import UserError

class AresConnector(models.AbstractModel):
    _name = 'l10n_cz.ares.connector'
    _description = 'Centralized ARES API Logic'

    MFCR_SOAP_URL = "https://adisrws.mfcr.cz/dpr/axis2/services/rozhraniCRPDPH.rozhraniCRPDPHSOAP"
    MFCR_NAMESPACE = "http://adis.mfcr.cz/rozhraniCRPDPH/"

    @api.model
    def fetch_ares_data(self, ico):
        """Fetches company details from ARES by ICO"""
        url = f"https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/{ico}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            raise UserError(_("ARES Connection Error: %s") % str(e))

    @api.model
    def check_unreliable_payer(self, vat_id):
        """
        Check if a VAT payer is unreliable using the official MFČR SOAP service.
        
        Returns:
            True - if the payer is unreliable (nespolehlivý plátce)
            False - if the payer is reliable or not found in VAT payer registry
            None - if an error occurred during the check
        """
        if not vat_id:
            return False
        
        # Extract DIČ - remove 'CZ' prefix and whitespace, keep only digits
        dic = vat_id.upper().replace('CZ', '').strip()
        
        # Validate DIČ format (1-10 digits)
        if not dic.isdigit() or len(dic) < 1 or len(dic) > 10:
            return False
        
        # Build SOAP request
        soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:roz="{self.MFCR_NAMESPACE}">
    <soapenv:Header/>
    <soapenv:Body>
        <roz:StatusNespolehlivyPlatceRequest>
            <roz:dic>{dic}</roz:dic>
        </roz:StatusNespolehlivyPlatceRequest>
    </soapenv:Body>
</soapenv:Envelope>"""

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://adis.mfcr.cz/rozhraniCRPDPH/getStatusNespolehlivyPlatce',
        }

        try:
            response = requests.post(
                self.MFCR_SOAP_URL,
                data=soap_envelope.encode('utf-8'),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return self._parse_unreliable_payer_response(response.text)
            
            return None
            
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None

    @api.model
    def _parse_unreliable_payer_response(self, xml_response):
        """
        Parse SOAP response to extract nespolehlivyPlatce attribute.
        
        Returns:
            True - if nespolehlivyPlatce="ANO"
            False - if nespolehlivyPlatce="NE" or "NENALEZEN"
            None - if parsing failed
        """
        try:
            import re
            
            # Look for nespolehlivyPlatce attribute in the response
            # The attribute can be in statusPlatceDPH element
            match = re.search(r'nespolehlivyPlatce\s*=\s*["\'](\w+)["\']', xml_response)
            
            if match:
                status = match.group(1).upper()
                if status == 'ANO':
                    return True
                elif status in ('NE', 'NENALEZEN'):
                    return False
            
            # If no statusPlatceDPH found, check if the response indicates no results
            # This can happen when DIČ is not registered as VAT payer
            if 'statusPlatceDPH' not in xml_response:
                return False
                
            return None
            
        except Exception:
            return None