/** @odoo-module **/
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useRef } from "@odoo/owl";

class TakeAwayButton extends ProductScreen {
    static template = "TakeAwayButton";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.TakeAway = useRef("TakeAway");
    }
    async onClick() {
        const SelectedOrder = this.pos.get_order();
        const DeliveryButtonElement = document.querySelector('.DeliveryButtonClass');
        const OrderPhoneButtonElement = document.querySelector('.OrderPhoneButtonClass');
        const TalabatButtonElement = document.querySelector('.TalabatButtonClass'); // Added

        if (SelectedOrder.is_empty()) {
            return alert('Please add product!!');
        } else {
            if (this.TakeAway.el.classList.contains('btn-primary')) {
                this.TakeAway.el.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                SelectedOrder.is_take_away = false;
                SelectedOrder.generate_token = false;
                delete SelectedOrder.token_number;
            } else {
                this.TakeAway.el.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate btn-primary";
                if (DeliveryButtonElement) {
                    DeliveryButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                if (OrderPhoneButtonElement) {
                    OrderPhoneButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                if (TalabatButtonElement) {
                    TalabatButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate"; // Added
                }
                SelectedOrder.is_take_away = true;
                SelectedOrder.is_delivery = false;
                SelectedOrder.is_order_phone = false;
                SelectedOrder.is_talabat = false; // Added
                SelectedOrder.generate_token = true;
                SelectedOrder.token_number = await this.orm.call('pos.order', 'token_generate', [SelectedOrder.uid]);
            }
        }
    }
}

class DeliveryButton extends ProductScreen {
    static template = "DeliveryButton";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.Delivery = useRef("Delivery");
    }
    async onClick() {
        const SelectedOrder = this.pos.get_order();
        const TakeAwayButtonElement = document.querySelector('.TakeAwayButtonClass');
        const OrderPhoneButtonElement = document.querySelector('.OrderPhoneButtonClass');
        const TalabatButtonElement = document.querySelector('.TalabatButtonClass'); // Added

        if (SelectedOrder.is_empty()) {
            return alert('Please add product!!');
        } else {
            if (this.Delivery.el.classList.contains('btn-primary')) {
                this.Delivery.el.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                SelectedOrder.is_delivery = false;
                SelectedOrder.generate_token = false;
                delete SelectedOrder.token_number;
            } else {
                this.Delivery.el.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate btn-primary";
                if (TakeAwayButtonElement) {
                    TakeAwayButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                if (OrderPhoneButtonElement) {
                    OrderPhoneButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                if (TalabatButtonElement) {
                    TalabatButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate"; // Added
                }
                SelectedOrder.is_delivery = true;
                SelectedOrder.is_take_away = false;
                SelectedOrder.is_order_phone = false;
                SelectedOrder.is_talabat = false; // Added
                SelectedOrder.generate_token = true;
                SelectedOrder.token_number = await this.orm.call('pos.order', 'token_generate', [SelectedOrder.uid]);
            }
        }
    }
}

class OrderPhoneButton extends ProductScreen {
    static template = "OrderPhoneButton";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.OrderPhone = useRef("OrderPhone");
    }
    async onClick() {
        const SelectedOrder = this.pos.get_order();
        const TakeAwayButtonElement = document.querySelector('.TakeAwayButtonClass');
        const DeliveryButtonElement = document.querySelector('.DeliveryButtonClass');
        const TalabatButtonElement = document.querySelector('.TalabatButtonClass'); // Added

        if (SelectedOrder.is_empty()) {
            return alert('Please add product!!');
        } else {
            if (this.OrderPhone.el.classList.contains('btn-primary')) {
                this.OrderPhone.el.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                SelectedOrder.is_order_phone = false;
                SelectedOrder.generate_token = false;
                delete SelectedOrder.token_number;
            } else {
                this.OrderPhone.el.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate btn-primary";
                if (TakeAwayButtonElement) {
                    TakeAwayButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                if (DeliveryButtonElement) {
                    DeliveryButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                if (TalabatButtonElement) {
                    TalabatButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate"; // Added
                }
                SelectedOrder.is_order_phone = true;
                SelectedOrder.is_take_away = false;
                SelectedOrder.is_delivery = false;
                SelectedOrder.is_talabat = false; // Added
                SelectedOrder.generate_token = true;
                SelectedOrder.token_number = await this.orm.call('pos.order', 'token_generate', [SelectedOrder.uid]);
            }
        }
    }
}

class TalabatButton extends ProductScreen {
    static template = "TalabatButton";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.Talabat = useRef("Talabat");
    }
    async onClick() {
        const SelectedOrder = this.pos.get_order();
        const TakeAwayButtonElement = document.querySelector('.TakeAwayButtonClass');
        const DeliveryButtonElement = document.querySelector('.DeliveryButtonClass');
        const OrderPhoneButtonElement = document.querySelector('.OrderPhoneButtonClass');

        if (SelectedOrder.is_empty()) {
            return alert('Please add product!!');
        } else {
            if (this.Talabat.el.classList.contains('btn-primary')) {
                this.Talabat.el.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                SelectedOrder.is_talabat = false;
                SelectedOrder.generate_token = false;
                delete SelectedOrder.token_number;
            } else {
                this.Talabat.el.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate btn-primary";
                if (TakeAwayButtonElement) {
                    TakeAwayButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                if (DeliveryButtonElement) {
                    DeliveryButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                if (OrderPhoneButtonElement) {
                    OrderPhoneButtonElement.className = "control-button customer-button btn rounded-0 fw-bolder text-truncate";
                }
                SelectedOrder.is_talabat = true;
                SelectedOrder.is_take_away = false;
                SelectedOrder.is_delivery = false;
                SelectedOrder.is_order_phone = false;
                SelectedOrder.generate_token = true;
                SelectedOrder.token_number = await this.orm.call('pos.order', 'token_generate', [SelectedOrder.uid]);
            }
        }
    }
}

class OpenCashboxButton extends ProductScreen {
    static template = "OpenCashboxButton";
    setup() {
        this.pos = usePos();
        this.hardwareProxy = useService("hardware_proxy");
    }
    onClick() {
        if (this.hardwareProxy && this.hardwareProxy.openCashbox) {
            this.hardwareProxy.openCashbox();
        } else {
            console.error("Hardware proxy or openCashbox method is not available");
        }
    }
}

// Register the components

ProductScreen.addControlButton({
    component: TakeAwayButton,
    condition: function () {
        return this.pos.config.module_pos_restaurant && this.pos.config.is_pos_takeaway;
    },
});

ProductScreen.addControlButton({
    component: DeliveryButton,
    condition: function () {
        return this.pos.config.module_pos_restaurant && this.pos.config.is_pos_delivery;
    },
});

ProductScreen.addControlButton({
    component: OrderPhoneButton,
    condition: function () {
        return this.pos.config.module_pos_restaurant && this.pos.config.is_pos_order_phone;
    },
});

ProductScreen.addControlButton({
    component: TalabatButton,
    condition: function () {
        return this.pos.config.module_pos_restaurant && this.pos.config.is_pos_talabat;
    },
});

ProductScreen.addControlButton({
    component: OpenCashboxButton,
    condition: function () {
        return this.pos.config.module_pos_restaurant && this.pos.config.allow_open_cash_d;
    },
});
