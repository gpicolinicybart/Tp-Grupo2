from datetime import datetime
class UnidadDeTrabajo:
    id_unidad=0
    def __init__(self, nombre: str, capacidad_max_horas: float, costo_operativo_por_hora: float):
        UnidadDeTrabajo.id_unidad += 1
        self._id = UnidadDeTrabajo.id_unidad
        self._nombre = nombre
        self._capacidad_max_horas = float(capacidad_max_horas)
        self._horas_reservadas = 0.0 
        self._costo_operativo_por_hora = self.validar_costo_operativo(costo_operativo_por_hora)
        self._fecha_instalacion = datetime.now()
    @staticmethod
    def validar_costo_operativo(costo: float) -> float:
        if costo < 0:
            raise ValueError("Error: El costo operativo por hora debe ser un valor no negativo.")
        return costo

    def __str__(self):
        fecha_str = self._fecha_instalacion.strftime("%d/%m/%Y")
        return f"Unidad #{self._id} ({self._nombre}) | Capacidad Max: {self._capacidad_max_horas}hs | Costo/hr: ${self._costo_operativo_por_hora} | Fecha de instalación: {fecha_str}"

    def get_id(self) -> int:
        return self._id
    
    def get_nombre(self) -> str:
        return self._nombre
    
    def get_capacidad_max_horas(self) -> float:
        return self._capacidad_max_horas
    
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
        
    def reservar_horas(self, horas_necesarias: float) -> bool:
            if self.verificar_disponibilidad(horas_necesarias):
                self._horas_reservadas += horas_necesarias
                print(f"-> CHECK: Se reservaron {horas_necesarias}hs en la Unidad #{self._id}.")
                return True
            else:
                print(f"-> ERROR: La Unidad #{self._id} no tiene {horas_necesarias}hs disponibles.")
                return False
    def get_porcentaje_uso(self) -> float:
            if self._capacidad_max_horas == 0:
                return 0.0
            porcentaje = (self._horas_reservadas * 100) / self._capacidad_max_horas
            return porcentaje