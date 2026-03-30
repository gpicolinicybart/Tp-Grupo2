from itembom import ItemBOM

class SolicitudDeFabricacion:
    def __init__(self, id_solicitud: int, item_solicitado: ItemBOM, cantidad: int, es_para_cliente: bool):
        self._id = id_solicitud
        self._item_solicitado = item_solicitado
        self._cantidad = cantidad
        self._estado = "Creada" # estado inicial, despues tendria q variar entre en proceso, demorada, entregada,etc
        self._es_para_cliente = es_para_cliente #esto tenemos q hablarlo si cuando se solicita una mesa se generan automaticamente solicitudes de patas
        #o el programa internamente avanza con la creacion de patas sin que se generen solicitudes
        self._colaboradores_asignados = [] # es necesario?#guille: yo no creo.#nico: es necesario para mostrar la info de los colabs y pasarle la info a las tareas.

    def mostrar_info (self):
        print(f"-> SOLICITUD: ID {self._id} | Estado:{self._estado} | Fabricar: {self._cantidad} unidades de '{self._item_solicitado._nombre} colaboradores'{self._colaboradores_asignados} ")
    def planificar (self, inventario):#saque esto, duda, no rompe encapsulamiento?(self, inventario, unidades: list, colaboradores: list) -> bool:
        print(f"\n--- PLANIFICACIÓN ID: {self._id} ---")
        errores = []
        producto = self._item_solicitado # El ArticuloFabricado
        
        # 1. Preguntamos al Inventario (Encapsulado)
        for elem, cant in producto._bom.items():
            total = cant * self._cantidad
            if not inventario.hay_disponibilidad(elem, total):
                errores.append(f"Falta stock de {elem._nombre}")

        # 2. Preguntamos a las Unidades (Encapsulado)
        for tarea in producto._lista_tareas:
            horas = tarea._tiempo_por_unidad * self._cantidad
            if not tarea._unidad_requerida.verificar_disponibilidad(horas):
                errores.append(f"Sobrecarga en Unidad {tarea._unidad_requerida._id}")

        if errores:
            self._estado = "Fallida"
            for e in errores: 
                print(f" [!] {e}")
            return False

        # 3. Si todo OK, damos la orden de reservar (Delegación)
        for elem, cant in producto._bom.items():
            inventario.reservar_stock(elem, cant * self._cantidad)
            
        for tarea in producto._lista_tareas:
            tarea._unidad_requerida.reservar_horas(tarea._tiempo_por_unidad * self._cantidad)
            
        self._estado = "Planificada"
        return True
        
    def ejecutar(self, inventario):
        pass
        
    def finalizar(self, inventario): #ejecutar y finalizar no es lo mismo?
        pass

