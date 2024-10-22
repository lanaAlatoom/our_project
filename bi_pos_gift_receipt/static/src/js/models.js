odoo.define('bi_pos_gift_receipt.models', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
    var utils = require('web.utils');
    var {  Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');

    const posorder_super = (Order) => class posorder_super extends Order {
        constructor(obj, options) {
            super(...arguments);
			this.barcode = this.barcode || "";
			this.set_barcode();
			this.split_data = this.split_data || false;
        }
        init_from_JSON(json){
			super.init_from_JSON(...arguments);
			this.barcode = json.barcode;
			this.split_data = json.split_data;
		}
        set_barcode(){
			var self = this;
			var temp = Math.floor(100000000000+ Math.random() * 9000000000000)
			self.barcode =  temp.toString();
		}
		set_split_data(data){
		    this.split_data = data;
		}
		get_split_data(){
		    return this.split_data;
		}
        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.barcode = this.barcode;
			json.split_data = this.split_data;
            return json
        }
        export_for_printing(){
			const json = super.export_for_printing(...arguments);
			json.barcode = this.barcode;
			json.split_data = this.get_split_data();
			return json;
		}
    }
    Registries.Model.extend(Order, posorder_super);
});