
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
        
    def get_tipo_reabastecimiento(self) -> str:
        """Obliga a las clases hijas a decir cómo se consiguen"""
        raise NotImplementedError("Debe implementarse en las clases hijas")
    #Aca hice un getter que se refiere a lo que nos dijo lean. 
    # las clases hijas deben decir como se consguien, si en un futuro agregamos compra de paraguay ejemplo esta funcion se encarga de verificar si lo dice la clase hija o no. Si no lo dice, tira un error.
    # Esto es polimorfismo, cada clase hija tiene su propia implementación de esta función.