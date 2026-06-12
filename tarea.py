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
        return f"Tarea (ID Maestro: {self._id_tarea_maestra}) | Req. Habilidad ID: {self._id_habilidad_requerida} | Tiempo: {self._tiempo_por_unidad}hs/u | Colab: {self._cant_colaboradores_req} | Unidad: {self._unidad_requerida.get_id()}"
    
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
    def get_costo_mano_obra_hora(self) -> float:
        return self._costo_mano_obra_hora
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
            colab.asignar_tarea(self._id_habilidad_requerida, horas_totales)
    
    def liberar_reservas(self, horas_totales: float, colaboradores: list):
        self._unidad_requerida.liberar_horas(horas_totales)
        for colab in colaboradores:
            colab.liberar_tarea(horas_totales)

    COLUMNAS = ["ID_Tarea_M", "ID Unidad", "Cant Colab", "Tiempo", "ID_Hab_Req", "Costo MO"]

    def serialize(self):
        return [self._id_tarea_maestra, self._unidad_requerida.get_id(),
                self._cant_colaboradores_req, self._tiempo_por_unidad,
                self._id_habilidad_requerida, self._costo_mano_obra_hora]

    @classmethod
    def deserialize(cls, fila, unidades_por_id):
        unidad = unidades_por_id.get(int(fila["ID Unidad"]))
        if unidad is None:
            return None
        return cls(id_tarea_maestra=int(fila["ID_Tarea_M"]), unidad_requerida=unidad,
                   cant_colaboradores_req=int(fila["Cant Colab"]),
                   tiempo_por_unidad=float(fila["Tiempo"]),
                   id_habilidad_requerida=int(fila["ID_Hab_Req"]),
                   costo_mano_obra_hora=float(fila["Costo MO"]))