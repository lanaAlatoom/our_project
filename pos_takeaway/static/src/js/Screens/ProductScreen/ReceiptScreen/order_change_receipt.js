/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";
import { formatDate } from "@web/core/l10n/dates";


patch(Order.prototype, {
    setup(_defaultObj) {
        super.setup(...arguments);
    },

    async printChanges(cancelled) {
        const orderChange = this.changesToOrder(cancelled);
        let isPrintSuccessful = true;
        const { DateTime } = luxon;

        for (const printer of this.pos.unwatched.printers) {
            const changes = this._getPrintingCategoriesChanges(
                printer.config.product_categories_ids,
                orderChange
            );
            if (changes["new"].length > 0 || changes["cancelled"].length > 0) {
                const dateTime = DateTime.local();
                const printingChanges = {
                    new: changes["new"],
                    cancelled: changes["cancelled"],
                    table_name: this.pos.config.module_pos_restaurant
                        ? this.getTable().name
                        : false,
                    floor_name: this.pos.config.module_pos_restaurant
                        ? this.getTable().floor.name
                        : false,
                    name: this.name || "unknown order",
                    time: dateTime.toFormat("HH:mm"),
                    printerName: printer.config.name,
                    takeaway: this.pos.selectedOrder.is_take_away,
                    delivery: this.pos.selectedOrder.is_delivery,
                    order_phone: this.pos.selectedOrder.is_order_phone,
                    token_number: this.pos.selectedOrder.token_number,
                    talabat: this.pos.selectedOrder.is_talabat,
                    cashier: this.cashier.name,
                    date: formatDate(dateTime)
                };
                const receipt = renderToElement("point_of_sale.OrderChangeReceipt", {
                    changes: printingChanges,
                });
                const result = await printer.printReceipt(receipt);
                if (!result.successful) {
                    isPrintSuccessful = false;
                }
            }
        }

        return isPrintSuccessful;
    }
});
