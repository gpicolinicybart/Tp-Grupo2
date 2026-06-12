from datetime import datetime
class UnidadDeTrabajo:
    id_unidad=0
    def __init__(self, nombre: str, capacidad_max_horas: float, costo_operativo_por_hora: float, id: int = None):
        if id is None:
            UnidadDeTrabajo.id_unidad += 1
            self._id = UnidadDeTrabajo.id_unidad
        else:
            self._id = id
            if id > UnidadDeTrabajo.id_unidad:
                UnidadDeTrabajo.id_unidad = id
        self._nombre = self.validar_nombre(nombre)
        self._capacidad_max_horas = self.validar_capacidad(capacidad_max_horas)
        self._horas_reservadas = 0.0 
        self._costo_operativo_por_hora = self.validar_costo_operativo(costo_operativo_por_hora)
        self._fecha_instalacion = datetime.now()

    @staticmethod
    def validar_nombre(nombre: str) -> str:
        if not nombre:
            raise ValueError("Error: El nombre de la unidad de trabajo no puede estar vacío.")
        return nombre
    @staticmethod
    def validar_costo_operativo(costo: float) -> float:
        if costo < 0:
            raise ValueError("Error: El costo operativo por hora debe ser un valor no negativo.")
        return costo
    @staticmethod
    def validar_capacidad(capacidad: float) -> float:
        if capacidad <= 0:
            raise ValueError("Error: La capacidad máxima de horas debe ser un valor positivo.")
        return capacidad
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

    ARCHIVO = "csv/unidades.csv"
    COLUMNAS = ["ID Unidad", "Nombre", "Capacidad", "Costo Operativo"]

    def serialize(self):
        return [self._id, self._nombre, self._capacidad_max_horas, self._costo_operativo_por_hora]

    @classmethod
    def deserialize(cls, fila):
        return cls(fila["Nombre"], float(fila["Capacidad"]),
                float(fila["Costo Operativo"]), id=int(fila["ID Unidad"]))
    
    def liberar_horas(self, horas_liberadas: float) -> bool:
        if self._horas_reservadas >= horas_liberadas:
            self._horas_reservadas -= horas_liberadas
        else:
            self._horas_reservadas = 0.0
        print(f"-> CHECK: Se liberaron {horas_liberadas}hs en la Unidad #{self._id}.")
        return True