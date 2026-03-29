
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
        costo_materiales = 0.0
        for bom in self._bom:
            costo_materiales += bom.get_costo_total()
            
        costo_manufactura = 0.0
        for tarea in self._lista_tareas:
            costo_manufactura += tarea.get_costo()
            
        return costo_materiales + costo_manufactura
    
    def validar_ciclos(self, camino_actual=None) -> bool:
        if camino_actual is None:
            camino_actual = set()
            
        if self in camino_actual:
            print(f"-> ERROR DE DISEÑO: Ciclo detectado. El artículo '{self._nombre}' se requiere a sí mismo (directa o indirectamente).")
            return False

        camino_actual.add(self)
        for bom in self._bom:
            for elemento in bom.get_diccionario().keys():
                if isinstance(elemento, ArticuloFabricadoInternamente):
                    if not elemento.validar_ciclos(camino_actual.copy()):
                        return False
                        
        return True