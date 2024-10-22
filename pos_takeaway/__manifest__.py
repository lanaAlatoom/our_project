{
    'name': "Restaurant order type",
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': "This module will add the options Dine-in, Take away, and Delivery in Odoo POS.",
    'description': """The POS user can make orders as Dine-in, Take away, or Delivery and
                     it will create separate token for Take away orders.""",

    'depends': ['point_of_sale', 'pos_restaurant'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/pos_order_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_takeaway/static/src/xml/Screens/ProductScreen/ReceiptScreen/OrderReceipt.xml',
            'pos_takeaway/static/src/xml/Screens/ProductScreen/ReceiptScreen/ReceiptHeader.xml',
            'pos_takeaway/static/src/xml/Screens/ProductScreen/ReceiptScreen/OrderChangeReceipt.xml',
            'pos_takeaway/static/src/xml/Screens/ProductScreen/ControlButton/TakeAway.xml',
            'pos_takeaway/static/src/xml/order_change_receipt_template.xml',
            # 'pos_takeaway/static/src/xml/drawer_button.xml',
            'pos_takeaway/static/src/js/Screens/ProductScreen/ReceiptScreen/ReceiptScreen.js',
            'pos_takeaway/static/src/js/Screens/ProductScreen/ReceiptScreen/order_change_receipt.js',
            'pos_takeaway/static/src/js/Screens/ProductScreen/ControlButton/TakeAway.js',
            # 'pos_takeaway/static/src/js/Screens/ProductScreen/ControlButton/open_drawer.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
