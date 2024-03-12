{
    'name' : 'Cuentas Analíticas Automatizadas',
    'version': '2024.03.10.20.00',
    'author': 'PrimateUY',
    'website': 'https://primate.com.uy/',
    'category': 'Accounting/Accounting',
    'depends' : ['base', 'analytic', 'account'],
    'description': """
Módulo de automatizaciones para las cuentas analíticas.
===============================================

A pertir de la creación de una cuenta analítica, crea un modelo de distribución 
asociado a esta.
    """,
    'data': [
        'views/analytic_account_views.xml',
        'security/analytic_account_auto_group.xml',
        'views/analytic_distribution_model_views.xml',
        'views/account_move_views.xml',
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
