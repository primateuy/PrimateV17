

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):

        analytic_account_id = self.analytic_account_id or False

        # Se busca un modelo de distribución asociado a la cuenta analítica seleccionada
        analytic_distribution = False
        if analytic_account_id:
            analytic_distribution = self.env['account.analytic.distribution.model'].search(
                [('auto_account_id', '=', analytic_account_id.auto_account_id.id)]).analytic_distribution or False

        # Si se encuentra un modelo de distribución asociado a la cuenta analítica, se asigna a las líneas de la orden
        if analytic_distribution:
            for line in self.order_line:
                line.analytic_distribution = analytic_distribution

            # Se busca un plan asociado a la cuenta analítica seleccionada para tomar sus términos y condiciones
            if analytic_account_id.plan_id:
                # Computo de terminos y condiciones nativo de odoo para la orden de venta (es como resetear los terminos y condiciones para evitar acumulaciones)
                self._compute_note()

                plan_note = analytic_account_id.plan_id.note
                self.note += plan_note


    def _recursive_get_notes(self, plan_id):
        note = ''
        for subplan in plan_id.children_ids:
            note += f'{subplan.name}: {subplan.note} <br>'
            note += self._recursive_get_notes(subplan)

        if note == '':
            note = plan_id.note
        return note



