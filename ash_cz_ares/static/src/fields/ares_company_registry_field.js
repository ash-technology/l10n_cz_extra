import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { CharField, charField } from "@web/views/fields/char/char_field";

export class AresCompanyRegistryField extends CharField {
    static template = "ash_cz_ares.AresCompanyRegistryField";

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    async onFetchFromAres() {
        // Read the input directly: the typed value may not be committed to the record yet
        const result = await this.orm.call("res.partner", "ares_get_partner_values", [
            this.input.el.value,
            this.props.record.data.vat,
        ]);
        await this.props.record.update(result.values);
        if (result.warning) {
            this.notification.add(result.warning, { type: "warning", sticky: true });
        }
    }
}

export const aresCompanyRegistryField = {
    ...charField,
    component: AresCompanyRegistryField,
    additionalClasses: ["d-flex", "align-items-center", "gap-2"],
};

registry.category("fields").add("ares_company_registry", aresCompanyRegistryField);
