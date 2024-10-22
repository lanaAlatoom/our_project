# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Gift Receipt Print',
    'version': '16.0.0.3',
    'category': 'Point of Sale',
    'summary': 'Print POS gift receipt print point of sale gift receipt print Print POS gift card print point of sale gift card print generate gift receipt from point of sale screen point of sale order gift receipt print from pos gift card receipt print pos receipt gift',
    'description': """
       This odoo app helps user to generate gift receipt from point of sale screen. User can generate gift receipt from point of sale screen along with point of sale order receipt in odoo.
       
       pos gift receipt
       print pos gift receipt
       generate point of sale gift receipt
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    "price": 20,
    "currency": 'EUR',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_config.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'bi_pos_gift_receipt/static/src/css/GiftReceipt.css',
            'bi_pos_gift_receipt/static/src/css/GiftScreen.css',
            "bi_pos_gift_receipt/static/src/js/JsBarcode.all.min.js",
            'bi_pos_gift_receipt/static/src/js/ReceiptScreen.js',
            'bi_pos_gift_receipt/static/src/js/GiftScreen.js',
            'bi_pos_gift_receipt/static/src/js/GiftReceipt.js',
            'bi_pos_gift_receipt/static/src/js/models.js',
            'bi_pos_gift_receipt/static/src/js/Popups/GiftReceiptDetailPopup.js',
            'bi_pos_gift_receipt/static/src/js/Screens/ProductScreen/ControlButtons/EnableGiftReceiptButton.js',

            'bi_pos_gift_receipt/static/src/xml/GiftButton.xml',
            'bi_pos_gift_receipt/static/src/xml/GiftScreen.xml',
            'bi_pos_gift_receipt/static/src/xml/GiftReceipt.xml',
            'bi_pos_gift_receipt/static/src/xml/Popups/GiftReceiptDetailPopup.xml',
            'bi_pos_gift_receipt/static/src/xml/Screens/ProductScreen/ControlButtons/EnableGiftReceiptButton.xml',
        ],
    },
    'license': 'OPL-1',
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/QvK09DcKmj4',
    "images": ['static/description/Banner.gif'],
}
