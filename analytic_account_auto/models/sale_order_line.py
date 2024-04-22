from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()

        analytic_account_id = self.order_id.analytic_account_id or False
        if analytic_account_id:

            analytic_distribution_model = self.env['account.analytic.distribution.model'].search([('auto_account_id', '=', analytic_account_id.auto_account_id.id)])
            if analytic_distribution_model:
                if analytic_distribution_model:
                    self.analytic_distribution = analytic_distribution_model.analytic_distribution

        return res
