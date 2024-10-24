from odoo import models, fields, api

class AccountAnalyticDistributionModel(models.Model):
    _inherit = 'account.analytic.plan'

    can_add_analytic_distibution_lines = fields.Char(compute="_compute_can_add_analytic_distibution_lines", store=False, default='False')

    # can_add_analytic_distibution_lines = fields.Boolean(related='user_id.can_add_analytic_distibution_lines',
    #                                                     string="Can Add Analytic Distribution Lines", store=False)

    @api.depends('name')
    def _compute_can_add_analytic_distibution_lines(self):
        edita = self._has_analytic_distribution_no_add_lines_group()
        bloquea = self._is_analytic_distribution_add_lines_blocked()
        if bloquea and not edita:
            self.can_add_analytic_distibution_lines = 'False'
        else:
            self.can_add_analytic_distibution_lines = 'True'

    def _has_analytic_distribution_no_add_lines_group(self):
        self.ensure_one()
        return self.env.user.has_group('analytic_distribution_no_add_lines.analytic_distribution_no_add_lines_group')

    def _is_analytic_distribution_add_lines_blocked(self):
        self.ensure_one()
        return self.company_id.is_analytic_distribution_add_lines_blocked