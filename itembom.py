
class ItemBOM:
    def __init__(self, id_item: int, nombre: str, diccionario_elementos: dict):
        self._id = id_item
        self._nombre = nombre
        self._diccionario = diccionario_elementos 
    
    def __str__(self):
        cant_componentes = len(self._diccionario)
        return f"Receta (Item BOM) -> ID: {self._id} | Nombre: '{self._nombre}' | Cantidad de insumos distintos: {cant_componentes}"

    def get_id(self) -> int:
        return self._id
        
    def get_nombre(self) -> str:
        return self._nombre
        
    def get_diccionario(self) -> dict:
        return self._diccionario
     
    def validar_entero_positivo(self):
        pass
        
    def get_costo_total(self) -> float:
        pass