from odoo import models, fields
from ..transact_ws.Transaccion import Transaccion
from ..transact_ws.Enums import MonedaISO


class TransactionModel(models.Model):
    _name = 'transact.transaction'
    _description = 'Modelo de Transacción'

    #Busssines fields
    term_cod = fields.Char(string="Código de Terminal", required=True)
    emisor_id = fields.Selection([
        ('0', 'Todos'), ('11', 'HSBC'), ('1', 'BROU'), ('12', 'Itaú'),
        ('7', 'Bandes'), ('9', 'Citibank'), ('8', 'Scotiabank'),
        ('14', 'OCA'), ('13', 'Santander'), ('15', 'Fucac'), ('10', 'BBVA'),
        ('1301', 'Santander Molinetes'), ('22', 'Pronto'), ('1302', 'Santander Select')
    ], string="ID de Emisor", default='0')

    tarjeta_tipo = fields.Char(string="Tipo de Tarjeta", default='')
    tarjeta_alimentacion = fields.Boolean(string="Tarjeta de Alimentación")
    factura_consumidor_final = fields.Boolean(string="Factura Consumidor Final", default=True)
    factura_monto = fields.Float(string="Monto de la Factura", default=0.0)
    factura_monto_gravado = fields.Float(string="Monto Gravado de la Factura", default=0.0)
    factura_monto_iva = fields.Float(string="Monto IVA de la Factura", default=0.0)
    factura_nro = fields.Integer(string="Número de Factura", default=0)

    moneda_iso = fields.Selection([
        ('0858', 'Pesos'), ('0840', 'Dólares')
    ], string="Moneda ISO", default='0858')

    monto = fields.Float(string="Monto", default=0.0)
    monto_cash_back = fields.Float(string="Monto Cash Back", default=0.0)
    monto_propina = fields.Float(string="Monto Propina", default=0.0)

    operacion = fields.Selection([
        ('VTA', 'Venta'), ('DEV', 'Devolución')
    ], string="Operación", default='VTA')

    tarjeta_id = fields.Selection([
        ('0', 'Todas'), ('1', 'Mastercard'), ('2', 'Visa'), ('3', 'Diners'),
        ('4', 'American Express'), ('5', 'Tarjeta D'), ('6', 'OCA'),
        ('8', 'Cabal'), ('9', 'Anda'), ('12', 'Creditel'), ('14', 'Passcard'),
        ('15', 'Lider'), ('16', 'Club del Este'), ('17', 'Maestro'),
        ('19', 'Edenred Alimentación'), ('20', 'Sodexo Alimentación'),
        ('21', 'Mi Dinero Alimentación'), ('22', 'Mides')
    ], string="ID de Tarjeta", default='0')

    token_nro = fields.Char(string="Número de Token", default='')
    ticket_original = fields.Char(string="Ticket Original")

    # #Integration fields
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Move', required=True, readonly=True, ondelete='cascade',
        index='btree_not_null',
        check_company=True)

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        store=True, readonly=True,
        help="La moneda del pago.")

    def moneda_to_currency_id(self, moneda_iso):
        mapeo = {
            '0858': 46,
            '0840': 1
        }

        return mapeo[moneda_iso]


    def to_transaccion_instance(self):
        """Convierte el registro de Odoo a una instancia de la clase Transaccion"""

        res = Transaccion()

        res.emisorId = self.emisor_id if self.emisor_id else None
        res.tarjetaTipo = self.tarjeta_tipo
        res.tarjetaAlimentacion = self.tarjeta_alimentacion
        res.facturaConsumidorFinal = self.factura_consumidor_final
        res.facturaMonto = self.factura_monto
        res.facturaMontoGravado = self.factura_monto_gravado
        res.facturaMontoIVA = self.factura_monto_iva
        res.facturaNro = self.factura_nro
        res.monedaISO = self.moneda_iso
        res.monto = self.monto
        res.montoCashBack = self.monto_cash_back
        res.montoPropina = self.monto_propina
        res.operacion = self.operacion
        res.tarjetaId = self.tarjeta_id if self.tarjeta_id else None
        res.tokenNro = self.token_nro
        res.ticketOriginal = self.ticket_original
        return res

    def from_transaccion_instance(self, transaccion_instance):
        """Crea un diccionario con los valores de una instancia de Transaccion y lo devuelve"""

        # Crear y devolver un diccionario con los valores de transaccion_instance
        return {
            'term_cod': transaccion_instance.termCod,
            'emisor_id': transaccion_instance.emisorId,
            'tarjeta_tipo': transaccion_instance.tarjetaTipo,
            'tarjeta_alimentacion': transaccion_instance.tarjetaAlimentacion,
            'factura_consumidor_final': transaccion_instance.facturaConsumidorFinal,
            'factura_monto': transaccion_instance.facturaMonto,
            'factura_monto_gravado': transaccion_instance.facturaMontoGravado,
            'factura_monto_iva': transaccion_instance.facturaMontoIVA,
            'factura_nro': transaccion_instance.facturaNro,
            'moneda_iso': transaccion_instance.monedaISO,
            'monto': transaccion_instance.monto,
            'monto_cash_back': transaccion_instance.montoCashBack,
            'monto_propina': transaccion_instance.montoPropina,
            'operacion': transaccion_instance.operacion,
            'tarjeta_id': transaccion_instance.tarjetaId if transaccion_instance.tarjetaId else None,
            'token_nro': transaccion_instance.tokenNro,
            'ticket_original': str(int(transaccion_instance.ticketOriginal)) if transaccion_instance.ticketOriginal else None,
            'move_id':transaccion_instance.move_id,
            'currency_id': self.moneda_to_currency_id(transaccion_instance.monedaISO)
        }





