from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        self.set_move_lines_analytic_account_unique_id(vals)
        res =  super(AccountMove, self).write(vals)
        return res


    @api.model_create_multi
    def create(self, vals_list):
        self.set_move_lines_analytic_account_unique_id(vals_list)
        res = super(AccountMove, self).create(vals_list)
        return res

    def set_move_lines_analytic_account_unique_id(self, vals):
        if ('state' in vals) and vals['state'] == 'posted':
            for move in self.line_ids:
                move.set_analytic_account_unique_id(True)

    def _action_set_analytic_account_unique_id(self):
        for move in self.line_ids:
            move.set_analytic_account_unique_id(False)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_unique_id = fields.Many2one("account.analytic.account", string="Cuenta analítica única")

    def _action_set_analytic_account_unique_id(self):
        self.set_analytic_account_unique_id(False)

    def set_analytic_account_unique_id(self, posting):

        if not posting and not self.move_id.state == "posted":
            pass
        else:
            if self.analytic_distribution:
                account_ids = list(self.analytic_distribution.keys())
                if len(account_ids) == 1:
                    self.analytic_account_unique_id = int(account_ids[0])
            elif self.analytic_account_unique_id:
                self.analytic_account_unique_id = None
