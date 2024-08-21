from odoo import models, fields, api

class Company(models.Model):
    _inherit = "res.company"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ResCountry(models.Model):
    _inherit = "res.country"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ResPartner(models.Model):
    _inherit = "res.partner"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ResPartnerTitle(models.Model):
    _inherit = "res.partner.title"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ResUsers(models.Model):
    _inherit = "res.users"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ResCurrency(models.Model):
    _inherit = "res.currency"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class AccountAccount(models.Model):
    _inherit = "account.account"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ProductCategory(models.Model):
    _inherit = "product.category"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class ProductProduct(models.Model):
    _inherit = "product.product"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class AccountMove(models.Model):
    _inherit = "account.move"

    old_id = fields.Integer(string="ID on old DB", copy=False)
    old_name = fields.Char(string="Name")
    old_full_reconcile_ids = fields.Char(string="Full reconcile IDs on old DB")
    old_state = fields.Selection(selection=[("draft", "Draft"), ("open", "Posted"), ("cancel", "Cancelled"), ("paid", "Pago"), ("posted", "Publicado"), ("reconciled", "Reconcilado")])
    migration_error = fields.Boolean(string="Migration Error")
    no_post_migrator = fields.Boolean(string="No post move in migration")

    def _must_check_constrains_date_sequence(self):
        ctx = self.env.context.copy()
        if ctx.get('dont_check_constrains_date_sequence', False):
            return False
        return super()._must_check_constrains_date_sequence()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_old_id = fields.Integer(string="Invoice Line ID on old DB", copy=False)
    old_id = fields.Integer(string="ID on old DB", copy=False)
    move_version = fields.Selection(selection=[("old_move", "Old Move"), ("new_move", "New Move")], default="old_move")

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        if self._context.get('check_move_validity', True):
            super(AccountMoveLine, self)._check_payable_receivable()

    def _check_constrains_account_id_journal_id(self):
        if not self._context.get('from_migrator', False):
            super(AccountMoveLine, self)._check_constrains_account_id_journal_id()


class AccountPayment(models.Model):
    _inherit = "account.payment"

    old_id = fields.Integer(string="ID on old DB", copy=False)
    old_name = fields.Char(string="Name")
    old_full_reconcile_ids = fields.Char(string="Full reconcile IDs on old DB")


class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    old_id = fields.Integer(string="ID on old DB", copy=False)


class AccountTax(models.Model):
    _inherit = "account.tax"

    old_id = fields.Integer(string="ID on old DB", copy=False)


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    old_id = fields.Integer(string="ID on old DB", copy=False)
