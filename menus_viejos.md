#--------------- lo viejo, no lo borro por las dudas ---------------


menu admin

    def crear_insumo(self):
       print("\n--- REGISTRO DE INSUMO BÁSICO ---")
       try:
            nombre = input("Nombre del insumo: ").strip()
            costo = float(input("Costo unitario: $"))
            
            # El ID se genera solo en la clase Elemento
            insumo = InsumoBasico(nombre, costo)
            id_insumo = insumo.get_id()
            
            if self.empresa.registrar_producto_nuevo(insumo):
                self.insumos[id_insumo] = insumo
                print(f"CONFIRMACIÓN: Insumo '{nombre}' registrado con ID: {id_insumo}")
                
        except ValueError as e:
            print(f"ERROR: Datos inválidos. {e}")
        
    def crear_producto(self):
            print("\n--- REGISTRO DE PRODUCTO FABRICADO ---")
            if not self.unidades or not self.insumos:
                return print(" [!] ERROR: Faltan unidades o insumos para crear un producto.")

            if not self.empresa._catalogo_tareas or not self.empresa._catalogo_habilidades:
                return print(" [!] ERROR: Cargue los catálogos de tareas y habilidades (opciones 12 y 13) primero.")

            try:
                nombre = input("Nombre del producto: ").strip()
                
                # --- RECETA BOM ---
                print("\nInsumos disponibles:")
                for id_ins, ins in self.insumos.items():
                    print(f"  ID {id_ins}: {ins.get_nombre()}")
                
                bom_dict = {}
                while True:
                    entrada = input("\nIngrese ID del insumo (o '0' para finalizar receta): ")
                    if entrada == "0": break
                    id_i = int(entrada)
                    if id_i in self.insumos:
                        cant = int(input(f"Cantidad de '{self.insumos[id_i].get_nombre()}': "))
                        bom_dict[self.insumos[id_i]] = cant
                    else: print("ID no encontrado.")
                
                if not bom_dict: return print("CANCELADO: Requiere materiales.")
                bom = ItemBOM(f"Receta {nombre}", bom_dict)
                
                # --- TAREAS ---
                print("\n--- ASIGNACIÓN DE TAREAS ---")
                tareas_producto = ListaEnlazadaTareas()
                while True:
                    if input("¿Desea agregar una Tarea? (S/N): ").strip().upper() != 'S': break

                    print("\nTipos de Tareas Maestras:")
                    for id_tarea, datos_tarea in self.empresa._catalogo_tareas.items():
                        print(f"  ID {id_tarea}: {datos_tarea['nombre']} (Mesa: #{datos_tarea['id_unidad']} | Hab: #{datos_tarea['id_habilidad']})")
                    id_t_maestra = int(input("ID de tarea maestra a usar: "))
                    
                    if id_t_maestra not in self.empresa._catalogo_tareas:
                        print(" [!] ERROR: ID de tarea no existe.")
                        continue

                    datos_maestros = self.empresa._catalogo_tareas[id_t_maestra]
                    id_unidad = datos_maestros["id_unidad"]
                    id_hab = datos_maestros["id_habilidad"]

                    cant_colabs = int(input("Cantidad de operarios para esta receta: "))
                    tiempo = float(input("Tiempo (hs/unidad): "))

                    aptos = [colaborador for colaborador in self.colaboradores.values() if colaborador.tiene_habilidad(id_hab)]
                    costo_mo = (sum(colaborador.get_salario_hora() for colaborador in aptos) / len(aptos)) if aptos else 0.0

                    nueva_tarea = Tarea(id_t_maestra, self.unidades[id_unidad], cant_colabs, tiempo, id_hab, costo_mo)
                    tareas_producto.agregar_al_final(nueva_tarea)
                    print("-> Tarea añadida a la receta.")

                if not tareas_producto.cabecera: return print("ERROR: No se puede fabricar sin tareas.")

                producto = ArticuloFabricadoInternamente(nombre, [bom], tareas_producto)
                if self.empresa.registrar_producto_nuevo(producto):
                    self.productos[producto.get_id()] = producto
                    print(f"\nCONFIRMACIÓN: Producto '{nombre}' (ID: {producto.get_id()}) registrado.")
                    
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
            if not self.empresa._catalogo_habilidades:
                print(" [!] ERROR: No hay habilidades en el catálogo maestro. Cargue una con la opción 12.")
                return
            print("\nCatálogo de Habilidades Disponibles:")
            for id_h, nom in self.empresa._catalogo_habilidades.items():
                print(f"  ID {id_h}: {nom}")
            try:
                entrada = input("\nIngrese los IDs de las habilidades (separados por coma): ").split(",")
                habilidades_ids = []
                for id_texto in entrada:
                    id_texto = id_texto.strip()
                    if id_texto.isdigit() and int(id_texto) in self.empresa._catalogo_habilidades:
                        habilidades_ids.append(int(id_texto))
                if not habilidades_ids:
                    return print(" [!] ERROR: Debe ingresar IDs válidos.")
                
                horas = float(input("Horas de disponibilidad: "))
                salario = float(input("Salario por hora: $"))
                colab = Colaborador(habilidades_ids, horas, salario)
                id_c = colab.get_id()
                self.colaboradores[id_c] = colab
                self.empresa.agregar_colaborador(colab)
                nombres_h = [self.empresa._catalogo_habilidades[hid] for hid in habilidades_ids]
                print(f"CONFIRMACIÓN: Colaborador {id_c} registrado con habilidades: {nombres_h}")
                
            except ValueError as e:
                print(f"ERROR: Datos inválidos. {e}")

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

    def cargar_demo(self):
        print("\n--- CARGANDO DEMO INDUSTRIAL ---")
        
        # 1. Creamos Habilidad Maestra
        id_hab_armado = self.empresa.agregar_habilidad("Armado General")
        
        # 2. Creamos Unidad de Trabajo
        ensambladora = UnidadDeTrabajo("Mesa de Ensamblaje", 80.0, 500.0)
        self.unidades[ensambladora.get_id()] = ensambladora
        self.empresa.agregar_unidad_trabajo(ensambladora)
        
        # 3. Creamos Tareas Maestras (ahora vinculan Máquina y Habilidad)
        id_tarea_ensamble = self.empresa.agregar_tarea_maestra("Ensamblaje Manual", ensambladora.get_id(), id_hab_armado)
        id_tarea_corte = self.empresa.agregar_tarea_maestra("Corte de Madera", ensambladora.get_id(), id_hab_armado)
        
        # 4. Insumos y Stock
        madera = InsumoBasico("Tablón de Madera", 5000.0)
        tornillos = InsumoBasico("Tornillos 10mm", 5.0)
        for insumo in [madera, tornillos]:
            if self.empresa.registrar_producto_nuevo(insumo):
                self.insumos[insumo.get_id()] = insumo
                self.empresa._inventario.ingresar_stock(insumo, 1000)
        
        # 5. Colaborador
        carpintero = Colaborador([id_hab_armado], 40.0, 2500.0)
        self.colaboradores[carpintero.get_id()] = carpintero
        self.empresa.agregar_colaborador(carpintero)

        # 6. Definición de Productos
        # --- PATA DE MESA ---
        tarea_pata = Tarea(id_tarea_corte, ensambladora, 1, 0.5, id_hab_armado, 1000.0)
        bom_pata = ItemBOM("Receta Pata", {madera: 1, tornillos: 4})
        
        lista_pata = ListaEnlazadaTareas()
        lista_pata.agregar_al_final(tarea_pata)
        pata = ArticuloFabricadoInternamente("Pata de Mesa", [bom_pata], lista_pata)
        if self.empresa.registrar_producto_nuevo(pata):
            self.productos[pata.get_id()] = pata

        # --- MESA COMPLETA ---
        tarea_mesa = Tarea(id_tarea_ensamble, ensambladora, 1, 1.5, id_hab_armado, 2500.0)
        bom_mesa = ItemBOM("Receta Mesa", {madera: 1, pata: 4})
        
        lista_mesa = ListaEnlazadaTareas()
        lista_mesa.agregar_al_final(tarea_mesa)
        mesa = ArticuloFabricadoInternamente("Mesa Completa", [bom_mesa], lista_mesa)
        if self.empresa.registrar_producto_nuevo(mesa):
            self.productos[mesa.get_id()] = mesa
        
        print("\n-> [ÉXITO] Demo cargada con éxito")

    def crear_tarea_maestra(self):
            print("\n--- NUEVA TAREA MAESTRA ---")
            if not self.unidades or not self.empresa._catalogo_habilidades:
                return print("ERROR: Debe cargar al menos una Unidad y una Habilidad primero.")
                
            nombre = input("Nombre del Tipo de Tarea: ")
            
            print("\nUnidades Disponibles:")
            for uid, u in self.unidades.items(): print(f"  ID {uid}: {u.get_nombre()}")
            id_u = int(input("ID de la Unidad asociada: "))
            
            print("\nHabilidades Disponibles:")
            for hid, hnom in self.empresa._catalogo_habilidades.items(): print(f"  ID {hid}: {hnom}")
            id_h = int(input("ID de la Habilidad requerida: "))
            
            if id_u in self.unidades and id_h in self.empresa._catalogo_habilidades:
                self.empresa.agregar_tarea_maestra(nombre, id_u, id_h)
                print("CONFIRMACIÓN: Tarea Maestra creada exitosamente.")
            else:
                print("ERROR: IDs no válidos.")
                
                
                
    ----menu produccion--
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
            for id_producto, producto in self.productos.items():
                print(f"  ID {id_producto}: {producto.get_nombre()}")
            
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



menu principal

import csv
from empresa import Empresa
from menu_admin import MenuAdministrativo
from menu_prod import MenuProduccion
from inventario import Inventario
from articulo_fabricado import ArticuloFabricadoInternamente
from insumo_basico import InsumoBasico
class MenuPrincipal:
    def __init__(self):
        mi_inventario = Inventario()
        self.empresa = Empresa(mi_inventario)
        
        self.dicc_insumos = {}
        self.dicc_productos = {}
        self.dicc_unidades = {}
        self.dicc_colaboradores = {}
        

        for elem in self.empresa._catalogo_elementos:
            if isinstance(elem, ArticuloFabricadoInternamente):
                self.dicc_productos[elem.get_id()] = elem
            elif isinstance(elem, InsumoBasico):
                self.dicc_insumos[elem.get_id()] = elem
                
        
        for unidad in self.empresa._unidades:
            self.dicc_unidades[unidad.get_id()] = unidad

        for id_colaborador, colaborador in self.empresa._colaboradores.items():
            self.dicc_colaboradores[id_colaborador] = colaborador
        
        
        self.menu_admin = MenuAdministrativo(
            self.empresa, self.dicc_insumos, self.dicc_productos, 
            self.dicc_unidades, self.dicc_colaboradores
        )
        self.menu_prod = MenuProduccion(
            self.empresa, self.dicc_insumos, self.dicc_productos, 
            self.dicc_unidades, self.dicc_colaboradores
        )
        
        self.id_actual = None
        self.rol_actual = None

    def _leer_usuarios(self) -> dict:
        usuarios = {}
        try:
            with open("usuarios.csv", "r", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    usuarios[fila["id"].strip()] = {
                        "clave": fila["clave"].strip(),
                        "rol": fila["rol"].strip()
                    }
        except FileNotFoundError:
            print("Archivo usuarios.csv no encontrado. Creá el archivo para continuar.")
        return usuarios

    def iniciar_sesion(self) -> bool:
        usuarios_registrados = self._leer_usuarios()
        if not usuarios_registrados: 
            return False

        print("\n" + "="*40)
        print("INICIO DE SESIÓN - SISTEMA TECNOMECÁNICA ITBA ")
        print("="*40)
        
        intentos_maximos = 3
        intentos_realizados = 0
        
        while intentos_realizados < intentos_maximos:
            if intentos_realizados > 0:
                print(f"\nTe quedan {intentos_maximos - intentos_realizados} intento/s.")
                
            id_ingresado = input("Ingrese su ID de Empleado: ").strip()
            clave_ingresada = input("Contraseña: ").strip()
        
            if id_ingresado not in usuarios_registrados:
                print("Usuario incorrecto.")
                intentos_realizados += 1
                
            elif usuarios_registrados[id_ingresado]["clave"] != clave_ingresada:
                print("Contraseña incorrecta.")
                intentos_realizados += 1
            
            else:
                self.id_actual = id_ingresado
                self.rol_actual = usuarios_registrados[id_ingresado]["rol"]
                print(f"\nSesión iniciada. Acceso concedido al rol: {self.rol_actual.upper()}")
                return True
                
        print("\n Se ha superado la cantidad de intentos permitidos.")
        return False

    def ejecutar(self):
        if not self.iniciar_sesion():
            print("Apagando el sistema...")
            return 

        if self.rol_actual == "admin":
            menu_activo = self.menu_admin
        elif self.rol_actual == "prod":
            menu_activo = self.menu_prod
        else:
            print("Rol desconocido. Cerrando sesión.")
            return

        try:
            continuar = True
            while continuar:
                menu_activo.mostrar_opciones()
                opcion = input("\nSeleccione una opción: ").strip()
                continuar = menu_activo.ejecutar_opcion(opcion)
                
        except KeyboardInterrupt:
            print("\n\n[!] Programa interrumpido por el usuario (Ctrl+C).")
        except Exception as e:
            print(f"\n[!] Error crítico en el sistema: {e}")
        finally:
            print(f"\nSesión cerrada correctamente para el empleado ID: {self.id_actual}.")