class TareaMaestra:
    ARCHIVO = "csv/tareas_maestras.csv"
    COLUMNAS = ["ID", "Nombre", "ID_Unidad", "ID_Habilidad"]

    def __init__(self, id, nombre, id_unidad, id_habilidad):
        self._id = id
        self._nombre = nombre
        self._id_unidad = id_unidad
        self._id_habilidad = id_habilidad

    def get_id(self):
        return self._id

    def get_nombre(self):
        return self._nombre

    def get_id_unidad(self):
        return self._id_unidad

    def get_id_habilidad(self):
        return self._id_habilidad

    def serialize(self):
        return [self._id, self._nombre, self._id_unidad, self._id_habilidad]

    @classmethod
    def deserialize(cls, fila):
        return cls(int(fila["ID"]), fila["Nombre"],
                   int(fila["ID_Unidad"]), int(fila["ID_Habilidad"]))