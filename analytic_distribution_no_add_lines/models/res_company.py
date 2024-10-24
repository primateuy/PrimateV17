
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_analytic_distribution_add_lines_blocked = fields.Boolean(string="Require Time Type on Timesheets")
