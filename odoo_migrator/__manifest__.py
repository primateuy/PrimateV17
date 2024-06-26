# __manifest__.py

{
    "name": "Migración de Datos de entre versiones de Odoo",
    "version": "1.0",
    "category": "Tools",
    "summary": "Módulo para migrar datos de Odoo entre versiones de Odoo",
    "author": "Felipe Ferreira",
    "website": "https://proyectasoft.odoo.com",
    "depends": ["base","analytic","contacts", "account", "analytic", "sale", "purchase", "partner_contact_birthdate", "partner_contact_gender", "partner_contact_nationality"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/odoo_migrator_view.xml",
        "views/odoo_migrator_mapping_view.xml",
        "views/odoo_migrator_reconcile_view.xml",
        "views/odoo_models_inherits_view.xml",
    ],
    "installable": True,
}
