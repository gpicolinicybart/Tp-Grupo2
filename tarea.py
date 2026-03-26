from unidad_de_trabajo import UnidadDeTrabajo

class Tarea:
    def __init__(self, descripcion: str, unidad_requerida: UnidadDeTrabajo, cant_colaboradores_req: int, tiempo_por_unidad: float, habilidad_requerida: str):
        self._descripcion = descripcion
        self._unidad_requerida = unidad_requerida
        self._cant_colaboradores_req = cant_colaboradores_req
        self._tiempo_por_unidad = tiempo_por_unidad
        self._habilidad_requerida = habilidad_requerida

    def __str__(self):
        return f"Tarea: '{self._descripcion}' | Requiere: {self._habilidad_requerida} | Tiempo: {self._tiempo_por_unidad}hs/unidad"
    
    def get_descripcion(self) -> str:
        return self._descripcion
        
    def get_tiempo_por_unidad(self) -> float:
        return self._tiempo_por_unidad
    
    def get_costo(self) -> float:
        return self._tiempo_por_unidad * self._unidad_requerida.get_costo_operativo()