
class MenuBase():
    def __init__(self, empresa):
        self.empresa = empresa

    def mostrar_opciones(self):
        pass
    def ejecutar_opcion(self, opcion: str) -> bool:
        pass