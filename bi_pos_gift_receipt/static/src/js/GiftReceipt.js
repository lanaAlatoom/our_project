odoo.define('bi_pos_gift_receipt.GiftReceipt', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { onMounted } = owl;

    class GiftReceipt extends PosComponent {
        setup() {
            super.setup();
            var number = this.props.barcode
            var data = '"'+number+'"'
            onMounted(() => {
                JsBarcode("#barcode", data, {
                    lineColor: "#000000",
                    width: 1,
                    height: 50,
                    displayValue: true,
                    fontSize: 15,
                });
            });
        }
        get date_time(){
            var d = new Date,
            dformat = [d.getMonth()+1, d.getDate(), d.getFullYear()].join('/')+' '+
                      [d.getHours(), d.getMinutes()].join(':');
            return dformat
        }
        get products() {
            let prods = this.props.RecordLine.orderlines;
            let products = [];
            $.each(prods, function(i, prd) {products.push(prd)});
            return products;
        }
    }
    GiftReceipt.template = 'GiftReceipt';
    Registries.Component.add(GiftReceipt);
    return GiftReceipt;
});