# -*- coding: utf-8 -*-
{
    'name': "Corrección de Validación de Transferencias Internas",

    'summary': """
        Impide que las transferencias internas y sus asientos contables asociados puedan volver a borrador después de su validación.
    """,

    'description': """
        Este módulo asegura que, una vez validada una transferencia interna en Odoo, ni la transferencia ni los asientos contables asociados puedan volver a estado de borrador. Esto ayuda a mantener la consistencia de los datos y evita modificaciones accidentales en registros validados.
    """,

    'author': "Primate",
    'website': "primate.uy",

    'category': 'Contabilidad',
    'version': '17.0',

    'depends': ['account', 'l10n_latam_check'],

    'data': [
        'views/account_move.xml',
        'views/account_payment_view.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}

