
{
    'name': 'Logistic Providers Management',
    'version': '17.0',
    'category': 'Purchases',
    'summary': 'Manage logistic providers and link them with purchase orders',
    'description': """
        This module allows you to manage logistic providers and link them with purchase orders. Logistic providers can be managed directly from the purchase order form view.
    """,
    'depends': ['purchase'],
    'data': [
        'views/logistic_providers_view.xml',
        'views/purchase_order_view_inherit.xml',
        'security/ir.model.access.csv',

    ],
    'installable': True,
    'application': True,
}
