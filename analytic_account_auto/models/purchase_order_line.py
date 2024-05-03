
from odoo import api, fields, models, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    analytic_auto_account_id = fields.Many2one('analytic.account.auto', string="Mapeo con Cuenta Analítica")
    plan_id = fields.Many2one('account.analytic.plan', string="Plan analítico", compute="_compute_plan_id")

    @api.onchange('analytic_auto_account_id')
    def _onchange_analytic_auto_account_id(self):
        analytic_auto_account_id = self.analytic_auto_account_id.id
        self.analytic_distribution = self._get_analytic_distribution(analytic_auto_account_id)
        self._compute_plan_id()

    @api.model
    def create(self, vals):
        if 'analytic_auto_account_id' in vals and 'analytic_line_ids' is not False:
            analytic_auto_account_id = vals.get('analytic_auto_account_id')
            analytic_auto_account = self._get_analytic_auto_account(analytic_auto_account_id)
            if analytic_auto_account:
                vals['analytic_distribution'] = analytic_auto_account.distribution_model_id.analytic_distribution

        res = super(PurchaseOrderLine, self).create(vals)
        return res

    def _get_analytic_distribution(self, analytic_auto_account_id=False):
        if analytic_auto_account_id:
            analytic_auto_account = self._get_analytic_auto_account(analytic_auto_account_id)
            return analytic_auto_account.distribution_model_id.analytic_distribution
        return False

    def _get_analytic_auto_account(self, analytic_auto_account_id=False):
        if analytic_auto_account_id:
            analytic_auto_account = self.env['analytic.account.auto'].browse(analytic_auto_account_id)
            return analytic_auto_account
        return False

    def _compute_plan_id(self):
        for record in self:
            if record.analytic_auto_account_id:
                record.plan_id = record.analytic_auto_account_id.analytic_account_id.plan_id
            else:
                record.plan_id = False

