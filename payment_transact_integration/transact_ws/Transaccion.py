from .Enums import TarjetaId, EmisorId

class Transaccion():

    def __init__(self, empCod, empHASH, termCod):
        self.empCod = empCod
        self.empHASH = empHASH
        self.termCod = termCod


        # Valores por defecto
        self.modoEmulacion = None
        self.emisorId = EmisorId.TODOS.value
        self.tarjetaTipo = ''
        self.tarjetaAlimentacion = None
        self.facturaConsumidorFinal = None
        self.facturaMonto = 0
        self.facturaMontoGravado = 0
        self.facturaMontoIVA = 0
        self.facturaNro = 0
        self.monedaISO = ''
        self.monto = 0
        self.montoCashBack = 0
        self.montoPropina = 0
        self.operacion = ''
        self.tarjetaId = TarjetaId.TODAS.value
        self.tokenNro = ''
        self.ticketOriginal = None


    # def __init__(self, modoEmulacion, emisorId, empCod, empHASH, facturaConsumidorFinal, facturaMonto,
    #              facturaMontoGravado, facturaMontoIVA, facturaNro, monedaISO, monto, montoCashBack, montoPropina,
    #              operacion, tarjetaAlimentacion, tarjetaId, tarjetaTipo, termCod):
    #     self.modoEmulacion = modoEmulacion
    #     self.emisorId = emisorId
    #     self.empCod = empCod
    #     self.empHASH = empHASH
    #     self.facturaConsumidorFinal = facturaConsumidorFinal
    #     self.facturaMonto = facturaMonto
    #     self.facturaMontoGravado = facturaMontoGravado
    #     self.facturaMontoIVA = facturaMontoIVA
    #     self.facturaNro = facturaNro
    #     self.monedaISO = monedaISO
    #     self.monto = monto
    #     self.montoCashBack = montoCashBack
    #     self.montoPropina = montoPropina
    #     self.operacion = operacion
    #     self.tarjetaAlimentacion = tarjetaAlimentacion
    #     self.tarjetaId = tarjetaId
    #     self.termCod = termCod
    #     self.tarjetaTipo = tarjetaTipo

    def crear(self):
        return self

    def crearEmulacion(self):
        '''
        Establece el modo de emulacion
        :return: La misma instancia de Transaccion
        '''
        self.modoEmulacion = True
        return self

    def crearVenta(self):
        '''
        Establece la transaccion como una operacion de venta
        :return: La misma instancia de Transaccion
        '''
        self.operacion = 'VTA'
        return self

    def paraDevolucion(self, ticketOrigial):
        '''
        Establece la transaccion como una operacion de devolucion
        :return: La misma instancia de Transaccion
        '''
        self.ticketOriginal = int(ticketOrigial)
        self.operacion = 'DEV'
        return self

    def crearPesos(self):
        '''
        Establece la moneda de la transaccion como pesos
        :return: La misma instancia de Transaccion
        '''
        self.monedaISO = '0858'
        return self

    def crearDolares(self):
        '''
        Estaablece la moneda de la transaccion como dolares
        :return: La misma instancia de Transaccion
        '''
        self.monedaISO = '0840'
        return self

    def crearCredito(self):
        '''
        Establece la tarjeta del la transaccion como de credito
        :return: La misma instancia de Transaccion
        '''
        self.tarjetaTipo = 'CRE'
        return self

    def crearDebito(self):
        '''
        Establece la tarjeta del la transaccion como de debito
        :return: La misma instancia de Transaccion
        '''
        self.tarjetaTipo = 'DEB'
        return self

    def crearAlimentacion(self):
        '''
        Establece que la tarjeta del la transaccion será de alimentacion
        :return: La misma instancia de Transaccion
        '''
        self.tarjetaAlimentacion = True
        return self

    def crearNoAlimentacion(self):
        '''
        Establece que la tarjeta del la transaccion no podrá ser alimentacion
        :return: La misma instancia de Transaccion
        '''
        self.tarjetaAlimentacion = False
        return self

    def establecerTarjetaId(self, tarjetaId: TarjetaId):
        '''
        Establece que tipo de tarjeta debe ser utilizado en la transaccion
        :param tarjetaId: Un valor de la enumeracion TarjetaId
        :return: La misma instancia de Transaccion
        '''

        # Si el di de la tarjeta no esta en el enum de tarjetaId, se laza una excepcion
        # if TarjetaId(tarjetaId) not in TarjetaId:
        #     raise Exception('El valor de tarjetaId no es valido')

        self.tarjetaId = TarjetaId(tarjetaId).value
        return self

    def establecerEmisorId(self, emisorId: EmisorId):
        '''
        Establece de que emisor debe ser la tarjeta que se utilizará en la transaccion
        :param emisorId:
        :return: La misma instancia de Transaccion
        '''
        self.emisorId = EmisorId(emisorId).value
        return self

    def paraConsumidorFinal(self):
        '''
        Establece que la transaccion es para un consumidor final
        :return: La misma instancia de Transaccion
        '''
        self.facturaConsumidorFinal = True
        return self

    def establecerFactura(self, facturaNro, facturaMonto, facturaMontoGravado, facturaMontoIVA):
        '''
        Establece los valores de la factura
        :param facturaNro: El numero de la factura
        :param facturaMonto: El monto total de de la factura, donde (ejemplo) 12200 es 122.00
        :param facturaMontoGravado: El monto gravado de la factura, donde (ejemplo) 10000 es 100.00
        :param facturaMontoIVA: El monto de IVA de la factura, donde (ejemplo) 2200 es 22.00
        :return: La misma instancia de Transaccion
        '''
        self.facturaNro = facturaNro
        self.facturaMonto = facturaMonto
        self.facturaMontoGravado = facturaMontoGravado
        self.facturaMontoIVA = facturaMontoIVA
        return self

    def establecerMonto(self, monto, montoCashBack, montoPropina):
        '''
        Estaablece los montos de la transaccion
        :param monto: El monto de la transaccion
        :param montoCashBack: El monto de cashback de la transaccion
        :param montoPropina: El monto de propina de la transaccion
        :return: La misma instancia de Transaccion
        '''
        self.monto = monto
        self.montoCashBack = montoCashBack
        self.montoPropina = montoPropina
        return self


    def getPostearData(self):
        '''
        Devuelve un diccionario con los valores de la transaccion para ser posteado
        :return: El diccionario con los valores de la transaccion
        '''
        res = {
            'Configuracion': {
                'ModoEmulacion': self.modoEmulacion,
            },
            'EmisorId': self.emisorId,
            'EmpCod': self.empCod,
            'EmpHASH': self.empHASH,
            'FacturaConsumidorFinal': self.facturaConsumidorFinal,
            'FacturaMonto': self.facturaMonto,
            'FacturaMontoGravado': self.facturaMontoGravado,
            'FacturaMontoIVA': self.facturaMontoIVA,
            'FacturaNro': self.facturaNro,
            'MonedaISO': self.monedaISO,
            'Monto': self.monto,
            'MontoCashBack': self.montoCashBack,
            'MontoPropina': self.montoPropina,
            'Operacion': self.operacion,
            'TarjetaAlimentacion': self.tarjetaAlimentacion,
            'TarjetaId': self.tarjetaId,
            'TermCod': self.termCod,
            'TarjetaTipo': self.tarjetaTipo,
        }

        if self.operacion == 'DEV':
            res['TicketOriginal'] = self.ticketOriginal

        if 'TarjetaTipo' in res and res['TarjetaTipo'] == '':
            res.pop('TarjetaTipo')

        if 'TarjetaAlimentacion' in res and res['TarjetaAlimentacion'] == None:
            res.pop('TarjetaAlimentacion')

        return res

    def getDevolverData(self):
        '''
        Devuelve un diccionario con los valores de la transaccion para ser posteado
        :return: El diccionario con los valores de la transaccion
        '''
        res = {
            'Configuracion': {
                'ModoEmulacion': self.modoEmulacion,
            },
            'EmisorId': self.emisorId,
            'EmpCod': self.empCod,
            'EmpHASH': self.empHASH,

        }

        return res

    def getTokenNroData(self):
        '''
        Devuelve un string con el token de la transaccion
        :return: El token de la transaccion
        '''
        return self.tokenNro
