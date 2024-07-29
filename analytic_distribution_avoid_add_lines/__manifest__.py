{
    'name' : 'Impide agregar líneas en distribuciones analíticas',
    'version': '17.0.0.0',
    'author': 'PrimateUY',
    'website': 'https://primate.com.uy/',
    'category': 'Accounting/Accounting',
    'depends' : ['base', 'analytic', 'account'],
    'description': """
Impide agregar líneas en distribuciones analíticas.
===============================================

Quita la posibilidad de agregar líneas en los campos distribución analítica.
    """,
    'data': [
        'views/account_move_views.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
        'analytic_distribution_avoid_add_lines/static/src/components/analytic_distribution/analytic_distribution_avoid_add_lines_templates.xml',
        ],
        'web.qunit_suite_tests': [
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
