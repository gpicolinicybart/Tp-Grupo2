
from elemento import Elemento

class ArticuloFabricadoInternamente(Elemento):
    def __init__(self, id_elemento: int, nombre: str, bom: list, lista_tareas: list):
        super().__init__(id_elemento, nombre)
        self._bom = bom # Lista de elementos
        self._lista_tareas = lista_tareas 

    def __str__(self):
        materiales = []
        for bom in self._bom:
            for elemento, cantidad in bom.get_diccionario().items():
                materiales.append(f"{elemento.get_nombre()} (x{cantidad})")
                
        materiales_str = ", ".join(materiales)
        
        
        return f"Artículo Fabricado -> {super().__str__()} | Componentes BOM: {len(self._bom)} | Tareas: {len(self._lista_tareas)} | Materiales: [{materiales_str}]"
    
    def get_costo_total(self) -> float:
        # MAP + LAMBDA
        return sum(map(lambda item: item[0].get_costo_unitario() * item[1], self._diccionario.items()))
  
    def validar_ciclos(self, camino_actual=None) -> bool:
            if camino_actual is None:
                camino_actual = set() #usamos el set porque es un conjunto y no permite duplicados, lo que es ideal para detectar ciclos.
                
            if self in camino_actual:
                raise ValueError(f"CICLO DETECTADO: El artículo '{self._nombre}' se requiere a sí mismo.")
                
            # Agregamos el artículo actual al rastro
            camino_actual.add(self)
            
            for bom in self._bom:
                # FILTER + LAMBDA: Nos quedamos únicamente con los componentes que son fabricados internamente
                sub_articulos = filter(lambda elem: isinstance(elem, ArticuloFabricadoInternamente), bom.get_diccionario().keys())
                
                for elemento in sub_articulos:
                    elemento.validar_ciclos(camino_actual)
            
            # Antes de terminar, borramos el conjunto para que quede vacio para la siguiente validación
            camino_actual.remove(self)
            return True