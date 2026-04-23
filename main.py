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
import os
import csv

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
        print("3. Agregar Unidad de Trabajo (Sector/Taller/Máquina)")
        print("4. Agregar Colaborador (Personal)")
        print("5. Crear Solicitud de Fabricación")
        print("6. Procesar Solicitudes (Planificación)")
        print("7. Ejecutar Solicitud (Producción)")
        print("8. Finalizar Solicitud (Cierre)")
        print("9. Ver Estado General del Sistema")
        print("10. Cargar Escenario de Prueba (Demo)")
        print("11. Dar de baja a un Colaborador")
        print("12. Generar Reporte CSV de Materiales Críticos")
        print("13. Generar Reporte de Planta y Cuellos de Botella")
        print("14. Recibir Órdenes de Compra (Ingresar Stock de Insumos)")
        print("15. Ver Historial de Producción (Auditoría)")
        print("16. Generar Orden de Compra Manual para Insumo")
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
            
            # primero veo que hayan creado unidades e insumos asi no queda uno incompleto que no se puede editar despues
            if not self.unidades:
                print(" [!] ERROR: No se puede crear un producto fabricado si no existen Unidades de Trabajo.")
                print("     Primero registre las máquinas (Opción 3).")
                return
                
            if not self.insumos:
                print(" [!] ERROR: No hay insumos registrados para armar la receta.")
                print("     Primero registre los insumos básicos (Opción 1).")
                return
            
            try:
                nombre = input("Nombre del producto: ").strip()
                
                # insumo basicos
                print("\nInsumos disponibles para la receta (BOM):")
                for id_ins, ins in self.insumos.items():
                    print(f"  ID {id_ins}: {ins.get_nombre()}")
                
                bom_dict = {}
                while True:
                    entrada = input("\nIngrese ID del insumo (o '0' para finalizar receta): ")
                    if entrada == "0": break
                    
                    id_ins = int(entrada)
                    if id_ins in self.insumos:
                        cantidad = int(input(f"Cantidad de '{self.insumos[id_ins].get_nombre()}': "))
                        bom_dict[self.insumos[id_ins]] = cantidad
                    else: print("ID no encontrado.")
                
                if not bom_dict:
                    print(" [!] CANCELADO: Un producto requiere al menos un insumo.")
                    return

                bom = ItemBOM(f"Receta {nombre}", bom_dict)
                
                # tareas, unidad de trab
                print("\n--- ASIGNACIÓN DE TAREAS ---")
                tareas_producto = []
                
                while True:
                    agregar = input("¿Desea agregar una Tarea? (S/N): ").strip().upper()
                    if agregar != 'S': 
                        break
                    
                    desc_tarea = input("Descripción de la Tarea: ")
                    
                    print("\n Unidades de trabajo disponibles:")
                    for id_u, u in self.unidades.items():
                        print(f"  ID {id_u}: {u.get_nombre()}")
                        
                    id_unidad = int(input("Ingrese ID de la unidad de trabajo: "))
                    if id_unidad not in self.unidades:
                        print("ERROR: Unidad de trabajo no encontrada.")
                        continue
                    
                    habilidad = input("Habilidad requerida: ").strip()
                    empleados_aptos = [c for c in self.colaboradores.values() if c.tiene_habilidad(habilidad)]
                    
                    if empleados_aptos:
                        suma_sueldos = sum(c.get_salario_hora() for c in empleados_aptos)
                        costo_mo = suma_sueldos / len(empleados_aptos)
                        cant_colabs = int(input("Cantidad de operarios: "))
                        tiempo = float(input("Tiempo (hs/unidad): "))
                        nueva_tarea = Tarea(desc_tarea, self.unidades[id_unidad], cant_colabs, tiempo, habilidad, costo_mo)
                        tareas_producto.append(nueva_tarea)
                        print("-> Tarea añadida.")
                    else:
                        print(f" [!] ERROR: No hay personal con habilidad '{habilidad}'. Tarea descartada.")

                #¿Se cargó al menos una tarea? x lo mismo que antes, si dice que no requiere nignuna tarea tiene q tirar error 
                if not tareas_producto:
                    print(f" [!] ERROR CRÍTICO: No se puede registrar '{nombre}' sin un proceso de manufactura.")
                    print("     El registro ha sido abortado para evitar errores en la producción.")
                    return

                # Si pasó todos los filtros, recién ahí lo creamos
                producto = ArticuloFabricadoInternamente(nombre, [bom], tareas_producto)
                self.productos[producto.get_id()] = producto
                self.empresa.registrar_producto_nuevo(producto)
                print(f"\nCONFIRMACIÓN: Producto '{nombre}' (ID: {producto.get_id()}) registrado con éxito.")
                
            except ValueError as e:
                print(f"ERROR: Datos inválidos. {e}")
            
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
                self.colaboradores[id_c] = colab # anoto el colaborador en el diccionario del menu
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
    
    def recibir_compras_pendientes(self):
        print("\n--- RECEPCIÓN DE ÓRDENES DE COMPRA ---")
        cantidad = self.empresa.recibir_compras()
        if cantidad > 0:
            print(f"\n-> ÉXITO: Se ingresaron {cantidad} órdenes al inventario.")
            print("-> AVISO: Podés volver a presionar '6' para que las solicitudes demoradas retomen su curso.")
        else:
            print("No hay órdenes de compra en tránsito para recibir.")

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
        
        print("\nColaboradores Activos:")
        hay_activos = False
        for id_col, colab in self.colaboradores.items():
            if colab.get_fecha_baja() is None:
                print(f"  ID {id_col}: {colab}")
                hay_activos = True

        if not hay_activos:
            print("No hay colaboradores activos en este momento.")
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

    def ver_historial_produccion(self):            
            print("\n" + "="*70)
            print("              HISTORIAL DE PRODUCCIÓN TERMINADA")
            print("="*70)
            
            nombre_archivo = "historial_solicitudes.csv"
            if not os.path.isfile(nombre_archivo):
                print("Todavía no hay un historial. Finalizá alguna solicitud primero.")
                return
            try:
                with open(nombre_archivo, mode='r', encoding='utf-8') as archivo:
                    lector = csv.reader(archivo)
                    encabezados = next(lector) # primera fila (títulos)
                    # los títulos los pongo con un formato espaciado para que parezca una tabla
                    print(f"{encabezados[0]:<15} | {encabezados[1]:<20} | {encabezados[2]:<8} | {encabezados[5]:<15}")
                    print("-" * 70)
                    filas = 0
                    for fila in lector:
                        # Fila 0=ID, Fila 1=Producto, Fila 2=Cantidad, Fila 5=Tiempo
                        print(f"#{fila[0]:<14} | {fila[1]:<20} | {fila[2]:<8} | {fila[5]:<15} hs")
                        filas += 1
                    print("-" * 70)
                    print(f"Total de registros históricos: {filas}")
            except Exception as e:
                print(f"-> [ERROR] No se pudo leer el archivo: {e}")

    def generar_reporte_criticos(self):
        print("\n--- REPORTE DE MATERIALES CRÍTICOS ---")
        if not self.productos:
            return print("No hay productos registrados.")
        
        print("\nCatálogo de Productos:")
        for id_prod, producto in self.productos.items():
            print(f"  - ID: {id_prod} | {producto.get_nombre()}")   
        try:
            id_p = int(input("Ingrese el ID del producto a evaluar: "))
            if id_p not in self.productos: return print("Error: ID no encontrado.")
            
            cantidad = int(input("Ingrese la cantidad a simular: "))
            if cantidad <= 0: 
                return print("Error: La cantidad debe ser positiva.")
            
            self.empresa.generar_reporte_materiales_criticos(self.productos[id_p], cantidad)

        except ValueError:
            print("ERROR: Ingrese números enteros válidos.")

    def emitir_reporte_y_sobrecarga(self):
        lista_unidades = list(self.unidades.values())
        self.empresa.generar_reporte_estado_planta(lista_unidades)
        
        print("\n¿Desea calcular la sobrecarga para un pedido específico?")
        if input("Ingrese 'S' para calcular o 'N' para salir: ").strip().upper() == 'S':
            if not self.unidades or not self.productos:
                return print("Faltan datos base para el cálculo.")
            
            print("\nUnidades de Trabajo Disponibles:")
            for id_u, unidad in self.unidades.items():
                print(f"  - ID: {id_u} | {unidad.get_nombre()}")
                
            print("\nProductos Disponibles:")
            for id_p, producto in self.productos.items():
                print(f"  - ID: {id_p} | {producto.get_nombre()}") 
                
            try:
                id_u = int(input("\nIngrese el ID de la Unidad de Trabajo: "))
                id_p = int(input("Ingrese el ID del Producto: "))
                
                if id_u in self.unidades and id_p in self.productos:
                    cant = int(input("Cantidad a fabricar: "))
                    if cant > 0:
                        self.empresa.calcular_sobrecarga_unidad_trabajo(self.unidades[id_u], self.productos[id_p], cant)
                    else:
                        print("La cantidad debe ser mayor a 0.")
                else:
                    print("IDs no encontrados.")
            except ValueError:
                print("Error: Ingrese números enteros válidos.")

    def comprar_insumos_manual(self):
        print("\n=== GENERADOR DE ÓRDENES DE COMPRA MANUAL ===")
        if not self.insumos:
            return print("ERROR: No hay insumos registrados en el sistema.")

        print("\nCatálogo de Insumos Básicos y Stock Disponible:")
        for id_ins, ins in self.insumos.items():
            stock_actual = self.empresa._inventario.obtener_stock_disponible(ins)
            print(f"  - ID: {id_ins} | {ins.get_nombre()} | Stock: {stock_actual} unid.")

        try:
            id_insumo = int(input("\nIngrese el ID del Insumo a reponer: "))
            
            if id_insumo in self.insumos:
                cantidad = int(input("Ingrese la cantidad que desea comprar: "))
                if cantidad > 0:
                    insumo_seleccionado = self.insumos[id_insumo]
                    
                    insumo_seleccionado.gestionar_reabastecimiento(self.empresa, cantidad)
                    
                    print("\n-> AVISO: El pedido se encuentra en tránsito.")
                    print("-> Recuerde usar la Opción 14 cuando el camión llegue a la fábrica para ingresar el stock físico.")
                else:
                    print("ERROR: La cantidad a comprar debe ser mayor a 0.")
            else:
                print("ERROR: El ID ingresado no corresponde a ningún insumo básico de la lista.")
        except ValueError:
            print("ERROR: Por favor ingrese números enteros válidos.")

    def cargar_demo(self):
        print("\n--- CARGANDO DEMO INDUSTRIAL ---")
        
        # 1.  insumos basicos
        madera = InsumoBasico("Tablón de Madera", 5000.0)
        tornillos = InsumoBasico("Tornillos 10mm", 5.0)

        for insumo in [madera, tornillos]:
            self.insumos[insumo.get_id()] = insumo
            self.empresa.registrar_producto_nuevo(insumo)
            self.empresa._inventario.ingresar_stock(insumo, 1000)
        
        # 2. unidades de trabajo y personal
        ensambladora = UnidadDeTrabajo("Mesa de Ensamblaje", 80.0, 500.0)
        self.unidades[ensambladora.get_id()] = ensambladora
        self.empresa.agregar_unidad_trabajo(ensambladora)
        
        carpintero = Colaborador(["Armado"], 40.0, 2500.0)
        self.colaboradores[carpintero.get_id()] = carpintero
        self.empresa.agregar_colaborador(carpintero)

        #mostramos la recursividad de manera simple: el producto final requiere un sub-ensamble 
        # que a su vez requiere insumos básicos. El sistema va a poder calcular automáticamente 
        # los materiales necesarios para fabricar la mesa completa, multiplicando por 4 las patas
        #  y sumando los materiales de cada una. Además, al generar el reporte de materiales críticos,
        #  va a detectar si falta stock de alguno de los componentes, incluso si es un sub-ensamble.

        tarea_pata = Tarea("Armado de Pata", ensambladora, 1, 0.5, "Armado", 1000.0)
        bom_pata = ItemBOM("Receta Pata", {madera: 1, tornillos: 4})
        
        #sub-ensamble simple
        pata = ArticuloFabricadoInternamente("Pata de Mesa", [bom_pata], [tarea_pata])
        self.productos[pata.get_id()] = pata
        self.empresa.registrar_producto_nuevo(pata)

        #producto final que requiere el sub-ensamble
        tarea_mesa = Tarea("Ensamblaje Final Mesa", ensambladora, 1, 1.5, "Armado", 2500.0)
        bom_mesa = ItemBOM("Receta Mesa", {madera: 1, pata: 4})  
        
        mesa = ArticuloFabricadoInternamente("Mesa Completa", [bom_mesa], [tarea_mesa])
        self.productos[mesa.get_id()] = mesa
        self.empresa.registrar_producto_nuevo(mesa)
        
        print("\n-> [ÉXITO] Demo cargada con éxito.")


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
            elif opcion == "12": sistema.generar_reporte_criticos()
            elif opcion == "13": sistema.emitir_reporte_y_sobrecarga()
            elif opcion == "14": sistema.recibir_compras_pendientes()
            elif opcion == "15": sistema.ver_historial_produccion()
            elif opcion == "16": sistema.comprar_insumos_manual()
            elif opcion == "0":
                print("\nCerrando sistema de gestión manufacturera. Hasta luego.")
                break
            else:
                print("Opción no válida.")
                
    except KeyboardInterrupt:
        print("\n\n[!] Programa interrumpido por el usuario (Ctrl+C).")
    except Exception as e:
        print(f"\n[!] Error crítico en el sistema: {e}")