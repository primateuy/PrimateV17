# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Currency(models.Model):
    _inherit = "res.currency"
    _description = "Currency"

    @api.depends("rate_ids.rate")
    @api.depends_context("to_currency", "date", "company", "company_id")
    def _compute_current_rate(self):
        date = self._context.get("date") or fields.Date.context_today(self)
        company = (
            self.env["res.company"].browse(self._context.get("company_id"))
            or self.env.company
        )
        company = company.root_id
        to_currency = (
            self.browse(self.env.context.get("to_currency")) or company.currency_id
        )
        # the subquery selects the last rate before 'date' for the given currency/company
        currency_rates = (self + to_currency)._get_rates(self.env.company, date)
        for currency in self:
            currency.rate = currency_rates.get(to_currency.id) / currency_rates.get(
                currency._origin.id
            )
            currency.inverse_rate = 1 / currency.rate
            if currency != company.currency_id:
                currency.rate_string = "1 %s = %.6f %s" % (
                    to_currency.name,
                    currency.rate,
                    currency.name,
                )
            else:
                currency.rate_string = ""
