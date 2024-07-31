# migracion_datos_v13_v15/models/models.py
import datetime
from email.utils import parseaddr
from typing import Any, Dict, List, Tuple
from functools import partial
from odoo import models, fields, api, release, _
from odoo.exceptions import UserError
import xmlrpc.client
import logging

_logger = logging.getLogger("MIGRATION SERVICES LOGGER")

odoo_versions: List[Tuple[str, str]] = [
    ("10.0", "10.0"),
    ("11.0", "11.0"),
    ("12.0", "12.0"),
    ("13.0", "13.0"),
    ("14.0", "14.0"),
    ("15.0", "15.0"),
    ("16.0", "16.0"),
    ("17.0", "17.0"),
]

field_to_model: Dict[str, str] = {
    "parent_id": "res.partner",
    "partner_id": "res.partner",
    "state_id": "res.country.state",
    "country_id": "res.country",
    "nationality_id": "res.country",
    "move_id": "account.move",
    "journal_id": "account.journal",
    "destination_journal_id": "account.journal",
    "category_id": "res.partner.category",
    "child_ids": "res.partner",
    "child_id": "product.category",
    "currency_id": "res.currency",
    "company_id": "res.company",
    "account_id": "account.account",
    "product_id": "product.product",
    "tax_ids": "account.tax",
    "tax_group_id": "account.tax.group",
    "account_analytic_id": "account.analytic.account",
    "invoice_user_id": "res.users",
    "default_account_id": "account.account",
    "property_account_receivable_id": "account.account",
    "property_account_payable_id": "account.account",
    "title": "res.partner.title",
    "user_id": "res.users",
    "categ_id": "product.category",
    "property_account_income_id": "account.account",
    "property_account_expense_id": "account.account",
}

m2o_fields: List[str] = [
    "parent_id",
    "state_id",
    "country_id",
    "currency_id",
    "partner_id",
    "invoice_user_id",
    "default_account_id",
    "property_account_receivable_id",
    "property_account_payable_id",
]

m2m_fields: List[str] = ["child_ids", "category_id", "invoice_line_tax_ids"]

CONTACT_FIELDS: List[str] = [
    "name",
    "company_type",
    "street",
    "street2",
    "city",
    "state_id",
    "zip",
    "country_id",
    "vat",
    "phone",
    "mobile",
    "email",
    "website",
    "lang",
    "category_id",
    "child_ids",
    "title",
    "birthdate_date",
    "gender",
    "nationality_id",
    "user_id",
    #"image",
    "property_account_receivable_id",
    "property_account_payable_id",
]

COMPANY_FIELDS: List[str] = [
    "name",
    "email",
    "vat",
    "sale_note",
    "country_id",
    "currency_id",
    # 'logo_web',
    # 'logo',
    "font",
    "partner_id",
    "zip",
    "website",
    "fax",
    "street",
    "city",
    "street2",
    "phone",
    # 'footer_logo',
    # 'company_registry',
    # 'header_logo',
    "state_id",
    "mobile",
]

CHART_OF_ACCOUNT_FIELDS: List[str] = [
    "code",
    "id",
    "name",
    "reconcile",
    "currency_id",
    "internal_type",
    "user_type_id",
]

ANALYTIC_ACCOUNT_FIELDS: List[str] = [
    "id",
    "name",
    "company_id",
    "partner_id",
]
RES_USERS_FIELDS: List[str] = [
    "id",
    "name",
    "company_id",
    "partner_id",
    "login",
    "lang",
    "tz",
    "signature",
    "active",
]

ACCOUNT_JOURNAL_FIELDS: List[str] = [
    "name",
    "type",
    "code",
    "company_id",
    "default_debit_account_id",
    "currency_id",
    "show_on_dashboard",
]
PRODUCT_TEMPLATE_FIELDS: List[str] = [
    "id",
    "active",
    "name",
    "sale_ok",
    "purchase_ok",
    # "can_be_expensed",
    "purchase_method",
    "invoice_policy",
    "type",
    "categ_id",
    "property_account_income_id",
    "property_account_expense_id",
    # "company_id",
]
PRODUCT_FIELDS: List[str] = []

ACCOUNT_INVOICE_FIELDS: List[str] = [
    "id",
    "name",
    "number",
    "date_invoice",
    "journal_id",
    "currency_id",
    "type",
    "company_id",
    "partner_id",
    "user_id",
    "state",
    "move_id"
]

ACCOUNT_MOVE_FIELDS: List[str] = [
    "id",
    "name",
    "number",
    "date",
    "journal_id",
    "currency_id",
    "company_id",
    "partner_id",
    "user_id",
    "state",
    "move_id"
]
ACCOUNT_MOVE_LINE_FIELDS: List[str] = [
    "id",
    "product_id",
    "name",
    "account_id",
    "quantity",
    "price_unit",
    "invoice_line_tax_ids",
    "company_id",
    "currency_id",
    "invoice_id",
    "account_analytic_id",
    "move_id",
]
ACCOUNT_INVOICE_MOVE_LINE_FIELDS: List[str] = [
    "account_id",
    "amount_currency",
    "balance",
    "company_id",
    "company_currency_id",
    "currency_id",
    "invoice_id",
    "stored_invoice_id",
    "id",
    "name",
    "payment_id",
    "price_unit",
    "product_id",
    "quantity",
    "analytic_account_id",
]
ACCOUNT_PAYMENT_MOVE_LINE_FIELDS: List[str] = [
    "account_id",
    "amount_currency",
    "balance",
    "company_id",
    "company_currency_id",
    "currency_id",
    "debit",
    "credit",
    "id",
    "name",
    "move_id",
    "payment_id",
    "price_unit",
    "product_id",
    "quantity",
]
ACCOUNT_MOVE_TYPE_FIELDS: List[str] = []
ACCOUNT_PAYMENT_FIELDS: List[str] = []

move_type_map = {'entry': 'Asiento Contable',
                 'out_invoice': 'Factura de cliente',
                 'out_refund': 'Factura rectificativa de cliente',
                 'in_invoice': 'Factura de proveedor',
                 'in_refund': 'Factura rectificativa de proveedor',
                 'out_receipt': 'Recibo de ventas',
                 'in_receipt': 'Recibo de compra',
                 }

class MigratorLogLine(models.Model):
    _name = "odoo.migrator.log.line"
    _description = "Migrator Log Line"

    name = fields.Char(
        string="Name",
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "odoo.migrator.log.sequence"
        ),
        required=True,
        index="trigram",
    )
    error = fields.Text(string="Error")
    log_type = fields.Selection(
        [
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("error", "Error"),
        ],
        string="Log Type",
    )
    values = fields.Text(string="Values")
    migrator_id = fields.Many2one(
        "odoo.migrator", string="Migrator Reference", ondelete="cascade"
    )

    migration_model = fields.Selection(
        [
            # Contacts
            ("account_mapping", "Mapeo de Cuentas"),
            ("chart_accounts", "Plan de Cuentas"),
            ("analytic_accounts", "Plan de Cuentas analitico"),
            ("users", "Usuarios"),
            ("countries", "Paises"),
            ("states", "Estados"),
            ("contacts", "Contactos"),
            #
            # Currencies
            ("currencies", "Monedas"),
            ("currency_rates", "Tasas de la Monedas"),
            ("taxes", "Impuestos"),
            #
            # Journals
            ("account_journals", "Diarios"),
            #
            # Products
            ("product_categories", "Categorias de productos"),
            ("product_templates", "Plantillas de productos"),
            # ("products", "Productos"),
            #
            # Customer invoices
            ("customer_invoices", "Facturas de Clientes (cabezales)"),
            ("customer_invoice_lines", "Facturas de Clientes (lineas)"),
            ("customer_moves_lines", "Facturas de Clientes (movimientos)"),
            # ("customer_refunds", "Notas de Credito de Clientes (cabezales)"),
            # ("customer_refund_lines", "Notas de Credito de Clientes (lineas)"),
            #
            # Supplier invoices
            ("supplier_invoices", "Facturas de Proveedor (cabezales)"),
            ("supplier_invoice_lines", "Facturas de Proveedor (lineas)"),
            ("supplier_moves_lines", "Facturas de Proveedor (movimientos)"),

            # ("supplier_refunds", "Notas de Credito de Proveedor (cabezales)"),
            # ("supplier_refund_lines", "Notas de Credito de Proveedor (lineas)"),
            #
            # Account entries
            ("account_move", "Asientos contables (Cabezales)"),
            ("account_move_lines", "Asientos contables (lineas)"),
            #
            # Entries
            # ("entries", "Apuntes contables (cabezales)"),
            # ("entry_lines", "Apuntes contables (lineas)"),
            #
            # Payments
            ("customer_payments", "Pagos de Clientes"),
            ("customer_payment_moves", "Pagos de Clientes (movimientos)"),
            ("supplier_payments", "Pagos de Proveedores"),
            ("supplier_payment_moves", "Pagos de Proveedores (movimientos)"),
            # Conciliations
            ("customer_reconcile", "Conciliaciones de Clientes"),
            ("supplier_reconcile", "Conciliaciones de Proveedores"),
            #Publications
            ("post_customer_invoices", "Publicar facturas de cliente"),
            ("post_customer_payments", "Publicar pagos de cliente"),
            ("post_supplier_invoices", "Publicar facturas de proveedor"),
            ("post_supplier_payments", "Publicar pagos de proveedor"),
            ("post_entries", "Publicar apuntes contables")
        ],
        string="Modelo a Migrar",
        required=True,
    )

    # Puedes agregar más campos según tus necesidades


class OdooMigratorReconciliation(models.Model):
    _name = "odoo.migrator.reconciliation"
    _description = "Migrator reconciliation"

    name = fields.Char(
        string="Name",
        default=lambda self: self.env["ir.sequence"].next_by_code("odoo.migrator.reconciliation.sequence"),
        required=True,
        index="trigram",
    )
    old_id = fields.Char(string="Old ID")
    migrator_id = fields.Many2one(comodel_name="odoo.migrator", string="Migrator Reference", ondelete="cascade")
    old_debit_move_id = fields.Char(string="Old Debit")
    old_credit_move_id = fields.Char(string="Old Credit")
    debit_move_id = fields.Many2one(comodel_name='account.move.line', string="Debit Move")
    credit_move_id = fields.Many2one(comodel_name='account.move.line', string="Credit Move")
    successful_reconciliation = fields.Boolean(string="Successful Reconciliation", default=False)

    def reconcile(self):
        self = self.with_context(skip_account_move_synchronization=True)
        total = len(self)
        commit_count = 300
        side_count = 0
        for contador, rec in enumerate(self, start=1):
            side_count += 1
            if side_count > commit_count:
                self.env.cr.commit()
                side_count = 0
            _logger.info(f'vamos en el {contador} de {total}')
            debit_move = rec.debit_move_id
            if debit_move.move_id.state == "draft":
                message = f'El asiento de debito {debit_move.move_id.name} no se encuentra validado (id: --> {debit_move.move_id.id})'
                rec.successful_reconciliation = False
                continue

            credit_move = rec.credit_move_id

            if credit_move.move_id.state == "draft":
                message = f'El asiento de credito {credit_move.move_id.name} no se encuentra validado (id: --> {credit_move.move_id.id})'
                rec.successful_reconciliation = False
                continue

            if not credit_move and not debit_move:
                raise UserError(
                    f'No se encontro el asiento de debito {rec.old_debit_move_id} y el asiento de credito {rec.old_credit_move_id}')
            if debit_move.reconciled:
                debit_move.remove_move_reconcile()
                debit_move._compute_amount_residual()
            if credit_move.reconciled:
                credit_move.remove_move_reconcile()
                credit_move._compute_amount_residual()

            try:
                (debit_move + credit_move).with_context(skip_account_move_synchronization=True).reconcile()
                rec.successful_reconciliation = True
            except Exception as error:
                rec.successful_reconciliation = False
                self.env.cr.commit()
                raise UserError(error)
        return True

    def view_record(self):
        """
        model_to_view
        :return:
        debit
        credit
        """

        ctx = self._context.copy()
        model_to_view = ctx.get('model_to_view')
        if model_to_view == 'debit':
            res_id = self.debit_move_id.move_id.id
            if not res_id:
                raise UserError('No se encontro el asiento de debito')
            action = self.env.ref("account.action_move_journal_line").read()[0]
            action['res_id'] = res_id
            action['domain'] = [('id', '=', res_id)]
        elif model_to_view == 'credit':
            res_id = self.credit_move_id.payment_id.id
            if not res_id:
                raise UserError('No se encontro el asiento de credito')
            action = self.env.ref("account.action_account_payments").read()[0]
            action['res_id'] = res_id
            action['domain'] = [('id', '=', res_id)]
        else:
            raise UserError('No se encontro el modelo a visualizar')

        return action


class OdooMigrator(models.Model):
    _name = "odoo.migrator"
    _description = "Migración de Datos"

    name = fields.Char(
        string="Name",
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "odoo.migrator.sequence"
        ),
        required=True,
        index="trigram",
        copy=False
    )

    source_version = fields.Selection(
        selection=odoo_versions, string="Versión de Origen", readonly=True
    )
    target_version = fields.Selection(
        selection=odoo_versions,
        string="Versión de Destino",
        compute="_get_current_version",
        store=False,
    )
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("company_ok", "Company Connected"),
            ("company_done", "Company data copied"),
            ("in_progress", "En Progreso"),
            ("done", "Completado"),
            ("cancelled", "Cancelado"),
        ],
        string="Estado",
        default="draft",
        required=True,
    )

    # Campos para la información de conexión XML-RPC
    source_server_url = fields.Char(string="URL del Servidor de Origen", required=True)
    source_database = fields.Char(string="Base de Datos de Origen", required=True)
    source_username = fields.Char(string="Nombre de Usuario de Origen", required=True)
    source_password = fields.Char(string="Contraseña de Origen", required=True)
    migration_model = fields.Selection(
        [
            # Currencies
            ("currencies", "Monedas"),
            ("currency_rates", "Tasas de la Monedas"),
            #
            # Contacts
            ("account_mapping", "Mapeo de Cuentas"),
            ("chart_accounts", "Plan de Cuentas"),
            ("analytic_accounts", "Plan de Cuentas analitico"),
            ("users", "Usuarios"),
            ("countries", "Paises"),
            ("states", "Estados"),
            ("contacts", "Contactos"),
            #
            # Taxes
            ("taxes", "Impuestos"),
            #
            # Journals
            ("account_journals", "Diarios"),
            #
            # Products
            ("product_categories", "Categorias de productos"),
            ("product_templates", "Plantillas de productos"),
            # ("products", "Productos"),
            #
            # Customer invoices
            ("customer_invoices", "Facturas de Clientes (cabezales)"),
            ("customer_invoice_lines", "Facturas de Clientes (lineas)"),
            ("customer_moves_lines", "Facturas de Clientes (movimientos)"),
            # ("customer_refunds", "Notas de Credito de Clientes (cabezales)"),
            # ("customer_refund_lines", "Notas de Credito de Clientes (lineas)"),
            #
            # Supplier invoices
            ("supplier_invoices", "Facturas de Proveedor (cabezales)"),
            ("supplier_invoice_lines", "Facturas de Proveedor (lineas)"),
            ("supplier_moves_lines", "Facturas de Proveedor (movimientos)"),

            # ("supplier_refunds", "Notas de Credito de Proveedor (cabezales)"),
            # ("supplier_refund_lines", "Notas de Credito de Proveedor (lineas)"),
            #
            # Account entries
            ("account_move", "Asientos contables (Cabezales)"),
            ("account_move_lines", "Asientos contables (lineas)"),
            #
            # Entries
            # ("entries", "Apuntes contables (cabezales)"),
            # ("entry_lines", "Apuntes contables (lineas)"),
            #
            # Payments
            ("customer_payments", "Pagos de Clientes"),
            ("customer_payment_moves", "Pagos de Clientes (movimientos)"),
            ("supplier_payments", "Pagos de Proveedores"),
            ("supplier_payment_moves", "Pagos de Proveedores (movimientos)"),
            # Conciliations
            ("customer_reconcile", "Conciliaciones de Clientes"),
            ("supplier_reconcile", "Conciliaciones de Proveedores"),
            #Publications
            ("post_customer_invoices", "Publicar facturas de cliente"),
            ("post_customer_payments", "Publicar pagos de cliente"),
            ("post_supplier_invoices", "Publicar facturas de proveedor"),
            ("post_supplier_payments", "Publicar pagos de proveedor"),
            ("post_entries", "Publicar apuntes contables")
        ],
        string="Modelo a Migrar",
        required=True,
    )

    pagination_offset = fields.Integer(string="Offset", default=0)
    pagination_limit = fields.Integer(string="Limit", default=500)

    contact_ids = fields.Many2many(comodel_name="res.partner", string="Contactos")
    state_ids = fields.Many2many(comodel_name="res.country.state", string="Estados")
    tax_ids = fields.Many2many(comodel_name="account.tax", string="Impuestos")
    currency_ids = fields.Many2many(comodel_name="res.currency", string="Monedas")
    currency_rate_ids = fields.Many2many(
        comodel_name="res.currency.rate", string="tasas de Monedas"
    )
    chart_of_accounts_ids = fields.Many2many(
        comodel_name="account.account", string="Plan de Cuentas"
    )

    journal_ids = fields.Many2many(
        comodel_name="account.journal", string="Diarios"
    )
    product_categories_ids = fields.Many2many(
        comodel_name="product.category", string="Categorias de producto"
    )
    product_templates_ids = fields.Many2many(
        comodel_name="product.template", string="Plantillas de producto"
    )
    # products_ids = fields.Many2many(comodel_name="product.product", string="Productos")
    products_ids = fields.Many2many(comodel_name="product.product", string="Productos")
    account_moves_ids = fields.Many2many(comodel_name="account.move", string="Facturas")
    migration_error_account_moves_ids = fields.Many2many(comodel_name="account.move",
                                                         string="Facturas con errores",
                                                         column1="migrator_id",
                                                         column2="account_move_id",
                                                         relation="odoo_migrator_account_move_rel")
    account_move_line_ids = fields.Many2many(
        comodel_name="account.move.line", string="Lineas de Facturas"
    )
    country_ids = fields.Many2many(comodel_name="res.country", string="Países")
    analytic_account_ids = fields.Many2many(comodel_name="account.analytic.account", string="Cuentas Analiticas")
    user_ids = fields.Many2many(comodel_name="res.users", string="Usuarios")
    account_move_types_ids = fields.Many2many(
        comodel_name="account.move",
        relation="odoo_migrator_account_move_type_rel",
        column1="migrator_id",
        column2="account_move_type_id",
        string="Apuntes Contables",
        context={"move_type": "entry"},
        # domain=lambda self: self.move_type == "entry",
    )
    account_payments_ids = fields.Many2many(
        comodel_name="account.payment", string="Pagos"
    )
    account_full_reconciles_ids = fields.Many2many(
        comodel_name="account.full.reconcile", string="Conciliaciones"
    )

    log_ids = fields.One2many(
        comodel_name="odoo.migrator.log.line",
        inverse_name="migrator_id",
        string="Log Lines",
    )
    reconciliation_line_ids = fields.One2many(comodel_name="odoo.migrator.reconciliation", inverse_name="migrator_id",
                                              string="Conciliaciones")
    is_multicompany = fields.Boolean(string="¿Es Multicompañía?", default=False)
    company_count = fields.Integer(string="Número de Compañías")
    company_data = fields.Text(string="Datos de Compañías")
    odoo_company_ids = fields.One2many(
        comodel_name="odoo.migrator.company", inverse_name="migrator_id"
    )
    company_id = fields.Many2one(comodel_name="res.company", string="Compañía")
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", related="company_id.partner_id"
    )
    contact_count = fields.Integer(string="Número de Contactos", compute="_get_models_data_count")
    user_count = fields.Integer(string="Número de Usuarios", compute="_get_models_data_count")
    countries_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    states_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    currencies_count = fields.Integer(string="Número de")
    product_categories_count = fields.Integer(string="Número de")
    supplier_payments_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    supplier_invoice_lines_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    supplier_invoices_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    customer_moves_lines_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    customer_invoice_lines_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    customer_invoices_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    product_templates_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    customer_payment_moves_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    supplier_reconcile_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    customer_reconcile_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    customer_payments_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    account_entries_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    chart_of_accounts_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    currency_rates_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    account_journals_count = fields.Integer(string="Número de ", compute='_get_models_data_count')
    tax_count = fields.Integer(string="Número de ", compute='_get_models_data_count')

    def paginate(self):
        self.ensure_one()
        self.pagination_offset += self.pagination_limit

    def clear_logs(self):
        self.log_ids.unlink()

    def clear_error_logs(self):
        self.log_ids.filtered_domain([('log_type', '=', 'error')]).unlink()

    def clear_success_logs(self):
        self.log_ids.filtered_domain([('log_type', '=', 'success')]).unlink()

    def action_draft(self):
        self.write({"state": "draft"})

    @api.depends("contact_ids")
    def _get_models_data_count(self):
        for rec in self:
            rec.contact_count = len(rec.contact_ids)
            rec.countries_count = len(rec.country_ids)
            rec.states_count = len(rec.state_ids)
            rec.currencies_count = len(rec.currency_ids)
            rec.product_categories_count = len(rec.product_categories_ids)
            rec.supplier_payments_count = len(rec.account_payments_ids)
            rec.supplier_invoice_lines_count = len(rec.account_move_line_ids)
            rec.supplier_invoices_count = len(rec.account_move_line_ids)
            rec.customer_moves_lines_count = len(rec.account_move_line_ids)
            rec.customer_invoice_lines_count = len(rec.account_move_line_ids)
            rec.customer_invoices_count = len(rec.account_move_line_ids)
            rec.product_templates_count = len(rec.product_templates_ids)
            rec.customer_payment_moves_count = len(rec.account_payments_ids)
            rec.supplier_reconcile_count = len(rec.account_move_line_ids)
            rec.customer_reconcile_count = len(rec.account_move_line_ids)
            rec.customer_payments_count = len(rec.account_payments_ids)
            rec.customer_payments_count = len(rec.account_payments_ids)
            rec.account_entries_count = len(rec.account_moves_ids.filtered(lambda x: x.move_type == 'entry'))
            rec.chart_of_accounts_count = len(rec.chart_of_accounts_ids)
            rec.currency_rates_count = len(rec.currency_rate_ids)
            rec.account_journals_count = len(rec.journal_ids)
            rec.user_count = len(rec.user_ids)
            rec.tax_count = len(rec.tax_ids)

    def action_view_model(self):
        model_name = self._context.get('model_name', False)
        if not model_name:
            raise UserError('No se pudo encontrar el modelo')
        action = False
        if model_name == 'contact':
            action = self.env.ref("contacts.action_contacts").read()[0]
            action["domain"] = [("id", "in", self.contact_ids.ids)]

        if model_name == 'account_move_entries':
            action = self.env.ref("account.action_move_journal_line").read()[0]
            action["domain"] = [("id", "in", self.account_moves_ids.filtered(lambda x: x.move_type == 'entry').ids)]

        elif model_name == 'countries':
            action = self.env.ref("base.action_country").read()[0]
            action["domain"] = [("id", "in", self.country_ids.ids)]

        elif model_name == 'states':
            action = self.env.ref("base.action_country_state").read()[0]
            action["domain"] = [("id", "in", self.state_ids.ids)]

        elif model_name == 'currencies':
            action = self.env.ref("base.action_currency_form").read()[0]
            action["domain"] = [("id", "in", self.currency_ids.ids)]
            return action

        elif model_name == 'account_journals':
            action = self.env.ref("account.action_account_journal_form").read()[0]
            action["domain"] = [("id", "in", self.journal_ids.ids)]

        elif model_name == 'currency_rates':
            action = self.env.ref("base.act_view_currency_rates").read()[0]
            action["domain"] = [("id", "in", self.currency_rate_ids.ids)]

        elif model_name == 'chart_of_accounts':
            action = self.env.ref("account.action_account_form").read()[0]
            action["domain"] = [("id", "in", self.chart_of_accounts_ids.ids)]

        elif model_name == 'product_categories':
            action = self.env.ref("product.product_category_action_form").read()[0]
            action["domain"] = [("id", "in", self.product_categories_ids.ids)]

        elif model_name == 'product_templates':
            action = self.env.ref("account.product_product_action_sellable").read()[0]
            action['context'] = {}
            action["domain"] = [("id", "in", self.product_templates_ids.ids)]

        elif model_name == 'customer_invoices':
            action = self.env.ref("account.action_move_line_form").read()[0]
            action["domain"] = [("id", "in", self.account_moves_ids.ids)]

        elif model_name == 'customer_invoice_lines':
            action = self.env.ref("account.action_move_line_form").read()[0]
            action["domain"] = [("id", "in", self.account_moves_ids.ids)]

        elif model_name == 'customer_moves_lines':
            action = self.env.ref("account.action_move_line_form").read()[0]
            action["domain"] = [("id", "in", self.account_moves_ids.ids)]
            return action

        elif model_name == 'supplier_invoices':
            action = self.env.ref("account.action_move_line_form").read()[0]
            action["domain"] = [("id", "in", self.account_moves_ids.ids)]

        elif model_name == 'supplier_invoice_lines':
            action = self.env.ref("account.action_move_line_form").read()[0]
            action["domain"] = [("id", "in", self.account_moves_ids.ids)]

        elif model_name == 'account_move_lines':
            action = self.env.ref("account.action_move_line_form").read()[0]
            action["domain"] = [("id", "in", self.account_moves_ids.ids)]

        elif model_name == 'customer_payments':
            action = self.env.ref("account.action_account_all_payments").read()[0]
            action["domain"] = [("id", "in", self.account_payments_ids.ids)]

        elif model_name == 'customer_payment_moves':
            action = self.env.ref("account.action_account_all_payments").read()[0]
            action["domain"] = [("id", "in", self.account_payments_ids.ids)]

        elif model_name == 'customer_reconcile':
            action = self.env.ref("contacts.action_contacts").read()[0]
            action["domain"] = [("id", "in", self.contact_ids.ids)]

        elif model_name == 'supplier_reconcile':
            action = self.env.ref("contacts.action_contacts").read()[0]
            action["domain"] = [("id", "in", self.contact_ids.ids)]

        elif model_name == 'supplier_payments':
            action = self.env.ref("contacts.action_contacts").read()[0]
            action["domain"] = [("id", "in", self.contact_ids.ids)]

        elif model_name == 'user':
            action = self.env.ref("base.action_res_users").read()[0]
            action["domain"] = [("id", "in", self.user_ids.ids)]

        elif model_name == 'tax':
            action = self.env.ref("account.action_tax_form").read()[0]
            action["domain"] = [("id", "in", self.tax_ids.ids)]

        if not action:
            raise UserError('No se pudo encontrar la vista')
        return action

    def connect_with_source(self):
        self.ensure_one()
        source_models, source_uid, source_database, source_password = (self._get_source_odoo_connection())
        odoo_migrator_company_obj = self.env["odoo.migrator.company"]
        company_obj = self.env["res.company"].sudo()
        # Consulta los contactos en el Odoo de origen
        try:
            company_data = source_models.execute_kw(
                source_database,
                source_uid,
                source_password,
                "res.company",
                "search_read",
                [[]],
                {"fields": COMPANY_FIELDS},
            )
            _logger.info(f"Company data: {company_data}")

        except Exception as error:
            raise UserError(error)
        if len(company_data) > 1:
            self.is_multicompany = True
            self.company_count = len(company_data)
            self.company_data = company_data
            lang_obj = self.env["res.lang"]
            total = len(company_data)
            for counter, company in enumerate(company_data, start=1):
                _logger.info(f"Company {counter}/{total}")
                odoo_migrator_company_exists = odoo_migrator_company_obj.search([('old_id', '=', company['id'])], limit=1)
                if odoo_migrator_company_exists:
                    odoo_migrator_company_exists.migrator_id = self.id
                    continue
                company_partner_id = company["partner_id"][0]
                company_context = source_models.execute_kw(
                    source_database,
                    source_uid,
                    source_password,
                    "res.partner",
                    "search_read",
                    [[("id", "=", company_partner_id)]],
                    {"fields": ["name", "lang"]},
                )
                company_lang = company_context[0]["lang"]
                if not lang_obj._read_group([("code", "=", company_lang)], ["id"]):
                    raise UserError(f"Debe activar el idioma {company_lang} en Odoo")

                for contador, company_field in enumerate(company, start=1):
                    _logger.info(f"Migrando campo {contador}/{len(company)}: {company_field}")
                    if company_field not in odoo_migrator_company_obj._fields:
                        continue
                    if odoo_migrator_company_obj._fields[company_field].type == "many2one" and company.get(company_field, False):
                        _logger.info(f"Resolviendo many2one {company_field}")
                        if company_field == 'partner_id':
                            company = self.with_context(dont_search_for_no_actives=True, from_company=True).resolve_m2o_fields(
                                value=company, m2o=company_field, odoo_object=odoo_migrator_company_obj,
                                lang=company_lang)
                        else:
                            company = self.with_context(dont_search_for_no_actives=True).resolve_m2o_fields(value=company, m2o=company_field, odoo_object=odoo_migrator_company_obj,lang=company_lang)

                    elif odoo_migrator_company_obj._fields[company_field].type in ["many2many", "one2many"] and company.get(company_field, False):
                        _logger.info(f"Resolviendo many2many o one2many {company_field}")
                        company = self.resolve_m2m_o2m_fields(value=company_data, field_type=odoo_migrator_company_obj._fields[company_field].type,field=company_field)
                company_values = {
                    "name": company.get("name", False),
                    "logo": company.get("logo", False),
                    "logo_web": company.get("logo_web", False),
                    "currency_id": company.get("currency_id", False),
                    "street": company.get("street", False),
                    "street2": company.get("street2", False),
                    "zip": company.get("zip", False),
                    "city": company.get("city", False),
                    "state_id": company.get("state_id", False),
                    "country_id": company.get("country_id", False),
                    "email": company.get("email", False),
                    "phone": company.get("phone", False),
                    "mobile": company.get("mobile", False),
                    "website": company.get("website", False),
                    "vat": company.get("vat", False),
                    "paperformat_id": company.get("paperformat_id", False),
                    "lang": company.get("lang", False),
                    "partner_id": company.get("partner_id", False),
                    "migrator_id": self.id,
                    "old_id": company.get("id", False),
                }
                _logger.info(f"Company values: {company_values}")
                _logger.info(f'Creationg new company: {company.get("name", False)}')
                new_company = odoo_migrator_company_obj.create(company_values)

        return self.write({"state": "company_ok"})

    def copy_company_data(self):
        migrator_company = self.odoo_company_ids.filtered(lambda x: x.migrate_this_company)
        migrator_partner = migrator_company.partner_id
        if not migrator_company:
            raise UserError("No se encontraron compañías a migrar o no selecciono una compañía")
        company = self.company_id
        partner = self.partner_id
        if not company:
            raise UserError("Debe seleccionar una compañía")

        for field in company._fields.keys():
            if field == "id":
                continue
            if field not in migrator_company._fields.keys():
                continue

            value = getattr(migrator_company, field)
            try:
                setattr(company, field, value)
            except Exception as error:
                raise UserError(error)

        for partner_field in partner._fields.keys():
            if partner_field == "id":
                continue

            value = getattr(migrator_partner, partner_field)
            try:
                setattr(partner, partner_field, value)
            except Exception as error:
                raise UserError(error)
        # migrator_partner.unlink()
        # migrator_partner.active = False
        self.company_id.old_id = migrator_company.old_id
        source_models, source_uid, source_database, source_password = (self._get_source_odoo_connection())
        model_name: str = "account.account"
        partner_data = source_models.execute_kw(
            source_database,
            source_uid,
            source_password,
            "res.partner",
            "search_read",
            [[("id", "=", company.partner_id.old_id)]],
            {"fields": ['property_account_receivable_id', 'property_account_payable_id']},
        )
        if partner_data:
            partner_data = partner_data[0]
            partner_data.pop("id")
            for account in partner_data:
                account_id = self.env[model_name].search([('old_id', '=', partner_data[account][0])])
                if account_id:
                    account_id.company_id = company.id
                    company.partner_id.write({account: account_id.id})
        return self.write({"state": "company_done"})

    @api.depends("source_version")
    def _get_current_version(self):
        """
        Obtiene la versión actual de Odoo en formato "X.Y".
        """
        version_info = release.version_info
        current_version = f"{version_info[0]}.{version_info[1]}"
        for rec in self:
            rec.target_version = current_version

    @api.model
    def test_odoo_connection(self):
        """
        Prueba la conexión con un servidor de Odoo mediante XML-RPC.

        :return: True si la conexión es exitosa, False en caso contrario.
        """
        server_url = self.source_server_url
        database = self.source_database
        username = self.source_username
        password = self.source_password
        common = xmlrpc.client.ServerProxy(f"{server_url}/xmlrpc/2/common")

        try:
            # Intenta autenticarse con las credenciales proporcionadas
            uid = common.authenticate(database, username, password, {})
            if not uid:
                _logger.info("¡Error de Conexión!")
                return (
                    False,
                    False,
                    f"Error al intentar contectarse con:\n\nDB: {database}\nUser: {username}\nPassword: {password}",
                )
            _logger.info("¡Conexión exitosa!")
            return True, common, ""
        except Exception as e:
            # Captura cualquier error de conexión
            return False, False, e

    def test_connection(self):
        """
        Método invocado por el botón "Probar Conexión" para probar la conexión XML-RPC.
        """
        for migrator in self:
            success, common, error_msg = migrator.test_odoo_connection()
            if not success:
                split_point = "OperationalError: "
                if split_point in error_msg:
                    error_msg = str(error_msg).split(split_point)[1][:-6]
                raise UserError(error_msg)

            # La conexión fue exitosa, puedes mostrar un mensaje de éxito si lo deseas
            info = common.version()
            version = info["server_version"]
            self.source_version = version
            message = f"¡Conexión exitosa! \n\n - Versión del Servidor: {info['server_version']}"
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "message": message,
                    "type": "success",
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }

    def _get_source_odoo_connection(self):
        """
        Obtener la conexión al Odoo de origen utilizando los datos proporcionados.
        :return: Una instancia del cliente XML-RPC para el Odoo de origen.
        """
        for migrator in self:
            # Datos de conexión al Odoo de origen
            source_server_url = migrator.source_server_url
            source_database = migrator.source_database
            source_username = migrator.source_username
            source_password = migrator.source_password

            # Inicializar el cliente XML-RPC para el Odoo de origen
            source_common = xmlrpc.client.ServerProxy(
                f"{source_server_url}/xmlrpc/2/common"
            )
            source_uid = source_common.authenticate(
                source_database, source_username, source_password, {}
            )
            source_models = xmlrpc.client.ServerProxy(
                f"{source_server_url}/xmlrpc/2/object"
            )

            return source_models, source_uid, source_database, source_password

    def remove_unused_fields(self, record_data=None, odoo_model="res.partner"):
        allowed_fields = [x for x in self.env[odoo_model]._fields]
        #allowed_fields.extend(["image",])
        unwanted_fields = [
            "message_follower_ids",
            "activity_date_deadline",
            "activity_exception_decoration",
            "activity_exception_icon",
            "activity_ids",
            "activity_state",
            "activity_summary",
            "activity_type_id",
            "activity_user_id",
            "additional_info",
            "property_account_receivable_id",
            "property_account_payable_id",
            "property_product_pricelist",
            "title",
            "bank_ids",
            "active",
            "active_lang_count",
            "user_ids",
            "industry_id",
            "same_vat_partner_id",
            "user_id",
            "create_uid",
            "create_date",
            "write_date",
            "write_uid",
            "__last_update",
            "self",
            "image_1920",
            "image_1024",
            "image_512",
            "image_256",
            "image_128",
            "commercial_partner_id",
            # "company_id",
        ]
        for field in list(record_data):
            if field not in allowed_fields or field in unwanted_fields:
                del record_data[field]
        return record_data

    def create_odoo_record(self, m2oid=None, value=None, odoo_object=None, lang=None):
        _logger.info(f"vamos a intentar crear el registro {value} de {odoo_object._name}")
        ctx = self.env.context.copy()
        if lang is None:
            lang = self.env.lang
        odoo_object = odoo_object.with_context(lang=lang)
        source_models, source_uid, source_database, source_password = (self._get_source_odoo_connection())
        domain = [("name", "ilike", value)]

        if odoo_object._name == "res.partner":
            odoo_object_required_fields = CONTACT_FIELDS
            if ctx.get("from_company", False):
                if 'property_account_receivable_id' in odoo_object_required_fields:
                    odoo_object_required_fields.remove('property_account_receivable_id')
                if 'property_account_payable_id' in odoo_object_required_fields:
                    odoo_object_required_fields.remove('property_account_payable_id')
        else:
            odoo_object_required_fields = [x.name for x in self.env["ir.model"].search([("model", "=", odoo_object._name)]).field_id.filtered_domain([("required", "=", True)])]
        record_data = source_models.execute_kw(
            source_database,
            source_uid,
            source_password,
            odoo_object._name,
            "search_read",
            [[("id", "=", m2oid)]],
            {
                "fields": odoo_object_required_fields,
                "limit": 1,
                "context": {"lang": lang},
            },
        )

        for value in list(record_data):
            for field_record in list(value):
                if odoo_object._fields[field_record].type == "many2one":
                    value = self.resolve_m2o_fields(value=value, odoo_object=odoo_object, m2o=field_record, lang=lang)
        if odoo_object._name == "res.country":
            domain.insert(0, "|")
            domain.append(("code", "=", value["code"]))
        record = odoo_object.with_context(default_lang=lang, lang=lang).search(
            domain, limit=1
        )
        if not record:
            try:
                value["old_id"] = value.pop("id")

                if "fiscalyear_last_month" in value:
                    value["fiscalyear_last_month"] = str(value["fiscalyear_last_month"])

                record = odoo_object.create(value)
            except Exception as error:
                self.create_error_log(msg=str(error), values=value)
                raise UserError(error)
        else:
            record.old_id = m2oid
        return record

    def resolve_m2o_fields(self, value=None, odoo_object=None, m2o=None, lang=None):
        """
        los campos m2o vienen en el formato
        {'field_name': [id, name_get]} donde el primer elemento es el id del registro en la base de datos de origen
        y el segundo el nombre del registro
        """
        ctx = self.env.context.copy()
        dont_search_for_no_actives = ctx.get("dont_search_for_no_actives", False)
        if lang is None:
            lang = self.env.lang
        m2ovalue = value.get(m2o, False)
        if not m2ovalue:
            return value
        # source_models, source_uid, source_database, source_password = migrator._get_source_odoo_connection()
        try:
            record_name = m2ovalue[-1]
            record_old_id = value[m2o][0]
            odoo_object = self.env[field_to_model.get(m2o)].with_context(lang=lang)
        except Exception as error:

            raise UserError(error)
        try:
            domain = ["|", ("name", "ilike", record_name), ("old_id", "=", record_old_id)]
            record = odoo_object.search(domain, limit=1)
            if not record and odoo_object._fields.get("active", False) and not dont_search_for_no_actives:
                domain = ["|", ("active", "=", False), ("name", "ilike", record_name)]
                record = odoo_object.search(domain, limit=1)
                record.old_id = record_old_id
        except Exception as error:
            raise UserError(error)
        if not record and odoo_object._name == "account.account":
            account_code = value[m2o][-1].split()[0]
            domain = [("code", "=", account_code)]
            record = odoo_object.search(domain, limit=1)
        if not record:
            """
            aca lo que podemos hacer es ir contra la tabla 'ir.model' para este odoo_object
            y quedarme con la lista de campos requeridos, hacer la llamada a la api con esos campos
            re-formatear la llamada y hacer el create de los odoo_object
            """
            m2oid = record_old_id
            if ctx.get("from_company", False):
                record = self.with_context(from_company=True).create_odoo_record(m2oid=m2oid, value=record_name, odoo_object=odoo_object, lang=lang)
            else:
                record = self.create_odoo_record(m2oid=m2oid, value=record_name, odoo_object=odoo_object, lang=lang)
            record.old_id = record_old_id
        value[m2o] = record.id
        return value

    def resolve_m2m_o2m_fields(self, value=None, field_type=None, field=None, lang=None):
        """
        los campos m2m vienen en el formato
        {'field_name': [1,2,3,4]} donde la lista son los ids del registro
        """

        if lang is None:
            lang = self.env.lang
        value_ids = []
        m2m_ids = value.get(field, False)
        for m2m_id in m2m_ids:
            odoo_object = self.env[field_to_model.get(field)]
            domain = [("old_id", "=", m2m_id)]
            record = odoo_object.search(domain, limit=1)
            if record:
                value_ids.append(record.id)
            if not record:
                source_models, source_uid, source_database, source_password = (self._get_source_odoo_connection())
                if odoo_object._name == "res.partner":
                    try:
                        record = source_models.execute_kw(
                            source_database,
                            source_uid,
                            source_password,
                            field_to_model.get(field),
                            "search_read",
                            [[("id", "=", m2m_id)]],
                            {
                                "fields": ["name", "type", "email"],
                                "limit": 1,
                                "context": {"lang": "es_UY"},
                            },
                        )
                        record = record[0]
                        old_id = record.pop('id')
                        child_record = odoo_object.search([("old_id", "=", old_id)], limit=1)
                        if not child_record:
                            record['old_id'] = old_id
                            child_record = odoo_object.with_context(lang=lang).create(record)
                        value_ids.append(child_record.id)
                    except Exception as error:
                        _logger.info(error)
                else:
                    try:
                        record = source_models.execute_kw(
                            source_database,
                            source_uid,
                            source_password,
                            field_to_model.get(field),
                            "search_read",
                            [[("id", "=", m2m_id)]],
                            {"fields": ["name"], "limit": 1, "context": {"lang": "es_UY"}},
                        )
                        record_name = record[0]["name"]
                        child_record = odoo_object.search([("name", "ilike", record_name)], limit=1)
                        if not child_record:
                            child_record = odoo_object.with_context(lang=lang).create(record[0])
                        value_ids.append(child_record.id)
                    except Exception as error:
                        _logger.info(error)
        if field_type == "one2many":
            value[field] = [(6, 0, value_ids)]
        elif field_type == "many2many":
            value[field] = [(6, 0, value_ids)]
        else:
            raise UserError(
                "No se ha implementado la migración para este tipo de campo"
            )
        return value

    def create_log_line(self, error="", log_type=None, values=None, record=False):
        error_log_line_obj = self.env["odoo.migrator.log.line"]
        log_line = error_log_line_obj.create(
            {
                "migrator_id": self.id,
                "error": error,
                "log_type": log_type,
                "values": values,
                "migration_model": self.migration_model,
            }
        )
        return True

    def create_error_log(self, values=None, msg: str = "") -> bool:
        msg = f"ERROR => Message: {msg}\nValues: {values}"
        _logger.info(msg)
        _logger.error(msg)
        self.create_log_line(error=msg, log_type="error", values=values)

    def create_success_log(self, values=None) -> bool:
        msg = f"SUCCESS => Values: {values}"
        _logger.info(msg)
        _logger.info(msg)
        self.create_log_line(log_type="success", values=values)

    def try_to_create_record(self, odoo_object=None, value=None, old_odoo_obj=None):
        currency_rate_model = "res.currency.rate"
        #
        if odoo_object._name == currency_rate_model:
            record_id = self._find_a_currency_rate_for(
                rate_name=value["name"][:10],
                rate_company_id=value["company_id"],
                rate_currency_id=value["currency_id"],
            )
            if bool(record_id):
                record = odoo_object.sudo().browse(record_id)
                record.old_id = value["id"]
                return True, record
                # if record._name == "product.template":
                #     return True, record
        try:
            if old_odoo_obj and old_odoo_obj == "account.invoice.line":
                if isinstance(value, list):
                    for val in value:
                        val["invoice_old_id"] = val.pop("id")
                else:
                    value["invoice_old_id"] = value.pop("id")
            else:
                value["old_id"] = value.pop("id")
            if not self._context.get('check_move_validity', True):
                record = odoo_object.sudo().with_context(check_move_validity=False).create(value)
            else:
                record = odoo_object.sudo().create(value)
            return True, record
        except Exception as error:
            return False, error

    #################### UTILITY FUNC ####################
    def _remove_m2o_o2m_and_m2m_data_from(self, data, model_obj=None, lang=None):
        if not bool(data) or model_obj is None:
            _logger.info("¡Parametros incorrectos, data y model_obj tienen que estar seteados!")
            return
        for field in list(data):
            if field == 'image' and model_obj._name == "res.partner":
                data['image_1920'] = data.pop(field)
                continue
            if field == 'type' and model_obj._name == "product.template":
                data['detailed_type'] = data.pop(field)
                continue
            elif field == "move_id" and model_obj._name == "account.move.line":
                old_id = self.env["account.move"].search([("old_id", "=", data.get("move_id")[0])], limit=1)
                data[field] = old_id.id
                continue
            elif field == "account_analytic_id" and model_obj._name == "account.move.line":
                new_field = 'analytic_distribution'
                analytic_old_id = data[field][0]
                analytic_id = self.env[field_to_model.get(field)].search([("old_id", "=", analytic_old_id)], limit=1)
                data[new_field] = {analytic_id.id: 100}
                continue
            is_field_empty = bool(data.get(field, False))
            if not is_field_empty:
                if isinstance(data.get(field, []), list):
                    data.pop(field)
                continue

            field_type = model_obj._fields[field].type
            if field_type == "many2one" and is_field_empty:
                data = self.resolve_m2o_fields(value=data, m2o=field, lang=lang)
            elif field_type in ["many2many", "one2many"] and is_field_empty:
                data = self.resolve_m2m_o2m_fields(value=data, field_type=field_type, field=field, lang=lang)

    def _run_remote_command_for(
            self,
            model_name: str,
            operation: str = "search_read",
            operation_params_list: List[Tuple] = [],
            command_params_dict: Dict = {},
    ):
        source_models, source_uid, source_database, source_password = (
            self._get_source_odoo_connection()
        )
        datas = source_models.execute_kw(
            source_database,
            source_uid,
            source_password,
            model_name,
            operation,
            [operation_params_list],
            command_params_dict,
        )
        return datas

    def _clean_relational_fields_for(self, data: Dict, model_obj=None) -> None:
        if not bool(data) or model_obj is None:
            _logger.info(
                "¡Parametros incorrectos, data y model_obj tienen que estar seteados!"
            )
            return
        for field_name in data:
            if not field_name in field_to_model:
                #
                # _logger.info(f"El field {field_name} no esta en la list {field_to_model}")
                continue

            field_model: str = field_to_model.get(field_name, "")
            if not field_model:
                continue

            # field_obj = self.env[field_model]
            field_type: str = model_obj._fields[field_name].type
            if field_type in ("one2many", "many2many"):
                del data[field_name]
                continue

            if field_type != "many2one":
                continue

            field_data: List = data[field_name]
            if not bool(field_data):
                continue

            old_id = field_data[0]
            new_model_id = self.env[field_model].search([("old_id", "=", old_id)], order="id asc", limit=1)
            if not bool(new_model_id):
                message = f"No se ha encontrado el registro para {field_name} con old_id {old_id}"
                self.create_error_log(msg=message)
                continue
            data[field_name] = new_model_id.id

    def _try_to_create_model(self, model_name: str, values: Dict) -> Tuple[Any, str]:
        """
        Tries to create the model with the values given
        """
        model_obj = self.env[model_name].sudo()
        try:
            model_id = model_obj.create(values)
            model_id.old_id = values["id"]
            return True, model_id
        except Exception as error:
            return False, str(error)

    #################### MIGRATORS ####################
    def migrate_contacts(self) -> bool:
        """
        Método para migrar contactos desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando los Contactos")

        limit = 1000
        model_name: str = "res.partner"
        migrated_ids = []
        contact_obj = self.env[model_name]
        migrated_contacts = contact_obj.search([("old_id", "!=", False)])
        if migrated_contacts:
            migrated_ids = migrated_contacts.mapped("old_id")
        commit_count = 500
        side_count = 0
        to_create = []
        for migrator in self:
            lang = self.company_id.partner_id.lang
            contact_datas = migrator._run_remote_command_for(
                model_name=model_name,
                command_params_dict={
                    "fields": CONTACT_FIELDS,
                    "limit": migrator.pagination_limit,
                    "context": {"lang": lang},
                    "offset": migrator.pagination_offset,
                    # "limit": 10,
                },
                operation_params_list=[("id", "not in", migrated_ids)],
                # operation_params_list=[("id", "in", [751])],
            )

            if not bool(contact_datas):
                continue
            total = len(contact_datas)
            for contador, contact_data in enumerate(contact_datas, start=1):
                side_count += 1
                if side_count >= commit_count:
                    side_count = 0
                    result = contact_obj.create(to_create)
                    migrator.contact_ids += result
                    self.env.cr.commit()
                    _logger.info('***\n******\n******\n***commit***\n******\n******\n***')
                    print('***\n******\n******\n***commit***\n******\n******\n***')
                    continue
                _logger.info(f"vamos {contador} / {total}")
                old_contact_id = contact_data["id"]
                search_conditions = ['&', ("old_id", "=", old_contact_id), '|', ("active", "=", True), ("active", "=", False)]
                contact_id = contact_obj.search(search_conditions, limit=1)
                if contact_id:
                    _logger.info(f'el contacto {contact_data["name"]} ya existe')
                    contact_id.old_id = contact_data["id"]
                    migrator.contact_ids += contact_id
                    continue
                contact_data = migrator.remove_unused_fields(record_data=contact_data, odoo_model=model_name)
                migrator._remove_m2o_o2m_and_m2m_data_from(data=contact_data, model_obj=contact_obj, lang=lang)
                contact_data['old_id'] = old_contact_id
                # if contact_data not in to_create:
                #     to_create.append(contact_data)
                is_success, result = migrator.try_to_create_record(odoo_object=contact_obj, value=contact_data)
                if not is_success:
                    self.env.cr.rollback()
                    migrator.create_error_log(msg=str(result), values=contact_data)
                    continue
                migrator.contact_ids += result
                migrator.create_success_log(values=contact_data)
                _logger.info(f"se creo el contacto {result.name}")

            # result = contact_obj.create(to_create)
            # migrator.contact_ids += result
            _logger.info(f"se crearon {len(self.contact_ids)} contactos")
            self.env.cr.commit()

        return True

    def migrate_countries(self) -> bool:
        """
        Método para migrar paises desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando los paises")
        limit = 100000
        model_name: str = "res.country"
        country_obj = self.env[model_name]
        for migrator in self:
            lang = self.company_id.partner_id.lang
            country_datas = migrator._run_remote_command_for(
                model_name=model_name,
                command_params_dict={
                    "fields": ["name", "code"],
                    "limit": limit,
                    "context": {"lang": lang},
                },
                # operation_params_list=[("code", "=", False)],
            )

            if not bool(country_datas):
                continue

            total = len(country_datas)
            countries_without_code = []
            for contador, country_data in enumerate(country_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                country_code = country_data.get("code", False)
                if not country_code:
                    countries_without_code.append(country_data)
                    continue
                search_conditions = [
                    "|",
                    "|",
                    ("old_id", "=", country_data["id"]),
                    ("name", "ilike", country_data["name"]),
                    ("code", "=", country_data["code"]),
                ]
                country_id = country_obj.search(
                    search_conditions,
                    limit=1,
                )
                if country_id:
                    _logger.info(f'el país {country_data["name"]} ya existe')
                    country_id.old_id = country_data["id"]
                    migrator.country_ids += country_id
                    continue
                is_success, result = migrator.try_to_create_record(
                    odoo_object=country_obj, value=country_data
                )
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=country_data)
                    continue
                migrator.create_success_log(values=country_data)
                _logger.info(f"se creo el contacto {result.name}")
                migrator.country_ids += result
            if countries_without_code:
                message = f'Los siguienes países no tienen código: {[(x["name"], x["id"]) for x in countries_without_code]}'
                migrator.create_error_log(
                    msg=str(message), values=countries_without_code
                )
            _logger.info(f"se crearon {len(self.country_ids)} paises")

        return True

    def migrate_states(self) -> bool:
        """
        Método para migrar paises desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando los estados")
        limit = 100000
        model_name: str = "res.country.state"
        state_obj = self.env[model_name]
        for migrator in self:
            lang = self.company_id.partner_id.lang
            state_datas = migrator._run_remote_command_for(
                model_name=model_name,
                command_params_dict={
                    "fields": ["name", "code", "country_id"],
                    "limit": limit,
                    "context": {"lang": lang},
                },
                # operation_params_list=[("code", "=", False)],
            )

            if not bool(state_datas):
                continue

            total = len(state_datas)
            states_without_code = []
            for contador, state_data in enumerate(state_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                state_code = state_data.get("code", False)
                if not state_code:
                    states_without_code.append(state_data)
                    continue
                search_conditions = [
                    "|",
                    "|",
                    ("old_id", "=", state_data["id"]),
                    ("name", "ilike", state_data["name"]),
                    ("code", "=", state_data["code"]),
                ]
                state_id = state_obj.search(
                    search_conditions,
                    limit=1,
                )
                if state_id:
                    _logger.info(f'el estado {state_data["name"]} ya existe')
                    state_id.old_id = state_data["id"]
                    migrator.state_ids += state_id
                    continue
                state_data = self.resolve_m2o_fields(
                    value=state_data, odoo_object=state_obj, m2o="country_id", lang=lang
                )
                is_success, result = migrator.try_to_create_record(
                    odoo_object=state_obj, value=state_data
                )
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=state_data)
                    continue
                migrator.create_success_log(values=state_data)
                _logger.info(f"se creo el contacto {result.name}")
                migrator.state_ids += result
            if states_without_code:
                message = f'Los siguienes estados no tienen código: {[(x["name"], x["id"]) for x in states_without_code]}'
                migrator.create_error_log(msg=str(message), values=states_without_code)
            _logger.info(f"se crearon {len(self.state_ids)} estados")

        return True

    def migrate_currencies(self) -> bool:
        """
        Método para migrar monedas desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando las Monedas")

        limit = 100
        model_name: str = "res.currency"
        currency_obj = self.env[model_name]
        for migrator in self:
            lang = self.company_id.partner_id.lang

            currencies_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("active", "=", True)],
                command_params_dict={
                    "fields": ["name", "symbol", "position", "rounding", "decimal_places"],
                    "limit": limit,
                    "context": {"lang": lang}},
            )

            if not bool(currencies_datas):
                continue

            total = len(currencies_datas)

            for contador, currency_data in enumerate(currencies_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                # domain = ["|", "|", ("old_id", "=", currency_data["id"]), ("name", "ilike", currency_data["name"]),("active", "=", False)]
                domain = [("name", "ilike", currency_data["name"])]
                currency_id = currency_obj.search(domain, limit=1, )
                if not currency_id:
                    domain.append(("active", "=", False))
                    currency_id = currency_obj.search(domain, limit=1, )

                if currency_id:
                    _logger.info(f'la moneda {currency_data["name"]} ya existe')
                    if not currency_id.active:
                        currency_id.active = True
                        migrator.env.cr.commit()
                    currency_data["old_id"] = currency_data.pop("id")
                    currency_id.update(currency_data)
                    # currency_id.old_id = currency_data["id"]
                    migrator.currency_ids += currency_id
                    continue

                is_success, result = migrator.try_to_create_record(odoo_object=currency_obj, value=currency_data)
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=currency_data)
                    continue
                migrator.create_success_log(values=currency_data)
                _logger.info(f"se creo la cotiacion {result.name}")
                migrator.currency_ids += result

            _logger.info(f"se crearon {len(self.currency_ids)} monedas")

        return True

    def migrate_currency_rates(self) -> bool:
        """
        Método para migrar tasas monedas desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando las tasas de Cambio de las Monedas")

        if not bool(self.currency_ids):
            raise UserError("No hay Monedas migradas")

        model_name: str = "res.currency.rate"
        currency_rate_obj = self.env[model_name]
        for migrator in self:
            for currency in migrator.currency_ids.filtered(
                    lambda x: not x.is_current_company_currency
            ):
                search_conditions = [
                    ("currency_id", "=", currency.old_id),
                    "|",
                    ("company_id", "=", migrator.company_id.old_id),
                    ("company_id", "=", False),
                ]
                currency_rate_datas = migrator._run_remote_command_for(
                    model_name=model_name,
                    operation_params_list=search_conditions,
                    # command_params_dict={
                    #     "offset": migrator.pagination_offset,
                    #     "limit": migrator.pagination_limit,
                    # },
                )

                if not bool(currency_rate_datas):
                    continue

                total = len(currency_rate_datas)
                for contador, currency_rate_data in enumerate(
                        currency_rate_datas, start=1
                ):
                    _logger.info(f"vamos {contador} / {total}")

                    rate_name = currency_rate_data["name"][:10]
                    rate_currency_id = currency.id
                    rate_company_id = migrator.company_id.id

                    ################################################
                    ################################################

                    rate_id = migrator._find_a_currency_rate_for(
                        rate_name=rate_name,
                        rate_company_id=rate_company_id,
                        rate_currency_id=rate_currency_id,
                    )

                    if bool(rate_id):
                        currency_rate_id = currency_rate_obj.sudo().browse(rate_id)
                        _logger.info(f'la cotización {currency_rate_data["name"]} ya existe')
                        currency_rate_id.old_id = currency_rate_data["id"]
                        migrator.currency_rate_ids += currency_rate_id
                        continue

                    currency_rate_data = migrator.remove_unused_fields(
                        record_data=currency_rate_data, odoo_model=model_name
                    )
                    currency_rate_data["company_id"] = rate_company_id
                    currency_rate_data["currency_id"] = rate_currency_id
                    # migrator._remove_m2o_o2m_and_m2m_data_from(data=currency_rate_data, model_obj=currency_rate_obj)

                    is_success, result = migrator.try_to_create_record(
                        odoo_object=currency_rate_obj, value=currency_rate_data
                    )
                    if not is_success:
                        migrator.create_error_log(
                            msg=str(result), values=currency_rate_data
                        )
                        continue
                    migrator.create_success_log(values=currency_rate_data)
                    _logger.info(f"se creo la tasa {result.name}")

                    migrator.currency_rate_ids += result

            # Marca la migración de monedas como completa
            _logger.info(f"se crearon {len(migrator.currency_rate_ids)} tasas de monedas")
        return True

    def _find_a_currency_rate_for(
            self, rate_name: str, rate_company_id: int, rate_currency_id: int
    ):
        self._cr.execute(
            self._get_sql_to_find_currency_rate(),
            (
                rate_name,
                rate_currency_id,
                rate_company_id,
            ),
        )
        return self._cr.fetchone()

    def _get_sql_to_find_currency_rate(self) -> str:
        return """
            SELECT cr.id
            FROM res_currency_rate cr
            WHERE cr.name = %s AND cr.currency_id = %s AND cr.company_id = %s
        """

    def migrate_account_type_mapping(self) -> bool:
        """
        Método para migrar el plan de cuentas de odoo origen a destino.
        """
        _logger.info("\nMigrando Tipos de cuenta")
        model_name: str = "account.account.type"
        migrator_account_type_obj = self.env['odoo.migrator.account.type']
        for migrator in self:
            company = migrator.company_id
            is_company_old_id_set = company.old_id <= 0
            if is_company_old_id_set:
                raise UserError(f"¡La Old_id de la Compañía {company.name} no es correcta!")

            account_type_datas = migrator._run_remote_command_for(
                model_name=model_name,
                command_params_dict={
                    "fields": [
                        "name",
                    ],
                },
            )

            if not bool(account_type_datas):
                continue

            total = len(account_type_datas)
            for contador, account_type_data in enumerate(account_type_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                account_type_name = account_type_data["name"]
                migrator_account_type_id = migrator_account_type_obj.search([("name", "=", account_type_name)], limit=1)

                if not migrator_account_type_id:
                    migrator_account_type_id = migrator_account_type_obj.create({'name': account_type_name})

                    migrator.create_success_log(values=account_type_datas)
                    _logger.info(f"se creo el tipo de  cuentas {migrator_account_type_id.name}")

        _logger.info(f"se crearon {len(migrator_account_type_obj.search([]))} tipos de cuentas")
        return True

    def migrate_chart_of_accounts(self) -> bool:
        """
        Método para migrar el plan de cuentas de odoo origen a destino.
        """
        _logger.info("\nMigrando Plan de cuenta")
        model_name: str = "account.account"
        chart_of_accounts_obj = self.env[model_name]
        currency_obj = self.env['res.currency']
        have_local_charts_of_accounts = chart_of_accounts_obj.search([])
        if not bool(have_local_charts_of_accounts):
            _logger.info("¡Sin Planes de cuenta que actualizar!")
            return False
        chart_accounts_ids = have_local_charts_of_accounts.filtered(lambda x: not x.old_id).mapped('code')
        odoo_account_type_obj = self.env['odoo.migrator.account.type']
        for migrator in self:
            company = migrator.company_id
            is_company_old_id_set = company.old_id <= 0
            if is_company_old_id_set:
                raise UserError(
                    f"¡La Old_id de la Compañía {company.name} no es correcta!"
                )

            chart_of_accounts_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("company_id", "=", company.old_id)],
                command_params_dict={
                    "fields": CHART_OF_ACCOUNT_FIELDS,
                    # "offset": migrator.pagination_offset,
                    # "limit": 10,
                },
            )
            if not bool(chart_of_accounts_datas):
                continue

            old_chart_of_accounts_ids = [x['code'] for x in chart_of_accounts_datas]
            #estas son las cuentas que ya existen en el odoo destino (es decir, existen en ambos)
            #le pedimos al usuario que resuelva estos conflictos
            conflictive_accounts = [x for x in old_chart_of_accounts_ids if x in chart_accounts_ids]
            if conflictive_accounts:
                message = f"Las siguientes cuentas ya existen en el sistema: {conflictive_accounts} \n Por favor, resuelva estos conflictos antes de continuar"
                migrator.create_error_log(msg=str(message), values='n/a')
                self.env.cr.commit()
                raise UserError(message)

            account_type_mapping = odoo_account_type_obj.search([])
            if not account_type_mapping:
                self.migrate_account_type_mapping()
            elif account_type_mapping.filtered(lambda x: not x.account_type):
                raise UserError(
                    "Se encontraron mapeos de tipos de cuentas sin tipo de cuenta asociado. \n Por favor, resuelva estos conflictos antes de continuar (Menu Mapeo de Datos/Tipos de Cuentas)")

            total = len(chart_of_accounts_datas)

            for contador, chart_of_accounts_data in enumerate(chart_of_accounts_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                account_old_id = chart_of_accounts_data["id"]
                search_conditions = [("old_id", "=", account_old_id)]
                account_exists = chart_of_accounts_obj.search(search_conditions, limit=1)
                if account_exists:
                    _logger.info(f'la cuenta {chart_of_accounts_data["name"]} ya existe')
                    print(f'la cuenta {chart_of_accounts_data["name"]} ya existe')
                    migrator.chart_of_accounts_ids += account_exists
                    continue

                user_type_name = chart_of_accounts_data.pop("user_type_id")[1]
                account_type_id = odoo_account_type_obj.search([("name", "=", user_type_name)], limit=1)
                chart_of_accounts_data["account_type"] = account_type_id.account_type
                chart_of_accounts_data["old_id"] = chart_of_accounts_data.pop("id")
                chart_of_accounts_data["internal_group"] = chart_of_accounts_data.pop("internal_type")
                if chart_of_accounts_data.get("currency_id", False):
                    currency_id = currency_obj.search([('old_id', '=', chart_of_accounts_data.get("currency_id")[0])])
                    if currency_id:
                        chart_of_accounts_data["currency_id"] = currency_id.id
                account_id = chart_of_accounts_obj.create(chart_of_accounts_data)
                _logger.info(f"Se creo la cuenta {account_id.name}")
                migrator.create_success_log(values=chart_of_accounts_data)
                _logger.info(f"Se creo la cuenta {account_id.name}")
                migrator.chart_of_accounts_ids += account_id
        final_message = f"se actualizaron {len(self.chart_of_accounts_ids)} Planes de cuentas"
        migrator.create_success_log( values=final_message)
        _logger.info(final_message)
        return True

    def _migrate_analytic_account_plan(self):
        return self.env.ref('odoo_migrator.migration_analytic_plan').id

    def migrate_analytic_accounts(self) -> bool:
        """
        Método para migrar el plan de cuentas de odoo origen a destino.
        """
        _logger.info("\nMigrando Plan de cuentas analitico")
        model_name: str = "account.analytic.account"
        analytic_accounts_obj = self.env[model_name]
        for migrator in self:
            company = migrator.company_id
            is_company_old_id_set = company.old_id <= 0
            if is_company_old_id_set:
                raise UserError(f"¡La Old_id de la Compañía {company.name} no es correcta!")

            analytic_accounts_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("company_id", "=", company.old_id)],
                command_params_dict={
                    "fields": ANALYTIC_ACCOUNT_FIELDS,
                },
            )
            if not bool(analytic_accounts_datas):
                continue
            total = len(analytic_accounts_datas)
            for contador, analytic_accounts_data in enumerate(analytic_accounts_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                analytic_account_old_id = analytic_accounts_data["id"]
                search_conditions = [("old_id", "=", analytic_account_old_id)]
                analytic_account_exists = analytic_accounts_obj.search(search_conditions, limit=1)
                if analytic_account_exists:
                    _logger.info(f'El plan de cuentas analitico {analytic_accounts_data["name"]} ya existe')
                    print(f'El plan de cuentas analitico {analytic_accounts_data["name"]} ya existe')
                    continue
                analytic_accounts_data = migrator.remove_unused_fields(record_data=analytic_accounts_data,odoo_model=model_name)
                migrator._remove_m2o_o2m_and_m2m_data_from(data=analytic_accounts_data, model_obj=analytic_accounts_obj)
                analytic_accounts_id = analytic_accounts_data["id"]
                analytic_account_id = analytic_accounts_obj.search([("old_id", "=", analytic_accounts_id)])
                analytic_accounts_data["plan_id"] = self._migrate_analytic_account_plan()
                # analytic_accounts_data["company_id"] = migrator.company_id.old_id
                if not bool(analytic_account_id):
                    is_success, result = migrator._try_to_create_model(model_name=model_name,
                                                                       values=analytic_accounts_data)
                    if not is_success:
                        migrator.create_error_log(msg=str(result), values=analytic_accounts_data)
                        continue
                    migrator.analytic_account_ids += result

                migrator.create_success_log(values=analytic_accounts_data)
                _logger.info(f"Se creo la cuenta analitica {analytic_account_id.name}")

        _logger.info(f"se migraron {len(self.analytic_account_ids)} cuentas analiticas")
        return True

    def migrate_users(self) -> bool:
        """
        Método para migrar los usuarios de odoo origen a destino.
        """
        _logger.info("\nMigrando los usuarios")
        model_name: str = "res.users"
        res_users_obj = self.env[model_name]
        to_create = []
        for migrator in self:
            company = migrator.company_id
            is_company_old_id_set = company.old_id <= 0
            if is_company_old_id_set:
                raise UserError(f"¡La Old_id de la Compañía {company.name} no es correcta!")

            res_users_datas = migrator._run_remote_command_for(
                model_name=model_name,
                # operation_params_list=['&', '|', ("company_id", "=", company.old_id), ("company_id", "=", False), '|', ("active", "=", True), ("active", "=", False)],
                operation_params_list=['&', ("company_id", "=", company.old_id), '|', ("active", "=", True), ("active", "=", False)],
                # operation_params_list=['|', ("active", "=", True), ("active", "=", False)],
                command_params_dict={
                    "fields": RES_USERS_FIELDS,
                    "order": "id asc",
                },
            )
            if not bool(res_users_datas):
                continue
            total = len(res_users_datas)
            commit_count = 5
            side_count = 0
            for contador, res_users_data in enumerate(res_users_datas, start=1):
                side_count += 1
                if side_count > commit_count:
                    side_count = 0
                    self.env.cr.commit()
                    _logger.info(f"commit {contador // commit_count}")
                _logger.info(f"vamos {contador} / {total}")
                res_users_data = migrator.remove_unused_fields(record_data=res_users_data, odoo_model=model_name)
                migrator._remove_m2o_o2m_and_m2m_data_from(data=res_users_data, model_obj=res_users_obj)
                res_users_data_id = res_users_data["id"]
                res_users_data_name = res_users_data["login"]
                # user_id = res_users_obj.search(['|', ("old_id", "=", res_users_data_id), ("login", "=", res_users_data_name)])
                user_id = res_users_obj.search([("old_id", "=", res_users_data_id)])
                if not user_id:
                    user_id = res_users_obj.search([("login", "=", res_users_data_name)])
                    if not user_id:
                        user_id = res_users_obj.search([("login", "=", res_users_data_name),("active", "=", False)])
                    if user_id:
                        user_id.old_id = res_users_data_id
                        migrator.user_ids += user_id
                        continue
                migrator.user_ids += user_id

                if not bool(user_id):
                    res_users_data['old_id'] = res_users_data_id
                    to_create.append(res_users_data)
                    #   is_success, result = migrator._try_to_create_model(model_name=model_name, values=res_users_data)
                    #if not is_success:
                        #migrator.create_error_log(msg=str(result), values=res_users_data)
                        #continue
                    #migrator.user_ids += result
                    #else:
                    #user_id.old_id = res_users_data_id
                migrator.create_success_log(values=res_users_data)
                _logger.info(f"Se creo el usuario {user_id.name}")
            result = self.env["res.users"].create(to_create)
            migrator.user_ids += result


        _logger.info(f"se migraron {len(self.user_ids)} usuarios")
        return True

    def create_journal_id(self, values: Dict) -> bool:
        account_journal_obj = self.env["account.journal"].sudo()
        journal_id = False
        try:
            journal_id = account_journal_obj.create(values)
            journal_id.old_id = values["id"]
            _logger.info(f"creamos el diario {journal_id.name}")
            self.create_success_log(values=values)
        except Exception as error:
            self.create_error_log(msg=str(error), values=values)
        return journal_id

    def migrate_journals(self) -> bool:
        """
        Método para actualizar los Diarios desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando los Diarios contables")

        model_name: str = "account.journal"
        journals_obj = self.env[model_name]
        for migrator in self:
            company = migrator.company_id
            is_company_old_id_set = company.old_id <= 0
            if is_company_old_id_set:
                raise UserError(
                    f"¡La Old_id de la Compañía {company.name} no es correcta!"
                )

            journal_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("company_id", "=", company.old_id)],
                command_params_dict={
                    "fields": ACCOUNT_JOURNAL_FIELDS,
                },
            )

            if not bool(journal_datas):
                continue

            total = len(journal_datas)
            for contador, journal_data in enumerate(journal_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                print(f"vamos {contador} / {total}")
                journal_old_id = journal_data["id"]
                journal_code = journal_data["code"]
                journal_id = journals_obj.search(['&',("old_id", "=", journal_old_id), '|', ("active", "=", True),("active", "=", False)])
                if not journal_id:
                    journal_id = journals_obj.search(['&',("code", "=", journal_code), '|', ("active", "=", True),("active", "=", False)], limit=1)
                    if journal_id:
                        raise UserError(f"Ya existe un diario con el código {journal_code}")
                journal_data['default_account_id'] = journal_data.pop('default_debit_account_id')
                migrator._remove_m2o_o2m_and_m2m_data_from(data=journal_data, model_obj=journals_obj)

                if not bool(journal_id):
                    is_success, result = migrator._try_to_create_model(model_name=model_name, values=journal_data)
                    if not is_success:
                        self.env.cr.rollback()
                        migrator.create_error_log(msg=str(result), values=journal_data)
                        self.env.cr.commit()
                        raise UserError(result)
                        # continue
                    migrator.journal_ids += result
                    _logger.info(f"se creó el Diario {journal_id.name}")
                    migrator.create_success_log(values=journal_data)
                else:
                    journal_data['old_id'] = journal_data.pop('id')
                    journal_id.update(journal_data)
                    message = f'Se actualizó el Diario {journal_id.name}'
                    _logger.info(message)
                    _logger.info(message)
                    migrator.create_success_log(values=message)

                migrator.journal_ids += journal_id

        _logger.info(f"se actualizaron {len(self.journal_ids)} Diarios contables")
        return True

    def migrate_product_categories(self) -> bool:
        """
        Método para migrar las Categorias de producto desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando las Categorias de Producto")
        model_name: str = "product.category"
        product_category_obj = self.env[model_name]
        for migrator in self:

            product_category_datas = migrator._run_remote_command_for(
                model_name=model_name,
                command_params_dict={
                    "fields": [
                        "id",
                        "name",
                        "parent_id",
                        "child_id",
                    ],
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(product_category_datas):
                continue

            total = len(product_category_datas)
            for contador, product_category_data in enumerate(product_category_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                category_old_id = product_category_data["id"]
                category_name = product_category_data["name"]
                category_parent = (product_category_data["parent_id"] if "parent_id" in product_category_data else False)
                search_params = ["|", ("old_id", "=", category_old_id), ("name", "ilike", category_name)]
                product_category_id = product_category_obj.search(search_params, limit=1,)

                if bool(product_category_id):
                    _logger.info(f"la Categoria de producto {category_name} ya existe")
                    product_category_id.old_id = category_old_id
                    migrator.product_categories_ids += product_category_id
                    continue

                product_category_data = migrator.remove_unused_fields(record_data=product_category_data,odoo_model=model_name)
                migrator._remove_m2o_o2m_and_m2m_data_from(data=product_category_data, model_obj=product_category_obj)

                category_creation_data = {
                    "id": category_old_id,
                    "name": category_name,
                }

                is_success, result = migrator.try_to_create_record(
                    odoo_object=product_category_obj, value=category_creation_data
                )

                if not is_success:
                    migrator.create_error_log(
                        msg=str(result), values=product_category_data
                    )
                    continue

                if bool(category_parent):
                    category_parent_old_id = category_parent[0]
                    category_parent_id = product_category_obj.search(
                        [("old_id", "=", category_parent_old_id)]
                    )
                    result.parent_id = category_parent_id.id

                migrator.create_success_log(values=product_category_data)
                _logger.info(f"se creo la Categoria {result.name}")
                migrator.product_categories_ids += result

            _logger.info(
                f"se crearon {len(self.product_categories_ids)} Categorias de producto"
            )
        return True

    def migrate_product_template(self) -> bool:
        """
        Método para migrar las Plantillas de producto desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando las Plantillas de Producto")
        self = self.sudo()
        model_name: str = "product.template"
        categ_model_name: str = "product.category"
        categ_field_name: str = "categ_id"

        if not bool(self.product_categories_ids):
            raise UserError("No hay Categorias de productos migradas")

        product_template_obj = self.env[model_name]
        for migrator in self:
            for categ_id in migrator.product_categories_ids:
                _logger.info(f"migrando Plantillas para la Categoria {categ_id.display_name}")
                domain = ['&', ('categ_id', '=', categ_id.old_id), '|', ('active', '=', True), ('active', '=', False)]
                operation_params_list = domain
                product_template_datas = migrator._run_remote_command_for(
                    model_name=model_name,
                    operation_params_list=operation_params_list,
                    command_params_dict={
                        "fields": PRODUCT_TEMPLATE_FIELDS,
                        "offset": migrator.pagination_offset,
                        "limit": migrator.pagination_limit,
                    },
                )
                if not bool(product_template_datas):
                    continue

                total = len(product_template_datas)
                commit_count = 5
                side_count = 0
                for contador, product_template_data in enumerate(product_template_datas, start=1):
                    _logger.info(f"vamos {contador} / {total}")
                    side_count += 1
                    if side_count >= commit_count:
                        _logger.info("committing...")
                        print("committing...")
                        self.env.cr.commit()
                        side_count = 0
                    template_old_id = product_template_data["id"]
                    template_name = product_template_data["name"]
                    _logger.info(template_name)
                    template_domain = ['&', ('old_id', '=', template_old_id), '|', ('active', '=', True), ('active', '=', False)]
                    product_template_id = product_template_obj.search(template_domain,limit=1)

                    if bool(product_template_id):
                        _logger.info(f"la Plantilla de producto {template_name} ya existe")
                        product_template_id.old_id = template_old_id
                        product_template_id.categ_id = categ_id.id
                        product_template_id.company_id = self.company_id.id
                        migrator.product_templates_ids += product_template_id
                        continue

                    migrator._remove_m2o_o2m_and_m2m_data_from(data=product_template_data, model_obj=product_template_obj)

                    is_success, result = migrator.try_to_create_record(odoo_object=product_template_obj, value=product_template_data)

                    if not is_success:
                        migrator.create_error_log(msg=str(result), values=product_template_data)
                        continue

                    # result.company_id = migrator.company_id.id
                    result.product_variant_id.old_id = result.old_id
                    migrator.product_templates_ids += result
                    migrator.create_success_log(values=product_template_data)
                    _logger.info(f"se creo el producto ->> {result.name}")

            _logger.info(
                f"se crearon {len(self.product_templates_ids)} Plantillas de producto"
            )
        return True


    def migrate_taxes(self) -> bool:
        """
        Método para migrar los impuestoso desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando los impuestos")

        model_name: str = "account.tax"

        tax_obj = self.env[model_name]
        for migrator in self:
            tax_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("active", "=", True), ('company_id', '=', self.company_id.old_id)],
                command_params_dict={
                    # "fields": PRODUCT_TEMPLATE_FIELDS,
                    # "offset": migrator.pagination_offset,
                    # "limit": migrator.pagination_limit,
                },
            )
            if not bool(tax_datas):
                continue

            total = len(tax_datas)
            for contador, tax_data in enumerate(tax_datas, start=1):
                tax_data = self.remove_unused_fields(record_data=tax_data, odoo_model=model_name)
                _logger.info(f"vamos {contador} / {total}")
                tax_old_id = tax_data["id"]
                tax_name = tax_data["name"]
                _logger.info(tax_name)
                tax_id = tax_obj.search([("old_id", "=", tax_old_id)], limit=1, )

                if bool(tax_id):
                    _logger.info(f"la Plantilla de producto {tax_name} ya existe")
                    # tax_id.old_id = tax_old_id
                    # tax_id.company_id = self.company_id.id
                    migrator.tax_ids += tax_id
                    continue
                migrator._remove_m2o_o2m_and_m2m_data_from(data=tax_data, model_obj=tax_obj, lang=self.company_id.partner_id.lang)

                is_success, result = migrator.try_to_create_record(odoo_object=tax_obj, value=tax_data)

                if not is_success:
                    migrator.create_error_log(msg=str(result), values=tax_data)
                    continue

                # result.company_id = migrator.company_id.id
                migrator.create_success_log(values=tax_data)
                _logger.info(f"se creo el Impuesto {result.name}")
                migrator.tax_ids += result

        _logger.info(f"se crearon {len(self.tax_ids)} impuestos")
        return True

    def migrate_products(self) -> bool:
        return False

    def get_old_full_reconcile_id_for(self, old_move_ids: List[int] = [], from_payment: bool = False) -> List[int]:
        if not bool(old_move_ids):
            _logger.info("¡old_move_ids esta vacia!")
            return []
        operation_params_list = [("id", "in", old_move_ids)]
        if not from_payment:
            operation_params_list = [("move_id", "in", old_move_ids)]
        account_move_line_datas = self._run_remote_command_for(
            model_name="account.move.line",
            operation_params_list=operation_params_list,
            command_params_dict={
                "fields": ["id", "full_reconcile_id"],
                "offset": self.pagination_offset,
                "limit": self.pagination_limit,
                "order": "id asc",
            },
        )
        result = [x.get("full_reconcile_id")[0] for x in account_move_line_datas if x.get("full_reconcile_id")]

        return result

    def migrate_account_moves(self, move_type: str = "") -> bool:
        """
        Método para migrar las Facturas desde el Odoo de origen al Odoo de destino.
        """
        self = self.with_context(check_move_validity=False)
        _logger.info(f"\nMigrando las Facturas {move_type}")
        if move_type == 'entry':
            journal_type = "general"
            old_journal_ids = self.journal_ids.filtered(lambda x: x.type == journal_type).mapped("old_id")
            operation_params_list = [
                ("company_id", "=", self.company_id.old_id),
                ("currency_id", "in", self.currency_ids.mapped("old_id")),
                ("journal_id", "in", old_journal_ids),
            ]
        else:
            journal_type = "sale" if move_type == "out_invoice" else "purchase"
            old_journal_ids = self.journal_ids.filtered(lambda x: x.type == journal_type).mapped("old_id")
            operation_params_list = [
                ("company_id", "=", self.company_id.old_id),
                ("currency_id", "in", self.currency_ids.mapped("old_id")),
                ("partner_id", "in", self.contact_ids.mapped("old_id")),
                ("journal_id", "in", old_journal_ids),
            ]
        _logger.info("\n\n¡¡¡SE ESTA FILTRANDO POR CONTACTOS y DIARIOS!!!\n\n")

        if bool(move_type) and move_type != "entry":
            inverse_move_type = "out_refund" if move_type == "out_invoice" else "in_refund"
            operation_params_list.append(("type", "in", (move_type, inverse_move_type)))
        else:
            _logger.info("ASIENTOS ENTRY")
            #operation_params_list.append(("id", "not in", self.account_moves_ids.mapped("old_id")))

        model_name: str = "account.move"
        model_name_old: str = "account.invoice"
        account_move_obj = self.env[model_name].sudo()
        to_create = []
        for migrator in self:
            account_move_datas = migrator._run_remote_command_for(
                model_name=model_name if move_type == "entry" else model_name_old,
                operation_params_list=operation_params_list,
                command_params_dict={
                    "fields": ACCOUNT_MOVE_FIELDS if move_type == "entry" else ACCOUNT_INVOICE_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                    "order": "date asc" if move_type == "entry" else  "date_invoice asc" ,
                },
            )

            if not bool(account_move_datas):
                continue

            total = len(account_move_datas)
            _logger.info(f'Se encontraron {total} facturas {move_type}')
            for contador, account_move_data in enumerate(account_move_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                move_old_id = account_move_data["id"]
                move_name = account_move_data["name"]
                account_move_id = account_move_obj.search([("old_id", "=", move_old_id)], limit=1, )

                if bool(account_move_id):
                    _logger.info(f"la Factura {move_name} ya existe")
                    account_move_id.old_id = move_old_id
                    migrator.account_moves_ids += account_move_id
                    continue
                if move_type != "entry":
                    account_move_data["move_type"] = account_move_data.pop("type")
                    account_move_data["invoice_date"] = account_move_data.pop("date_invoice")
                    account_move_data["invoice_user_id"] = account_move_data.pop("user_id")
                    account_move_data["name"] = account_move_data.pop("number")
                else:
                    account_move_data["move_type"] = "entry"

                account_move_data["old_state"] = account_move_data.pop("state")
                old_move_id_data = account_move_data.get('move_id', False)
                if old_move_id_data and False:
                    old_move_id = old_move_id_data[0]
                    if move_type != "entry":
                        account_move_data["old_full_reconcile_ids"] = (migrator.get_old_full_reconcile_id_for(old_move_ids=[old_move_id], from_payment=False))
                if 'move_id' in account_move_data:
                    account_move_data.pop("move_id")
                migrator._clean_relational_fields_for(data=account_move_data, model_obj=account_move_obj)
                is_success, result = migrator.try_to_create_record(odoo_object=account_move_obj, value=account_move_data)
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=account_move_data)
                    continue
                migrator.create_success_log(values=account_move_data)
                _logger.info(f"se creo la Factura {result.name}")
                migrator.account_moves_ids += result
            _logger.info(f"se crearon {len(self.account_moves_ids.filtered(lambda x: x.move_type == move_type))} {move_type_map.get(move_type)}")
        return True

    def migrate_account_moves_lines(self, move_type: str = "") -> bool:
        """
        Método para migrar las Lineas de Asientos desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando las Lineas de Asientos")
        moves_types = []
        if not bool(self.account_moves_ids):
            raise UserError("No hay Asientos contables migrados")

        account_moves_ids = self.account_moves_ids
        if bool(move_type):
            moves_types.append(move_type)
            inverse_move_type = "out_refund" if move_type == "out_invoice" else "in_refund"
            moves_types.append(inverse_move_type)
            account_moves_ids = account_moves_ids.filtered(lambda move: move.move_type in moves_types)

        model_name: str = "account.move.line"
        model_name_old: str = "account.invoice.line"
        move_line_obj = self.env[model_name]
        tax_obj = self.env['account.tax']
        sale_exempt_tax = tax_obj.search([('type_tax_use', '=', 'sale'), ('amount', '=', 0.00), ('active', '=', True)], limit=1)
        purchase_exempt_tax = tax_obj.search([('type_tax_use', '=', 'purchase'), ('amount', '=', 0.00), ('active', '=', True)], limit=1)
        to_create = []
        for migrator in self:
            already_migrated_ids = migrator.account_move_line_ids.mapped("old_id")
            domain = [("invoice_id", "in", account_moves_ids.mapped("old_id")), ("id", "not in", already_migrated_ids)]
            move_line_datas = migrator._run_remote_command_for(
                model_name=model_name_old,
                operation_params_list=domain,
                command_params_dict={
                    "fields": ACCOUNT_MOVE_LINE_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(move_line_datas):
                continue

            total = len(move_line_datas)
            commit_count = 500
            side_count = 0
            for contador, move_line_data in enumerate(move_line_datas, start=1):
                side_count += 1
                if side_count > commit_count:
                    _logger.info(
                        f'***\n******\n******\n******\n******\n******\n************\n******\n******\n******\n******\n******\n***')
                    _logger.info(
                        f'***\n******\n******\n******\n******\n******\n***COMMIT***\n******\n******\n******\n******\n******\n***')
                    _logger.info(
                        f'***\n******\n******\n******\n******\n******\n************\n******\n******\n******\n******\n******\n***')
                    self.env.cr.commit()
                    side_count = 0
                _logger.info(f"vamos {contador} / {total}")
                old_data = move_line_data
                if move_line_data.get("invoice_line_tax_ids", False):
                    move_line_data["tax_ids"] = move_line_data.pop("invoice_line_tax_ids")
                else:
                    if move_type == 'out_invoice' and sale_exempt_tax and sale_exempt_tax.old_id:
                        move_line_data["tax_ids"] = [sale_exempt_tax.old_id]
                    elif purchase_exempt_tax and purchase_exempt_tax.old_id:
                        move_line_data["tax_ids"] = [purchase_exempt_tax.old_id]
                move_line_data["move_id"] = move_line_data.pop("invoice_id")
                move_line_old_id = move_line_data["id"]
                move_line_name = move_line_data["name"]
                move_line_id = move_line_obj.search([("invoice_old_id", "=", move_line_old_id)], limit=1)
                move_line_id = move_line_id.with_context(check_move_validity=False)
                if bool(move_line_id):
                    _logger.info(f"la Linea de asiento {move_line_name} ya existe")
                    move_line_id.with_context(check_move_validity=False).invoice_old_id = move_line_old_id
                    migrator.account_move_line_ids += move_line_id
                    continue

                migrator._remove_m2o_o2m_and_m2m_data_from(data=move_line_data, model_obj=move_line_obj)
                move_line_data.pop("account_analytic_id")
                to_create.append(move_line_data)
                is_success, result = migrator.try_to_create_record(odoo_object=move_line_obj, value=move_line_data, old_odoo_obj=model_name_old)

                if not is_success:
                    if 'no está balanceado' in str(result):
                        move_line_data["id"] = move_line_data.pop("invoice_old_id")
                        is_success, result = migrator.with_context(check_move_validity=False).try_to_create_record(odoo_object=move_line_obj, value=move_line_data, old_odoo_obj=model_name_old, )
                        move = self.env['account.move'].browse(move_line_data["move_id"])
                        payment_lines = move.line_ids.filtered(lambda x: x.display_type == 'payment_term')
                        if len(payment_lines) > 1:
                            print('Problema')
                        if payment_lines.credit > 0:
                            payment_lines.credit = sum(move.line_ids.mapped('debit'))
                        else:
                            payment_lines.credit = sum(move.line_ids.mapped('credit'))
                        if not is_success:
                            migrator.create_error_log(msg=str(result), values=move_line_data)
                        else:
                            migrator.account_move_line_ids += result
                            migrator.create_success_log(values=move_line_data)
                            _logger.info(f"se creo la Linea de asiento {result.name}")
                    else:
                        migrator.create_error_log(msg=str(result), values=move_line_data)
                    continue
                else:
                    migrator.account_move_line_ids += result
                    migrator.create_success_log(values=move_line_data)
                    _logger.info(f"se creo la Linea de asiento {result.name}")

            _logger.info(f"se crearon {len(self.account_move_line_ids)} Lineas de asientos")
        return True

    def post_moves(self, move_type: str = "", payment_type: str = "") -> bool:
        global moves
        if bool(move_type):
            if move_type == 'entry':
                moves = self.account_moves_ids.filtered(lambda x: x.state == 'draft' and x.move_type == 'entry')
            else:
                moves = self.account_moves_ids.filtered(lambda move: move.move_type in (move_type, 'out_refund') if move_type == 'out_invoice' else move.move_type in (move_type, 'in_refund'))
        if bool(payment_type):
            moves = self.account_payments_ids.filtered(lambda move: move.partner_type == payment_type and not move.is_internal_transfer)
        if not bool(moves):
            raise UserError("No hay Asientos contables migrados")
        moves_draft = moves.filtered(
            lambda x: x.state == "draft" and x.old_state != "draft" and x.name != 'Draft Payment')
        total = len(moves_draft)
        commit_count = 50
        side_count = 0
        for contador, move in enumerate(moves_draft, start=1):
            _logger.info(f"vamos {contador} / {total}")
            _logger.info(f"vamos {contador} / {total}")
            side_count += 1
            if side_count > commit_count:
                _logger.info(
                    f'***\n******\n******\n******\n******\n******\n************\n******\n******\n******\n******\n******\n***')
                _logger.info(
                    f'***\n******\n******\n******\n******\n******\n***COMMIT***\n******\n******\n******\n******\n******\n***')
                _logger.info(
                    f'***\n******\n******\n******\n******\n******\n************\n******\n******\n******\n******\n******\n***')
                self.env.cr.commit()
                side_count = 0
            if move.old_state == "draft":
                body = 'Esta factura/pago se deja en borrador porque la factura original esta en borrador'
                _logger.info(body)
                _logger.info(body)
                move.message_post(body=body)
            elif move.old_state == "cancel":
                body = 'Cancelamos esta factura porque la factura original esta cancelada'
                _logger.info(body)
                _logger.info(body)
                move.message_post(body=body)
                move.button_cancel()
            else:
                if bool(payment_type):
                    name = move.move_id.old_name
                    move.move_id.name = name
                    if move.old_id in (31282, 31274):
                        move.message_post(body=f'Error al validar la factura')
                        move.migration_error = True
                        self.create_error_log(msg=str('Error al validar la factura'), values=move)
                        continue
                try:
                    _logger.info(f'Vamos a validar la factura / pago {move.name} de id {move.id}')
                    move.with_context(dont_check_constrains_date_sequence=True).action_post()
                except Exception as error:
                    move.message_post(body=f'Error al validar la factura {error}')
                    move.migration_error = True
                    self.create_error_log(msg=str(error), values=move)
                    #
                    continue

        return True

    def migrate_invoice_account_moves_lines(self, move_type: str = "") -> bool:
        """
        Método para migrar las Lineas de Asientos desde el Odoo de origen al Odoo de destino.
        @agus
        """
        self = self.with_context(check_move_validity=False)
        _logger.info("\nMigrando las Lineas de Asientos de las Facturas")
        moves_types = []
        if not bool(self.account_moves_ids):
            raise UserError("No hay Asientos contables migrados")
        fix_error = False
        if fix_error:
            account_moves_ids = self.migration_error_account_moves_ids
        else:
            account_moves_ids = self.account_moves_ids
        if bool(move_type):
            moves_types.append(move_type)
            inverse_move_type = "out_refund" if move_type == "out_invoice" else "in_refund"
            moves_types.append(inverse_move_type)
            account_moves_ids = account_moves_ids.filtered(lambda move: move.move_type in moves_types)

        model_name: str = "account.move.line"
        model_name_old: str = "account.move.line"
        invoice_obj = self.env["account.move"]
        account_obj = self.env["account.account"]
        move_line_obj = self.env[model_name]
        if move_type == 'out_invoice':
            operation_param = ("invoice_id", "in", account_moves_ids.mapped("old_id"))
        else:
            operation_param = ("stored_invoice_id", "in", account_moves_ids.mapped("old_id"))
        for migrator in self:
            move_line_datas = migrator._run_remote_command_for(
                model_name=model_name_old,
                operation_params_list=[
                    operation_param
                ],
                command_params_dict={
                    # "fields": ['analytic_account_id'],
                    "fields": ACCOUNT_INVOICE_MOVE_LINE_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(move_line_datas):
                continue

            total = len(move_line_datas)

            for contador, move_line_data in enumerate(move_line_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                old_data = move_line_data
                if move_type == 'out_invoice':
                    invoice_id = move_line_data.pop("invoice_id")[0]
                else:
                    invoice_id = move_line_data.pop("stored_invoice_id")[0]
                old_account_id = move_line_data.get('account_id')[0]

                invoice = invoice_obj.search([("old_id", "=", invoice_id)])
                if invoice.move_type == "out_refund":
                    _logger.info(
                        "****\n********\n********\n********\n********\n****ES UNA NOTA DE CREDITO\n********\n********\n********\n****")
                balance = move_line_data.get("balance")
                line_name = move_line_data.get("name")
                amount_currency = move_line_data.get("amount_currency")
                same_currency = invoice.currency_id == self.env.company.currency_id
                aml = invoice.line_ids.filtered(lambda x: x.balance == balance or x.balance == round(balance, 2))
                #
                if not aml and not same_currency:
                    _logger.info(
                        f'****\n********\n********\n********\n********\n****FILTRAMOS POR EL AMOUNT CURRENCY\n********\n********\n********\n****')
                    aml = invoice.line_ids.filtered(
                        lambda x: abs(x.amount_currency) == abs(amount_currency) or abs(x.amount_currency) == abs(
                            round(amount_currency, 2)))

                if aml and same_currency:
                    if len(aml) == 1:
                        aml.old_id = move_line_data.get("id")
                        migrator.create_success_log(values=move_line_data)
                        _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                    else:
                        aml = invoice.line_ids.filtered(lambda x: (x.balance == move_line_data.get("balance") or x.balance == round(move_line_data.get("balance"), 2)) and x.name[:64].replace('\n', '') == line_name)
                        if not aml:
                            aml = invoice.line_ids.filtered(lambda x: (x.balance == move_line_data.get(
                                "balance") or x.balance == round(move_line_data.get("balance"), 2)) and (line_name in x.name[:64].replace('\n', '') or (x.name[:64].replace('\n', '') in line_name)))
                        if len(aml) == 1:
                            aml.old_id = move_line_data.get("id")
                            migrator.create_success_log(values=move_line_data)
                            _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                        else:
                            if not invoice.amount_total:
                                migrator.create_error_log(
                                    msg=f'omitimos esta factura porque tiene importe cero {invoice_id}',
                                    values=move_line_data)
                                continue
                            #Tenemos que diferenciar por cuenta analitica
                            if aml:
                                field_is_not_empty = move_line_data['analytic_account_id']
                                if field_is_not_empty:
                                    analytic_account_id = self.env['account.analytic.account'].search(
                                        [('old_id', '=', move_line_data['analytic_account_id'][0])]).id
                                else:
                                    continue
                                aml = invoice.line_ids.filtered(lambda x: (x.balance == move_line_data.get(
                                    "balance") or x.balance == round(move_line_data.get("balance"), 2)) and x.name[
                                                                                                            :64] == line_name and str(
                                    analytic_account_id) in x.analytic_distribution)
                                if len(aml) == 1:
                                    aml.old_id = move_line_data.get("id")
                                    migrator.create_success_log(values=move_line_data)
                                    _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                                else:
                                    aml = invoice.line_ids.filtered(lambda x: (x.balance == move_line_data.get(
                                        "balance") or x.balance == round(move_line_data.get("balance"), 2)) and x.name[
                                                                                                                :64] == move_line_data.get(
                                        "name") and str(
                                        analytic_account_id) in x.analytic_distribution and not x.old_id)
                                    if aml:
                                        aml = aml[0]
                                        aml.old_id = move_line_data.get("id")
                                        migrator.create_success_log(values=move_line_data)
                                        _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                            else:
                                if move_line_data.get('id') in (151157, 149142, 151156, 149141, 150147, 131242, 101112, 101111, 96796, 96795, 96144, 96143, 93442, 93441, 90185, 90184, 86139, 86138, 78995, 78994, 78194, 78193, 70700, 70699, 149176, 149175):
                                    invoice.no_post_migrator = True
                                elif move_line_data.get('id') not in (92048, 92045):
                                    print('ojo')
                                result = f"No se encontro una la linea {move_line_data.get('id')} para la factura {invoice.name}"
                                migrator.create_error_log(msg=str(result), values=move_line_data)
                                continue
                elif aml and not same_currency:
                    if len(aml) == 1:
                        aml.old_id = move_line_data.get("id")
                        migrator.create_success_log(values=move_line_data)
                        _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                        _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                    else:
                        aml = invoice.line_ids.filtered(lambda x: (abs(x.amount_currency) == abs(amount_currency) or abs(x.amount_currency) == round(abs(amount_currency), 2)) and x.name[:64] == line_name)
                        if not aml:
                            aml = invoice.line_ids.filtered(lambda x: (abs(x.amount_currency) == abs(amount_currency) or abs(x.amount_currency) == round(abs(amount_currency), 2)) and not x.old_id)
                            if len(aml) > 1:
                                aml = invoice.line_ids.filtered(lambda x: (x.amount_currency == amount_currency or x.amount_currency == round(amount_currency, 2)) and not x.old_id)
                        if len(aml) == 1:
                            aml.old_id = move_line_data.get("id")
                            migrator.create_success_log(values=move_line_data)
                            _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                        else:
                            if not invoice.amount_total:
                                migrator.create_error_log(
                                    msg=f'omitimos esta factura porque tiene importe cero {invoice_id}',
                                    values=move_line_data)
                                continue
                            #Tenemos que diferenciar por cuenta analitica
                            if aml:
                                field_is_not_empty = move_line_data['analytic_account_id']
                                if field_is_not_empty:
                                    analytic_account_id = self.env['account.analytic.account'].search(
                                        [('old_id', '=', move_line_data['analytic_account_id'][0])]).id
                                else:
                                    continue

                                aml = invoice.line_ids.filtered(lambda x: (abs(x.amount_currency) == abs(
                                    amount_currency) or abs(x.amount_currency) == round(abs(amount_currency),
                                                                                        2)) and x.name[
                                                                                                :64] == line_name and str(
                                    analytic_account_id) in x.analytic_distribution)
                                if len(aml) == 1:
                                    aml.old_id = move_line_data.get("id")
                                    migrator.create_success_log(values=move_line_data)
                                    _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                                else:
                                    aml = invoice.line_ids.filtered(lambda x: (abs(x.amount_currency) == abs(
                                        amount_currency) or abs(x.amount_currency) == round(abs(amount_currency),
                                                                                            2)) and x.name[
                                                                                                    :64] == line_name and str(
                                        analytic_account_id) in x.analytic_distribution and not x.old_id)
                                    if aml:
                                        aml = aml[0]
                                        aml.old_id = move_line_data.get("id")
                                        migrator.create_success_log(values=move_line_data)
                                        _logger.info(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                            else:
                                self.migration_error_account_moves_ids += invoice
                                invoice.migration_error = True
                                result = f"No se encontro una la linea {move_line_data.get('id')} para la factura {invoice.name}"
                                migrator.create_error_log(msg=str(result), values=move_line_data)
                                continue
                else:
                    if move_line_data.get('id') in (151157, 149142, 151156, 149141, 150147, 131242, 101112, 101111, 96796, 96795, 96144, 96143, 93442, 93441, 90185, 90184, 86139, 86138, 78995, 78994, 78194, 78193, 70700, 70699, 149176, 149175):
                        invoice.no_post_migrator = True
                    elif move_line_data.get('id') not in (92048, 92045):
                        print('ojo')
                    self.migration_error_account_moves_ids += invoice
                    invoice.migration_error = True
                    result = f"No se encontro una la linea {move_line_data.get('id')} para la factura {invoice.name}"
                    migrator.create_error_log(msg=str(result), values=move_line_data)
                    continue

                if aml and len(aml) == 1:
                    if aml.account_id.old_id != old_account_id:
                        account_id = account_obj.search([('old_id', '=', old_account_id)], limit=1)
                        if not account_id:
                            raise UserError('¡¡¡¡Esto no deberia suceder!!!!')
                        aml.account_id = account_id.id
                        _logger.info('cambiamos la cuenta')

            _logger.info(f"se crearon {len(self.account_move_line_ids)} Lineas de asientos")
        return True

    def migrate_account_move_types(self) -> bool:
        return False

    def migrate_account_move_lines(self, move_type: str = "") -> bool:
        """
        Método para migrar los Asientos contables desde el Odoo de origen al Odoo de destino.
        Nota: Esto migra lo que en origen son account.move.lines para poder conciliar.
        """
        self = self.with_context(check_move_validity=False)
        journal_type = "general"
        old_journal_ids = self.journal_ids.filtered(lambda x: x.type == journal_type).mapped("old_id")
        _logger.info("\nMigrando los Asientos contables")
        if move_type == "entry":
            operation_params_list = [
                ("invoice_id", "=", False),
                ("move_id", "!=", False),
                ("company_id", "=", self.company_id.old_id),
                ("currency_id", "in", self.currency_ids.mapped("old_id")),
                ("journal_id", "in", old_journal_ids),
            ]
            ACCOUNT_MOVE_LINE_FIELDS.append("credit")
            ACCOUNT_MOVE_LINE_FIELDS.append("debit")
            ACCOUNT_MOVE_LINE_FIELDS.append("amount_currency")
            ACCOUNT_MOVE_LINE_FIELDS.append("balance")
        else:
            operation_params_list = [
                ("invoice_id", "!=", False),
                ("move_id", "=", False),
                ("company_id", "=", self.company_id.old_id),
                ("currency_id", "in", self.currency_ids.mapped("old_id")),
                ("journal_id", "in", self.journal_ids.mapped("old_id")),
            ]
        _logger.info("\n\n¡¡¡SE ESTA FILTRANDO POR CONTACTOS y DIARIOS!!!\n\n")
        if move_type == "entry":
            entries = self.account_moves_ids.filtered(lambda x: x.state == 'draft' and x.move_type == 'entry' and not x.line_ids or len(x.line_ids) == 1)
            if entries:
                operation_params_list = []
                operation_params_list.append(('move_id', "in", entries.mapped('old_id')))
        model_name: str = "account.move.line"
        aml_obj = self.env[model_name]
        for migrator in self:
            aml_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=operation_params_list,
                command_params_dict={
                    "fields": ACCOUNT_MOVE_LINE_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(aml_datas):
                continue

            total = len(aml_datas)
            for contador, aml_data in enumerate(aml_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                account_entries_old_id = aml_data["id"]
                account_entries_name = aml_data["name"]
                aml_data["move_version"] = "old_move"
                account_entries_id = aml_obj.search([("old_id", "=", account_entries_old_id)], limit=1)

                if bool(account_entries_id):
                    _logger.info(f"la línea de asiento contable {account_entries_name} ya existe")
                    account_entries_id.old_id = account_entries_old_id
                    migrator.account_move_line_ids += account_entries_id
                    continue
                if move_type != "entry":
                    aml_data["move_id"] = aml_data.pop("invoice_id")
                else:
                    aml_data.pop("invoice_id")
                migrator._clean_relational_fields_for(data=aml_data, model_obj=aml_obj)
                if move_type == "entry":
                    if not aml_data.get('amount_currency', 0):
                        aml_data["amount_currency"] = aml_data.pop("balance")
                    if not aml_data.get('currency_id', False):
                        aml_data["currency_id"] = self.env.company.currency_id.id
                is_success, result = migrator.with_context(dont_check_constrains_date_sequence=True).try_to_create_record(odoo_object=aml_obj, value=aml_data)
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=aml_data)
                    continue

                migrator.create_success_log(values=aml_data)
                _logger.info(f"se creó la linea de asiento contable {result.name}")
                migrator.account_move_line_ids += result

            _logger.info(
                f"se crearon {len(self.account_move_line_ids.filtered(lambda move: move.move_version == 'old_move'))} Asientos contables"
            )
        return True

    def migrate_account_payments(self, payment_type: str = "") -> bool:
        """
        Método para migrar los Pagos desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando los Pagos")

        operation_params_list: List[Tuple] = [
            ("journal_id", "in", self.journal_ids.mapped("old_id")),
            ("currency_id", "in", self.currency_ids.mapped("old_id")),
        ]
        if bool(payment_type):
            operation_params_list.append(("partner_type", "=", payment_type))
        payments = self.env["account.payment"].search([("old_id", "!=", False)])
        if payments:
            operation_params_list.append(("id", "not in", payments.mapped("old_id")))
        model_name: str = "account.payment"
        payment_obj = self.env[model_name]
        for migrator in self:
            payment_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=operation_params_list,
                command_params_dict={
                    "fields": [
                        "id",
                        "name",
                        "journal_id",
                        "destination_journal_id",
                        "partner_type",
                        "payment_type",
                        "payment_date",
                        "amount",
                        "currency_id",
                        "state",
                        # "move_line_ids",
                    ],
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(payment_datas):
                continue
            total = len(payment_datas)
            transfer_count = 0

            for contador, payment_data in enumerate(payment_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                payment_old_id = payment_data["id"]
                payment_data["date"] = payment_data.pop("payment_date")
                payment_data["old_state"] = payment_data.pop("state")
                payment_name = payment_data["name"]
                old_move_id = (payment_data.pop("move_line_ids") if "move_line_ids" in payment_data else [])
                # if old_move_id:
                #     payment_data["old_full_reconcile_ids"] = (migrator.get_old_full_reconcile_id_for(old_move_ids=old_move_id, from_payment=True))
                payment_id = payment_obj.search([("old_id", "=", payment_old_id)], limit=1)

                if bool(payment_id):
                    _logger.info(f"el Pago {payment_name} ya existe")
                    payment_id.old_id = payment_old_id
                    migrator.account_payments_ids += payment_id
                    continue

                if payment_data["payment_type"] == "transfer":
                    transfer_count += 1
                    payment_data["is_internal_transfer"] = True
                    payment_data.pop("payment_type")
                    _logger.info(f"el Pago {payment_name}, es una Transferencia")
                migrator._clean_relational_fields_for(data=payment_data, model_obj=payment_obj)
                is_success, result = migrator.try_to_create_record(odoo_object=payment_obj, value=payment_data)
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=payment_data)
                    continue
                else:
                    result.old_name = payment_name
                migrator.create_success_log(values=payment_data)
                _logger.info(f"se creo el Pago {result.name}")
                migrator.account_payments_ids += result

            _logger.info(
                f"se crearon {len(self.account_payments_ids)} Pagos y hubo {transfer_count} Transferencias"
            )
        return True

    def migrate_payments_account_moves_lines(self, payment_type: str = "") -> bool:
        """
        Método para migrar las Lineas de Asientos desde el Odoo de origen al Odoo de destino.
        @agus
        """

        _logger.info("\nMigrando las Lineas de Asientos de los Pagos")

        if not bool(self.account_payments_ids):
            raise UserError("No hay Pagos migrados")

        account_payments_ids = self.account_payments_ids
        if bool(payment_type):
            account_payments_ids = account_payments_ids.filtered(lambda payment: payment.partner_type == payment_type and payment.state != "posted" and not payment.is_internal_transfer)
        model_name: str = "account.move.line"
        model_name_old: str = "account.move.line"
        payment_obj = self.env["account.payment"]
        account_obj = self.env["account.account"]
        currency_obj = self.env["res.currency"]
        for migrator in self:
            move_line_datas = migrator._run_remote_command_for(
                model_name=model_name_old,
                operation_params_list=[
                    ("payment_id", "in", account_payments_ids.mapped("old_id"))
                ],
                command_params_dict={
                    "fields": ACCOUNT_PAYMENT_MOVE_LINE_FIELDS,
                    "offset": migrator.pagination_offset,
                },
            )
            if not bool(move_line_datas):
                continue
            payment_currency_dict = {
                item["move_id"][0]: item["payment_id"][0]
                for item in move_line_datas
                if item["move_id"] and item["payment_id"]
            }
            move_ids = list(payment_currency_dict.keys())
            move_line_datas = migrator._run_remote_command_for(
                model_name=model_name_old,
                operation_params_list=[("move_id", "in", move_ids)],
                command_params_dict={
                    "fields": ACCOUNT_PAYMENT_MOVE_LINE_FIELDS,
                    "offset": migrator.pagination_offset,
                },
            )
            total = len(move_line_datas)
            dic_moves = {}
            for contador, move_line_data in enumerate(move_line_datas, start=1):
                _logger.info(f"vamos {contador} / {total}")
                payment_id = (
                    move_line_data.get("payment_id")[0]
                    if move_line_data.get("payment_id", False)
                    else payment_currency_dict[move_line_data.get("move_id", False)[0]]
                )
                payment = payment_obj.search([("old_id", "=", payment_id)])
                move = payment.move_id
                move.old_name = move_line_data.get("move_id", False)[1]
                company_currency = False
                if move_line_data.get("currency_id", False):
                    currency_id = move_line_data.get("currency_id")[0]
                    currency_line = currency_obj.search([("old_id", "=", currency_id)])
                else:
                    company_currency = True
                    currency_line = payment.company_currency_id
                if not currency_line:
                    result = f"No se migro la moneda {move_line_data('currency_id')[1]} de la linea {move_line_data.get('id')}"
                    migrator.create_error_log(msg=str(result), values=move_line_data)
                    dic_moves[move] = "Error en una linea"
                    continue
                account = move_line_data.get("account_id")

                if not (account or account[0]):
                    result = f"No trajo la cuenta contable para la linea {move_line_data.get('id')}"
                    migrator.create_error_log(msg=str(result), values=move_line_data)
                    dic_moves[move] = "Error en una linea"
                    continue
                #
                old_account_id = account[0]
                account_line = account_obj.search([("old_id", "=", old_account_id)])
                if not account_line:
                    result = f"No se encontro la cuenta contable de id {old_account_id} de la linea {move_line_data.get('id')}"
                    migrator.create_error_log(msg=str(result), values=move_line_data)
                    dic_moves[move] = "Error en una linea"
                    continue
                amount_currency = (
                    (move_line_data.get("balance"))
                    if company_currency
                    else move_line_data.get("amount_currency")
                )
                dic_move_line = {
                    "account_id": account_line.id,
                    "amount_currency": amount_currency,
                    "credit": move_line_data.get("credit"),
                    "currency_id": currency_line.id,
                    "debit": move_line_data.get("debit"),
                    "move_id": move.id,
                    "old_id": move_line_data.get("id"),
                    "partner_id": (
                        payment.partner_id.id if payment.partner_id else False
                    ),
                }
                if move in dic_moves:
                    if dic_moves[move] == "Error en una linea":
                        result = f"Dentro del account.move hay otra linea que fallo por eso no se puede crear la linea {move_line_data.get('id')}"
                        migrator.create_error_log(
                            msg=str(result), values=move_line_data
                        )
                        continue
                    else:
                        dic_moves[move].append((0, 0, dic_move_line))
                else:
                    dic_moves[move] = [(0, 0, dic_move_line)]
            filtered_moves = {
                key: value
                for key, value in dic_moves.items()
                if value != "Error en una linea"
            }
            total_moves = len(filtered_moves)
            for new_contador, move in enumerate(filtered_moves, start=1):
                _logger.info(f"vamos recreando{new_contador} / {total_moves}")
                if move.old_name == 'EXCR/2022/0026':
                    continue
                move.line_ids.unlink()
                try:
                    move.with_context(skip_account_move_synchronization=True).write({"line_ids": filtered_moves[move]})
                    # move.payment_id.action_post()
                except Exception as e:
                    result = f"{e} Este error se encontro al querer agregar las lineas del movimiento de pago {move.name}"
                    migrator.create_error_log(msg=str(result), values=filtered_moves[move])
                    continue
                move.name = move.old_name
                move.payment_id.name = move.payment_id.old_name
        return True

    def migrate_customer_reconcile(self) -> bool:
        """
        Método para migrar las Conciliaciones desde el Odoo de origen al Odoo de destino.
        """
        _logger.info("\nMigrando las Conciliaciones")

        model_name: str = "account.partial.reconcile"
        aml_obj = self.env["account.move.line"]
        odoo_reconciliation_obj = self.env["odoo.migrator.reconciliation"].sudo()
        for migrator in self:
            move_ids = []
            if migrator.account_payments_ids.filtered(lambda x: x.state == "posted"):
                move_ids += migrator.account_payments_ids.move_id.line_ids.filtered(lambda line: line.old_id).mapped(
                    "old_id")
            if migrator.account_moves_ids.filtered(lambda x: x.state == "posted"):
                move_ids += migrator.account_moves_ids.line_ids.filtered(lambda line: line.old_id).mapped("old_id")
            if not move_ids:
                raise UserError("No se migraron asientos para conciliar")
            reconcile_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[
                    ("debit_move_id", "in", move_ids),
                    ("credit_move_id", "in", move_ids),
                ],
                command_params_dict={
                    "fields": [
                        "debit_move_id",
                        "credit_move_id",
                    ],
                    "limit": migrator.pagination_limit,
                },
            )
            values = {}
            to_create = []
            total = len(reconcile_datas)
            commit_count = 500
            side_count = 0
            for contador, reconcile in enumerate(reconcile_datas, start=1):
                side_count += 1
                if side_count > commit_count:
                    _logger.info(
                        f'***\n******\n******\n******\n******\n******\n************\n******\n******\n******\n******\n******\n***')
                    _logger.info(
                        f'***\n******\n******\n******\n******\n******\n***COMMIT***\n******\n******\n******\n******\n******\n***')
                    _logger.info(
                        f'***\n******\n******\n******\n******\n******\n************\n******\n******\n******\n******\n******\n***')
                    self.env.cr.commit()
                    side_count = 0
                _logger.info(f"vamos {contador} / {total}")
                old_id = reconcile.get("id")
                old_debit_move_id = reconcile.get("debit_move_id")[0]
                old_credit_move_id = reconcile.get("credit_move_id")[0]
                debit_move = aml_obj.search([("old_id", "=", old_debit_move_id)])
                credit_move = aml_obj.search([("old_id", "=", old_credit_move_id)])

                values = {
                    'old_id': old_id,
                    'old_debit_move_id': old_debit_move_id,
                    'old_credit_move_id': old_credit_move_id,
                    'debit_move_id': debit_move.id if debit_move else False,
                    'credit_move_id': credit_move.id if credit_move else False,
                    'migrator_id': migrator.id
                }
                to_create.append(values)
                # result = odoo_reconciliation_obj.search([('old_id', '=', old_id)])
                # if not result:
                #     result = odoo_reconciliation_obj.create(values)

                debit_move = aml_obj.search([("old_id", "=", old_debit_move_id), ('reconciled', '=', False)])

                if debit_move.move_id.state == "draft":
                    message = f'El asiento de debito {debit_move.move_id.name} no se encuentra validado (id: --> {debit_move.move_id.id})'
                    migrator.create_error_log(msg=message, values=reconcile)
                credit_move = aml_obj.search([("old_id", "=", old_credit_move_id), ('reconciled', '=', False)])
                if credit_move.move_id.state == "draft":
                    message = f'El asiento de credito {credit_move.move_id.name} no se encuentra validado (id: --> {credit_move.move_id.id})'
                    migrator.create_error_log(msg=message, values=reconcile)
                if not credit_move and not debit_move:
                    migrator.create_error_log(msg=f'No se encontro el asiento de debito {old_debit_move_id} y el asiento de credito {old_credit_move_id}', values=reconcile)
                    continue
                try:
                    (debit_move + credit_move).with_context(skip_account_move_synchronization=True).reconcile()
                except Exception as error:
                    migrator.create_error_log(msg=str(error), values=reconcile)

        return True

    def reconcile_lines(self):

        lines_to_reconcile = self.reconciliation_line_ids.filtered(
            lambda x: x.debit_move_id and x.credit_move_id and not x.successful_reconciliation)
        total = len(lines_to_reconcile)
        commit_count = 500
        side_count = 0
        for contador, line in enumerate(lines_to_reconcile, start=1):
            _logger.info(f'Vamos {contador} / {total}')
            if side_count > commit_count:
                _logger.info(
                    f'***\n******\n******\n******\n******\n******\n************\n******\n******\n******\n******\n******\n***')
                _logger.info(
                    f'***\n******\n******\n******\n******\n******\n***COMMIT***\n******\n******\n******\n******\n******\n***')
                _logger.info(
                    f'***\n******\n******\n******\n******\n******\n************\n******\n******\n******\n******\n******\n***')
                self.env.cr.commit()
                side_count = 0
            try:
                line.reconcile()
                self.create_success_log("Se creo una conciliación para la linea %s" % line.id)
            except Exception as error:
                self.env.cr.commit()
                #pepe
                self.create_error_log(msg=str(error), values=line)

    def _get_migrator_for(self, migrator_type: str):
        migrators = {
            "chart_accounts": self.migrate_chart_of_accounts,
            "account_mapping": self.migrate_account_type_mapping,
            "analytic_accounts": self.migrate_analytic_accounts,
            "users": self.migrate_users,
            "countries": self.migrate_countries,
            "states": self.migrate_states,
            "contacts": self.migrate_contacts,
            "currencies": self.migrate_currencies,
            "currency_rates": self.migrate_currency_rates,
            "taxes": self.migrate_taxes,
            "account_journals": self.migrate_journals,
            "product_categories": self.migrate_product_categories,
            "product_templates": self.migrate_product_template,
            # "products": self.migrate_products,
            #
            # Invoices
            "customer_invoices": partial(self.migrate_account_moves, move_type="out_invoice"),
            "supplier_invoices": partial(self.migrate_account_moves, move_type="in_invoice"),
            #
            # Invoice lines
            "customer_invoice_lines": partial(self.migrate_account_moves_lines, move_type="out_invoice"),
            "customer_moves_lines": partial(self.migrate_invoice_account_moves_lines, move_type="out_invoice"),
            "supplier_invoice_lines": partial(self.migrate_account_moves_lines, move_type="in_invoice"),
            "supplier_moves_lines": partial(self.migrate_invoice_account_moves_lines, move_type="in_invoice"),

            "account_move_types": self.migrate_account_move_types,
            #
            # Account entries
            "account_move": partial(self.migrate_account_moves, move_type="entry"),
            "account_move_lines": partial(self.migrate_account_move_lines, move_type="entry"),
            #
            # Payments
            "customer_payments": partial(self.migrate_account_payments, payment_type="customer"),
            "customer_payment_moves": partial(self.migrate_payments_account_moves_lines, payment_type="customer"),
            "supplier_payments": partial(self.migrate_account_payments, payment_type="supplier"),
            "supplier_payment_moves": partial(self.migrate_payments_account_moves_lines, payment_type="supplier"),
            # "account_payments": self.migrate_account_payments,
            "customer_reconcile": self.migrate_customer_reconcile,

            "post_customer_invoices": partial(self.post_moves, move_type="out_invoice"),
            "post_customer_payments": partial(self.post_moves, payment_type="customer"),
            "post_supplier_invoices": partial(self.post_moves, move_type="in_invoice"),
            "post_supplier_payments": partial(self.post_moves, payment_type="supplier"),
            "post_entries": partial(self.post_moves, move_type="entry"),
        }
        if migrator_type not in migrators:
            raise UserError("No se ha implementado la migración para este modelo")
        return migrators[migrator_type]

    def migrate_data(self):
        selected_company = self.odoo_company_ids.filtered(lambda x: x.migrate_this_company)
        current_company = self.env.company
        migrator_company = self.company_id
        if not (selected_company.old_id == current_company.old_id == migrator_company.old_id):
            raise UserError(f'La compañia seleccionada {selected_company.name} no coincide con la compañia actual {current_company.name} o la compañia del migrador {migrator_company.name}')
        for rec in self:
            migrate_func = rec._get_migrator_for(rec.migration_model)
            migrate_func()
