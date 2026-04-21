from itembom import ItemBOM
from datetime import datetime

class SolicitudDeFabricacion:
    id_solicitud=0
    def __init__(self, item_solicitado: ItemBOM, cantidad: int, es_para_cliente: bool):
        SolicitudDeFabricacion.id_solicitud += 1
        self._id = SolicitudDeFabricacion.id_solicitud
        self._item_solicitado = item_solicitado
        self._cantidad =self.validar_entero_positivo(cantidad)
        self._estado = "Creada" 
        self._es_para_cliente = es_para_cliente 
        self._colaboradores_asignados = [] 
        self._fecha_creacion = datetime.now()
        self._fecha_finalizacion = None


    def get_id(self):
        return self._id
    def get_item_solicitado(self):
        return self._item_solicitado
    def get_estado(self):
        return self._estado
    def get_cantidad(self):
        return self._cantidad
    def set_estado(self, nuevo_estado: str):
        self._estado = nuevo_estado
    def agregar_colaborador(self, id_colaborador: int):
        if id_colaborador not in self._colaboradores_asignados:
            self._colaboradores_asignados.append(id_colaborador)

    def __str__(self):
        fecha_str= self._fecha_creacion.strftime("%d/%m/%Y %H:%M")
        
        if self._estado == "Terminada" and self._fecha_finalizacion:
            fin_str = self._fecha_finalizacion.strftime("%d/%m/%Y %H:%M")
            estado_visual = f"TERMINADA el {fin_str}, Tiempo transcurrido: {(self._fecha_finalizacion - self._fecha_creacion).total_seconds()/3600:.2f} horas"
        else:
            estado_visual = f"Estado: {self._estado}"
            
        return f"-> SOLICITUD: ID {self._id} ({fecha_str}) | {estado_visual} | Fabricar: {self._cantidad} unidades de '{self._item_solicitado.get_nombre()}' | Colaboradores: {self._colaboradores_asignados}"
    
    def validar_entero_positivo(self, cantidad: int):
        if not isinstance(cantidad, int):
            raise TypeError(f"Error: La cantidad debe ser un número entero. Ingresaste un {type(cantidad).__name__}.")
        if cantidad <= 0:
            raise ValueError(f"Error: La cantidad debe ser mayor a cero. Ingresaste: {cantidad}.")
        return cantidad

    def marcar_como_terminada(self):
        self._estado = "Terminada"
        self._fecha_finalizacion = datetime.now()