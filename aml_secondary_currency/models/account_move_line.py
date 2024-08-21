# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    # Activate the currency update
    secondary_currency_id = fields.Many2one(comodel_name='res.currency', string='Divisa secundaria')


class AccountMove(models.Model):
    _inherit = 'account.move'

    secondary_currency_id = fields.Many2one(comodel_name='res.currency', string='Divisa secundaria', compute='_compute_data_secondary_currency')

    def _compute_data_secondary_currency(self):
        for rec in self.sudo():
            rec.secondary_currency_id = rec.company_id.secondary_currency_id
            try:
                for tax_info in rec.tax_totals['groups_by_subtotal']['Untaxed Amount']:
                    tax_info['tax_group_base_amount_secondary'] = rec.currency_id._convert(tax_info['tax_group_base_amount'], rec.company_id.secondary_currency_id, rec.company_id, rec.invoice_date or datetime.date.today())
                    tax_info['tax_group_amount_secondary'] = rec.currency_id._convert(tax_info['tax_group_amount'], rec.company_id.secondary_currency_id, rec.company_id, rec.invoice_date or datetime.date.today())
                rec.tax_totals['amount_secondary_currency'] = rec.currency_id._convert(rec.amount_total, rec.company_id.secondary_currency_id, rec.company_id, rec.invoice_date or datetime.date.today())
                rec.tax_totals['rate_used'] = rec.currency_id._convert(1, rec.company_id.secondary_currency_id, rec.company_id, rec.invoice_date or datetime.date.today())
            except Exception as e:
                print(f"Error al calcular importes en moneda secundaria: {e}")

    def post(self):
        res = super(AccountMove, self).post()
        self.line_ids.compute_amount_secondary()
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    secondary_currency_id = fields.Many2one(comodel_name='res.currency', string='Divisa secundaria',
                                            related='company_id.secondary_currency_id')
    tipo_cambio = fields.Float(string='TC')
    amount_secondary = fields.Monetary(string='Importe Divisa Secundaria', currency_field='secondary_currency_id')

    def compute_amount_secondary(self):
        for rec in self:
            tipo_cambio = self.env['res.currency.rate'].search([('name', '<=', rec.move_id.date), ('currency_id', '=', self.env.companies.secondary_currency_id.id)],limit=1)
            if tipo_cambio:
                debit_credit = rec.debit or (rec.credit * -1)
                rec.amount_secondary = debit_credit * tipo_cambio.rate
                rec.tipo_cambio = tipo_cambio.inverse_company_rate
            else:
                rec.amount_secondary = 0



