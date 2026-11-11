# AGENTS.md

Guidance for AI coding agents working on this repository, and a statement of how AI is used in its development.

## AI-assisted development

Parts of this repository are developed with the help of AI coding agents. A human maintainer reviews, tests and takes responsibility for every change; AI tools are never listed as authors.

Commits with any AI involvement carry an `Assisted-by:` trailer naming the tool or model, one line per tool (following the [OCA AI policy](https://github.com/OCA/.github/blob/master/AI_POLICY.md)):

```text
Assisted-by: Claude Code
```

Never use `Co-authored-by:` for AI tools.

## Repository

Odoo 19.0 addons for the Czech market:

| Module | Purpose |
|---|---|
| `ash_cz_ares` | Create and update partners from the ARES business register by IČ; check VAT payer reliability in the MFČR registry |
| `ash_cz_qr_payment` | Czech QR Platba (SPAYD) payment QR code on CZK invoices, as a standard `res.partner.bank` QR method |

## Commands

```bash
pre-commit run -a

odoo-bin -d <test_db> -i ash_cz_ares,ash_cz_qr_payment \
    --test-tags /ash_cz_ares,/ash_cz_qr_payment --stop-after-init
```

Run tests on a fresh database. A test run must log no warnings.

## Conventions

- Follow the OCA guidelines and the Odoo 19 framework; extend core behaviour (`_inherit`, framework hooks) instead of replacing views or copying core code.
- Keep the code minimal: no speculative options, no one-off helpers, no broad `except Exception`, no silent fallbacks.
- Commit messages in English with OCA tags: `[ADD]`, `[IMP]`, `[FIX]`, `[REF]`, `[MIG]`, e.g. `[FIX] ash_cz_ares: ...`.
- A version bump goes with a `changelog.md` entry of the module in the same commit; renaming a stored field or xmlid needs a migration script in `migrations/<version>/`.
- User-facing strings use `self.env._()`; Czech translations live in `i18n/cs.po`, the template in `i18n/<module>.pot`.

## Pitfalls

- Tests must never call ARES or MFČR: mock `requests.get` / `requests.post`.
- Do not add or rename stored fields on `res.partner` without a strong reason: until the module is upgraded, every login reads the partner columns and fails, so the Apps › Upgrade button cannot be reached.
- MFČR answers at most 100 DICs per request (`MFCR_BATCH_SIZE`).
- A VAT group member has its own DIC with an ended registration in ARES; only the group DIC (`dicSkDph`) is valid.
- `ash_cz_qr_payment` follows the `czk_qr` method of `l10n_cz` in Odoo 20.0, so that migrating to 20.0 means uninstalling it. Deviations, documented in the README: the Czech account number printed next to the IBAN on the invoice (`_get_cz_acc_number`); the invoice is passed to the QR method in the context (`ash_cz_qr_move_id`) instead of being searched, the variable symbol is its `payment_reference` and the message its `ref` on outgoing payments, its number otherwise. The QR code needs a CZK invoice and an IBAN-type, trusted Recipient Bank, which Odoo picks from the company bank accounts, preferring the invoice currency and trusted accounts (linking an account to a bank journal trusts it).
