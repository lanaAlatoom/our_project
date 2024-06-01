# -*- coding: utf-8 -*-
{

    'name': 'Car Management',
    'version': '17.0',
    'summary': 'Manage car brands, models, and chevy numbers',
    'author': "Eng Lana Alatoom",
    'website': "https://www.midaad.com",

    'depends': ['base', 'contacts','helpdesk','sale'],
    'data': [
        'views/car_brands_views.xml',
        'views/car_models_views.xml',
        'views/sale_order_inherit.xml',
        'views/chevy_number_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,







}


