from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    create_distribution = fields.Boolean(string="Crear distribución", default=True)
    auto_account_id = fields.Many2one('analytic.account.auto', string="Analytic Account Auto")

    @api.depends('name')
    def _compute_can_edit(self):
        can_edit = self.env.user.has_group('analytic_account_auto.analytic_account_auto_group')
        for record in self:
            record.can_edit = can_edit

    can_edit = fields.Boolean(compute=_compute_can_edit)

    def create(self, vals_list):
        account_analytic_account = super(AccountAnalyticAccount, self).create(vals_list)
        if account_analytic_account and account_analytic_account.create_distribution:
            # TODO: Acá tengo que estblecer los valores con los que voy a crear estos registros.
            # El registro que va en la tabla nuestra
            analytic_account_auto = self.env['analytic.account.auto'].create({})

            account_analytic_account.write({'auto_account_id': analytic_account_auto.id})

            # El registro que va en la tabla de modelos de distribución.
            analytic_distribution_model = self.env['account.analytic.distribution.model']

            # Crea un nuevo registro en el modelo 'account.analytic.distribution.model'
            new_record = analytic_distribution_model.create({
                'auto_account_id': analytic_account_auto.id,
                'partner_id': account_analytic_account.partner_id.id,
                'analytic_distribution': {str(account_analytic_account.id): 100},
            })

        return account_analytic_account
