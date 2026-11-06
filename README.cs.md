🇬🇧 [English version](README.md)

# Česká lokalizace Odoo – Rozšíření (ARES, QR platby a ověřování plátců)

Tento repozitář obsahuje moduly rozšiřující standardní systém Odoo o specifické funkce pro český trh. Cílem je automatizovat zakládání partnerů, zajistit správnost fakturačních údajů a zjednodušit platební procesy.

## Dostupné moduly
* [Veřejné rejstříky (ARES, Registr plátců DPH)](./ash_cz_ares) (ash_cz_ares)
* [České QR kódy pro bankovní platby](./ash_cz_qr_payment) (ash_cz_qr_payment)

## Instalace modulů
V Odoo v modulu Aplikace nejprve ve vyhledávacím poli vypněte filtr na "Aplikace" a následně do něj zadejte text "ash_cz". To zobrazí všechny moduly z tohoto balíčku. Výsledek bude vypadat podobně jako na obrázku:

![Instalace modulů](installation.png)

Následně už jen kliknete na "Aktivovat" u těch modulů, které chcete nainstalovat.

## Aktualizace modulů

Po nahrání nové verze moduly aktualizujte: v Aplikacích otevřete modul a klikněte na **Upgrade**, nebo restartujte Odoo s parametrem `-u ash_cz_ares,ash_cz_qr_payment`. Odoo.sh to udělá automaticky, když se změní verze modulu. Do aktualizace mohou některé funkce (např. tisk faktur) hlásit chybu.

Verze 19.0.2.x modulu `ash_cz_qr_payment` mění požadavky na bankovní účet a týká se i kopií šablony faktury: před jejím upgradem si přečtěte [poznámky k přechodu](ash_cz_qr_payment/README.cs.md#přechod-z-verze-1901x). Pokud tisknete faktury z kopie šablony faktury (např. zduplikované ve Studiu), aktualizace modulu se do kopie nepropíší: viz [Kopie šablony faktury](ash_cz_qr_payment/README.cs.md#kopie-šablony-faktury-např-studio).

## Vývoj

Moduly vyvíjíme s pomocí AI agentů pod lidskou kontrolou. Konvence a prohlášení o využití AI jsou v souboru [AGENTS.md](AGENTS.md).

---

## O projektu

Tyto moduly jsou vyvíjeny a spravovány společností **[Ash technology s.r.o.](https://www.ashtechnology.eu)**, oficiálním partnerem Odoo v České republice.

Moduly jsou zdarma a open-source. Uvítáme vaši zpětnou vazbu a návrhy na vylepšení – pokud váš nápad pomůže komunitě, rádi ho zapracujeme.

**Kontakt:**
- Web: [www.ashtechnology.eu](https://www.ashtechnology.eu)
- Email: info@ashtechnology.eu

Pro zakázkový vývoj v Odoo nebo větší projekty nás neváhejte kontaktovat.

---

*Odoo je ochranná známka společnosti Odoo S.A.*
