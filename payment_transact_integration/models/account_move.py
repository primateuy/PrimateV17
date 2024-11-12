from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    transact_ticket = fields.Integer()
    transact_id = fields.Many2one(
        comodel_name='transact.transaction',
        string="Transact Transaction",
        index='btree_not_null',
        copy=False,
        check_company=True,
    )
