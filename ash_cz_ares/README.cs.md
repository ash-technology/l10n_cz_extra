🇬🇧 [English version](README.md)

# Modul Veřejné rejstříky (ARES, Registr plátců DPH)
## 1. Aktualizace základních údajů
Modul umožňuje založit nového partnera podle IČ, nebo v případě, že používáte funkci "Partner autocomplete", ověřit adresu a název podle ARES.

* **Kde najdete:** V aplikaci Kontakty v horní liště: **Veřejné rejstříky > Vytvořit z ARES**.
![Vytvořit z ARES](static/description/new_from_ares_menu.png)
* Funkce je dostupná také z aplikace **Fakturace z menu Zákazníci**
* Poslední možností je zadat IČ přímo v editoru kontaktu a kliknout na tlačítko **Načíst z ARES** vedle IČ:
![Aktualizovat z ARES](static/description/new_from_ares_form.png)
Pokud už IČ má jiný kontakt, systém vás na to upozorní. Pole IČ je vidět u českých partnerů a u partnerů bez vyplněné země.

* **Funkčnost:** Stačí zadat osmimístné IČ. Systém se spojí s registrem ARES a automaticky vyplní:
    * Obchodní jméno
    * Kompletní adresu (včetně správného formátování ulice a čísel)
    * DIČ (pokud je subjekt plátcem)
    * IČ do pole "IČ"

* **Aktualizace stávajícího kontaktu:**
V editoru kontaktu zkontrolujte IČ a klikněte na **Načíst z ARES** podobně, jako je to popsáno výše. Systém údaje na vašem kontaktu přepíše hodnotami z ARES. Údaje se doplní do formuláře a uloží se až uložením kontaktu.

* **Skupinoví plátci DPH:**
Pokud je společnost členem skupiny DPH, načte se z ARES do pole "DIČ" DIČ skupiny (např. CZ699004572), protože vlastní DIČ člena skupiny pro DPH neplatí. Spolehlivost se pak ověřuje u DIČ skupiny.

## 2. Ověřování spolehlivosti plátce DPH
U každého českého partnera systém sleduje stav spolehlivosti v registru DPH:
* **Neověřeno (šedá):** Kontrola u tohoto partnera zatím neproběhla.
* **Spolehlivý plátce (zelená):** Subjekt je řádně registrovaný a bez negativního záznamu.
* **Neplátce DPH (oranžová):** Subjekt není v registru plátců DPH. Kontakty založené z ARES dostanou tento stav automaticky a nemají vyplněné DIČ.
* Při načtení z ARES se plátci DPH ověří automaticky. Pokud je registr plátců DPH nedostupný, údaje se přesto vyplní, stav zůstane „Neověřeno“ a systém vás vyzve, abyste později spustili **Ověřit plátce DPH**.
* **Nespolehlivý plátce (červená):** Subjekt je označen jako nespolehlivý. V tomto případě se na kartě partnera zobrazí výrazná **červená stuha (ribbon)**.
![Ověření spolehlivosti](static/description/check_reliability.png)

## 3. Hromadné akce
* **Hromadná kontrola:** V seznamu kontaktů (List View) můžete označit více záznamů a přes tlačítko **Akce > Zkontrolovat spolehlivost plátce DPH** aktualizovat stav všech najednou.
![Hromadné ověření spolehlivosti](static/description/check_reliability_batch.png)

## Často kladené dotazy (FAQ)

**Proč se mi nezobrazuje tlačítko "Vytvořit z ARES"?**
Ujistěte se, že máte nainstalovanou aplikaci Fakturace nebo Kontakty a že váš uživatel má příslušná oprávnění.

**Jak systém pozná nespolehlivého plátce?**
Systém volá oficiální API registru plátců DPH (veřejná část je dostupná na adrese https://adisspr.mfcr.cz/adis/jepo/epo/dpr/apl_ramce.htm?R=/dpr/DphReg?ZPRAC=FDPHI1%26poc_dic=2%26OK=Zobraz)

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
