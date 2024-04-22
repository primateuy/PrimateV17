from odoo import api, fields, models, _

class AccountAnalyticDistributionModel(models.Model):
    _inherit = 'account.analytic.distribution.model'

    # analytic_auto_id = fields.Many2one(
    #     'analytic.account.auto',
    #     string='Mapeo con Cuenta',
    # )

    auto_account_id = fields.Many2one('analytic.account.auto', string="Mapeo con cuenta analítica", deferred=True)



