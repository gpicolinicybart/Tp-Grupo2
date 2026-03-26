from itembom import ItemBOM

class SolicitudDeFabricacion:
    def __init__(self, id_solicitud: int, item_solicitado: ItemBOM, cantidad: int, es_para_cliente: bool):
        self._id = id_solicitud
        self._item_solicitado = item_solicitado
        self._cantidad = self.validar_entero_positivo(cantidad)
        self._estado = "Creada" 
        self._es_para_cliente = es_para_cliente 
        self._colaboradores_asignados = [] 

    def validar_entero_positivo(self,cantidad: int):
        if not isinstance(cantidad, int):
            raise TypeError(f"Error: La cantidad debe ser un número entero. Ingresaste un {type(cantidad).__name__}.")
        
        if cantidad <= 0:
            raise ValueError(f"Error: La cantidad debe ser mayor a cero. Ingresaste: {cantidad}.")
        return cantidad
    
    def __str__(self):
        return f"Solicitud #{self._id} | Estado: {self._estado} | Fabricar: {self._cantidad}x '{self._item_solicitado._nombre}'"
    
    def get_id(self) -> int:
        return self._id
        
    def get_estado(self) -> str:
        return self._estado
        
    def get_item_solicitado(self):
        return self._item_solicitado
        
    def get_cantidad(self) -> int:
        return self._cantidad
    
    def planificar(self, inventario, unidades: list = None, colaboradores: list = None) -> bool:
        print(f"\n[Sistema] Planificando solicitud {self._id}...")
        pudo_reservar = inventario.reservar_stock(self._item_solicitado, self._cantidad)
        if pudo_reservar:
            self._estado = "Planificada"
            return True
        else:
            self._estado = "Demorada por falta de stock"
            return False
            
    def ejecutar(self, inventario):
        if self._estado == "Planificada":
            print(f"\n[Sistema] Ejecutando solicitud {self._id}. La producción arranca...")
            inventario.descontar_stock(self._item_solicitado, self._cantidad)
            self._estado = "En curso"
        else:
            print(f"\n[Error] No se puede ejecutar la solicitud {self._id}. Estado actual: {self._estado}")
            
    def finalizar(self, inventario): 
        if self._estado == "En curso":
            print(f"\n[Sistema] Finalizando solicitud {self._id}. Producción terminada.")
            inventario.ingresar_stock(self._item_solicitado, self._cantidad)
            self._estado = "Terminada"
        else:
            print(f"\n[Error] No se puede finalizar la solicitud {self._id}. Estado actual: {self._estado}")
   