from odoo import models, fields, api


class Company(models.Model):
    _inherit = "res.company"

    old_id = fields.Integer(string="ID on old DB")


class ResCountry(models.Model):
    _inherit = "res.country"

    old_id = fields.Integer(string="ID on old DB")


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    old_id = fields.Integer(string="ID on old DB")


class ResPartner(models.Model):
    _inherit = "res.partner"

    old_id = fields.Integer(string="ID on old DB")

class ResPartnerTitle(models.Model):
    _inherit = "res.partner.title"

    old_id = fields.Integer(string="ID on old DB")


class ResUsers(models.Model):
    _inherit = "res.users"

    old_id = fields.Integer(string="ID on old DB")


class ResCurrency(models.Model):
    _inherit = "res.currency"

    old_id = fields.Integer(string="ID on old DB")


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    old_id = fields.Integer(string="ID on old DB")


class AccountAccount(models.Model):
    _inherit = "account.account"

    old_id = fields.Integer(string="ID on old DB")


class AccountJournal(models.Model):
    _inherit = "account.journal"

    old_id = fields.Integer(string="ID on old DB")


class ProductCategory(models.Model):
    _inherit = "product.category"

    old_id = fields.Integer(string="ID on old DB")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    old_id = fields.Integer(string="ID on old DB")


class ProductProduct(models.Model):
    _inherit = "product.product"

    old_id = fields.Integer(string="ID on old DB")


class AccountMove(models.Model):
    _inherit = "account.move"

    old_id = fields.Integer(string="ID on old DB")
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

    invoice_old_id = fields.Integer(string="Invoice Line ID on old DB")
    old_id = fields.Integer(string="ID on old DB")
    move_version = fields.Selection(selection=[("old_move", "Old Move"), ("new_move", "New Move")], default="old_move")

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        if self._context.get('check_move_validity', True):
            super(AccountMoveLine, self)._check_payable_receivable()


class AccountPayment(models.Model):
    _inherit = "account.payment"

    old_id = fields.Integer(string="ID on old DB")
    old_name = fields.Char(string="Name")
    old_full_reconcile_ids = fields.Char(string="Full reconcile IDs on old DB")


class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"

    old_id = fields.Integer(string="ID on old DB")


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    old_id = fields.Integer(string="ID on old DB")

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    old_id = fields.Integer(string="ID on old DB")

class AccountTax(models.Model):
    _inherit = "account.tax"

    old_id = fields.Integer(string="ID on old DB")

class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    old_id = fields.Integer(string="ID on old DB")
