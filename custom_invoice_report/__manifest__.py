# -*- coding: utf-8 -*-
{
    'name': "Invoice custom report",

    'summary': """
        Print invoice with amount with secondary currency of the company""",

    'description': """
        Print invoice with amount with secondary currency of the company.
    """,

    'author': "Proyecta",
    'website': "https://odoo.proyectasoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '17.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'aml_secondary_currency'],

    # always loaded
    'data': [
        'views/invoice_template_custom.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
