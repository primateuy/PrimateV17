{
    'name' : 'Cuentas Analíticas Automatizadas',
    'version': '2024.03.10',
    'author': 'PrimateUY',
    'website': 'https://primate.com.uy/',
    'category': 'Accounting/Accounting',
    'depends' : ['base', 'analytic', 'account', 'sale'],
    'description': """
Módulo de automatizaciones para las cuentas analíticas.
===============================================

A pertir de la creación de una cuenta analítica, crea un modelo de distribución 
asociado a esta.
    """,
    'data': [
        'views/analytic_account_views.xml',
        'security/analytic_account_auto_group.xml',
        'security/ir.model.access.csv',
        'views/analytic_distribution_model_views.xml',
        'views/account_move_views.xml',
        'views/analytic_plan_views.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.qunit_suite_tests': [
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
