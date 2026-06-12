class MenuBase():
    def __init__(self, empresa):
        self.empresa = empresa

    def mostrar_opciones(self):
        pass
        
    def ejecutar_opcion(self, opcion: str) -> bool:
        pass

    def ver_estado(self):
        print("\n" + "="*60)
        print("==========  ESTADO ACTUAL DEL SISTEMA  ==========")
        print("="*60)
        insumos = self.empresa.obtener_diccionario_insumos()
        print(f"\nCATÁLOGO DE INSUMOS: {len(insumos)}")
        for id_ins, ins in insumos.items():
            disponible = self.empresa.consultar_stock_insumo(ins)
            print(f"  ID {id_ins}: {ins.get_nombre()} | Stock Disponible: {disponible}")
        productos = self.empresa.obtener_diccionario_productos()
        print(f"\nPRODUCTOS REGISTRADOS: {len(productos)}")
        
        for id_prod, prod in productos.items():
            print(f"  ID {id_prod}: {prod.get_nombre()}")
        unidades = self.empresa.obtener_diccionario_unidades()
        print(f"\nUNIDADES DE TRABAJO: {len(unidades)}")
        
        for unit in unidades.values():
            print(f"  {unit}")
        colaboradores = self.empresa.obtener_diccionario_colaboradores()
        print(f"\nCOLABORADORES: {len(colaboradores)}")
        
        for colab in colaboradores.values():
            print(f"  {colab}")
        print("\nSOLICITUDES EN EL SISTEMA:")
        self.empresa.mostrar_solicitudes()
        
        print("="*60)