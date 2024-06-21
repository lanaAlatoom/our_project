odoo.define('bi_pos_combo.BiProductScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen'); 

	const BiProductScreen = (ProductScreen) =>
		class extends ProductScreen {
			
			async _clickProduct(event) {
				var self = this;
				const product = event.detail;
				if(self.env.pos.config.allow_product_variants){
                    if (product.product_variant_count > 1) {
                        var prod_template = this.env.pos.db.product_template_by_id[product.product_tmpl_id];
                        var prod_list = [];
                        var alternative_prod_list = [];
                        prod_template.product_variant_ids.forEach(function (prod) {
                            prod_list.push(self.env.pos.db.get_product_by_id(prod));
                        });
                        product.product_ids.forEach(function (product) {
                            alternative_prod_list.push(self.env.pos.db.get_product_by_id(product));
                        });
                        this.showPopup('ProductTemplatePopupWidget', {'variant_ids':prod_list, 'alternative_prod':alternative_prod_list});
                    } else {
                        if(product.to_weight && this.env.pos.config.iface_electronic_scale){
                            this.showScreen('scale',{product: product});
                        }else{
                            this.env.pos.get_order().add_product
                        }
                        super._clickProduct(event);
                    }
				}else{
				    super._clickProduct(event);
				}
			}
		};

	Registries.Component.extend(ProductScreen, BiProductScreen);
	return ProductScreen;

});
