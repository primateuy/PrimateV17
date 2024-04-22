

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):

        analytic_account_id = self.analytic_account_id or False

        analytic_distribution = False
        if analytic_account_id:
            analytic_distribution = self.env['account.analytic.distribution.model'].search(
                [('auto_account_id', '=', analytic_account_id.auto_account_id.id)]).analytic_distribution or False

        if analytic_distribution:
            for line in self.order_line:
                line.analytic_distribution = analytic_distribution




