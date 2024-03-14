from odoo import fields, models, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_auto_account_id = fields.Many2one('analytic.account.auto', string="Mapeo con Cuenta Analítica")

    @api.onchange('analytic_auto_account_id')
    def _onchange_analytic_auto_account_id(self):
        self = self.sudo()
        analytic_auto_account_id = self.analytic_auto_account_id.id
        self.analytic_distribution = self._get_analytic_distribution(analytic_auto_account_id)

    @api.model
    def create(self, vals):
        self = self.sudo()
        if 'analytic_auto_account_id' in vals and 'analytic_line_ids' is not False:
            analytic_auto_account_id = vals.get('analytic_auto_account_id')
            analytic_auto_account = self._get_analytic_auto_account(analytic_auto_account_id)
            if analytic_auto_account:
                vals['analytic_distribution'] = analytic_auto_account.distribution_model_id.analytic_distribution

        res = super(AccountMoveLine, self).create(vals)
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
