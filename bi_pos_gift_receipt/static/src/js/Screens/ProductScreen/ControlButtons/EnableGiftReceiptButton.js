odoo.define('bi_pos_gift_receipt.EnableGiftReceipt', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const { useState } = owl;
    const Registries = require('point_of_sale.Registries');
    const models = require('point_of_sale.models');
    var utils = require('web.utils');

    class EnableGiftReceipt extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            let orderLines = this.env.pos.get_order().get_orderlines();
            if(orderLines.length > 0){
                const { confirmed , payload } = await this.showPopup('GiftReceiptDetailPopup', {
                            title: this.env._t('Products'), lines: orderLines,});
            } else{
                alert("Please Select The Product First ");
            }
        }
    }
    EnableGiftReceipt.template = 'EnableGiftReceipt';
    ProductScreen.addControlButton({
    component: EnableGiftReceipt,
    condition: function() {
            return this.env.pos.config.enable_gift_receipt;
        },
    });
    Registries.Component.add(EnableGiftReceipt);
    return EnableGiftReceipt;
});