{
    'name': 'POS Custom',
    'version': '17.0.2.1.1',
    "category": 'Point of Sale',
    'summary': 'To Restrict POS features for cashiers',
    'description': 'This app allows you to enable or disable POS features '
                   'depending on the access rights granted to the cashiers',
    'author': 'Midaad company',
    'company': 'Midaad company',
    'depends': ['pos_hr'],
    'data': [
        'views/hr_employee_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_access_right_hr/static/src/js/PosStore.js',
            'pos_access_right_hr/static/src/js/ActionpadWidget.js',
            'pos_access_right_hr/static/src/js/ProductScreen.js',
            'pos_access_right_hr/static/src/xml/ActionpadWidget.xml',
            'pos_access_right_hr/static/src/css/info_fi.css'
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
