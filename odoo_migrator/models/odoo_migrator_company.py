# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging
import warnings

from odoo import api, fields, models, tools, _, Command, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from odoo.tools import html2plaintext, file_open, ormcache

_logger = logging.getLogger(__name__)



class OdooMigratorCompany(models.Model):
    _name = "odoo.migrator.company"
    _description = "Odoo Migrator Companies"

    name = fields.Char(string="Company Name", required=True, store=True, readonly=False)
    logo = fields.Binary(string="Company Logo", readonly=False)
    logo_web = fields.Binary(string="Web Logo")
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    zip = fields.Char(string="Zip")
    city = fields.Char(string="City")
    state_id = fields.Many2one(comodel_name="res.country.state", string="Fed. State")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    website = fields.Char(string="Website")
    vat = fields.Char(string="VAT")
    paperformat_id = fields.Many2one(
        comodel_name="report.paperformat", string="Paper format"
    )
    lang = fields.Selection(string="Language", related="partner_id.lang")
    migrator_id = fields.Many2one(comodel_name="odoo.migrator", string="Migrator")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Related Partner")
    migrate_this_company = fields.Boolean(string="Migrate this company", default=False)
    old_id = fields.Integer(string="Old ID", readonly=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The company name must be unique!")
    ]
