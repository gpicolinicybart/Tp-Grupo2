from unidad_de_trabajo import UnidadDeTrabajo

class Tarea:
    def __init__(self, id_tarea_maestra: int, unidad_requerida, cant_colaboradores_req: int, tiempo_por_unidad: float, id_habilidad_requerida: int, costo_mano_obra_hora: float):
        self._id_tarea_maestra = id_tarea_maestra
        self._unidad_requerida = unidad_requerida
        self._cant_colaboradores_req = cant_colaboradores_req
        self._tiempo_por_unidad = tiempo_por_unidad
        self._id_habilidad_requerida = id_habilidad_requerida
        self._costo_mano_obra_hora = self.validar_costo_mano_obra(costo_mano_obra_hora)
        
    @staticmethod
    def validar_costo_mano_obra(costo: float) -> float:
        if costo < 0:
            raise ValueError("Error: El costo de mano de obra por hora debe ser un valor no negativo.")
        return costo

    def __str__(self):
        # Como no tenemos el texto, imprimimos los IDs para el reporte técnico
        return f"Tarea (ID Maestro: {self._id_tarea_maestra}) | Req. Habilidad ID: {self._id_habilidad_requerida} | Tiempo: {self._tiempo_por_unidad}hs/u | Colab: {self._cant_colaboradores_req} | Unidad: {self._unidad_requerida.get_id()}"
    
    # --- GETTERS ACTUALIZADOS ---
    def get_id_tarea_maestra(self) -> int:
        return self._id_tarea_maestra
        
    def get_id_habilidad_requerida(self) -> int:
        return self._id_habilidad_requerida

    def get_tiempo_por_unidad(self) -> float:
        return self._tiempo_por_unidad
    
    def get_unidad_requerida(self) -> UnidadDeTrabajo:
        return self._unidad_requerida

    def get_cant_colaboradores_req(self) -> int:
        return self._cant_colaboradores_req

    def get_costo(self) -> float:
        costo_maquina = self._unidad_requerida.get_costo_operativo() * self._tiempo_por_unidad
        costo_personal = self._costo_mano_obra_hora * self._cant_colaboradores_req * self._tiempo_por_unidad
        return costo_maquina + costo_personal

    def calcular_horas_totales(self, cantidad_pedida: float) -> float:
        return float(self._tiempo_por_unidad) * float(cantidad_pedida)

    def filtrar_colaboradores_aptos(self, diccionario_colabs: dict, horas_totales: float) -> list:
        aptos = list(filter(
            lambda c: c.tiene_habilidad(self._id_habilidad_requerida) and c.verificar_disponibilidad(horas_totales), 
            diccionario_colabs.values()))
        return sorted(aptos, key=lambda c: c.get_salario_hora())

    def ejecutar_reservas(self, horas_totales: float, colaboradores: list):
        self._unidad_requerida.reservar_horas(horas_totales)
        for colab in colaboradores:
            # ACÁ HABÍA UN BUG: Se usaba _habilidad_requerida (viejo)
            colab.asignar_tarea(self._id_habilidad_requerida, horas_totales)