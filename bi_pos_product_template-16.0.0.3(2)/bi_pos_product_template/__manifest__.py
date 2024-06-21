# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "POS Product Variants/template in Odoo",
    "version": "16.0.0.3",
    "category": "Point of Sale",
    "depends": ['base', 'sale', 'point_of_sale'],
    "author": "BrowseInfo",
    'summary': 'App point of sales product template POS Product Multi variant pos product attributes pos product variants pos product multiple template point of sale product template item variant pos product variant pos product template pos multiple product variants',
    "description": """This apps allows users to select product from 
    pos product and variants from pop-up window on pos screen.
    also pos display total count of every product variants.
					 
    odoo pos product attributes product variants in pos
	odoo pos product variants point of sales product variants
	odoo pos item variants item variants in pos 
	odoo pos product template point of sales product template point of sales	
	odoo pos with product template 
	odoo point of sales product template point of sales

    odoo point of sale product attributes product variants in point of sales
    odoo point of sale product variants point of sale product variants
    odoo point of sales item variants item variants in point of sales 
    odoo point of sale product template pos order product template point of sales    
    odoo point of sales with product template 
    odoo point of sales product template point of sales					 
    """,

    "website": "https://www.browseinfo.com",
    "price": '15.00',
    "currency": 'EUR',
    "data": [
        'views/pos_config_view.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'bi_pos_product_template/static/src/js/ProductTemplateListWidget.js',
            'bi_pos_product_template/static/src/js/screens.js',
            'bi_pos_product_template/static/src/js/BiProductScreen.js',
            'bi_pos_product_template/static/src/js/ProductsWidget.js',
            'bi_pos_product_template/static/src/js/ProductTemplatePopupWidget.js',
            'bi_pos_product_template/static/src/xml/**/*',
        ],
        
    },
    "auto_install": False,
    "installable": True,
    "live_test_url": "https://youtu.be/0dfArVaJqBo",
    "images": ['static/description/Banner.gif'],
    'license': 'OPL-1',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
