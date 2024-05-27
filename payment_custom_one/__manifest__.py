# -*- coding: utf-8 -*-
{
    'name': "Bank Commitments",

    'description': """
        Bank Commitments 
    """,

    "author": "Midaad Company",
    'website': "https://midaad.com/",

    
    'category': 'accounting',
    'version': '16.1',

    'depends': ['mail','base','account'],

    # always loaded
    "data": [
        'security/ir.model.access.csv',

        "views/stock_picking_views.xml"
    ],
}
