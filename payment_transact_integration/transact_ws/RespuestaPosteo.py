from typing import Optional, Dict

from .Abstract.Respuesta import Respuesta
from .Enums import Resp_CodigoRespuesta

class RespuestaPosteo(Respuesta):
    def __init__(self):
        self.Resp_CodigoRespuesta: Optional[Resp_CodigoRespuesta] = Resp_CodigoRespuesta.NONE.value
        self.Resp_MensajeError: Optional[str] = None
        self.TokenNro: Optional[str] = None
        self.TokenSegundosConsultar: Optional[int] = None

    @staticmethod
    def desde_diccionario(diccionario: Dict) -> 'RespuestaPosteo':
        instancia = RespuestaPosteo()
        instancia.Resp_CodigoRespuesta = diccionario['Resp_CodigoRespuesta']
        instancia.Resp_MensajeError = diccionario['Resp_MensajeError']
        instancia.TokenNro = diccionario['TokenNro']
        instancia.TokenSegundosConsultar = diccionario['TokenSegundosConsultar']
        return instancia
