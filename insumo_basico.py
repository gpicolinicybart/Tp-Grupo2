from elemento import Elemento
class InsumoBasico(Elemento):
    def __init__(self, nombre: str, costo_fijo: float, id: int = None):
        super().__init__(nombre, id=id)
        self._costo_fijo = self.validar_costo_fijo(costo_fijo)


    @staticmethod
    def validar_costo_fijo(costo: float) -> float:
        if costo < 0:
            raise ValueError("Error: El costo fijo no puede ser negativo.")
        return costo
    def get_lista_tareas(self):
        return []
    def __str__(self):
        return f"Insumo Básico -> {super().__str__()} | Costo Fijo: ${self._costo_fijo}"
    
    def get_costo_fijo(self) -> float:
        return self._costo_fijo
    
    def get_tipo_elemento(self):
        return "Insumo Básico"
      
    def set_costo_fijo(self, nuevo_costo: float):
        if nuevo_costo >= 0:
            self._costo_fijo = self.validar_costo_fijo(nuevo_costo)
        else:
            raise ValueError("Error: El costo no puede ser negativo.")

    def get_costo_unitario(self):
        return self._costo_fijo
    

    def gestionar_reabastecimiento(self, empresa, cantidad_faltante: int):
        from compra_insumo import Compra_Insumo
        nueva_compra = Compra_Insumo(self, cantidad_faltante)
        empresa.registrar_compra(nueva_compra)
        return f"Se ha generado una orden de compra para reabastecer {cantidad_faltante} unidades de '{self.get_nombre()}'. (Orden ID: {nueva_compra.get_id()})"
    
    def acumular_necesidades(self, cantidad: int, necesidades: dict, camino=None):
        necesidades[self] = necesidades.get(self, 0) + cantidad

    ARCHIVO = "csv/productos.csv"
    COLUMNAS = ["ID Producto", "Nombre Producto", "Tipo", "Costo Fijo"]

    def serialize(self):
        return [self._id, self.get_nombre(), self.get_tipo_elemento(), self._costo_fijo]

    @classmethod
    def deserialize(cls, fila):
        return cls(fila["Nombre Producto"], float(fila["Costo Fijo"]),
                id=int(fila["ID Producto"]))