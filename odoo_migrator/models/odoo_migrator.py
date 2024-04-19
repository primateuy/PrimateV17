# migracion_datos_v13_v15/models/models.py
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
    "move_id": "account.move",
    "journal_id": "account.journal",
    "category_id": "res.partner.category",
    "child_ids": "res.partner",
    "currency_id": "res.currency",
    "company_id": "res.company",
    "account_id": "account.account",
    "product_id": "product.product",
    "tax_ids": "account.tax",
}

m2o_fields: List[str] = [
    "parent_id",
    "state_id",
    "country_id",
    "currency_id",
    "partner_id",
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
    "child_ids" "title",
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
]

ACCOUNT_JOURNAL_FIELDS: List[str] = [
    "name",
    "type",
    "code",
    # "update_posted",
    # "show_on_dashboard",
]
PRODUCT_TEMPLATE_FIELDS: List[str] = [
    "id",
    "name",
    "sale_ok",
    "purchase_ok",
    "can_be_expensed",
    "purchase_method",
]
PRODUCT_FIELDS: List[str] = []
ACCOUNT_MOVE_FIELDS: List[str] = []
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
]
ACCOUNT_INVOICE_MOVE_LINE_FIELDS: List[str] = [
    "account_id",
    "amount_currency",
    "balance",
    "company_id",
    "company_currency_id",
    "currency_id",
    "invoice_id",
    "id",
    "name",
    "payment_id",
    "price_unit",
    "product_id",
    "quantity",
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

    # Puedes agregar más campos según tus necesidades


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
            # Contacts
            ("countries", "Paises"),
            ("states", "Estados"),
            ("contacts", "Contactos"),
            #
            # Currencies
            ("currencies", "Monedas"),
            ("currency_rates", "Tasas de la Monedas"),
            ("chart_of_accounts", "Plan de Cuentas"),
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
            # ("supplier_refunds", "Notas de Credito de Proveedor (cabezales)"),
            # ("supplier_refund_lines", "Notas de Credito de Proveedor (lineas)"),
            #
            # Account entries
            ("account_entries", "Asientos contables"),
            #
            # Entries
            # ("entries", "Apuntes contables (cabezales)"),
            # ("entry_lines", "Apuntes contables (lineas)"),
            #
            # Payments
            ("customer_payments", "Pagos de Clientes"),
            ("customer_payment_moves", "Pagos de Clientes (movimientos)"),
            ("supplier_payments", "Pagos de Proveedores"),
            # Conciliations
            ("customer_reconcile", "Conciliaciones de Clientes"),
            ("supplier_reconcile", "Conciliaciones de Proveedores"),
        ],
        string="Modelo a Migrar",
        required=True,
    )

    pagination_offset = fields.Integer(string="Offset", default=0)
    pagination_limit = fields.Integer(string="Limit", default=500)

    contact_ids = fields.Many2many(comodel_name="res.partner", string="Contactos")
    currency_ids = fields.Many2many(comodel_name="res.currency", string="Monedas")
    currency_rate_ids = fields.Many2many(
        comodel_name="res.currency.rate", string="tasas de Monedas"
    )
    chart_of_accounts_ids = fields.Many2many(
        comodel_name="account.account", string="Plan de Cuentas"
    )

    account_journals_ids = fields.Many2many(
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
    account_move_line_ids = fields.Many2many(
        comodel_name="account.move.line", string="Lineas de Facturas"
    )
    country_ids = fields.Many2many(comodel_name="res.country", string="Países")
    state_ids = fields.Many2many(comodel_name="res.country.state", string="Estados")
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
    contact_count = fields.Integer(
        string="Número de Contactos", compute="_get_contact_count"
    )

    def clear_logs(self):
        self.log_ids.unlink()

    def action_draft(self):
        self.write({"state": "draft"})

    @api.depends("contact_ids")
    def _get_contact_count(self):
        for rec in self:
            rec.contact_count = len(rec.contact_ids)

    def action_view_contacts(self):
        action = self.env.ref("contacts.action_contacts").read()[0]
        action["domain"] = [("id", "in", self.contact_ids.ids)]
        return action

    def connect_with_source(self):
        self.ensure_one()
        source_models, source_uid, source_database, source_password = (
            self._get_source_odoo_connection()
        )
        odoo_migrator_company_obj = self.env["odoo.migrator.company"]
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

        except Exception as error:
            raise UserError(error)

        if len(company_data) > 1:
            self.is_multicompany = True
            self.company_count = len(company_data)
            self.company_data = company_data
            lang_obj = self.env["res.lang"]
            for company in company_data:
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

                for company_field in company:
                    if company_field not in odoo_migrator_company_obj._fields:
                        continue
                    if odoo_migrator_company_obj._fields[
                        company_field
                    ].type == "many2one" and company.get(company_field, False):
                        company = self.with_context(
                            dont_search_for_no_actives=True
                        ).resolve_m2o_fields(
                            value=company,
                            m2o=company_field,
                            odoo_object=odoo_migrator_company_obj,
                            lang=company_lang,
                        )

                    elif odoo_migrator_company_obj._fields[company_field].type in [
                        "many2many",
                        "one2many",
                    ] and company.get(company_field, False):
                        company = self.resolve_m2m_o2m_fields(
                            value=company_data,
                            field_type=odoo_migrator_company_obj._fields[
                                company_field
                            ].type,
                            field=company_field,
                        )
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
                }
                new_company = odoo_migrator_company_obj.create(company_values)

        return self.write({"state": "company_ok"})

    def copy_company_data(self):
        migrator_company = self.odoo_company_ids.filtered(
            lambda x: x.migrate_this_company
        )
        migrator_partner = migrator_company.partner_id
        if not migrator_company:
            raise UserError("No se encontraron compañías a migrar")
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
                print("¡Error de Conexión!")
                return (
                    False,
                    False,
                    f"Error al intentar contectarse con:\n\nDB: {database}\nUser: {username}\nPassword: {password}",
                )
            print("¡Conexión exitosa!")
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
        print(f"vamos a intentar crear el registro {value} de {odoo_object._name}")
        if lang is None:
            lang = self.env.lang
        odoo_object = odoo_object.with_context(lang=lang)
        source_models, source_uid, source_database, source_password = (
            self._get_source_odoo_connection()
        )
        domain = [("name", "ilike", value)]

        if odoo_object._name == "res.partner":
            odoo_object_required_fields = CONTACT_FIELDS
        else:
            odoo_object_required_fields = [
                x.name
                for x in self.env["ir.model"]
                .search([("model", "=", odoo_object._name)])
                .field_id.filtered_domain([("required", "=", True)])
            ]
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

        for value in record_data:
            for field_record in value:
                if odoo_object._fields[field_record].type == "many2one":
                    value = self.resolve_m2o_fields(
                        value=value,
                        odoo_object=odoo_object,
                        m2o=field_record,
                        lang=lang,
                    )
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
        # source_models, source_uid, source_database, source_password = migrator._get_source_odoo_connection()
        record_name = m2ovalue[-1]
        try:
            odoo_object = self.env[field_to_model.get(m2o)].with_context(lang=lang)
        except Exception as error:
            raise UserError(error)
        try:
            record = odoo_object.search(
                [
                    "|",
                    ("name", "ilike", record_name),
                    ("old_id", "=", value[m2o][0]),
                ],
                limit=1,
            )
            if (
                not record
                and odoo_object._fields.get("active", False)
                and not dont_search_for_no_actives
            ):
                record = odoo_object.search(
                    ["|", ("active", "=", False), ("name", "ilike", record_name)],
                    limit=1,
                )
                record.old_id = value[m2o][0]
        except Exception as error:
            raise UserError(error)
        if not record:
            """
            aca lo que podemos hacer es ir contra la tabla 'ir.model' para este odoo_object
            y quedarme con la lista de campos requeridos, hacer la llamada a la api con esos campos
            re-formatear la llamada y hacer el create de los odoo_object
            """
            m2oid = value[m2o][0]
            record = self.create_odoo_record(
                m2oid=m2oid, value=record_name, odoo_object=odoo_object, lang=lang
            )
            record.old_id = value[m2o][0]
        value[m2o] = record.id
        return value

    def resolve_m2m_o2m_fields(
        self, value=None, field_type=None, field=None, lang=None
    ):
        """
        los campos m2m vienen en el formato
        {'field_name': [1,2,3,4]} donde la lista son los ids del registro
        """
        source_models, source_uid, source_database, source_password = (
            self._get_source_odoo_connection()
        )
        if lang is None:
            lang = self.env.lang
        value_ids = []
        m2m_ids = value.get(field, False)
        for m2m_id in m2m_ids:
            odoo_object = self.env[field_to_model.get(field)]
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
                    record_name = record[0]["name"]
                    child_record = odoo_object.search(
                        [("name", "ilike", record_name)], limit=1
                    )
                    if not child_record:
                        child_record = odoo_object.with_context(lang=lang).create(
                            record[0]
                        )
                    value_ids.append(child_record.id)
                except Exception as error:
                    print(error)
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
                    child_record = odoo_object.search(
                        [("name", "ilike", record_name)], limit=1
                    )
                    if not child_record:
                        child_record = odoo_object.with_context(lang=lang).create(
                            record[0]
                        )
                    value_ids.append(child_record.id)
                except Exception as error:
                    print(error)
        if field_type == "one2many":
            value[field] = [(0, 0, value_ids)]
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
            }
        )
        return True

    def create_error_log(self, values=None, msg: str = "") -> bool:
        msg = f"ERROR => Message: {msg}\nValues: {values}"
        print(msg)
        _logger.error(msg)
        self.create_log_line(error=msg, log_type="error", values=values)

    def create_success_log(self, values=None) -> bool:
        msg = f"SUCCESS => Values: {values}"
        print(msg)
        _logger.info(msg)
        self.create_log_line(log_type="success", values=values)

    def try_to_create_record(self, odoo_object=None, value=None, old_odoo_obj=None):
        currency_rate_model = "res.currency.rate"
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
                value["invoice_old_id"] = value.pop("id")
            else:
                value["old_id"] = value.pop("id")
            record = odoo_object.sudo().create(value)
            return True, record
        except Exception as error:
            return False, error

    #################### UTILITY FUNC ####################
    def _remove_m2o_o2m_and_m2m_data_from(self, data, model_obj=None, lang=None):
        if not bool(data) or model_obj is None:
            print(
                "¡Parametros incorrectos, data y model_obj tienen que estar seteados!"
            )
            return
        for field in data:
            if field == "move_id" and model_obj._name == "account.move.line":
                old_id = self.env["account.move"].search(
                    [("old_id", "=", data.get("move_id")[0])], limit=1
                )
                data[field] = old_id.id
                continue

            is_field_empty = bool(data.get(field, False))
            if not is_field_empty:
                continue

            field_type = model_obj._fields[field].type
            if field_type == "many2one" and is_field_empty:
                data = self.resolve_m2o_fields(value=data, m2o=field, lang=lang)
            elif field_type in ["many2many", "one2many"] and is_field_empty:
                data = self.resolve_m2m_o2m_fields(
                    value=data, field_type=field_type, field=field, lang=lang
                )

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
            print(
                "¡Parametros incorrectos, data y model_obj tienen que estar seteados!"
            )
            return
        for field_name in data:
            if not field_name in field_to_model:
                print(f"El field {field_name} no esta en la list {field_to_model}")
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
            new_model_id = self.env[field_model].search(
                [("old_id", "=", old_id)], order="id asc", limit=1
            )
            if not bool(new_model_id):
                raise UserError(
                    f"No se ha encontrado el registro para {field_name} con old_id {old_id}"
                )
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
        print("\nMigrando los Contactos")

        limit = 1000
        model_name: str = "res.partner"
        migrated_ids = []
        contact_obj = self.env[model_name]
        migrated_contacts = contact_obj.search([("old_id", "!=", False)])
        if migrated_contacts:
            migrated_ids = migrated_contacts.mapped("old_id")

        for migrator in self:
            lang = self.company_id.partner_id.lang
            contact_datas = migrator._run_remote_command_for(
                model_name=model_name,
                command_params_dict={
                    "fields": CONTACT_FIELDS,
                    # "limit": limit,
                    "context": {"lang": lang},
                    # "offset": migrator.pagination_offset,
                    # "limit": migrator.pagination_limit,
                },
                operation_params_list=[("id", "not in", migrated_ids)],
            )

            if not bool(contact_datas):
                continue

            total = len(contact_datas)
            for contador, contact_data in enumerate(contact_datas, start=1):
                print(f"vamos {contador} / {total}")
                search_conditions = [("old_id", "=", contact_data["id"])]
                contact_id = contact_obj.search(search_conditions, limit=1)
                if contact_id:
                    print(f'el contacto {contact_data["name"]} ya existe')
                    contact_id.old_id = contact_data["id"]
                    migrator.contact_ids += contact_id
                    continue
                    contact_data = migrator.remove_unused_fields(
                        record_data=contact_data, odoo_model=model_name
                    )
                migrator._remove_m2o_o2m_and_m2m_data_from(
                    data=contact_data, model_obj=contact_obj, lang=lang
                )

                is_success, result = migrator.try_to_create_record(
                    odoo_object=contact_obj, value=contact_data
                )
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=contact_data)
                    continue
                migrator.create_success_log(values=contact_data)
                print(f"se creo el contacto {result.name}")
                migrator.contact_ids += result

            print(f"se crearon {len(self.contact_ids)} contactos")
            self.env.cr.commit()

        return True

    def migrate_countries(self) -> bool:
        """
        Método para migrar paises desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando los paises")
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
                print(f"vamos {contador} / {total}")
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
                    print(f'el país {country_data["name"]} ya existe')
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
                print(f"se creo el contacto {result.name}")
                migrator.country_ids += result
            if countries_without_code:
                message = f'Los siguienes países no tienen código: {[(x["name"], x["id"]) for x in countries_without_code]}'
                migrator.create_error_log(
                    msg=str(message), values=countries_without_code
                )
            print(f"se crearon {len(self.country_ids)} paises")

        return True

    def migrate_states(self) -> bool:
        """
        Método para migrar paises desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando los paises")
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
                print(f"vamos {contador} / {total}")
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
                    print(f'el estado {state_data["name"]} ya existe')
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
                print(f"se creo el contacto {result.name}")
                migrator.state_ids += result
            if states_without_code:
                message = f'Los siguienes estados no tienen código: {[(x["name"], x["id"]) for x in states_without_code]}'
                migrator.create_error_log(msg=str(message), values=states_without_code)
            print(f"se crearon {len(self.state_ids)} estados")

        return True

    def migrate_currencies(self) -> bool:
        """
        Método para migrar monedas desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las Monedas")

        limit = 100
        model_name: str = "res.currency"
        currency_obj = self.env[model_name]
        for migrator in self:
            lang = self.company_id.partner_id.lang

            currencies_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("active", "=", True)],
                command_params_dict={"limit": limit, "context": {"lang": lang}},
            )

            if not bool(currencies_datas):
                continue

            total = len(currencies_datas)
            for contador, currency_data in enumerate(currencies_datas, start=1):
                print(f"vamos {contador} / {total}")
                currency_id = currency_obj.search(
                    [
                        "|",
                        "|",
                        ("old_id", "=", currency_data["id"]),
                        ("name", "ilike", currency_data["name"]),
                        ("active", "=", False),
                    ],
                    limit=1,
                )

                if currency_id:
                    print(f'la moneda {currency_data["name"]} ya existe')
                    if not currency_id.active:
                        currency_id.active = True
                        migrator.env.cr.commit()
                    currency_id.old_id = currency_data["id"]
                    migrator.currency_ids += currency_id
                    continue

                currency_data = migrator.remove_unused_fields(
                    record_data=currency_data, odoo_model=model_name
                )
                migrator._remove_m2o_o2m_and_m2m_data_from(
                    data=currency_data, model_obj=currency_obj, lang=lang
                )

                is_success, result = migrator.try_to_create_record(
                    odoo_object=currency_obj, value=currency_data
                )
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=currency_data)
                    continue
                migrator.create_success_log(values=currency_data)
                print(f"se creo la cotiacion {result.name}")
                migrator.currency_ids += result

            print(f"se crearon {len(self.currency_ids)} monedas")

        return True

    def migrate_currency_rates(self) -> bool:
        """
        Método para migrar tasas monedas desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las tasas de Cambio de las Monedas")

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
                    command_params_dict={
                        "offset": migrator.pagination_offset,
                        "limit": migrator.pagination_limit,
                    },
                )

                if not bool(currency_rate_datas):
                    continue

                total = len(currency_rate_datas)
                for contador, currency_rate_data in enumerate(
                    currency_rate_datas, start=1
                ):
                    print(f"vamos {contador} / {total}")

                    rate_name = currency_rate_data["name"][:10]
                    rate_currency_id = currency.id
                    rate_company_id = migrator.company_id.id

                    ################################################
                    import ipdb

                    ipdb.set_trace()
                    print("IPDB")
                    ################################################

                    rate_id = migrator._find_a_currency_rate_for(
                        rate_name=rate_name,
                        rate_company_id=rate_company_id,
                        rate_currency_id=rate_currency_id,
                    )

                    if bool(rate_id):
                        currency_rate_id = currency_rate_obj.sudo().browse(rate_id)
                        print(f'la cotización {currency_rate_data["name"]} ya existe')
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
                    print(f"se creo la tasa {result.name}")

                    migrator.currency_rate_ids += result

            # Marca la migración de monedas como completa
            print(f"se crearon {len(migrator.currency_rate_ids)} tasas de monedas")
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

    def migrate_chart_of_accounts(self) -> bool:
        """
        Método para actualiza los old_id de los Planes de cuenta desde el Odoo de origen al Odoo de destino.
        """
        print("\nActualizando IDs de Planes de cuenta")

        model_name: str = "account.account"
        chart_of_accounts_obj = self.env[model_name]
        have_local_charts_of_accounts = chart_of_accounts_obj.search([])
        if not bool(have_local_charts_of_accounts):
            print("¡Sin Planes de cuenta que actualizar!")
            return False

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
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(chart_of_accounts_datas):
                continue

            total = len(chart_of_accounts_datas)
            for contador, chart_of_accounts_data in enumerate(
                chart_of_accounts_datas, start=1
            ):
                print(f"vamos {contador} / {total}")
                chart_of_account_code = chart_of_accounts_data["code"]
                chart_of_accounts_id = chart_of_accounts_obj.search(
                    [("code", "=", chart_of_account_code)],
                    limit=1,
                )

                if not bool(chart_of_accounts_id):
                    message = f"¡El Plan de cuentas con Codigo {chart_of_account_code} no existe!"
                    migrator.create_error_log(
                        msg=message, values=chart_of_accounts_data
                    )
                    continue

                chart_of_accounts_id.old_id = chart_of_accounts_data["id"]
                migrator.create_success_log(values=chart_of_accounts_data)
                print(f"se actualizó el Plan de cuentas {chart_of_accounts_id.name}")
                migrator.chart_of_accounts_ids += chart_of_accounts_id

        print(f"se actualizaron {len(self.chart_of_accounts_ids)} Planes de cuentas")
        return True

    def create_account_journal_id(self, values: Dict) -> bool:
        account_journal_obj = self.env["account.journal"].sudo()
        account_journal_id = False
        try:
            account_journal_id = account_journal_obj.create(values)
            account_journal_id.old_id = values["id"]
            print(f"creamos el diario {account_journal_id.name}")
            self.create_success_log(values=values)
        except Exception as error:
            self.create_error_log(msg=str(error), values=values)
        return account_journal_id

    def migrate_account_journals(self) -> bool:
        """
        Método para actualizar los Diarios desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando los Diarios contables")

        model_name: str = "account.journal"
        account_journals_obj = self.env[model_name]
        for migrator in self:
            company = migrator.company_id
            is_company_old_id_set = company.old_id <= 0
            if is_company_old_id_set:
                raise UserError(
                    f"¡La Old_id de la Compañía {company.name} no es correcta!"
                )

            account_journal_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("company_id", "=", company.old_id)],
                command_params_dict={
                    "fields": ACCOUNT_JOURNAL_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(account_journal_datas):
                continue

            total = len(account_journal_datas)
            for contador, account_journal_data in enumerate(
                account_journal_datas, start=1
            ):
                print(f"vamos {contador} / {total}")

                account_journal_code = account_journal_data["code"]
                account_journal_id = account_journals_obj.search(
                    [("code", "=", account_journal_code)]
                )

                if not bool(account_journal_id):
                    message = f"¡El Diario con Codigo {account_journal_code} no existe!"
                    migrator.create_error_log(msg=message, values=account_journal_data)
                    is_success, result = migrator._try_to_create_model(
                        model_name=model_name, values=account_journal_data
                    )
                    if not is_success:
                        migrator.create_error_log(
                            msg=str(result), values=account_journal_data
                        )
                        continue
                    migrator.account_journals_ids += result

                account_journal_id.old_id = account_journal_data["id"]
                migrator.create_success_log(values=account_journal_data)
                print(f"se actualizó el Diario {account_journal_id.name}")
                migrator.account_journals_ids += account_journal_id

        print(f"se actualizaron {len(self.account_journals_ids)} Diarios contables")
        return True

    def migrate_product_categories(self) -> bool:
        """
        Método para migrar las Categorias de producto desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las Categorias de Producto")

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
            for contador, product_category_data in enumerate(
                product_category_datas, start=1
            ):
                print(f"vamos {contador} / {total}")
                category_old_id = product_category_data["id"]
                category_name = product_category_data["name"]
                category_parent = (
                    product_category_data["parent_id"]
                    if "parent_id" in product_category_data
                    else False
                )
                product_category_id = product_category_obj.search(
                    [
                        "|",
                        ("old_id", "=", category_old_id),
                        ("name", "ilike", category_name),
                    ],
                    limit=1,
                )

                if bool(product_category_id):
                    print(f"la Categoria de producto {category_name} ya existe")
                    product_category_id.old_id = category_old_id
                    migrator.product_categories_ids += product_category_id
                    continue

                product_category_data = migrator.remove_unused_fields(
                    record_data=product_category_data, odoo_model=model_name
                )
                migrator._remove_m2o_o2m_and_m2m_data_from(
                    data=product_category_data, model_obj=product_category_obj
                )

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
                print(f"se creo la Categoria {result.name}")
                migrator.product_categories_ids += result

            print(
                f"se crearon {len(self.product_categories_ids)} Categorias de producto"
            )
        return True

    def migrate_product_template(self) -> bool:
        """
        Método para migrar las Plantillas de producto desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las Plantillas de Producto")

        model_name: str = "product.template"
        categ_model_name: str = "product.category"
        categ_field_name: str = "categ_id"

        if not bool(self.product_categories_ids):
            raise UserError("No hay Categorias de productos migradas")

        product_template_obj = self.env[model_name]
        for migrator in self:
            for categ_id in migrator.product_categories_ids:
                print(f"migrando Plantillas para la Categoria {categ_id.display_name}")
                product_template_datas = migrator._run_remote_command_for(
                    model_name=model_name,
                    operation_params_list=[
                        "|",
                        (categ_field_name, "=", categ_id.old_id),
                        "|",
                        ("active", "=", True),
                        ("active", "=", True),
                    ],
                    command_params_dict={
                        "fields": PRODUCT_TEMPLATE_FIELDS,
                        "offset": migrator.pagination_offset,
                        "limit": migrator.pagination_limit,
                    },
                )
                if not bool(product_template_datas):
                    continue

                total = len(product_template_datas)
                for contador, product_template_data in enumerate(
                    product_template_datas, start=1
                ):
                    print(f"vamos {contador} / {total}")
                    template_old_id = product_template_data["id"]
                    template_name = product_template_data["name"]
                    print(template_name)
                    product_template_id = product_template_obj.search(
                        [("old_id", "=", template_old_id)],
                        limit=1,
                    )

                    if bool(product_template_id):
                        print(f"la Plantilla de producto {template_name} ya existe")
                        product_template_id.old_id = template_old_id
                        product_template_id.categ_id = categ_id.id
                        product_template_id.company_id = self.company_id.id
                        migrator.product_templates_ids += product_template_id
                        continue

                    migrator._remove_m2o_o2m_and_m2m_data_from(
                        data=product_template_data, model_obj=product_template_obj
                    )

                    is_success, result = migrator.try_to_create_record(
                        odoo_object=product_template_obj, value=product_template_data
                    )

                    if not is_success:
                        migrator.create_error_log(
                            msg=str(result), values=product_template_data
                        )
                        continue

                    result.categ_id = categ_id.id
                    result.company_id = migrator.company_id.id
                    result.product_variant_id.old_id = result.old_id
                    migrator.create_success_log(values=product_template_data)
                    print(f"se creo la Plantilla {result.name}")
                    migrator.product_templates_ids += result

            print(
                f"se crearon {len(self.product_templates_ids)} Plantillas de producto"
            )
        return True

    def migrate_products(self) -> bool:
        return False

    def get_old_full_reconcile_id_for(
        self, old_move_ids: List[int] = [], from_payment: bool = False
    ) -> List[int]:
        if not bool(old_move_ids):
            print("¡old_move_ids esta vacia!")
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
        result = [
            x.get("full_reconcile_id")[0]
            for x in account_move_line_datas
            if x.get("full_reconcile_id")
        ]

        return result

    def migrate_account_moves(self, move_type: str = "") -> bool:
        """
        Método para migrar las Facturas desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las Facturas")
        journal_type = "sale" if move_type == "out_invoice" else "purchase"
        old_journal_ids = self.account_journals_ids.filtered(
            lambda x: x.type == journal_type
        ).mapped("old_id")
        operation_params_list = [
            ("company_id", "=", self.company_id.old_id),
            ("currency_id", "in", self.currency_ids.mapped("old_id")),
            ("partner_id", "in", self.contact_ids.mapped("old_id")),
            ("journal_id", "in", old_journal_ids),
        ]
        print("\n\n¡¡¡SE ESTA FILTRANDO POR CONTACTOS y DIARIOS!!!\n\n")

        if bool(move_type):
            operation_params_list.append(("type", "=", move_type))

        model_name: str = "account.move"
        model_name_old: str = "account.invoice"
        account_move_obj = self.env[model_name].sudo()
        for migrator in self:
            account_move_datas = migrator._run_remote_command_for(
                model_name=model_name_old,
                operation_params_list=operation_params_list,
                command_params_dict={
                    "fields": [
                        "id",
                        "name",
                        "number",
                        "date_invoice",
                        "journal_id",
                        "currency_id",
                        "type",
                        "company_id",
                        "partner_id",
                        "move_id",
                    ],  # ACCOUNT_MOVE_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                    "order": "date_invoice asc",
                },
            )
            if not bool(account_move_datas):
                continue

            total = len(account_move_datas)
            for contador, account_move_data in enumerate(account_move_datas, start=1):
                print(f"vamos {contador} / {total}")
                move_old_id = account_move_data["id"]
                move_name = account_move_data["name"]
                account_move_id = account_move_obj.search(
                    [("old_id", "=", move_old_id)],
                    limit=1,
                )

                if bool(account_move_id):
                    print(f"la Factura {move_name} ya existe")
                    account_move_id.old_id = move_old_id
                    migrator.account_moves_ids += account_move_id
                    continue

                account_move_data["move_type"] = account_move_data.pop("type")
                account_move_data["invoice_date"] = account_move_data.pop(
                    "date_invoice"
                )
                account_move_data["name"] = account_move_data.pop("number")
                old_move_id = account_move_data["move_id"][0]
                account_move_data.pop("move_id")
                account_move_data["old_full_reconcile_ids"] = (
                    migrator.get_old_full_reconcile_id_for(
                        old_move_ids=[old_move_id], from_payment=False
                    )
                )
                migrator._clean_relational_fields_for(
                    data=account_move_data, model_obj=account_move_obj
                )

                is_success, result = migrator.try_to_create_record(
                    odoo_object=account_move_obj, value=account_move_data
                )
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=account_move_data)
                    continue
                migrator.create_success_log(values=account_move_data)
                print(f"se creo la Factura {result.name}")
                migrator.account_moves_ids += result

            print(f"se crearon {len(self.account_moves_ids)} Facturas")
        return True

    def migrate_account_moves_lines(self, move_type: str = "") -> bool:
        """
        Método para migrar las Lineas de Asientos desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las Lineas de Asientos")

        if not bool(self.account_moves_ids):
            raise UserError("No hay Asientos contables migrados")

        account_moves_ids = self.account_moves_ids
        if bool(move_type):
            account_moves_ids = account_moves_ids.filtered(
                lambda move: move.move_type == move_type
            )

        model_name: str = "account.move.line"
        model_name_old: str = "account.invoice.line"
        move_line_obj = self.env[model_name]
        for migrator in self:
            move_line_datas = migrator._run_remote_command_for(
                model_name=model_name_old,
                operation_params_list=[
                    ("invoice_id", "in", account_moves_ids.mapped("old_id"))
                ],
                command_params_dict={
                    "fields": ACCOUNT_MOVE_LINE_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(move_line_datas):
                continue

            total = len(move_line_datas)
            for contador, move_line_data in enumerate(move_line_datas, start=1):
                print(f"vamos {contador} / {total}")
                old_data = move_line_data
                move_line_data["tax_ids"] = move_line_data.pop("invoice_line_tax_ids")
                move_line_data["move_id"] = move_line_data.pop("invoice_id")
                move_line_old_id = move_line_data["id"]
                move_line_name = move_line_data["name"]
                move_line_id = move_line_obj.search(
                    [("invoice_old_id", "=", move_line_old_id)],
                    limit=1,
                )

                if bool(move_line_id):
                    print(f"la Linea de asiento {move_line_name} ya existe")
                    move_line_id.invoice_old_id = move_line_old_id
                    migrator.account_move_line_ids += move_line_id
                    continue

                migrator._remove_m2o_o2m_and_m2m_data_from(
                    data=move_line_data, model_obj=move_line_obj
                )
                is_success, result = migrator.try_to_create_record(
                    odoo_object=move_line_obj,
                    value=move_line_data,
                    old_odoo_obj=model_name_old,
                )

                if not is_success:
                    migrator.create_error_log(msg=str(result), values=move_line_data)
                    continue

                migrator.create_success_log(values=move_line_data)
                print(f"se creo la Linea de asiento {result.name}")
                migrator.account_move_line_ids += result

            print(f"se crearon {len(self.account_move_line_ids)} Lineas de asientos")
        return True

    def migrate_invoice_account_moves_lines(self, move_type: str = "") -> bool:
        """
        Método para migrar las Lineas de Asientos desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las Lineas de Asientos de las Facturas")

        if not bool(self.account_moves_ids):
            raise UserError("No hay Asientos contables migrados")

        account_moves_ids = self.account_moves_ids
        if bool(move_type):
            account_moves_ids = account_moves_ids.filtered(
                lambda move: move.move_type == move_type
            )

        model_name: str = "account.move.line"
        model_name_old: str = "account.move.line"
        invoice_obj = self.env["account.move"]
        move_line_obj = self.env[model_name]
        for migrator in self:
            move_line_datas = migrator._run_remote_command_for(
                model_name=model_name_old,
                operation_params_list=[
                    ("invoice_id", "in", account_moves_ids.mapped("old_id"))
                ],
                command_params_dict={
                    "fields": ACCOUNT_INVOICE_MOVE_LINE_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(move_line_datas):
                continue

            total = len(move_line_datas)
            for contador, move_line_data in enumerate(move_line_datas, start=1):
                print(f"vamos {contador} / {total}")
                old_data = move_line_data
                invoice_id = move_line_data.pop("invoice_id")[0]
                invoice = invoice_obj.search([("old_id", "=", invoice_id)])
                aml = invoice.line_ids.filtered(
                    lambda x: x.balance == move_line_data.get("balance")
                    or x.balance == round(move_line_data.get("balance"), 2)
                )
                if aml:
                    if len(aml) == 1:
                        aml.old_id = move_line_data.get("id")
                        migrator.create_success_log(values=move_line_data)
                        print(f"Se asigno el old_id a la Linea de asiento {aml.name}")
                    else:
                        result = f"Se encontro mas de una la linea {move_line_data.get('id')} para la factura {invoice.name}"
                        migrator.create_error_log(
                            msg=str(result), values=move_line_data
                        )
                        continue
                else:
                    result = f"No se encontro una la linea {move_line_data.get('id')} para la factura {invoice.name}"
                    migrator.create_error_log(msg=str(result), values=move_line_data)
                    continue
            for invoice in account_moves_ids:
                invoice.action_post()
            print(f"se crearon {len(self.account_move_line_ids)} Lineas de asientos")
        return True

    def migrate_account_move_types(self) -> bool:
        return False

    def migrate_account_entries(self) -> bool:
        """
        Método para migrar los Asientos contables desde el Odoo de origen al Odoo de destino.
        Nota: Esto migra lo que en origen son account.move.lines para poder conciliar.
        """
        print("\nMigrando los Asientos contables")

        operation_params_list = [
            ("invoice_id", "!=", False),
            ("company_id", "=", self.company_id.old_id),
            ("currency_id", "in", self.currency_ids.mapped("old_id")),
            ("journal_id", "in", self.account_journals_ids.mapped("old_id")),
        ]
        print("\n\n¡¡¡SE ESTA FILTRANDO POR CONTACTOS y DIARIOS!!!\n\n")

        model_name: str = "account.move.line"
        account_entries_obj = self.env[model_name]
        for migrator in self:
            account_entries_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=operation_params_list,
                command_params_dict={
                    "fields": ACCOUNT_MOVE_LINE_FIELDS,
                    "offset": migrator.pagination_offset,
                    "limit": migrator.pagination_limit,
                },
            )

            if not bool(account_entries_datas):
                continue

            total = len(account_entries_datas)
            for contador, account_entries_data in enumerate(
                account_entries_datas, start=1
            ):
                print(f"vamos {contador} / {total}")
                account_entries_old_id = account_entries_data["id"]
                account_entries_name = account_entries_data["name"]
                account_entries_data["move_version"] = "old_move"
                account_entries_id = account_entries_obj.search(
                    [("old_id", "=", account_entries_old_id)], limit=1
                )

                if bool(account_entries_id):
                    print(f"el Asiento contable {account_entries_name} ya existe")
                    account_entries_id.old_id = account_entries_old_id
                    migrator.account_move_line_ids += account_entries_id
                    continue

                account_entries_data["move_id"] = account_entries_data.pop("invoice_id")
                migrator._clean_relational_fields_for(
                    data=account_entries_data, model_obj=account_entries_obj
                )
                is_success, result = migrator.try_to_create_record(
                    odoo_object=account_entries_obj, value=account_entries_data
                )

                if not is_success:
                    migrator.create_error_log(
                        msg=str(result), values=account_entries_data
                    )
                    continue

                migrator.create_success_log(values=account_entries_data)
                print(f"se creo el Asiento contable {result.name}")
                migrator.account_move_line_ids += result

            print(
                f"se crearon {len(self.account_move_line_ids.filtered(lambda move:move.move_version=='old_move'))} Asientos contables"
            )
        return True

    def migrate_account_payments(self, payment_type: str = "") -> bool:
        """
        Método para migrar los Pagos desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando los Pagos")

        operation_params_list: List[Tuple] = [
            ("journal_id", "in", self.account_journals_ids.mapped("old_id")),
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
                        "partner_type",
                        "payment_type",
                        "payment_date",
                        "amount",
                        "currency_id",
                        "move_line_ids",
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
                print(f"vamos {contador} / {total}")
                payment_old_id = payment_data["id"]
                payment_data["date"] = payment_data.pop("payment_date")
                payment_name = payment_data["name"]
                old_move_id = (
                    payment_data.pop("move_line_ids")
                    if "move_line_ids" in payment_data
                    else []
                )
                if old_move_id:
                    payment_data["old_full_reconcile_ids"] = (
                        migrator.get_old_full_reconcile_id_for(
                            old_move_ids=old_move_id, from_payment=True
                        )
                    )
                payment_id = payment_obj.search(
                    [("old_id", "=", payment_old_id)], limit=1
                )

                if bool(payment_id):
                    print(f"el Pago {payment_name} ya existe")
                    payment_id.old_id = payment_old_id
                    migrator.account_payments_ids += payment_id
                    continue

                if payment_data["payment_type"] == "transfer":
                    transfer_count += 1
                    payment_data["is_internal_transfer"] = True
                    payment_data.pop("payment_type")
                    print(f"el Pago {payment_name}, es una Transferencia")
                    continue

                migrator._clean_relational_fields_for(
                    data=payment_data, model_obj=payment_obj
                )
                is_success, result = migrator.try_to_create_record(
                    odoo_object=payment_obj, value=payment_data
                )
                if not is_success:
                    migrator.create_error_log(msg=str(result), values=payment_data)
                    continue
                else:
                    result.old_name = payment_name
                migrator.create_success_log(values=payment_data)
                print(f"se creo el Pago {result.name}")
                migrator.account_payments_ids += result

            print(
                f"se crearon {len(self.account_payments_ids)} Pagos y hubo {transfer_count} Transferencias"
            )
        return True

    def migrate_payments_account_moves_lines(self, payment_type: str = "") -> bool:
        """
        Método para migrar las Lineas de Asientos desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las Lineas de Asientos de los Pagos")

        if not bool(self.account_payments_ids):
            raise UserError("No hay Pagos migrados")

        account_payments_ids = self.account_payments_ids
        if bool(payment_type):
            account_payments_ids = account_payments_ids.filtered(
                lambda payment: payment.partner_type == payment_type
                and payment.state != "posted"
            )
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
                print(f"vamos {contador} / {total}")
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
                if not (account or account[1]):
                    result = f"No trajo la cuenta contable para la linea {move_line_data.get('id')}"
                    migrator.create_error_log(msg=str(result), values=move_line_data)
                    dic_moves[move] = "Error en una linea"
                    continue
                account_code = account[1].split(" ")[0]
                account_line = account_obj.search([("code", "=", account_code)])
                if not account_line:
                    result = f"No se encontro la cuenta contable de codigo {account_code} de la linea {move_line_data.get('id')}"
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
            for move in filtered_moves:
                move.line_ids.unlink()
                try:
                    move.with_context(skip_account_move_synchronization=True).write(
                        {"line_ids": filtered_moves[move]}
                    )
                    move.payment_id.action_post()
                except Exception as e:
                    result = f"{e} Este error se encontro al querer agregar las lineas del movimiento de pago {move.name}"
                    migrator.create_error_log(
                        msg=str(result), values=filtered_moves[move]
                    )
                    continue
                move.name = move.old_name
                move.payment_id.name = move.payment_id.old_name
        return True

    def migrate_customer_reconcile(self) -> bool:
        """
        Método para migrar las Conciliaciones desde el Odoo de origen al Odoo de destino.
        """
        print("\nMigrando las Conciliaciones")

        model_name: str = "account.partial.reconcile"
        aml_obj = self.env["account.move.line"]
        for migrator in self:
            move_ids = []
            if migrator.account_payments_ids:
                move_ids += migrator.account_payments_ids.move_id.line_ids.filtered(
                    lambda line: line.old_id
                ).mapped("old_id")
            if migrator.account_moves_ids:
                move_ids += migrator.account_moves_ids.line_ids.filtered(
                    lambda line: line.old_id
                ).mapped("old_id")
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
            for reconcile in reconcile_datas:
                debit_move = aml_obj.search(
                    [("old_id", "=", reconcile.get("debit_move_id")[0])]
                )
                credit_move = aml_obj.search(
                    [("old_id", "=", reconcile.get("credit_move_id")[0])]
                )
                (debit_move + credit_move).with_context(
                    skip_account_move_synchronization=True
                ).reconcile()
        return True

    def _get_migrator_for(self, migrator_type: str):
        migrators = {
            "countries": self.migrate_countries,
            "states": self.migrate_states,
            "contacts": self.migrate_contacts,
            "currencies": self.migrate_currencies,
            "currency_rates": self.migrate_currency_rates,
            "chart_of_accounts": self.migrate_chart_of_accounts,
            "account_journals": self.migrate_account_journals,
            "product_categories": self.migrate_product_categories,
            "product_templates": self.migrate_product_template,
            # "products": self.migrate_products,
            #
            # Invoices
            "customer_invoices": partial(
                self.migrate_account_moves, move_type="out_invoice"
            ),
            "supplier_invoices": partial(
                self.migrate_account_moves, move_type="in_invoice"
            ),
            #
            # Invoice lines
            "customer_invoice_lines": partial(
                self.migrate_account_moves_lines, move_type="out_invoice"
            ),
            "customer_moves_lines": partial(
                self.migrate_invoice_account_moves_lines, move_type="out_invoice"
            ),
            "supplier_invoice_lines": partial(
                self.migrate_account_moves_lines, move_type="in_invoice"
            ),
            "account_move_types": self.migrate_account_move_types,
            #
            # Account entries
            "account_entries": self.migrate_account_entries,
            #
            # Payments
            "customer_payments": partial(
                self.migrate_account_payments, payment_type="customer"
            ),
            "customer_payment_moves": partial(
                self.migrate_payments_account_moves_lines, payment_type="customer"
            ),
            "supplier_payments": partial(
                self.migrate_account_payments, payment_type="supplier"
            ),
            # "account_payments": self.migrate_account_payments,
            "customer_reconcile": self.migrate_customer_reconcile,
        }
        if migrator_type not in migrators:
            raise UserError("No se ha implementado la migración para este modelo")
        return migrators[migrator_type]

    def migrate_data(self):
        for rec in self:
            migrate_func = rec._get_migrator_for(rec.migration_model)
            migrate_func()
