
from elemento import Elemento

class ArticuloFabricadoInternamente(Elemento):
    def __init__(self, id_elemento: int, nombre: str, bom: list, lista_tareas: list):
        super().__init__(id_elemento, nombre)
        self._bom = bom # Lista de elementos
        self._lista_tareas = lista_tareas 

    def get_costo_unitario(self) -> float:
       # 1. Costo de Materiales (Recorre la lista de ItemBOMs)
        costo_materiales = sum(bom.get_costo_total() for bom in self._bom)
        
        # 2. Costo de Manufactura (Delegado a Tarea)
        costo_manufactura = sum(tarea.get_costo() for tarea in self._lista_tareas)
        
        return costo_materiales + costo_manufactura
  
    def validar_ciclos(self, visitados=None) -> bool:
        if camino_actual is None:
            camino_actual = set()
            
        if self in camino_actual:
            # Usamos raise para que el error corte toda la ejecución y avise qué pasó
            raise ValueError(f"CICLO DETECTADO: El artículo '{self._nombre}' se requiere a sí mismo.")
            
        camino_actual.add(self)
        
        for bom in self._bom:
            # bom es un objeto ItemBOM, accedemos a su diccionario
            for elemento in bom.get_diccionario().keys():
                if isinstance(elemento, ArticuloFabricadoInternamente):
                    # Pasamos una copia del set para no ensuciar otras ramas
                    elemento.validar_ciclos(camino_actual.copy())
        
        return True # Si termina todo el recorrido sin saltar el raise, está OK
