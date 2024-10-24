
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_analytic_distribution_add_lines_blocked = fields.Boolean(
        string="Bloquear agregado de líneas en distribución analítica",
        related="company_id.is_analytic_distribution_add_lines_blocked",
        readonly=False,
    )
