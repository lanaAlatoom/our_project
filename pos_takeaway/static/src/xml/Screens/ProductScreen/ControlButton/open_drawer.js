/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { useRef } from "@odoo/owl";

class OpenCashDrawerButton extends owl.Component {
    static template = "OpenCashDrawerButton";
    setup() {
        this.popup = useService("popup");
        this.hardwareProxy = useService("hardware_proxy");
        this.OpenCashDrawer = useRef("OpenCashDrawer");
    }

    async onClick() {
        const { confirmed } = await this.popup.add("ConfirmPopup", {
            title: _t('Open Cash Drawer ?'),
            body: _t('Are you sure you want to Open Cash Drawer ?'),
        });

        if (confirmed) {
            this.hardwareProxy.openCashbox();
        }
    }
}

ProductScreen.addControlButton({
    component: OpenCashDrawerButton,
    condition: function () {
        return this.env.pos;
    },
});

export default OpenCashDrawerButton;
