from odoo import api, fields, models, _


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    note = fields.Html(string="Terms and conditions", store=True, readonly=False)