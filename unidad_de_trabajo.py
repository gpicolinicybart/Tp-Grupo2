class UnidadDeTrabajo:
    def __init__(self, id_unidad: int, capacidad_max_horas: float, limite_de_colab: int, costo_operativo_por_hora: float):
        self._id = id_unidad
        self._capacidad_max_horas = capacidad_max_horas
        self._limite_de_colab = limite_de_colab
        self._horas_reservadas = 0.0 
        self._costo_operativo_por_hora = costo_operativo_por_hora 

    def __str__(self):
        return f"Unidad #{self._id} | Capacidad Max: {self._capacidad_max_horas}hs | Costo/hr: ${self._costo_operativo_por_hora}"  

    def get_id(self) -> int:
        return self._id
        
    def get_costo_operativo(self) -> float:
        return self._costo_operativo_por_hora
        
    def set_costo_operativo(self, nuevo_costo: float):
        if nuevo_costo >= 0:
            self._costo_operativo_por_hora = nuevo_costo

    def verificar_disponibilidad(self, horas_necesarias: float) -> bool:
        horas_libres = self._capacidad_max_horas - self._horas_reservadas
        if horas_libres >= horas_necesarias:
            return True
        else:
            return False
