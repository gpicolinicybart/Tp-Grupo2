
from datetime import datetime


class Compra_Insumo:
    id = 0
    def __init__(self, insumo, cantidad, id=None, estado="Solicitada"):
        if id is None:
            Compra_Insumo.id += 1
            self._id = Compra_Insumo.id
        else:
            self._id = id
            if id > Compra_Insumo.id: 
                Compra_Insumo.id = id
                
        self._insumo = insumo
        self._cantidad = cantidad
        self._estado = estado
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
        
    # NUEVO GETTER
    def get_estado(self) -> str:
        return self._estado
    def get_fecha_emision(self):
        return self._fecha_emision  
    def get_fecha_recepcion(self):
        return self._fecha_recepcion
    
    def set_fechas_historicas(self, fecha_emision, fecha_recepcion=None):
        self._fecha_emision = fecha_emision
        self._fecha_recepcion = fecha_recepcion

    def recibir_materiales(self, inventario): 
        inventario.ingresar_stock(self._insumo, self._cantidad)
        self._estado = "Recibida"  # <--- Encapsulamiento respetado: la clase modifica su propio estado
        self._fecha_recepcion = datetime.now()
        print(f"Se ingresaron con éxito {self._cantidad} unidades de {self._insumo.get_nombre()} al inventario (Orden: {self._id}).")
    
    ARCHIVO = "csv/compras.csv"
    COLUMNAS = ["ID", "Insumo_ID", "Cantidad", "Estado", "Fecha_Emision", "Fecha_Recepcion"]

    def serialize(self):
        f_emision = self._fecha_emision.strftime("%Y-%m-%d %H:%M:%S")
        if self._fecha_recepcion is not None:
            f_recepcion = self._fecha_recepcion.strftime("%Y-%m-%d %H:%M:%S")
        else:
            f_recepcion = ""
        return [self._id, self._insumo.get_id(), self._cantidad,
                self._estado, f_emision, f_recepcion]

    @classmethod
    def deserialize(cls, fila, insumos_por_id):     # <-- recibe el contexto
        insumo = insumos_por_id.get(int(fila["Insumo_ID"]))
        if insumo is None:
            return None
        orden = cls(insumo, int(fila["Cantidad"]), id=int(fila["ID"]), estado=fila["Estado"])
        f_emision = datetime.strptime(fila["Fecha_Emision"], "%Y-%m-%d %H:%M:%S")
        f_recepcion = None
        if fila["Fecha_Recepcion"]:
            f_recepcion = datetime.strptime(fila["Fecha_Recepcion"], "%Y-%m-%d %H:%M:%S")
        orden.set_fechas_historicas(f_emision, f_recepcion)
        return orden