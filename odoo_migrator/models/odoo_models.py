from odoo import models, fields, api
from typing import Any, Dict, List, Tuple

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


class Company(models.Model):
    _inherit = "res.company"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResCountry(models.Model):
    _inherit = "res.country"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResPartner(models.Model):
    _inherit = "res.partner"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResPartnerTitle(models.Model):
    _inherit = "res.partner.title"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResUsers(models.Model):
    _inherit = "res.users"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResCurrency(models.Model):
    _inherit = "res.currency"

    old_id = fields.Integer(string="Old ID", copy=False)


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountAccount(models.Model):
    _inherit = "account.account"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    old_id = fields.Integer(string="Old ID", copy=False)


class ProductCategory(models.Model):
    _inherit = "product.category"

    old_id = fields.Integer(string="Old ID", copy=False)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    old_id = fields.Integer(string="Old ID", copy=False)


class ProductProduct(models.Model):
    _inherit = "product.product"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountMove(models.Model):
    _inherit = "account.move"

    old_id = fields.Integer(string="Old ID", copy=False)
    old_move_id = fields.Integer(string="Old move ID", copy=False)
    old_name = fields.Char(string="Name", copy=False)
    old_full_reconcile_ids = fields.Char(string="Full reconcile IDs on old DB", copy=False)
    old_state = fields.Selection(selection=[("draft", "Draft"), ("open", "Posted"), ("cancel", "Cancelled"), ("paid", "Pago"), ("posted", "Publicado"), ("reconciled", "Reconcilado")], copy=False)
    migration_error = fields.Boolean(string="Migration Error", copy=False)
    no_post_migrator = fields.Boolean(string="No post move in migration", copy=False)

    def _must_check_constrains_date_sequence(self):
        ctx = self.env.context.copy()
        if ctx.get('dont_check_constrains_date_sequence', False):
            return False
        return super()._must_check_constrains_date_sequence()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_old_id = fields.Integer(string="Invoice Line Old ID", copy=False)
    old_id = fields.Integer(string="Old ID", copy=False)
    move_version = fields.Selection(selection=[("old_move", "Old Move"), ("new_move", "New Move")], default="old_move", copy=False)

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        if self._context.get('check_move_validity', True):
            super(AccountMoveLine, self)._check_payable_receivable()

    def _check_constrains_account_id_journal_id(self):
        if not self._context.get('from_migrator', False):
            super(AccountMoveLine, self)._check_constrains_account_id_journal_id()


class AccountPayment(models.Model):
    _inherit = "account.payment"

    old_id = fields.Integer(string="Old ID", copy=False)
    old_name = fields.Char(string="Name", copy=False)
    old_full_reconcile_ids = fields.Char(string="Full reconcile IDs on old DB", copy=False)



    def action_post(self):
        ctx = self.env.context.copy()
        comes_from_migrator = ctx.get('from_migrator', False)

        if comes_from_migrator:
            """
            aca hacemos la magia
            """
            self.ensure_one()
            model_name = "account.move.line"
            migrator = ctx.get('migrator')
            move_line_datas = migrator._run_remote_command_for(
                model_name=model_name,
                operation_params_list=[("payment_id", "=", self.old_id)],
                command_params_dict={
                    "fields": ACCOUNT_PAYMENT_MOVE_LINE_FIELDS,
                },
            )
        else:
            return super(AccountMove, self).action_post()



class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountTax(models.Model):
    _inherit = "account.tax"

    old_id = fields.Integer(string="Old ID", copy=False)


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    old_id = fields.Integer(string="Old ID", copy=False)

class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    old_id = fields.Integer(string="Old ID", copy=False)
