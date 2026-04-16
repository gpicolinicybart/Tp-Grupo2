
class Elemento:
    def __init__(self, id_elemento: int, nombre: str):
        self._id = id_elemento
        self._nombre = nombre
        
    def __str__(self):
        return f"Elemento seleccionado -> ID: {self._id} | Nombre: '{self._nombre}'"
    
    def get_id(self) -> int:
        return self._id
        
    def get_nombre(self) -> str:
        return self._nombre
        
    def set_nombre(self, nuevo_nombre: str):
            if nuevo_nombre != "":
                self._nombre = nuevo_nombre
            else:
                raise ValueError("Error: El nombre no puede estar vacío.")