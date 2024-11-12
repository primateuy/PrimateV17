import logging
import time
from datetime import datetime, timedelta

from zeep import Client

from .Abstract import Respuesta
from .RespuestaCancelacion import RespuestaCancelacion
from .RespuestaConsulta import RespuestaConsulta
from .RespuestaPosteo import RespuestaPosteo
from .Transaccion import Transaccion


wsdl = "https://wwwi.transact.com.uy/Concentrador/TarjetasTransaccion_401.svc?wsdl"
client = Client(wsdl)


class TransAct:
    ISO_MONEDA_UYU = '0858'
    ISO_MONEDA_USD = '0840'
    TRX_TIMEOUT = 120

    def __init__(self, wsdl, empHASH, empCod, termCod):
        self.wsdl = wsdl
        self.empHASH = empHASH
        self.empCod = empCod
        self.termCod = termCod
        self.client = Client(wsdl)

    def procesarTransaccion(self, transaccion: Transaccion)-> Respuesta:
        '''
        Procesa una transaccion, postea la transaccion y consulta hasta que la transaccion finalice o se agote el tiempo.
        :param transaccion: La transaccion a procesar
        :return: La respuesta de la consulta sobre la transaccion
        '''

        transaccion.empHASH = self.empHASH
        transaccion.termCod = self.termCod
        transaccion.empCod = self.empCod


        res = RespuestaConsulta()
        resp_post = self._postearTransaccion(transaccion)

        if resp_post.Resp_CodigoRespuesta != 0:
            logging.error(f"Error: {resp_post.Resp_MensajeError}")
            logging.info(f"La transacción se va a cancelar")
            resp_cancelacion = self.cancelarTransaccion(transaccion)
            if resp_cancelacion.Resp_CodigoRespuesta != 0:
                logging.error(f"Error al cancelar {resp_cancelacion.Resp_MensajeError}")
            else:
                logging.info("Cancelada")
                res = resp_cancelacion
        else:
            logging.info("Posteada")

            time.sleep(resp_post.TokenSegundosConsultar)
            res = resp_cons = self._consultarTransaccion(transaccion)

            time_f = datetime.now() + timedelta(seconds=self.TRX_TIMEOUT)

            while resp_cons.Resp_TransaccionFinalizada == False:
                retry_after = resp_cons.Resp_TokenSegundosReConsultar
                time.sleep(retry_after)
                res = resp_cons = self._consultarTransaccion(transaccion)

                if datetime.now() > time_f:
                    raise Exception('Timeout de transaccion')

            transaccion.ticketOriginal = int(resp_cons.Ticket)

        return res

    def _postearTransaccion(self, transaccion):
        request_data = transaccion.getPostearData()
        response = self.client.service.PostearTransaccion(request_data)
        transaccion.tokenNro = response['TokenNro']
        return RespuestaPosteo.desde_diccionario(response)

    def _consultarTransaccion(self, transaccion: Transaccion):
        if transaccion.tokenNro == '':
            raise Exception('No se puede consultar una transaccion sin token')

        request_data = transaccion.getTokenNroData()
        response = self.client.service.ConsultarTransaccion(request_data)
        return RespuestaConsulta.desde_diccionario(response)

    def cancelarTransaccion(self, transaccion: Transaccion):
        if transaccion.tokenNro == '':
            raise Exception('No se puede cancelar una transaccion sin token')

        request_data = transaccion.getTokenNroData()
        response = self.client.service.CancelarTransaccion(request_data)
        return RespuestaCancelacion.desde_diccionario(response)

    def _crearTransaccion(self) -> Transaccion:
        transaccion = Transaccion(self.empCod, self.empHASH, self.termCod)
        return transaccion

    def crearVentaPesos(self) -> Transaccion:
        transaccion = self._crearTransaccion().crearVenta().crearPesos()
        return transaccion

    def paraDevolucion(self, ticketOriginal):
        transaccion = Transaccion(self.empCod, self.empHASH, self.termCod)
        transaccion.paraDevolucion(ticketOriginal)
        return transaccion
