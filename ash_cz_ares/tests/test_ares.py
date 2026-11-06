import json
from unittest.mock import patch

import requests

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

MFCR_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">'
    "<soapenv:Header/><soapenv:Body>"
    '<StatusNespolehlivyPlatceResponse xmlns="http://adis.mfcr.cz/rozhraniCRPDPH/">'
    '<status odpovedGenerovana="2026-09-28" statusCode="{code}" statusText="{text}"/>'
    "{payers}"
    "</StatusNespolehlivyPlatceResponse></soapenv:Body></soapenv:Envelope>"
)
MFCR_PAYER = '<statusPlatceDPH dic="{dic}" nespolehlivyPlatce="{status}"/>'
ARES_ADDRESS = {
    "nazevObce": "Praha",
    "nazevUlice": "Újezd",
    "cisloDomovni": 450,
    "cisloOrientacni": 40,
    "psc": 11800,
}
ARES_NON_PAYER = {
    "ico": "24148385",
    "obchodniJmeno": "SwimSport s.r.o.",
    "sidlo": ARES_ADDRESS,
    "seznamRegistraci": {
        "stavZdrojeDph": "NEEXISTUJICI",
        "stavZdrojeSkDph": "NEEXISTUJICI",
    },
}
ARES_VAT_PAYER = {
    "ico": "08500045",
    "obchodniJmeno": "Ash technology s.r.o.",
    "sidlo": ARES_ADDRESS,
    "dic": "CZ08500045",
    "seznamRegistraci": {"stavZdrojeDph": "AKTIVNI", "stavZdrojeSkDph": "NEEXISTUJICI"},
}
# Real ARES data: a VAT group member keeps its own DIC with an ended registration
ARES_VAT_GROUP_MEMBER = {
    "ico": "04116364",
    "obchodniJmeno": "Penta Hospitals CZ, s.r.o.",
    "sidlo": ARES_ADDRESS,
    "dic": "CZ04116364",
    "dicSkDph": "CZ699004572",
    "seznamRegistraci": {"stavZdrojeDph": "ZANIKLY", "stavZdrojeSkDph": "AKTIVNI"},
}
ARES_FORMER_PAYER = {
    "ico": "08500045",
    "obchodniJmeno": "Former Payer s.r.o.",
    "sidlo": ARES_ADDRESS,
    "dic": "CZ08500045",
    "seznamRegistraci": {"stavZdrojeDph": "ZANIKLY", "stavZdrojeSkDph": "NEEXISTUJICI"},
}


def _response(content=b"", json_data=None, status_code=200):
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(json_data).encode() if json_data else content
    return response


def _mfcr(status, dic="24148385", code="0", text="OK", other_payers=()):
    payers = "".join(
        MFCR_PAYER.format(dic=payer_dic, status=payer_status)
        for payer_dic, payer_status in [(dic, status), *other_payers]
    )
    body = MFCR_RESPONSE.format(payers=payers, code=code, text=text)
    return _response(content=body.encode())


@tagged("post_install", "-at_install")
class TestAres(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "SwimSport s.r.o.", "vat": "CZ24148385"}
        )

    def _check(self, partners, *responses):
        with patch.object(requests, "post", side_effect=responses) as post:
            partners.action_check_unreliable_vat_payer()
        return post

    def test_dic_not_in_vat_registry_is_not_vat_payer(self):
        self._check(self.partner, _mfcr("NENALEZEN"))
        self.assertEqual(self.partner.is_unreliable_payer, "not_vat_payer")

    def test_reliable_and_unreliable_payer(self):
        self._check(self.partner, _mfcr("NE"))
        self.assertEqual(self.partner.is_unreliable_payer, "reliable")
        self._check(self.partner, _mfcr("ANO"))
        self.assertEqual(self.partner.is_unreliable_payer, "unreliable")

    def test_batch_check_uses_one_request_for_all_partners(self):
        other = self.env["res.partner"].create(
            {"name": "Ash technology s.r.o.", "vat": "CZ08500045"}
        )
        post = self._check(
            self.partner | other,
            _mfcr("NENALEZEN", other_payers=[("08500045", "NE")]),
        )
        self.assertEqual(post.call_count, 1)
        payload = post.call_args.kwargs["data"].decode()
        self.assertIn("<roz:dic>24148385</roz:dic>", payload)
        self.assertIn("<roz:dic>08500045</roz:dic>", payload)
        self.assertEqual(self.partner.is_unreliable_payer, "not_vat_payer")
        self.assertEqual(other.is_unreliable_payer, "reliable")

    def test_batch_check_splits_requests_by_batch_size(self):
        other = self.env["res.partner"].create(
            {"name": "Ash technology s.r.o.", "vat": "CZ08500045"}
        )
        with patch("odoo.addons.ash_cz_ares.models.res_partner.MFCR_BATCH_SIZE", 1):
            post = self._check(
                self.partner | other, _mfcr("NE"), _mfcr("ANO", dic="08500045")
            )
        self.assertEqual(post.call_count, 2)
        self.assertEqual(self.partner.is_unreliable_payer, "reliable")
        self.assertEqual(other.is_unreliable_payer, "unreliable")

    def test_foreign_vat_keeps_status(self):
        self.partner.write({"vat": "DE136695976", "is_unreliable_payer": "reliable"})
        post = self._check(self.partner)
        post.assert_not_called()
        self.assertEqual(self.partner.is_unreliable_payer, "reliable")

    def test_partner_without_vat_keeps_status(self):
        self.partner.write({"vat": False, "is_unreliable_payer": "not_vat_payer"})
        post = self._check(self.partner)
        post.assert_not_called()
        self.assertEqual(self.partner.is_unreliable_payer, "not_vat_payer")

    def test_registry_error_is_reported(self):
        with self.assertRaises(UserError):
            self._check(self.partner, _mfcr("NE", code="2", text="Technical error"))
        self.assertEqual(self.partner.is_unreliable_payer, "not_checked")

    def test_unknown_registry_status_is_reported(self):
        with self.assertRaisesRegex(UserError, "unknown status"):
            self._check(self.partner, _mfcr("MOZNA"))

    def test_malformed_registry_response_is_reported(self):
        with self.assertRaises(UserError):
            self._check(self.partner, _response(content=b"<html>maintenance"))

    def _run_wizard(self, ares_data, *mfcr_responses):
        wizard = self.env["l10n_cz.ares.wizard"].create({"ico": ares_data["ico"]})
        with (
            patch.object(requests, "get", return_value=_response(json_data=ares_data)),
            patch.object(requests, "post", side_effect=mfcr_responses),
        ):
            return wizard.action_fetch_and_create()

    def _editor_values(self, ares_data, current_vat, *mfcr_responses, ico=None):
        with (
            patch.object(requests, "get", return_value=_response(json_data=ares_data)),
            patch.object(requests, "post", side_effect=mfcr_responses),
        ):
            return self.env["res.partner"].ares_get_partner_values(
                ico or ares_data["ico"], current_vat
            )

    def test_wizard_non_payer_gets_no_vat(self):
        action = self._run_wizard(ARES_NON_PAYER)
        partner = self.env["res.partner"].browse(action["res_id"])
        self.assertFalse(partner.vat)
        self.assertEqual(partner.is_unreliable_payer, "not_vat_payer")
        self.assertEqual(partner.street, "Újezd 450/40")

    def test_wizard_vat_payer_gets_dic_and_is_verified(self):
        action = self._run_wizard(ARES_VAT_PAYER, _mfcr("NE", dic="08500045"))
        partner = self.env["res.partner"].browse(action["res_id"])
        self.assertEqual(partner.vat, "CZ08500045")
        self.assertEqual(partner.is_unreliable_payer, "reliable")

    def test_wizard_vat_group_member_gets_group_dic_and_is_verified(self):
        action = self._run_wizard(ARES_VAT_GROUP_MEMBER, _mfcr("NE", dic="699004572"))
        partner = self.env["res.partner"].browse(action["res_id"])
        self.assertEqual(partner.vat, "CZ699004572")
        self.assertEqual(partner.is_unreliable_payer, "reliable")

    def test_wizard_fills_data_and_warns_when_vat_registry_is_down(self):
        action = self._run_wizard(
            ARES_VAT_GROUP_MEMBER, requests.exceptions.ConnectionError("down")
        )
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "warning")
        partner = self.env["res.partner"].browse(action["params"]["next"]["res_id"])
        self.assertEqual(partner.vat, "CZ699004572")
        self.assertEqual(partner.is_unreliable_payer, "not_checked")

    def test_former_vat_payer_gets_no_vat(self):
        result = self._editor_values(ARES_FORMER_PAYER, False)
        self.assertNotIn("vat", result["values"])
        self.assertEqual(result["values"]["is_unreliable_payer"], "not_vat_payer")

    def test_editor_values_use_web_client_many2one_format(self):
        result = self._editor_values(
            ARES_VAT_GROUP_MEMBER, False, _mfcr("NE", dic="699004572"), ico=" 04116364 "
        )
        czech_republic = self.env.ref("base.cz")
        self.assertEqual(
            result["values"]["country_id"],
            {"id": czech_republic.id, "display_name": czech_republic.display_name},
        )
        self.assertEqual(result["values"]["vat"], "CZ699004572")
        self.assertEqual(result["values"]["is_unreliable_payer"], "reliable")
        self.assertFalse(result["warning"])

    def test_editor_values_warn_when_vat_registry_is_down(self):
        result = self._editor_values(
            ARES_VAT_GROUP_MEMBER, False, requests.exceptions.ConnectionError("down")
        )
        self.assertIn("down", result["warning"])
        self.assertEqual(result["values"]["is_unreliable_payer"], "not_checked")

    def test_editor_values_warn_when_vat_registry_response_is_malformed(self):
        result = self._editor_values(
            ARES_VAT_GROUP_MEMBER, False, _response(content=b"<html>maintenance")
        )
        self.assertTrue(result["warning"])
        self.assertEqual(result["values"]["vat"], "CZ699004572")
        self.assertEqual(result["values"]["is_unreliable_payer"], "not_checked")

    def test_editor_keeps_status_of_unchanged_dic_when_vat_registry_is_down(self):
        for current_vat in ("CZ699004572", "CZ 699004572"):
            result = self._editor_values(
                ARES_VAT_GROUP_MEMBER,
                current_vat,
                requests.exceptions.ConnectionError("down"),
            )
            self.assertNotIn("is_unreliable_payer", result["values"])

    def test_editor_never_clears_vat_of_non_payer(self):
        result = self._editor_values(ARES_NON_PAYER, "CZ24148385")
        self.assertNotIn("vat", result["values"])
        self.assertEqual(result["values"]["is_unreliable_payer"], "not_vat_payer")

    def test_short_ico_is_zero_padded(self):
        with patch.object(
            requests, "get", return_value=_response(json_data=ARES_NON_PAYER)
        ) as get:
            result = self.env["res.partner"].ares_get_partner_values("123", False)
        self.assertTrue(get.call_args.args[0].endswith("/00000123"))
        self.assertEqual(result["values"]["company_registry"], "00000123")

    def test_house_number_letter_is_kept(self):
        data = dict(
            ARES_NON_PAYER, sidlo=dict(ARES_ADDRESS, cisloOrientacniPismeno="a")
        )
        result = self._editor_values(data, False)
        self.assertEqual(result["values"]["street"], "Újezd 450/40a")

    def test_missing_address_parts_give_empty_values(self):
        data = dict(ARES_NON_PAYER, sidlo=None, seznamRegistraci=None)
        result = self._editor_values(data, False)
        self.assertEqual(result["values"]["street"], "")
        self.assertEqual(result["values"]["zip"], "")
        self.assertEqual(result["values"]["is_unreliable_payer"], "not_vat_payer")

    def test_empty_or_invalid_ico_is_rejected_without_request(self):
        for ico in ("12AB", "", "123456789"):
            with patch.object(requests, "get") as get, self.assertRaises(UserError):
                self.env["res.partner"].ares_get_partner_values(ico, False)
            get.assert_not_called()

    def test_ico_not_found_in_ares_is_reported(self):
        with (
            patch.object(requests, "get", return_value=_response(status_code=404)),
            self.assertRaisesRegex(UserError, "not found in ARES"),
        ):
            self.env["res.partner"].ares_get_partner_values("24148385", False)

    def test_malformed_ares_response_is_reported(self):
        with (
            patch.object(
                requests, "get", return_value=_response(content=b"<html>maintenance")
            ),
            self.assertRaises(UserError),
        ):
            self.env["res.partner"].ares_get_partner_values("24148385", False)

    def test_missing_business_name_is_reported(self):
        data = dict(ARES_NON_PAYER, obchodniJmeno="")
        with (
            patch.object(requests, "get", return_value=_response(json_data=data)),
            self.assertRaisesRegex(UserError, "no business name"),
        ):
            self.env["res.partner"].ares_get_partner_values("24148385", False)

    def test_connection_error_message_is_translated(self):
        self.env["res.lang"]._activate_lang("cs_CZ")
        connector = self.env["l10n_cz.ares.connector"].with_context(lang="cs_CZ")
        with (
            patch.object(
                requests, "get", side_effect=requests.exceptions.ConnectionError("down")
            ),
            self.assertRaises(UserError) as error,
        ):
            connector._fetch_ares_data("24148385")
        self.assertEqual(str(error.exception), "Chyba spojení s ARES: down")
