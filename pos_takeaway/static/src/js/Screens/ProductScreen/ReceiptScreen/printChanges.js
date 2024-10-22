import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

async printChanges(cancelled) {
    const orderChange = this.changesToOrder(cancelled);
    let isPrintSuccessful = true;
    const d = new Date();
    let hours = "" + d.getHours();
    hours = hours.length < 2 ? "0" + hours : hours;
    let minutes = "" + d.getMinutes();
    minutes = minutes.length < 2 ? "0" + minutes : minutes;
        for (const printer of this.pos.unwatched.printers) {
            const changes = this._getPrintingCategoriesChanges(
                printer.config.product_categories_ids,
                orderChange
            );
            if (changes["new"].length > 0 || changes["cancelled"].length > 0) {
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
                    time: {
                        hours,
                        minutes,
                    },
                    takeaway: this.is_take_away,
                    delivery: this.is_delivery,
                    order_phone: this.is_order_phone,
                    token_number: this.token_number,
                    talabat: this.is_talabat,
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
    _getPrintingCategoriesChanges(categories, currentOrderChange) {
    return {
        new: currentOrderChange["new"].filter((change) =>
            this.pos.db.is_product_in_category(categories, change["product_id"])
        ),
        cancelled: currentOrderChange["cancelled"].filter((change) =>
            this.pos.db.is_product_in_category(categories, change["product_id"])
        ),
    };



