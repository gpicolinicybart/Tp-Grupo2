
class Elemento:
    id=0
    def __init__(self, nombre: str):
        Elemento.id += 1
        self._id = Elemento.id
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
        
    def gestionar_reabastecimiento(self) -> str:
        pass
 