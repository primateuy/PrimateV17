from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    transact_ticket = fields.Integer()
    transact_id = fields.Many2one(
        comodel_name='payment.transact.integration',
        string="Transact",
        index='btree_not_null',
        copy=False,
        check_company=True,
    )
