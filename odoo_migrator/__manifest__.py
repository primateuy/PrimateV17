# __manifest__.py

{
    "name": "Migración de Datos de entre versiones de Odoo",
    "version": "1.0",
    "category": "Tools",
    "summary": "Módulo para migrar datos de Odoo entre versiones de Odoo",
    "author": "Primate",
    "website": "https://www.primate.uy",
    "depends": [
        "base",
        "analytic",
        "contacts",
        "account",
        "analytic",
        "sale",
        "purchase",
        "partner_contact_birthdate",
        "partner_contact_gender",
        "partner_contact_nationality",
        #"account_accountant",# no podemos tener dependencias de odoo enterprise
        "account_analytic_tag"
                ],
    "data": [
        "security/odoo_migrator_groups.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/odoo_migrator_view.xml",
        "views/odoo_migrator_mapping_view.xml",
        "views/odoo_migrator_reconcile_view.xml",
        "views/odoo_models_inherits_view.xml",
    ],
    "installable": True,
    "license": 'LGPL-3',
}
