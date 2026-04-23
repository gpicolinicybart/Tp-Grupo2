from datetime import datetime

class Colaborador:
    id_colaborador=0
    def __init__(self, habilidades: list, horas_disponibles: float, salario_hora: float):
        Colaborador.id_colaborador += 1
        self._id = Colaborador.id_colaborador
        self._habilidades = habilidades
        self._horas_disponibles = self.validar_horas_disponibles(horas_disponibles)
        self._horas_asignadas = 0.0 
        self._salario_hora = self.validar_salario(salario_hora)
        self._fecha_alta=datetime.now()
        self._fecha_baja=None

    @staticmethod
    def validar_salario(salario: float) -> float:
        if salario <= 0:
            raise ValueError("Error: El salario por hora debe ser mayor a cero.")
        return salario 
    
    @staticmethod
    def validar_horas_disponibles(horas: float) -> float:
        if horas < 0:
            raise ValueError("Error: Las horas disponibles no pueden ser negativas.")
        return horas
    
    def __str__(self):
        alta_str = self._fecha_alta.strftime("%d/%m/%Y")
        
        if self._fecha_baja is not None:
            baja_str = self._fecha_baja.strftime("%d/%m/%Y")
            estado = f"BAJA ({baja_str})"
        else:
            estado = f"ACTIVO desde {alta_str}"
            
        horas_libres = self._horas_disponibles - self._horas_asignadas
        habilidades_str = ", ".join(self._habilidades) 
        
        return f"Colaborador #{self._id} [{estado}] | Disp: {horas_libres}hs | Habilidades: [{habilidades_str}]"
    
    def get_fecha_baja(self):
        return self._fecha_baja
    
    def get_id(self) -> int:
        return self._id
        
    def get_habilidades(self) -> list:
        return self._habilidades
        
    def get_salario_hora(self) -> float:
        return self._salario_hora
        
    def set_salario_hora(self, nuevo_salario: float):
        if nuevo_salario > 0:
            self._salario_hora = nuevo_salario
        else:
            print("Error: El salario debe ser mayor a cero.")

    def tiene_habilidad(self, habilidad: str) -> bool:
        habilidad_buscada = habilidad.strip().lower()
        habilidades_empleado=[hab.strip().lower() for hab in self._habilidades]
        
        return habilidad_buscada in habilidades_empleado
        
    def verificar_disponibilidad(self, horas_necesarias: float) -> bool:
        horas_libres=self._horas_disponibles-self._horas_asignadas
        if horas_libres>=horas_necesarias:
            return True
        else:
            return False
        
    def asignar_tarea(self, habilidad_requerida: str, duracion: float) -> bool:
        if duracion <= 0:
            raise ValueError("Error: La duración de la tarea debe ser mayor a cero.")
        
        if self._fecha_baja is not None:
            print(f"-> ERROR: El Colaborador {self._id} está dado de baja.")
            return False
        
        elif self.tiene_habilidad(habilidad_requerida) and self.verificar_disponibilidad(duracion):
            self._horas_asignadas += duracion
            print(f"-> CHECK: Tarea de {habilidad_requerida} asignada al Colaborador {self._id}.")
            return True
        else:
            print(f"-> ERROR: El Colaborador {self._id} no cumple los requisitos para {habilidad_requerida}.")
            return False
    
    def dar_de_baja(self):
        if self._fecha_baja is not None:
            print(f"El colaborador {self._id} ya estaba dado de baja.")
        else:
            self._fecha_baja = datetime.now()
        