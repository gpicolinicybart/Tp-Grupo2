from datetime import datetime

class Colaborador:
    id_colaborador = 0
    def __init__(self, habilidades_ids: list, horas_disponibles: float, salario_hora: float, id: int = None, fecha_alta=None, fecha_baja=None):        
        if id is None:
            Colaborador.id_colaborador += 1
            self._id = Colaborador.id_colaborador
        else:
            self._id = id
            if id > Colaborador.id_colaborador:
                Colaborador.id_colaborador = id
                
        self._habilidades_ids = set(habilidades_ids) 
        self._horas_disponibles = self.validar_horas_disponibles(horas_disponibles)
        self._horas_asignadas = 0.0 
        self._salario_hora = self.validar_salario(salario_hora)
        if fecha_alta is not None:
            self._fecha_alta = fecha_alta
        else:   
            self._fecha_alta = datetime.now()
        self._fecha_baja = fecha_baja

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
        habilidades_str = ", ".join(str(h_id) for h_id in self._habilidades_ids) 
        return f"Colaborador #{self._id} [{estado}] | Disp: {horas_libres}hs | Habilidades (IDs): [{habilidades_str}]"
    
    def get_fecha_baja(self):
        return self._fecha_baja
    def get_fecha_alta(self):
        return self._fecha_alta
    
    def get_id(self) -> int:
        return self._id
        
    def get_habilidades(self) -> set:
        return self._habilidades_ids
        
    def get_salario_hora(self) -> float:
        return self._salario_hora
        
    def set_salario_hora(self, nuevo_salario: float):
        if nuevo_salario > 0:
            self._salario_hora = nuevo_salario
        else:
            print("Error: El salario debe ser mayor a cero.")

    def tiene_habilidad(self, id_habilidad: int) -> bool:
        return id_habilidad in self._habilidades_ids
        
    def verificar_disponibilidad(self, horas_necesarias: float) -> bool:
        horas_libres=self._horas_disponibles-self._horas_asignadas
        if horas_libres>=horas_necesarias:
            return True
        else:
            return False
        
    def asignar_tarea(self, id_habilidad_requerida: int, duracion: float) -> bool:
        if duracion <= 0:
            raise ValueError("Error: La duración de la tarea debe ser mayor a cero.")
        
        if self._fecha_baja is not None:
            print(f"-> ERROR: El Colaborador {self._id} está dado de baja.")
            return False
        
        elif self.tiene_habilidad(id_habilidad_requerida) and self.verificar_disponibilidad(duracion):
            self._horas_asignadas += duracion
            print(f"-> CHECK: Tarea asignada al Colaborador {self._id}.")
            return True
        else:
            print(f"-> ERROR: El Colaborador {self._id} no cumple los requisitos.")
            return False
    
    def dar_de_baja(self):
        if self._fecha_baja is not None:
            print(f"El colaborador {self._id} ya estaba dado de baja.")
        else:
            self._fecha_baja = datetime.now()
            
    def get_horas_disponibles(self) -> float:
        return self._horas_disponibles
    
    ARCHIVO = "csv/colaboradores.csv"
    COLUMNAS = ["ID Colaborador", "Habilidades_IDs", "Horas Disponibles",
            "Salario Hora", "Fecha Alta", "Fecha Baja"]

    def serialize(self):
        habilidades_str = ";".join(map(str, self._habilidades_ids))
        f_alta = self._fecha_alta.strftime("%Y-%m-%d %H:%M:%S")
        if self._fecha_baja is not None:
            f_baja = self._fecha_baja.strftime("%Y-%m-%d %H:%M:%S")
        else:
            f_baja = ""
        return [self._id, habilidades_str, self._horas_disponibles,
                self._salario_hora, f_alta, f_baja]

    @classmethod
    def deserialize(cls, fila):
        ids = []
        if fila["Habilidades_IDs"].strip():
            for texto in fila["Habilidades_IDs"].split(";"):
                ids.append(int(texto.strip()))
        f_alta = None
        if fila.get("Fecha Alta"):
            f_alta = datetime.strptime(fila["Fecha Alta"], "%Y-%m-%d %H:%M:%S")
        f_baja = None
        if fila.get("Fecha Baja"):
            f_baja = datetime.strptime(fila["Fecha Baja"], "%Y-%m-%d %H:%M:%S")
        return cls(ids, float(fila["Horas Disponibles"]), float(fila["Salario Hora"]),
                id=int(fila["ID Colaborador"]), fecha_alta=f_alta, fecha_baja=f_baja)
    
    def liberar_tarea(self, duracion: float):
        if self._horas_asignadas >= duracion:
            self._horas_asignadas -= duracion
        else:
            self._horas_asignadas = 0.0
        print(f"-> CHECK: Se liberaron {duracion}hs del Colaborador #{self._id}.")