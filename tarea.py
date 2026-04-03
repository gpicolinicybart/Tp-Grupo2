from unidad_de_trabajo import UnidadDeTrabajo

class Tarea:
    def __init__(self, descripcion: str, unidad_requerida: UnidadDeTrabajo, cant_colaboradores_req: int, tiempo_por_unidad: float, habilidad_requerida: str,costo_mano_obra_hora: float):
        self._descripcion = descripcion
        self._unidad_requerida = unidad_requerida
        self._cant_colaboradores_req = cant_colaboradores_req
        self._tiempo_por_unidad = tiempo_por_unidad
        self._habilidad_requerida = habilidad_requerida
        self._costo_mano_obra_hora = costo_mano_obra_hora

    def __str__(self):
        return f"Tarea: '{self._descripcion}' | Requiere: {self._habilidad_requerida} | Tiempo: {self._tiempo_por_unidad}hs/unidad | Colab. Req: {self._cant_colaboradores_req} | Unidad: {self._unidad_requerida.get_id()} | Costo Mano Obra/hr: ${self._costo_mano_obra_hora}"
    
    def get_descripcion(self) -> str:
        return self._descripcion
        
    def get_tiempo_por_unidad(self) -> float:
        return self._tiempo_por_unidad
    
    def get_costo(self) -> float:
        costo_maquina = self._unidad_requerida.get_costo_operativo() * self._tiempo_por_unidad
        costo_personal = self._costo_mano_obra_hora * self._cant_colaboradores_req * self._tiempo_por_unidad
        return costo_maquina + costo_personal