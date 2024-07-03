# -*- coding: utf-8 -*-
{

    'name': 'Vehicle Repair',
    'version': '17.0',
    'summary': ' Vehicle Repair and Manage car brands, models, and chevy numbers',
    'author': "Eng Lana Alatoom",
    'website': "https://www.midaad.com",

    'depends': ['base', 'contacts','sale','crm'],
    'data': [
        'views/car_brands_views.xml',
        'views/all_ticket.xml',
        'views/car_models_views.xml',
        'views/sale_order_inherit.xml',
        'views/product_category.xml',
        'views/chevy_number_views.xml',
        'security/ir.model.access.csv',
        'report/technician_car_report.xml',
        'data/server_actions.xml'

    ],
    'assets': {
            'web.assets_backend': [
                '/vehicle_repair/static/src/css/card.css',

            ],

        },
    'installable': True,
    'application': True,







}
