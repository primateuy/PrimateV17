# __manifest__.py

{
    "name": "Migración de Datos de entre versiones de Odoo",
    "version": "1.0",
    "category": "Tools",
    "summary": "Módulo para migrar datos de Odoo entre versiones de Odoo",
    "author": "Felipe Ferreira",
    "website": "https://proyectasoft.odoo.com",
    "depends": ["base","contacts", "account", "analytic", "sale", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/odoo_migrator_view.xml",
        "views/odoo_migrator_mapping_view.xml",
    ],
    "installable": True,
}
