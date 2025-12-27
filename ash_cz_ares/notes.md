==========================================================================
## SLUŽBY MFČR:

Dotaz pro získání bankovních účtů a dalších informací:

```
URL
https://adisrws.mfcr.cz/adistc/axis2/services/rozhraniCRPDPH.rozhraniCRPDPHSOAP

HEADER
SOAPAction: http://adis.mfcr.cz/rozhraniCRPDPH/getStatusNespolehlivySubjektRozsirenyV2

BODY
<?xml version="1.0"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Body><StatusNespolehlivySubjektRozsirenyV2Request xmlns="http://adis.mfcr.cz/rozhraniCRPDPH/"><dic>44012373</dic></StatusNespolehlivySubjektRozsirenyV2Request></SOAP-ENV:Body></SOAP-ENV:Envelope>
```
==========================================================================
## DOCKER
docker run -v "/Users/Zahiro/OneDrive - Ash technology s.r.o/projekty/osh/osh_ashtech/asht.odoo.com:/mnt/extra-addons" -p 8069:8069 --name odoo --link db:db -t odoo -d asht -u l10n_cz_inv_enhanced


==========================================================================
## Odoo credentials - development

### Localhost NTB
master-password: gmjm-ez3a-7qiw
password: odoo
db-name: asht