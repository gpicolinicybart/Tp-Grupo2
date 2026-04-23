from unidad_de_trabajo import UnidadDeTrabajo

class Tarea:
    def __init__(self, descripcion: str, unidad_requerida: UnidadDeTrabajo, cant_colaboradores_req: int, tiempo_por_unidad: float, habilidad_requerida: str,costo_mano_obra_hora: float):
        self._descripcion = descripcion
        self._unidad_requerida = unidad_requerida
        self._cant_colaboradores_req = cant_colaboradores_req
        self._tiempo_por_unidad = tiempo_por_unidad
        self._habilidad_requerida = habilidad_requerida
        self._costo_mano_obra_hora = self.validar_costo_mano_obra(costo_mano_obra_hora)
        
    @staticmethod
    def validar_costo_mano_obra(costo: float) -> float:
        if costo < 0:
            raise ValueError("Error: El costo de mano de obra por hora debe ser un valor no negativo.")
        return costo

    def __str__(self):
        return f"Tarea: '{self._descripcion}' | Requiere: {self._habilidad_requerida} | Tiempo: {self._tiempo_por_unidad}hs/unidad | Colab. Req: {self._cant_colaboradores_req} | Unidad: {self._unidad_requerida.get_id()} | Costo Mano Obra/hr: ${self._costo_mano_obra_hora}"
    
    def get_descripcion(self) -> str:
        return self._descripcion
        
    def get_tiempo_por_unidad(self) -> float:
        return self._tiempo_por_unidad
    
    def get_unidad_requerida(self) -> UnidadDeTrabajo:
        return self._unidad_requerida

    def get_habilidad_requerida(self) -> str:
        return self._habilidad_requerida

    def get_cant_colaboradores_req(self) -> int:
        return self._cant_colaboradores_req

    def get_costo(self) -> float:
        costo_maquina = self._unidad_requerida.get_costo_operativo() * self._tiempo_por_unidad
        costo_personal = self._costo_mano_obra_hora * self._cant_colaboradores_req * self._tiempo_por_unidad
        return costo_maquina + costo_personal


    def calcular_horas_totales(self, cantidad_pedida: float) -> float:
        #Calcula el tiempo total necesario multiplicando por la cantidad pedida
        return float(self._tiempo_por_unidad) * float(cantidad_pedida)

    def filtrar_colaboradores_aptos(self, diccionario_colabs: dict, horas_totales: float) -> list:
        #Ufiltra personal apto y los ordena por salario para elegir los más baratos. 
        aptos = list(filter(
            lambda c: c.tiene_habilidad(self._habilidad_requerida) and c.verificar_disponibilidad(horas_totales), 
            diccionario_colabs.values()
        ))
        # Los ordena por salario (del más barato al más caro) para ahorrar plata
        return sorted(aptos, key=lambda c: c.get_salario_hora())

    def ejecutar_reservas(self, horas_totales: float, colaboradores: list):
        # Ejecuta las reservas de máquina y personal. 
        self._unidad_requerida.reservar_horas(horas_totales)
        for colab in colaboradores:
            colab.asignar_tarea(self._habilidad_requerida, horas_totales)