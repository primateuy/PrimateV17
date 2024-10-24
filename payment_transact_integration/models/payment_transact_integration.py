from odoo import models, fields, api

class AccountMove(models.Model):
    _name = "payment.transact.integration"

    ticket = fields.Integer()
    display_name = fields.Char(string="Pago", compute='_compute_display_name')
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Move', required=True, readonly=True, ondelete='cascade',
        index='btree_not_null',
        check_company=True)


    @api.depends("ticket", "move_id")
    def _compute_display_name(self):
        for record in self:
            # Personaliza cómo se formará el display_name
            record.display_name = f'[T]{record.ticket} - {record.move_id}'
