odoo.define('bi_pos_gift_receipt.GiftScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const { useRef } = owl;

    const GiftScreen = (ReceiptScreen) => {
        class GiftScreen extends ReceiptScreen {
            setup() {
                super.setup();
            }
            back(){
                this.trigger('close-temp-screen');
                this.showScreen('ProductScreen');
            }
        }
        GiftScreen.template = 'GiftScreen';
        return GiftScreen;
    };

    Registries.Component.addByExtending(GiftScreen, ReceiptScreen);
    return GiftScreen;

});

