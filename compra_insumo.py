
from datetime import datetime
from insumo_basico import InsumoBasico

class Compra_Insumo:
    id = 0
    def __init__(self, insumo: InsumoBasico, cantidad: int):
        Compra_Insumo.id += 1
        self._id = Compra_Insumo.id
        self._insumo = insumo
        self._cantidad = cantidad
        self._fecha_emision = datetime.now()
        self._fecha_recepcion = None
        
    def __str__(self):
        emision_str = self._fecha_emision.strftime("%d/%m/%Y %H:%M")
        if self._fecha_recepcion:
            rec_str = self._fecha_recepcion.strftime("%d/%m/%Y %H:%M")
            estado = f"RECIBIDA el {rec_str}"
        else:
            estado = "EN TRÁNSITO"
        return f"Orden de Compra #{self._id} -> {self._cantidad}x {self._insumo.get_nombre()} ({estado} | Emitida: {emision_str})"    
    
    def get_id(self) -> int:
        return self._id
        
    def get_insumo(self):
        return self._insumo
        
    def get_cantidad(self) -> int:
        return self._cantidad
    
    def recibir_materiales(self, inventario): 
        inventario.ingresar_stock(self._insumo,self._cantidad)
        self._fecha_recepcion = datetime.now()
        print(f"Se ingresaron  con éxito {self._cantidad} unidades de {self._insumo._nombre} al inventario (Orden: {self._id}).")
        