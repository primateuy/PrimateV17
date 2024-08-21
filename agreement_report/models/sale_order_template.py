from odoo import fields, models, api


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    agreement_terms = fields.Html()
