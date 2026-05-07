from solicitud_fabricacion import SolicitudDeFabricacion
from menu_base import MenuBase

class MenuProduccion(MenuBase):
    def __init__(self, empresa, insumos, productos, unidades, colaboradores):
        super().__init__(empresa, insumos, productos, unidades, colaboradores)

    def mostrar_opciones(self):
        print("\n" + "="*60)
        print(" MENÚ DE PRODUCCIÓN (Fábrica y Ejecución)")
        print("="*60)
        print("1. Crear Solicitud de Fabricación")
        print("2. Procesar Solicitudes (Planificación)")
        print("3. Ejecutar Solicitud (Producción)")
        print("4. Finalizar Solicitud (Cierre)")
        print("5. Ver Estado General del Sistema")
        print("6. Recibir Órdenes de Compra (Ingresar Stock de Insumos)")
        print("0. Cerrar Sesión")
        print("="*60)

    def ejecutar_opcion(self, opcion: str) -> bool:
        if opcion == "1":
            self.crear_solicitud()
        elif opcion == "2":
            self.procesar_solicitud()  
        elif opcion == "3":
            self.ejecutar_solicitud()
        elif opcion == "4":
            self.finalizar_solicitud()
        elif opcion == "5":
            self.ver_estado()
        elif opcion == "6":
            self.recibir_compras_pendientes() 
        elif opcion == "0":
            print("\nCerrando sistema de gestion de producción. Hasta luego.")
            return False
        else:
            print("Opción no válida.")
        return True

    def crear_solicitud(self):
        print("\n--- NUEVA SOLICITUD DE FABRICACIÓN ---")
        if not self.productos:
            print("AVISO: No hay productos fabricados en el catálogo.")
            return
            
        try:
            print("Productos disponibles:")
            for id_p, p in self.productos.items():
                print(f"  ID {id_p}: {p.get_nombre()}")
            
            id_p = int(input("\nID del producto a fabricar: "))
            if id_p not in self.productos:
                print("ID inválido.")
                return
                
            cantidad = int(input("Cantidad de unidades: "))
            
            solicitud = SolicitudDeFabricacion(self.productos[id_p], cantidad, True)
            self.empresa.crear_solicitud(solicitud)
            print(f"CONFIRMACIÓN: Solicitud #{solicitud.get_id()} creada.")
            
            # --- PERSISTENCIA: Sincronizamos la Cola con el disco duro ---
            self.empresa.guardar_solicitudes_csv()
            
        except ValueError as e:
            print(f"ERROR: {e}")

    def procesar_solicitud(self):
        self.empresa.procesar_solicitud()
        # --- PERSISTENCIA: Guardamos el cambio de estado de la solicitud ---
        self.empresa.guardar_solicitudes_csv()

    def ejecutar_solicitud(self):
        self.empresa.ejecutar_solicitud()
        # --- PERSISTENCIA: Guardamos el avance ---
        self.empresa.guardar_solicitudes_csv()

    def finalizar_solicitud(self):
        self.empresa.finalizar_solicitud()
        # --- PERSISTENCIA: Eliminamos la solicitud terminada o la pasamos a historial ---
        self.empresa.guardar_solicitudes_csv()
    
    def recibir_compras_pendientes(self):
        print("\n--- RECEPCIÓN DE ÓRDENES DE COMPRA ---")
        cantidad = self.empresa.recibir_compras()
        if cantidad > 0:
            print(f"\n-> ÉXITO: Se ingresaron {cantidad} órdenes al inventario.")
            print("-> AVISO: Podés volver a presionar '6' para que las solicitudes demoradas retomen su curso.")
            # --- PERSISTENCIA: Actualizamos el inventario ---
            self.empresa.guardar_inventario_csv()
        else:
            print("No hay órdenes de compra en tránsito para recibir.")

    def ver_estado(self):
        print("\n" + "="*60)
        print("               ESTADO ACTUAL DEL SISTEMA")
        print("="*60)
        
        print(f"\nCATÁLOGO DE INSUMOS: {len(self.insumos)}")
        for id_ins, ins in self.insumos.items():
        
            disponible = self.empresa.consultar_stock_insumo(ins) 
            
            print(f"  ID {id_ins}: {ins.get_nombre()} | Stock Disponible: {disponible}")
        print(f"\nPRODUCTOS REGISTRADOS: {len(self.productos)}")
        for id_prod, prod in self.productos.items():
            print(f"  ID {id_prod}: {prod.get_nombre()}")
        
        print(f"\nUNIDADES DE TRABAJO: {len(self.unidades)}")
        for unit in self.unidades.values():
            print(f"  {unit}")
        
        print("\nSOLICITUDES EN EL SISTEMA:")
        self.empresa.mostrar_solicitudes()
        print("="*60)