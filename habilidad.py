class Habilidad:
    ARCHIVO = "csv/habilidades.csv"
    COLUMNAS = ["ID", "Nombre"]

    def __init__(self, id, nombre):
        self._id = id
        self._nombre = nombre

    def get_id(self):
        return self._id

    def get_nombre(self):
        return self._nombre

    def serialize(self):
        return [self._id, self._nombre]

    @classmethod
    def deserialize(cls, fila):
        return cls(int(fila["ID"]), fila["Nombre"])