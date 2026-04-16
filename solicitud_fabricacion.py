from itembom import ItemBOM

class SolicitudDeFabricacion:
    def __init__(self, id_solicitud: int, item_solicitado: ItemBOM, cantidad: int, es_para_cliente: bool):
        self._id = id_solicitud
        self._item_solicitado = item_solicitado
        self._cantidad =self.validar_entero_positivo(cantidad)
        self._estado = "Creada" # estado inicial, despues tendria q variar entre en proceso, demorada, entregada,etc
        self._es_para_cliente = es_para_cliente #esto tenemos q hablarlo si cuando se solicita una mesa se generan automaticamente solicitudes de patas
        #o el programa internamente avanza con la creacion de patas sin que se generen solicitudes
        self._colaboradores_asignados = [] # es necesario?#guille: yo no creo.#nico: es necesario para mostrar la info de los colabs y pasarle la info a las tareas.
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
    def __str__(self):
        return f"-> SOLICITUD: ID {self._id} | Estado:{self._estado} | Fabricar: {self._cantidad} unidades de '{self._item_solicitado._nombre}' | Colaboradores: {self._colaboradores_asignados}"
    
    def validar_entero_positivo(self, cantidad: int):
        if not isinstance(cantidad, int):
            raise TypeError(f"Error: La cantidad debe ser un número entero. Ingresaste un {type(cantidad).__name__}.")
        if cantidad <= 0:
            raise ValueError(f"Error: La cantidad debe ser mayor a cero. Ingresaste: {cantidad}.")
        return cantidad

