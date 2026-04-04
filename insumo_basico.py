from elemento import Elemento

class InsumoBasico(Elemento):
    def __init__(self, id_elemento: int, nombre: str, costo_fijo: float):
        super().__init__(id_elemento, nombre)
        self._costo_fijo = costo_fijo
        if costo_fijo < 0:
            raise ValueError("Error: El costo fijo inicial no puede ser negativo.")
        self._costo_fijo = costo_fijo
        
    def __str__(self):
        return f"Insumo Básico -> ID: {self._id} | Nombre: '{self._nombre}' | Costo Fijo: ${self._costo_fijo}"  
    
    def get_costo_fijo(self) -> float:
        return self._costo_fijo
        
    def set_costo_fijo(self, nuevo_costo: float):
        if nuevo_costo >= 0:
            self._costo_fijo = nuevo_costo
        else:
            raise ValueError("Error: El costo no puede ser negativo.")

    def get_costo_unitario(self):
        return self._costo_fijo