from odoo import fields, models, api


class AnalyticAccountAuto(models.Model):
    _name = 'analytic.account.auto'
    _description = 'Analytic Account Auto'

    analytic_account_id = fields.One2many('account.analytic.account', 'auto_account_id', string="Cuenta Analítica")
    distribution_model_id = fields.One2many('account.analytic.distribution.model', 'auto_account_id',
                                            string="Modelo de distribución")

    display_name = fields.Char(string='Nombre', compute='_compute_display_name')
    name = fields.Char(string='Nombre', compute='_compute_name')

    # @api.depends('analytic_account_id')
    # def _compute_display_name(self):
    #     for record in self:
    #         account_analytic_account = self.env['account.analytic.account'].search([('auto_account_id', '=', record.id)])
    #         record.display_name = account_analytic_account.name

    def _compute_name(self):
        for record in self:
            account_analytic_account = self.env['account.analytic.account'].search(
                [('auto_account_id', '=', record.id)])
            if account_analytic_account:
                if account_analytic_account.name:
                    record.name = f'[Map] {account_analytic_account.name}'
                else:
                    record.name = '[Map] Sin nombre'
            else:
                record.name = '[Map] Sin cuenta analítica'