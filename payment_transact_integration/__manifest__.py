{
    'name' : 'Integración de pagos con Transact',
    'version': '17.0.0.0',
    'author': 'PrimateUY',
    'website': 'https://primate.com.uy/',
    'category': 'Accounting/Accounting',
    'depends' : ['base', 'account'],
    'description': """
Permite realizar pagos con Transact
===============================================

    """,
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_payment_register_views.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'license': 'LGPL-3',
}
