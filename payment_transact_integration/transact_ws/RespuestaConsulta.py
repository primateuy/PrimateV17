from typing import Optional, Dict

from .Abstract.Respuesta import Respuesta
from .Enums import Resp_CodigoRespuesta, Resp_EstadoAvance

class RespuestaConsulta(Respuesta):
    def __init__(self):
        self.Aprobada: Optional[bool] = None
        self.CodRespAdq: Optional[str] = None
        self.DatosTransaccion: Optional[Dict] = None
        self.EsOffline: Optional[bool] = None
        self.Lote: Optional[float] = None
        self.MsgRespuesta: Optional[str] = None
        self.NroAutorizacion: Optional[str] = None
        self.Resp_CodigoRespuesta: Optional[Resp_CodigoRespuesta] = Resp_CodigoRespuesta.NONE.value
        self.Resp_EstadoAvance: Optional[Resp_EstadoAvance] = None
        self.Resp_MensajeError: Optional[str] = None
        self.Resp_TokenSegundosReConsultar: Optional[int] = None
        self.Resp_TransaccionFinalizada: Optional[bool] = None
        self.TarjetaId: Optional[int] = None
        self.TarjetaTipo: Optional[str] = None
        self.Ticket: Optional[float] = None
        self.TokenNro: Optional[str] = None
        self.TransaccionId: Optional[float] = None
        self.Voucher: Optional[str] = None

    @staticmethod
    def desde_diccionario(diccionario: Dict) -> 'RespuestaConsulta':
        instancia = RespuestaConsulta()
        instancia.Aprobada = diccionario['Aprobada']
        instancia.CodRespAdq = diccionario['CodRespAdq']
        instancia.DatosTransaccion = diccionario['DatosTransaccion']
        instancia.EsOffline = diccionario['EsOffline']
        instancia.Lote = diccionario['Lote']
        instancia.MsgRespuesta = diccionario['MsgRespuesta']
        instancia.NroAutorizacion = diccionario['NroAutorizacion']
        instancia.Resp_CodigoRespuesta = diccionario['Resp_CodigoRespuesta']
        instancia.Resp_EstadoAvance = diccionario['Resp_EstadoAvance']
        instancia.Resp_MensajeError = diccionario['Resp_MensajeError']
        instancia.Resp_TokenSegundosReConsultar = diccionario['Resp_TokenSegundosReConsultar']
        instancia.Resp_TransaccionFinalizada = diccionario['Resp_TransaccionFinalizada']
        instancia.TarjetaId = diccionario['TarjetaId']
        instancia.TarjetaTipo = diccionario['TarjetaTipo']
        instancia.Ticket = diccionario['Ticket']
        instancia.TokenNro = diccionario['TokenNro']
        instancia.TransaccionId = diccionario['TransaccionId']
        instancia.Voucher = diccionario['Voucher']
        return instancia
