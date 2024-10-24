from odoo import models, fields, api
from ..transact_ws.TransAct import TransAct

class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    transact_payment_id = fields.Many2one(
        comodel_name='payment.transact.integration', readonly=False)

    # display_name = fields.Char(string='Descripción', compute='_compute_display_name')

    # def _compute_display_name(self):
    #     for record in self:
    #         # Personaliza cómo se formará el display_name
    #         record.display_name = f'{record.reference} - {record.amount}'

    @api.depends("transact_payment_id")
    def _compute_amount(self):
        self.amount = 111

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        self.ensure_one()
        move = self.line_ids.move_id

        if res and move:
            if move.move_type == 'out_refund':
                # obtener el Ticket del account.move para crear la devolución.
                # return self.action_open_select_option_wizard()
                print('Crear devolución')
                self._procesar_devolucion(move)
            if move.move_type == 'out_invoice':
                print('Crear venta')
                respuest = self._procesar_venta(move)
                # guardar la información de la transacción
                # guardar la información del ticket

                print('out_invoice')
        # raise UserError('not implemented')

    def _calcular_monto_gravado(self):
        move = self.line_ids.move_id
        monto_gravado = 0
        for line in move.invoice_line_ids:
            if line.tax_ids.amount > 0:
                monto_gravado += abs(line.balance)
        return monto_gravado


    def _temp_get_transact(self):
        EmpHASH = 'DF4D21265D1F2F1DDF4D21265D1F2226'
        EmpCod = 'PRIMA1'
        TermCod = 'T00001'
        wsdl = "https://wwwi.transact.com.uy/Concentrador/TarjetasTransaccion_401.svc?wsdl"
        return TransAct(wsdl, EmpHASH, EmpCod, TermCod)

    def _procesar_venta(self, move):
        transact = self._temp_get_transact()

        data = self._get_data_from_move(move)


        transaccion = transact.crearVentaPesos() \
            .establecerMonto(data['monto'], 0, 0) \
            .establecerFactura(data['facturaNro'], data['facturaMonto'], data['facturaMontoGravado'], data['facturaMontoIVA'])

        respuesta = transact.procesarTransaccion(transaccion)



        # display_name = str(transaccion.monto) + str(transaccion.monedaISO)

        new_transact = self.env['payment.transact.integration'].create({
            'ticket': respuesta.Ticket,
            'move_id': move.id,
        })

        vals = {
            'transact_ticket': respuesta.Ticket,
            'transact_id': new_transact.id
        }
        move.write(vals)

        return

    def _procesar_devolucion(self, move):
        transact = self._temp_get_transact()
        if self.transact_payment_id:

            transaccion = transact.paraDevolucion(self.transact_payment_id.ticket)
            respuesta = transact.procesarTransaccion(transaccion)

            return respuesta


    def _get_data_from_move(self, move):
        data = {
            'facturaNro': move.id,
            'facturaMonto': move.amount_total * 100,
            'facturaMontoGravado': self._calcular_monto_gravado() * 100,
            'facturaMontoIVA': move.amount_tax * 100,
            'monto': self.amount * 100,
        }

        return data

    def action_open_select_option_wizard(self):
        # Retorna la acción que abre el wizard
        return {
            'type': 'ir.actions.act_window',
            'name': 'Seleccionar opción',
            'res_model': 'select.payment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('payment_transact_integration.view_payment_selection_wizard_form').id,
            'target': 'new',  # El wizard se abrirá como un popup
            'context': {
                'default_option_id': self.id,  # Pasar datos al wizard si es necesario
            },
        }



