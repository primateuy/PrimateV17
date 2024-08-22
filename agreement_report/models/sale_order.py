from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    family_members = fields.Integer()
    tax_totals_only_project = fields.Binary(compute='_compute_tax_totals_only_project', exportable=False)


    def _compute_tax_totals_only_project(self):
        self.tax_totals_only_project = False

        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type and x.product_id.service_tracking != 'no')

            if not order_lines:
                order_lines = order.order_line.filtered(lambda x: not x.display_type)
            order.tax_totals_only_project = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )


    # @api.depends_context('lang')
    # @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id')
    # def _compute_tax_totals(self):
    #     res = super(SaleOrder, self)._compute_tax_totals()
    #
    #     for order in self:
    #         order_lines = order.order_line.filtered(lambda x: not x.display_type and x.product_id.service_tracking != 'no')
    #         order.tax_totals_only_project = self.env['account.tax']._prepare_tax_totals(
    #             [x._convert_to_tax_base_line_dict() for x in order_lines],
    #             order.currency_id or order.company_id.currency_id,
    #         )
    #
    #     print(self.tax_totals)
    #     print("------------------------")
    #     print("------------------------")
    #     print(self.tax_totals)
    #     print(self.tax_totals_only_project)
    #
    #     return res
