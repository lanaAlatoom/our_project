odoo.define('bi_pos_gift_receipt.ReceiptScreen', function(require) {
    "use strict";

    const Registries = require('point_of_sale.Registries');
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');

    const BiReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {

            giftCard() {
                let self = this;
                let order = this.env.pos.get_order();
                let orderlines = order.get_orderlines();
                let product_data = { orderlines }
                if (product_data) {
                    this.product_data = product_data;
                }                
                this.orderDone();
                if(order.split_data){
                    this.barcode = order.barcode;
                    this.split_data_confirm = true
                    this.split_data = order.split_data
                } else{
                    this.barcode = false;
                    this.split_data_confirm = false
                    this.split_data = false
                }
                this.showTempScreen('GiftScreen',{'receiptLineData':this.product_data, 'orderlines':orderlines,
                                'confirm_split_data':this.split_data_confirm,
                                'split_data': this.split_data, 'barcode':this.barcode});
            }
        };

    Registries.Component.extend(ReceiptScreen, BiReceiptScreen);

    return ReceiptScreen;

});
