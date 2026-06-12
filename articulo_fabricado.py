from elemento import Elemento
from lista_tareas import ListaEnlazadaTareas
from itembom import ItemBOM

class ArticuloFabricadoInternamente(Elemento):
    def __init__(self, nombre: str, bom: list, lista_tareas: ListaEnlazadaTareas, id: int = None):
        super().__init__(nombre, id=id)
        self._bom = bom # Lista de elementos
        self._lista_tareas = lista_tareas

    def __str__(self):
        materiales = []
        for bom in self._bom:
            for elemento, cantidad in bom.get_diccionario().items():
                materiales.append(f"{elemento.get_nombre()} (x{cantidad})")
        materiales_str = ", ".join(materiales)
        return f"Artículo Fabricado -> {super().__str__()} | Componentes BOM: {len(self._bom)} | Tareas: {len(self._lista_tareas)} | Materiales: [{materiales_str}]"
    
    def get_tipo_elemento(self):
        return "Articulo Fabricado"
    
    def get_costo_unitario(self) -> float:
        costo_tareas = 0.0
        lista_tareas = self.get_lista_tareas()
        if lista_tareas is not None:
            costo_tareas = lista_tareas.get_costo_total()
        costo_materiales = 0.0
        for item in self.get_bom():
            costo_materiales += item.get_costo_total()
        return costo_materiales + costo_tareas
  
    def validar_ciclos(self) -> bool:
        try:
            self.acumular_necesidades(1, {})
            return True
        except ValueError as e:
            print(f"Error al validar '{self.get_nombre()}'")
            return False
    
    def gestionar_reabastecimiento(self, empresa, cantidad_faltante: int):
            from solicitud_fabricacion import SolicitudDeFabricacion
            nueva_solicitud = SolicitudDeFabricacion( self, cantidad_faltante, False)
            empresa.crear_solicitud(nueva_solicitud)
            return f"Se ha generado una solicitud de fabricación para reabastecer {cantidad_faltante} unidades de '{self.get_nombre()}'. (Solicitud ID: {nueva_solicitud.get_id()})"
    
    def get_bom(self):
        return self._bom
    
    def set_bom(self, nueva_bom: list):
        self._bom = nueva_bom
        
    def get_lista_tareas(self):
        return self._lista_tareas
        
    def acumular_necesidades(self, cantidad: int, necesidades: dict, camino=None):
        if camino is None:
            camino = set()
        if self in camino:
            raise ValueError(f"Error: Se detectó un ciclo en la estructura de fabricación del producto '{self.get_nombre()}'.")
        camino.add(self)
        for bom in self.get_bom():
            for componente,cant_unitaria in bom.get_diccionario().items():
                cantidad_total = cant_unitaria * cantidad
                componente.acumular_necesidades(cantidad_total, necesidades,camino)
        camino.remove(self) # liberamos para que ramas paralelas puedan usar el mismo elemento
            
    def calcular_materiales_necesarios(self, cantidad_pedida: int) -> dict:
        necesidades = {}
        self.acumular_necesidades(cantidad_pedida, necesidades)
        return necesidades

    def calcular_horas_en_unidad(self, unidad, cantidad: int) -> float:
        horas_acumuladas = 0
        for tarea in self.get_lista_tareas():
            if tarea.get_unidad_requerida().get_id() == unidad.get_id():
                horas_acumuladas += tarea.get_tiempo_por_unidad() * cantidad
        return horas_acumuladas
    
    def serialize(self):
        receta = []
        for bom_item in self._bom:
            for elemento, cantidad in bom_item.get_diccionario().items():
                receta.append(f"{elemento.get_id()}:{cantidad}")
        receta_str = ";".join(receta)
        return [self._id, self.get_nombre(), self.get_tipo_elemento(), 0.0, receta_str]

    @classmethod
    def deserialize(cls, fila):
        
        return cls(nombre=fila["Nombre Producto"], bom=[],lista_tareas=ListaEnlazadaTareas(), id=int(fila["ID Producto"]))

    @staticmethod
    def reconstruir_bom(producto, receta_str, elementos_por_id):
        if not receta_str:
            return
        items = []
        for par in receta_str.split(";"):
            if not par.strip():
                continue
            comp_id_str, cant_str = par.split(":")
            componente = elementos_por_id.get(int(comp_id_str))
            if componente is not None:
                items.append((componente, int(cant_str)))
        if items:
            producto.set_bom([ItemBOM(f"Receta {producto.get_nombre()}", dict(items))])