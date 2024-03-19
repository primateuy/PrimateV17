# -*- coding: utf-8 -*-
# from odoo import http


# class OdooMigrator(http.Controller):
#     @http.route('/odoo_migrator/odoo_migrator', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_migrator/odoo_migrator/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_migrator.listing', {
#             'root': '/odoo_migrator/odoo_migrator',
#             'objects': http.request.env['odoo_migrator.odoo_migrator'].search([]),
#         })

#     @http.route('/odoo_migrator/odoo_migrator/objects/<model("odoo_migrator.odoo_migrator"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_migrator.object', {
#             'object': obj
#         })
