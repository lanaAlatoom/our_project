# -*- coding: utf-8 -*-
{
    'name': "Hotel Report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    "author": "Midaad Company",
    'website': "https://midaad.com/",
    "category": "Midaad Modules/Report",

    'sequence': -100,
    'version': '0.1',
    'depends': ['base', 'hotel','hotel_management','account', ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/police_wizard.xml',
        'wizard/remaining_wizard.xml',
        'wizard/mael_wizard.xml',
        'wizard/roomstatus_wizard.xml',
        'wizard/daily_wizard.xml',
        'wizard/cash_wizard.xml',
        'wizard/cashier_wizard.xml',
        'wizard/daily_managment.xml',
        'report/police_wizard_report.xml',
        'report/remaining_wizard_report.xml',
        'report/mael_wizard_report.xml',
        'report/roomstatus_wizard_report.xml',
        'report/daily_wizard_report.xml',
        'report/cash_wizard_report.xml',
        'report/cashier_wizard_report.xml',
        'report/daily_management_wizard_report.xml',
        "data/mail_templates.xml",


    ],
    'demo': [
        'demo/demo.xml',
    ],
}
