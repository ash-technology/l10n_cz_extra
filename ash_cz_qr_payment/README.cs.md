🇬🇧 [English version](README.md)

# QR platby v českém prostředí 
Modul přidává na faktury QR kód pro rychlou platbu mobilem. Kódy jsou ve formátu SPAYD

* **Způsob zadání bankovního účtu** Česká bankovní účty zadávejte do standardního pole Odoo v českém formátu, např. `123-456/0800`
![Zadání bankovního účtu](static/description/bank_account.png)

* **Zahraniční účty:** Pokud se jedná o zahraniční účty, do stejného pole (standardní pole v Odoo) můžete zadat IBAN.
* **Podpora měny:** Český QR kód se generuje pro faktury v měně CZK. Pro zahraniční platby je ponechán původní QR kód Odoo.

#### Často kladené dotazy (FAQ)
**QR kód se na faktuře negeneruje**
Ujistěte se, že v konfiguraci aplikace **Fakturace** máte zaškrtnutou volbu **QR kódy**
![Nastavení QR kódů](static/description/qr_payment_settings.png)

**QR kód se na faktuře vygeneruje, ale jeho načtení hlásí chybu**
Zkontrolujte, zda máte na hlavní společnosti zadaný bankovní účet pro českou měnu. Podívejte se na část "Způsob zadání bankovního účtu" výše.

---

## O modulu

Tento modul je vyvíjen a spravován společností **[Ash technology s.r.o.](https://www.ashtechnology.eu)**, oficiálním partnerem Odoo v České republice.

Modul je zdarma a open-source. Uvítáme vaši zpětnou vazbu a návrhy na vylepšení – pokud váš nápad pomůže komunitě, rádi ho zapracujeme.

**Kontakt:**
- Web: [www.ashtechnology.eu](https://www.ashtechnology.eu)
- Email: info@ashtechnology.eu

Pro zakázkový vývoj v Odoo nebo větší projekty nás neváhejte kontaktovat.

---

*Odoo je ochranná známka společnosti Odoo S.A.*

