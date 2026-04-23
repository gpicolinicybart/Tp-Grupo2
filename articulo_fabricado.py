
from elemento import Elemento

class ArticuloFabricadoInternamente(Elemento):
    def __init__(self, nombre: str, bom: list, lista_tareas: list):
        super().__init__(nombre)
        self._bom = bom # Lista de elementos
        self._lista_tareas = lista_tareas 

    def __str__(self):
        materiales = []
        for bom in self._bom:
            for elemento, cantidad in bom.get_diccionario().items():
                materiales.append(f"{elemento.get_nombre()} (x{cantidad})")
                
        materiales_str = ", ".join(materiales)
        
        
        return f"Artículo Fabricado -> {super().__str__()} | Componentes BOM: {len(self._bom)} | Tareas: {len(self._lista_tareas)} | Materiales: [{materiales_str}]"
    
    def get_costo_unitario(self) -> float:
        costo_materiales = sum(map(lambda bom: bom.get_costo_total(), self._bom))
        costo_manufactura = sum(map(lambda tarea: tarea.get_costo(), self._lista_tareas))
        return costo_materiales + costo_manufactura
  
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
    
    def gestionar_reabastecimiento(self, empresa, cantidad_faltante: int):
            from solicitud_fabricacion import SolicitudDeFabricacion
            nueva_solicitud = SolicitudDeFabricacion( self, cantidad_faltante, False)
            empresa.crear_solicitud(nueva_solicitud)
            return f"Se ha generado una solicitud de fabricación para reabastecer {cantidad_faltante} unidades de '{self.get_nombre()}'. (Solicitud ID: {nueva_solicitud.get_id()})"
    
    def get_bom(self):
        return self._bom
        
    def get_lista_tareas(self):
        return self._lista_tareas
        
    def acumular_necesidades(self, cantidad: int, necesidades: dict):
        #articulo fabricado acumula sus necesidades multiplicando la cantidad pedida por la cantidad unitaria de cada componente en su bom.
        for bom in self.get_bom():
            for componente, cant_unitaria in bom.get_diccionario().items():
                cant_total = cant_unitaria * cantidad
                
                # Si es Insumo se suma, si es Artículo vuelve a bajar un nivel y acumula sus componentes multiplicados por 
                # la cantidad total necesaria de ese componente. Esto se hace de forma recursiva hasta llegar a los insumos básicos.
                componente.acumular_necesidades(cant_total, necesidades)
            
    def calcular_materiales_necesarios(self, cantidad_pedida: int, necesidades: dict = None) -> dict:
        necesidades = {}
        #arranca la reaccion en cadena
        self.acumular_necesidades(cantidad_pedida, necesidades)
        return necesidades

    def calcular_horas_en_unidad(self, unidad, cantidad: int) -> float:
        es_tarea_de_unidad = lambda x: x.get_unidad_requerida().get_id() == unidad.get_id()
        tareas_unidad = filter(es_tarea_de_unidad, self._lista_tareas)
        return sum(map(lambda x: x.get_tiempo_por_unidad() * cantidad, tareas_unidad))