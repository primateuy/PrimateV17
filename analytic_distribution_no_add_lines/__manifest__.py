{
    'name' : 'Permiso para agregar líneas en distribuciones analíticas',
    'version': '17.0.0.0',
    'author': 'PrimateUY',
    'website': 'https://primate.com.uy/',
    'category': 'Accounting/Accounting',
    'depends' : ['base', 'analytic', 'account'],
    'description': """
Permiso para agregar líneas en distribuciones analíticas.
===============================================

Permite gestionar, mediante configuración de a Compañía y permisos, la posibilidad de agregar líneas en los campos distribución analítica.
    """,
    'data': [
        'security/analytic_distribution_no_add_lines_group.xml',
        'views/res_config_settings.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
        # 'analytic_distribution_no_add_lines/static/src/components/analytic_distribution/analytic_distribution_no_add_lines_templates.xml',
        'analytic_distribution_no_add_lines/static/src/components/analytic_distribution/analytic_distribution.js'
        ],
        'web.qunit_suite_tests': [
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
