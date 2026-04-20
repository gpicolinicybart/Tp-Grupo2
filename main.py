from empresa import Empresa 
from inventario import Inventario
from compra_insumo import Compra_Insumo
from solicitud_fabricacion import SolicitudDeFabricacion
from insumo_basico import InsumoBasico
from colaboradores import Colaborador
from unidad_de_trabajo import UnidadDeTrabajo
from tarea import Tarea
from itembom import ItemBOM
from articulo_fabricado import ArticuloFabricadoInternamente

class SistemaGestion:
    def __init__(self):
        self.empresa = Empresa(Inventario())
        self.insumos = {}
        self.productos = {}
        self.unidades = {}
        self.colaboradores = {}

        
    def mostrar_menu_principal(self):
        print("\n" + "="*60)
        print("     SISTEMA DE GESTIÓN DE MANUFACTURA - MENÚ PRINCIPAL")
        print("="*60)
        print("1. Crear Insumo Básico")
        print("2. Crear Producto (Artículo Fabricado)")
        print("3. Agregar Unidad de Trabajo (Máquina)")
        print("4. Agregar Colaborador (Personal)")
        print("5. Crear Solicitud de Fabricación")
        print("6. Procesar Solicitudes (Planificación)")
        print("7. Ejecutar Solicitud (Producción)")
        print("8. Finalizar Solicitud (Cierre)")
        print("9. Ver Estado General del Sistema")
        print("10. Cargar Escenario de Prueba (Demo)")
        print("11. Dar de baja a un Colaborador")
        print("0. Salir")
        print("="*60)

    def crear_insumo(self):
        print("\n--- REGISTRO DE INSUMO BÁSICO ---")
        try:
            nombre = input("Nombre del insumo: ").strip()
            costo = float(input("Costo unitario: $"))
            
            # El ID se genera solo en la clase Elemento
            insumo = InsumoBasico(nombre, costo)
            id_insumo = insumo.get_id()
            
            self.insumos[id_insumo] = insumo
            self.empresa.registrar_producto_nuevo(insumo)
            print(f"CONFIRMACIÓN: Insumo '{nombre}' registrado con ID: {id_insumo}")
        except ValueError as e:
            print(f"ERROR: Datos inválidos. {e}")

    def crear_producto(self):
        print("\n--- REGISTRO DE PRODUCTO FABRICADO ---")
        if not self.insumos:
            print("AVISO: Debe registrar insumos antes de crear un producto.")
            return
        
        try:
            nombre = input("Nombre del producto: ").strip()
            
            print("\nInsumos disponibles para la receta (BOM):")
            for id_ins, ins in self.insumos.items():
                print(f"  ID {id_ins}: {ins.get_nombre()}")
            
            bom_dict = {}
            while True:
                entrada = input("\nIngrese ID del insumo (o '0' para finalizar): ")
                if entrada == "0": break
                
                id_ins = int(entrada)
                if id_ins in self.insumos:
                    cantidad = int(input(f"Cantidad de '{self.insumos[id_ins].get_nombre()}': "))
                    bom_dict[self.insumos[id_ins]] = cantidad
                else:
                    print("ID no encontrado en el catálogo.")
            
            if not bom_dict:
                print("ERROR: Un producto requiere al menos un componente.")
                return

           
            bom = ItemBOM(f"Receta {nombre}", bom_dict)
            
            # El ID se genera solo en la clase Elemento
            producto = ArticuloFabricadoInternamente(nombre, [bom], [])
            id_producto = producto.get_id()
            
            self.productos[id_producto] = producto
            self.empresa.registrar_producto_nuevo(producto)
            print(f"CONFIRMACIÓN: Producto '{nombre}' registrado con ID: {id_producto}")
        except ValueError as e:
            print(f"ERROR: {e}")

    def agregar_unidad_trabajo(self):
        print("\n--- REGISTRO DE UNIDAD DE TRABAJO ---")
        try:
        
            nombre = input("Descripción de la unidad (ej. Prensa): ").strip()
            capacidad = float(input("Capacidad máxima de horas: "))
            costo = float(input("Costo operativo por hora: $"))
            
            unidad = UnidadDeTrabajo(nombre, capacidad, costo)
            id_asignado=unidad.get_id()
            self.unidades[id_asignado] = unidad
            self.empresa.agregar_unidad_trabajo(unidad)
            print(f"CONFIRMACIÓN: Unidad '{nombre}' registrada exitosamente con ID: {id_asignado}")
        except ValueError as e:
            print(f"ERROR: {e}")

    def agregar_colaborador(self):
        print("\n--- REGISTRO DE COLABORADOR ---")
        try:
        
            habilidades = input("Habilidades (separadas por coma): ").split(",")
            habilidades = [h.strip() for h in habilidades]
            horas = float(input("Horas de disponibilidad: "))
            salario = float(input("Salario por hora: $"))
            
            colab = Colaborador(habilidades, horas, salario)
            id_c=colab.get_id()
            self.empresa.agregar_colaborador(colab)

            print(f"CONFIRMACIÓN: Colaborador {id_c} agregado a la nómina.")
        except ValueError as e:
            print(f"ERROR: {e}")

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
        except ValueError as e:
            print(f"ERROR: {e}")

    def procesar_solicitud(self):
        self.empresa.procesar_solicitud()

    def ejecutar_solicitud(self):
        self.empresa.ejecutar_solicitud()
   

    def finalizar_solicitud(self):
        self.empresa.finalizar_solicitud()

    def ver_estado(self):
        print("\n" + "="*60)
        print("               ESTADO ACTUAL DEL SISTEMA")
        print("="*60)
        
        print(f"\nCATÁLOGO DE INSUMOS: {len(self.insumos)}")
        for id_ins, ins in self.insumos.items():
            disponible = self.empresa._inventario.obtener_stock_disponible(ins)
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

    def dar_baja_colaborador(self):
        print("\n--- BAJA DE PERSONAL ---")
        if not self.colaboradores:
            print("No hay colaboradores registrados.")
            return
            
        try:
            id_baja = int(input("Ingrese el ID del colaborador a dar de baja: "))
            if id_baja in self.colaboradores:
                colab = self.colaboradores[id_baja]
                
                colab.dar_de_baja()
                print(f"\n[ÉXITO] El colaborador {id_baja} ha sido dado de baja correctamente.")
                print(colab) 
            else:
                print("ID no encontrado.")
        except ValueError:
            print("ERROR: Debe ingresar un número entero válido.")

    def cargar_demo(self):
        print("\n--- CARGANDO ESCENARIO DEMO E INDUSTRIAL ---")
        
        # 1. Insumos
        acero = InsumoBasico("Plancha de Acero", 500.0)
        tornillos = InsumoBasico("Tornillo 10mm", 5.0)

        self.insumos[acero.get_id()] = acero
        self.insumos[tornillos.get_id()] = tornillos

        self.empresa.registrar_producto_nuevo(acero)
        self.empresa.registrar_producto_nuevo(tornillos)
        
        # 2. Carga inicial de Stock
        self.empresa._inventario.ingresar_stock(acero, 50)
        self.empresa._inventario.ingresar_stock(tornillos, 200)
        
        # 3. Unidad y Colaborador
        prensa = UnidadDeTrabajo("Prensa Hidráulica", 40.0, 1500.0)
        self.unidades[prensa.get_id()] = prensa
        self.empresa.agregar_unidad_trabajo(prensa)
        
        operario = Colaborador(["Soldadura", "Montaje"], 40.0, 1200.0)
        self.colaboradores[operario.get_id()] = operario
        self.empresa.agregar_colaborador(operario)
        
        # 4. Tarea y Producto
        tarea = Tarea("Ensamblaje Estructural", prensa, 1, 2.5, "Montaje", 1000.0)
        bom = ItemBOM("BOM Mesa", {acero: 1, tornillos: 4})
        mesa = ArticuloFabricadoInternamente("Mesa Industrial", [bom], [tarea])
        
        self.productos[mesa.get_id()] = mesa
        self.empresa.registrar_producto_nuevo(mesa)
        
        print("CONFIRMACIÓN: Escenario demo cargado exitosamente.")

if __name__ == "__main__":
    try:
        sistema = SistemaGestion()
        
        while True:
            sistema.mostrar_menu_principal()
            opcion = input("Seleccione una opción: ").strip()
            
            if opcion == "1": sistema.crear_insumo()
            elif opcion == "2": sistema.crear_producto()
            elif opcion == "3": sistema.agregar_unidad_trabajo()
            elif opcion == "4": sistema.agregar_colaborador()
            elif opcion == "5": sistema.crear_solicitud()
            elif opcion == "6": sistema.procesar_solicitud()
            elif opcion == "7": sistema.ejecutar_solicitud()
            elif opcion == "8": sistema.finalizar_solicitud()
            elif opcion == "9": sistema.ver_estado()
            elif opcion == "10": sistema.cargar_demo()
            elif opcion == "11": sistema.dar_baja_colaborador()
            elif opcion == "0":
                print("\nCerrando sistema de gestión manufacturera. Hasta luego.")
                break
            else:
                print("Opción no válida.")
                
    except KeyboardInterrupt:
        print("\n\n[!] Programa interrumpido por el usuario (Ctrl+C).")
    except Exception as e:
        print(f"\n[!] Error crítico en el sistema: {e}")