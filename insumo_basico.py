from elemento import Elemento
class InsumoBasico(Elemento):
    def __init__(self, nombre: str, costo_fijo: float, id: int = None):
        super().__init__(nombre, id=id)
        self._costo_fijo = costo_fijo
        if costo_fijo < 0:
            raise ValueError("Error: El costo fijo inicial no puede ser negativo.")
        self._costo_fijo = costo_fijo
        
    def __str__(self):
        return f"Insumo Básico -> {super().__str__()} | Costo Fijo: ${self._costo_fijo}"
    
    def get_costo_fijo(self) -> float:
        return self._costo_fijo
        
    def set_costo_fijo(self, nuevo_costo: float):
        if nuevo_costo >= 0:
            self._costo_fijo = nuevo_costo
        else:
            raise ValueError("Error: El costo no puede ser negativo.")

    def get_costo_unitario(self):
        return self._costo_fijo
    

    def gestionar_reabastecimiento(self, empresa, cantidad_faltante: int):
        from compra_insumo import Compra_Insumo
        nueva_compra = Compra_Insumo(self, cantidad_faltante)
        empresa.registrar_compra(nueva_compra)
        return f"Se ha generado una orden de compra para reabastecer {cantidad_faltante} unidades de '{self.get_nombre()}'. (Orden ID: {nueva_compra.get_id()})"
    
    def acumular_necesidades(self, cantidad: int, necesidades: dict):
        #insumo basico solo suma su cantidad al diccionario de necesidades, no baja más niveles porque no tiene componentes
        necesidades[self] = necesidades.get(self, 0) + cantidad

    def validar_ciclos(self, camino_actual=None) -> bool:
        # es el ultimo eslabon asi que no va a generar ciclos, siempre retorna True
        return True