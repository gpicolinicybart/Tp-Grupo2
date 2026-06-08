class Usuario:
    ARCHIVO = "csv/usuarios.csv"
    COLUMNAS = ["id", "clave", "rol", "nombre", "apellido", "dni"]

    def __init__(self, id, clave, rol, nombre="", apellido="", dni=""):
        self._id = id
        self._clave = clave
        self._rol = rol
        self._nombre = nombre
        self._apellido = apellido
        self._dni = dni

    def get_id(self):
        return self._id

    def get_clave(self):
        return self._clave

    def get_rol(self):
        return self._rol

    def serialize(self):
        return [self._id, self._clave, self._rol, self._nombre, self._apellido, self._dni]

    @classmethod
    def deserialize(cls, fila):
        return cls(fila["id"].strip(), fila["clave"].strip(), fila["rol"].strip(),
                   fila.get("nombre", "").strip(), fila.get("apellido", "").strip(),
                   fila.get("dni", "").strip())