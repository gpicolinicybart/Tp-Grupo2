
from menu_base import MenuBase

class MenuProduccion(MenuBase):
    def __init__(self, empresa):
        super().__init__(empresa)

    def mostrar_opciones(self):
        print("\n" + "="*60)
        print(" MENÚ DE PRODUCCIÓN (Fábrica y Ejecución)")
        print("="*60)
        print("1. Crear Solicitud de Fabricación")
        print("2. Procesar Solicitudes (Planificación)")
        print("3. Ejecutar Solicitud (Producción)")
        print("4. Finalizar Solicitud (Cierre)")
        print("5. Ver Estado General del Sistema")
        print("6. Recibir Órdenes de Compra")
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
        productos = self.empresa.obtener_diccionario_productos()
        if not productos:
            return print("AVISO: No hay productos fabricados en el catálogo.")
            
        print("Productos disponibles:")
        for id_producto, producto in productos.items():
            print(f"  ID {id_producto}: {producto.get_nombre()}")
            
        try:
            # 1. Validamos el ingreso del ID
            entrada_id = input("\nID del producto a fabricar: ").strip()
            if not entrada_id.isdigit():
                return print(" [!] ERROR: Por favor, ingrese un número de ID válido.")
            
            id_p = int(entrada_id)
            if id_p not in productos:
                return print(" [!] ERROR: Ese ID de producto no existe.")
                
            # 2. Validamos el ingreso de la cantidad
            entrada_cant = input("Cantidad de unidades: ").strip()
            if not entrada_cant.isdigit():
                return print(" [!] ERROR: Por favor, ingrese una cantidad numérica válida.")
                
            cantidad = int(entrada_cant)
            
            # 3. Generamos la solicitud
            solicitud = self.empresa.generar_solicitud_desde_menu(productos[id_p], cantidad)
            print(f"CONFIRMACIÓN: Solicitud #{solicitud.get_id()} creada.")

            self.empresa.guardar_solicitudes()
            
        except ValueError as e:
            print(f" [!] ERROR: {e}")

    def procesar_solicitud(self):
        try:
            self.empresa.procesar_solicitud()
            self.empresa.guardar_solicitudes()
        except ValueError as e:
            print(f"Error de validación al procesar (Estado incorrecto o falta de stock): {e}")
        except KeyError as e:
            print(f"Error: No se encontró la solicitud en el sistema: {e}")
        except OSError as e:
            print(f"Error de sistema al intentar guardar el archivo CSV: {e}")

    def ejecutar_solicitud(self):
        try:
            self.empresa.ejecutar_solicitud()
            self.empresa.guardar_solicitudes()
        except ValueError as e:
            print(f"Error al ejecutar (La solicitud no está lista para producción): {e}")
        except KeyError as e:
            print(f"Error: ID de solicitud no encontrado: {e}")
        except OSError as e:
            print(f"Error al guardar el avance en el disco: {e}")

    def finalizar_solicitud(self):
        try:
            self.empresa.finalizar_solicitud()
            self.empresa.guardar_solicitudes()
        except ValueError as e:
            print(f"Error de negocio al finalizar (Quizás la solicitud aún no está en ejecución): {e}")
        except KeyError as e:
            print(f"Error: No se encontró la solicitud a finalizar: {e}")
        except OSError as e:
            print(f"Error al actualizar el historial CSV: {e}")
    
    def recibir_compras_pendientes(self):
        print("\n--- RECEPCIÓN DE ÓRDENES DE COMPRA ---")
        try:
            cantidad = self.empresa.recibir_compras()
            if cantidad > 0:
                print(f"\n-> ÉXITO: Se ingresaron {cantidad} órdenes al inventario.")
                print("-> AVISO: Podés volver a presionar '6' para que las solicitudes demoradas retomen su curso.")
                
                self.empresa.guardar_inventario()
            else:
                print("No hay órdenes de compra en tránsito para recibir.")
        except ValueError as e:
            print(f"Error con los datos de las órdenes de compra: {e}")
        except IndexError:
            print("Error: Se intentó procesar una cola de compras que ya estaba vacía.")
        except OSError as e:
            print(f"Error al intentar actualizar el archivo de inventario: {e}")