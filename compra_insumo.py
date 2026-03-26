
from insumo_basico import InsumoBasico

class Compra_Insumo:
    def __init__(self, id_orden: int, insumo: InsumoBasico, cantidad: int):
        self._id = id_orden
        self._insumo = insumo
        self._cantidad = cantidad
        
    def __str__(self):
        return f"Orden de Compra #{self._id} -> {self._cantidad}x {self._insumo._nombre}"    
    
    def get_id(self) -> int:
        return self._id
        
    def get_insumo(self):
        return self._insumo
        
    def get_cantidad(self) -> int:
        return self._cantidad
    
    def recibir_materiales(self, inventario): 
        inventario.ingresar_stock(self._insumo,self._cantidad)
        print(f"Se ingresaron  con éxito {self._cantidad} unidades de {self._insumo._nombre} al inventario (Orden: {self._id}).")
        