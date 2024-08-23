# -*- coding: utf-8 -*-
{
    'name': "Agreement report",

    'summary': "Agreement Custom report",

    'description': """
Agreement Custom report
    """,

    'author': "Proyectasoft",
    'website': "https://proyectasoft.odoo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management'],

    # always loaded
    'data': [
        'views/fields_for_report_view.xml',
        'report/sale_report_templates.xml',
        'report/ir_actions_report_templates.xml',
        'report/document_tax_totals.xml',
        'report/report_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

