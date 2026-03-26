
from elemento import Elemento

class ArticuloFabricadoInternamente(Elemento):
    def __init__(self, id_elemento: int, nombre: str, bom: list, lista_tareas: list):
        super().__init__(id_elemento, nombre)
        self._bom = bom 
        self._lista_tareas = lista_tareas 

    def __str__(self):
        cant_bom = len(self._bom)
        cant_tareas = len(self._lista_tareas)
        return f"Artículo Fabricado -> ID: {self._id} | Nombre: '{self._nombre}' | Componentes BOM: {cant_bom} | Tareas asociadas: {cant_tareas}"
    
    def get_bom(self) -> list:
        return self._bom
        
    def get_lista_tareas(self) -> list:
        return self._lista_tareas   
    
    def get_costo_unitario(self) -> float:
        pass
        
    def validar_ciclos(self) -> bool:
        pass