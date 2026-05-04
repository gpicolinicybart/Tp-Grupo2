
class MenuBase():
    def __init__(self, empresa, insumos, productos, unidades, colaboradores):
        self.empresa = empresa
        self.insumos = insumos
        self.productos = productos
        self.unidades = unidades
        self.colaboradores = colaboradores

    def mostrar_opciones(self):
        pass
    def ejecutar_opcion(self, opcion: str) -> bool:
        pass