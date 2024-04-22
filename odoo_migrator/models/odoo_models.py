from odoo import models, fields


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


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_old_id = fields.Integer(string="Invoice Line ID on old DB")
    old_id = fields.Integer(string="ID on old DB")


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
