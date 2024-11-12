{
    'name' : 'Mapeo de cuenta analítica única.',
    'version': '17.1.0',
    'author': 'PrimateUY',
    'website': 'https://primate.com.uy/',
    'category': 'Accounting/Accounting',
    'depends' : ['base', 'analytic', 'account', 'account_analytic_parent'],
    'description': """
Mapeo de cuenta analítica si es única en la distribución analítca.
===============================================

Mapea la cuanta analítica con el apunte contable, en caso de que se una sola en la distribución analítica.
    """,
    'data': [
        "views/account_move_views.xml",
        "views/account_analytic_account_view.xml",
        "wizard/wizard_account_move.xml",
        "wizard/wizard_account_move_line.xml",
        "data/unique_analytic_account_cron.xml"
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.qunit_suite_tests': [
        ],
    },
    'installable': True
}
