
class Colaborador:
    def __init__(self, id_colaborador: int, habilidades: list, horas_disponibles: float, salario_hora: float):
        self._id = id_colaborador
        self._habilidades = habilidades
        self._horas_disponibles = horas_disponibles
        self._horas_asignadas = 0.0 
        self._salario_hora = self.validar_salario(salario_hora)

    def validar_salario(self, salario: float) -> bool:
        if salario <= 0:
            raise ValueError("Error: El salario por hora debe ser mayor a cero.")
        return True
    
    def __str__(self):
        horas_libres = self._horas_disponibles - self._horas_asignadas
        habilidades_str = ", ".join(self._habilidades) 
        return f"Colaborador #{self._id} | Disp: {horas_libres}hs libres | Habilidades: [{habilidades_str}]"   
    
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
        if habilidad in self._habilidades:
            return True
        else:
            return False
        
    def verificar_disponibilidad(self, horas_necesarias: float) -> bool:
        horas_libres=self._horas_disponibles-self._horas_asignadas
        if horas_libres>=horas_necesarias:
            return True
        else:
            return False
        
    def asignar_tarea(self, habilidad_requerida: str, duracion: float) -> bool:
        if duracion <= 0:
            raise ValueError("Error: La duración de la tarea debe ser mayor a cero.")
        if self.tiene_habilidad(habilidad_requerida) and self.verificar_disponibilidad(duracion):
            self._horas_asignadas += duracion
            print(f"-> CHECK: Tarea de {habilidad_requerida} asignada al Colaborador {self._id}.")
            return True
        else:
            print(f"-> ERROR: El Colaborador {self._id} no cumple los requisitos para {habilidad_requerida}.")
            return False
    
    
        
#horas_libres se podria poner en un getter aparte y llamarlo desde str y verificar_disponibilidad, 
# ya que se repite su uso. pero bueno por ahora esta bien asi, no es tan grave la repeticion.