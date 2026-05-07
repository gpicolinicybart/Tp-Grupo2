
from datetime import datetime

class Elemento:
    id=0
    def __init__(self, nombre: str, id: int = None):
        if id is None:
            Elemento.id += 1
            self._id = Elemento.id
        else:
            self._id = id
            if id > Elemento.id:
                Elemento.id = id
        self._nombre = nombre
        self._fecha_registro = datetime.now()
        
    def __str__(self):
        fecha_str = self._fecha_registro.strftime("%d/%m/%Y")
        return f"Elemento seleccionado -> ID: {self._id} | Nombre: '{self._nombre}' | Fecha de registro: {fecha_str}"
    
    def get_id(self) -> int:
        return self._id
        
    def get_nombre(self) -> str:
        return self._nombre
        
    def set_nombre(self, nuevo_nombre: str):
            if nuevo_nombre != "":
                self._nombre = nuevo_nombre
            else:
                raise ValueError("Error: El nombre no puede estar vacío.")
        
    def gestionar_reabastecimiento(self) -> str:
        pass
        
    def validar_ciclos(self, camino_actual=None) -> bool:
        pass