/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useRef, Component } from "@odoo/owl";

class OpenCashDrawerButton extends Component {
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.popup = useService("popup");
        this.OpenCashDrawer = useRef("OpenCashDrawer");
    }

    async onClick() {
        const { confirmed } = await this.popup.add('ConfirmPopup', {
            title: _t('Open Cash Drawer?'),
            body: _t('Are you sure you want to open the cash drawer?'),
        });

        if (confirmed) {
            this.sendGetRequest();
        }
    }

    sendGetRequest() {
        const url = 'https://localhost:8443/open_cash_drawer';

        const requestOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        fetch(url, requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
}

OpenCashDrawerButton.template = "OpenCashDrawerButton";

ProductScreen.addControlButton({
    component: OpenCashDrawerButton,
    condition: function () {
        return this.pos;
    },
});

export default OpenCashDrawerButton;
