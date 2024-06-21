odoo.define('bi_pos_product_template.ProductsWidget', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductsWidget = require('point_of_sale.ProductsWidget');

	const BiProductsWidget = (ProductsWidget) =>
		class extends ProductsWidget {
            get productsToDisplay() {
                let list = [];
                if (this.searchWord !== '') {
                    list = this.env.pos.db.search_product_in_category(
                        this.selectedCategoryId,
                        this.searchWord
                    );
                } else {
                    if(this.env.pos.config.allow_product_variants){
                        list = this.env.pos.db.get_product_by_category_variants(this.selectedCategoryId);
                    }else{
                        list = this.env.pos.db.get_product_by_category(this.selectedCategoryId);
                    }
                }
                return list.sort(function (a, b) { return a.display_name.localeCompare(b.display_name) });
            }
		};

	Registries.Component.extend(ProductsWidget, BiProductsWidget);
	return ProductsWidget;

});