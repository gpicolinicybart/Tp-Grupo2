from collections import deque
from menu_base import MenuBase

class MenuAdministrativo(MenuBase):
    def __init__(self, empresa):
        super().__init__(empresa)

    def mostrar_opciones(self):
        print("\n" + "="*60)
        print("  MENÚ ADMINISTRATIVO  ")
        print("="*60)
        print("1. Crear Insumo Básico")
        print("2. Crear Producto (Artículo Fabricado)")
        print("3. Agregar Unidad de Trabajo (Sector/Taller/Máquina)")
        print("4. Agregar Colaborador (Personal)")
        print("5. Dar de baja a un Colaborador")
        print("6. Generar Orden de Compra Manual para Insumo")
        print("7. Generar Reporte CSV de Materiales Críticos")
        print("8. Generar Reporte de Planta y Cuellos de Botella")
        print("9. Ver Historial de Producción (Auditoría)")
        print("10. Ver Estado General del Sistema")
        print("11. Cargar Escenario de Prueba (Demo)")
        print("12. Agregar Nueva Habilidad al Catálogo")
        print("13. Agregar Nueva Tarea al Catálogo")
        print("14. Agregar Nuevo Usuario")
        print("0. Cerrar Sesión")
        print("="*60)

    def ejecutar_opcion(self, opcion: str) -> bool:

                if opcion == "1": self.crear_insumo()
                elif opcion == "2": self.crear_producto()    
                elif opcion == "3": self.agregar_unidad_trabajo()  
                elif opcion == "4": self.agregar_colaborador()  
                elif opcion == "5": self.dar_baja_colaborador()  
                elif opcion == "6": self.comprar_insumos_manual()  
                elif opcion == "7": self.generar_reporte_criticos()  
                elif opcion == "8": self.emitir_reporte_y_sobrecarga()   
                elif opcion == "9": self.ver_historial_produccion()  
                elif opcion == "10": self.ver_estado()
                elif opcion == "11": self.cargar_demo()
                elif opcion == "12": self.empresa.agregar_habilidad(input("Nombre de la nueva Habilidad: "))
                elif opcion == "13": self.crear_tarea_maestra()
                elif opcion == "14": self.agregar_usuario()
                elif opcion == "0":
                    print("\nCerrando sistema de gestion administrativa. Hasta luego.")
                    return False
                else:
                    print("Opción no válida.")
                return True
                    

    def crear_insumo(self):
        print("\n--- REGISTRO DE INSUMO BÁSICO ---")
        try:
            nombre = input("Nombre del insumo: ").strip()
            costo = float(input("Costo unitario: $"))
            insumo = self.empresa.crear_insumo_basico(nombre, costo)
            print(f"CONFIRMACIÓN: Insumo '{nombre}' registrado con ID: {insumo.get_id()}")
        except ValueError as e:
            print(f"ERROR: Datos inválidos.")

    def crear_producto(self):
        print("\n--- REGISTRO DE PRODUCTO FABRICADO ---")
        insumos = self.empresa.obtener_diccionario_insumos()
        unidades = self.empresa.obtener_diccionario_unidades()

        if not unidades or not insumos:
            return print(" [!] ERROR: Faltan unidades o insumos base.")
        if not self.empresa.obtener_catalogo_tareas() or not self.empresa.obtener_catalogo_habilidades():
            return print(" [!] ERROR: Cargue catálogos de tareas y habilidades primero.")

        try:
            nombre = input("Nombre del producto: ").strip()
            
            #receta bom
            print("\nInsumos disponibles:")
            for id_ins, ins in insumos.items():
                print(f"  ID {id_ins}: {ins.get_nombre()}")
            
            dict_bom_cantidades = {} 
            while True:
                entrada = input("\nIngrese ID del insumo (o '0' para finalizar receta): ")
                if entrada == "0": 
                    break
                id_i = int(entrada)
                if id_i in insumos:
                    cant = int(input(f"Cantidad de '{insumos[id_i].get_nombre()}': "))
                    dict_bom_cantidades[id_i] = cant
                else: 
                    print("ID no encontrado.")
            
            if not dict_bom_cantidades: 
                return print("CANCELADO: Requiere materiales.")

            # tareas
            print("\n--- ASIGNACIÓN DE TAREAS ---")
            lista_datos_tareas = [] 
            while True:
                if input("¿Desea agregar una Tarea? (S/N): ").strip().upper() != 'S':
                    break

                print("\nTipos de Tareas Maestras:")
                for id_tarea, datos_tarea in self.empresa.obtener_catalogo_tareas().items():
                    print(f"  ID {id_tarea}: {datos_tarea['nombre']} (Máquina: #{datos_tarea['id_unidad']} | Hab: #{datos_tarea['id_habilidad']})")
                
                id_t_maestra = int(input("ID de tarea maestra a usar: "))
                if id_t_maestra not in self.empresa.obtener_catalogo_tareas():
                    print(" [!] ERROR: ID de tarea no existe.")
                    continue

                cant_colabs = int(input("Cantidad de operarios para esta tarea: "))
                tiempo = float(input("Tiempo (hs/unidad): "))
                
                lista_datos_tareas.append({
                    'id_maestra': id_t_maestra, 
                    'cant_colabs': cant_colabs, 
                    'tiempo': tiempo
                })
                print("-> Tarea añadida a la hoja de ruta.")

            #la empresa crea todo
            producto = self.empresa.crear_producto_completo(nombre, dict_bom_cantidades, lista_datos_tareas)
            print(f"\n CONFIRMACIÓN: Producto '{nombre}' (ID: {producto.get_id()}) registrado.")
                
        except ValueError as e:
            print(f"ERROR: Ingresó texto donde se esperaba un número o viceversa.")

    def agregar_unidad_trabajo(self):
        print("\n--- REGISTRO DE UNIDAD DE TRABAJO ---")
        try:
            nombre = input("Descripción de la unidad: ").strip()
            capacidad = float(input("Capacidad máxima de horas: "))
            costo = float(input("Costo operativo por hora: $"))
            
            unidad = self.empresa.crear_unidad_trabajo(nombre, capacidad, costo)
            print(f"CONFIRMACIÓN: Unidad '{nombre}' registrada con ID: {unidad.get_id()}")
        except ValueError as e:
            print(f"ERROR: Datos inválidos. Asegúrese de ingresar números donde se solicitan.")

    def agregar_colaborador(self):
        print("\n--- REGISTRO DE COLABORADOR ---")
        if not self.empresa.obtener_catalogo_habilidades():
            return print(" [!] ERROR: No hay habilidades en el catálogo maestro.")
            
        print("\nCatálogo de Habilidades Disponibles:")
        for id_h, nom in self.empresa.obtener_catalogo_habilidades().items():
            print(f"  ID {id_h}: {nom}")
            
        try:
            entrada = input("\nIDs de habilidades (separados por coma): ").split(",")

            habilidades_ids = set()
            for i in entrada:
                texto_limpio = i.strip()
                if texto_limpio.isdigit():
                    habilidades_ids.add(int(texto_limpio))
            
            if not habilidades_ids: 
                return print(" [!] ERROR: Debe ingresar IDs válidos.")
            
            horas = float(input("Horas de disponibilidad: "))
            salario = float(input("Salario por hora: $"))
            
            colab = self.empresa.crear_colaborador(habilidades_ids, horas, salario)
            nombres_h = []
            for hid in habilidades_ids:
                nombre_habilidad = self.empresa.obtener_catalogo_habilidades().get(hid)
                nombres_h.append(nombre_habilidad)

            print(f"CONFIRMACIÓN: Colaborador {colab.get_id()} registrado con habilidades: {nombres_h}")
            
        except ValueError as e:
            print(f"ERROR: Ingresó texto donde iba un número")
        except KeyError as e:
            print(f"ERROR: El ID de habilidad ingresado no existe en el catálogo")

    def dar_baja_colaborador(self):
        print("\n--- BAJA DE PERSONAL ---")
        colaboradores = self.empresa.obtener_diccionario_colaboradores()
        hay_activos = False
        
        for id_col, colab in colaboradores.items():
            if colab.get_fecha_baja() is None:
                print(f"  ID {id_col}: {colab}")
                hay_activos = True

        if not hay_activos: return print("No hay colaboradores activos.")

        try:
            id_baja = int(input("Ingrese el ID del colaborador a dar de baja: "))
            colab_baja = self.empresa.dar_baja_colaborador_por_id(id_baja)
            print(f"\n[ÉXITO] El colaborador {id_baja} ha sido dado de baja.")
            print(colab_baja)
        except ValueError as e:
            print(f"ERROR: Ingrese un número entero válido para el ID.")

    def comprar_insumos_manual(self):
        print("\n=== GENERADOR DE ÓRDENES DE COMPRA MANUAL ===")
        insumos = self.empresa.obtener_diccionario_insumos()
        if not insumos:
            return print("ERROR: No hay insumos registrados.")

        print("\nCatálogo de Insumos Básicos y Stock Disponible:")
        for id_ins, ins in insumos.items():
            stock_actual = self.empresa.consultar_stock_insumo(ins)
            print(f"  - ID: {id_ins} | {ins.get_nombre()} | Stock: {stock_actual} unid.")

        try:
            id_insumo = int(input("\nIngrese el ID del Insumo a reponer: "))
            cantidad = int(input("Ingrese la cantidad que desea comprar: "))
            
            self.empresa.comprar_insumo_manual(id_insumo, cantidad)
            
            print("\n-> AVISO: El pedido se encuentra en tránsito.")
        except ValueError as e:
            print(f"ERROR: Ingrese números enteros válidos para ID y cantidad.")
        

    def generar_reporte_criticos(self):
        print("\n--- REPORTE DE MATERIALES CRÍTICOS ---")
        productos = self.empresa.obtener_diccionario_productos()
        if not productos:
            return print("No hay productos registrados.")
        
        for id_prod, producto in productos.items():
            print(f"  - ID: {id_prod} | {producto.get_nombre()}")   
            
        try:
            id_p = int(input("Ingrese el ID del producto a evaluar: "))
            if id_p not in productos: 
                return print("Error: ID no encontrado.")
            
            cantidad = int(input("Ingrese la cantidad a simular: "))
            if cantidad <= 0: 
                raise ValueError("La cantidad debe ser mayor a cero.")
            
            self.empresa.generar_reporte_materiales_criticos(productos[id_p], cantidad)
        except ValueError as e:
            print(f"ERROR: Ingrese números enteros válidos para ID y cantidad.")

    def emitir_reporte_y_sobrecarga(self):
        unidades = self.empresa.obtener_diccionario_unidades()
        productos = self.empresa.obtener_diccionario_productos()
        
        self.empresa.generar_reporte_estado_planta(list(unidades.values()))
        
        print("\n¿Desea calcular la sobrecarga para un pedido específico?")
        if input("Ingrese 'S' para calcular o 'N' para salir: ").strip().upper() == 'S':
            if not unidades or not productos:
                return print("Faltan datos base.")
            
            print("\nUnidades Disponibles:")
            for id_u, unidad in unidades.items(): print(f"  - ID: {id_u} | {unidad.get_nombre()}")
                
            print("\nProductos Disponibles:")
            for id_p, producto in productos.items(): print(f"  - ID: {id_p} | {producto.get_nombre()}") 
                
            try:
                id_u = int(input("\nID Unidad de Trabajo: "))
                id_p = int(input("ID Producto: "))
                cant = int(input("Cantidad a fabricar: "))
                
                if id_u in unidades and id_p in productos and cant > 0:
                    self.empresa.calcular_sobrecarga_unidad_trabajo(unidades[id_u], productos[id_p], cant)
                else:
                    print("Datos inválidos o cantidad menor a 1.")
            except ValueError:
                print("Error: Ingrese números enteros válidos.")

    def ver_historial_produccion(self):
        print("\n" + "="*70)
        print("    HISTORIAL DE PRODUCCIÓN TERMINADA    ")
        print("="*70)
        resultado = self.empresa.leer_historial_produccion()
        if resultado is None:
            return print("Todavía no hay un historial. Finalizá alguna solicitud primero.")
        encabezados, filas = resultado
        print(f"{encabezados[0]:<15} | {encabezados[1]:<20} | {encabezados[2]:<8} | {encabezados[5]:<15}")
        print("-" * 70)
        pila_historial = deque()
        for fila in filas:
            pila_historial.append(fila)
        total = len(pila_historial)
        while pila_historial:
            fila = pila_historial.pop()
            print(f"#{fila[0]:<14} | {fila[1]:<20} | {fila[2]:<8} | {fila[5]:<15} hs")
        print("-" * 70)
        print(f"Total de registros históricos: {total}")

    def cargar_demo(self):
        print("\n--- CARGANDO DEMO INDUSTRIAL ---")
        try:
            self.empresa.cargar_demo_completa()
            print("[ÉXITO] Demo cargada con éxito")
        except ValueError as e:
            print(f"Error en los datos de la demo (valores inválidos): {e}")

        except KeyError as e:
            print(f"Error de referencia en la demo (falta un ID): {e}")

        except TypeError as e:
            print(f"Error de tipo de dato al armar la demo: {e}")
        

    def crear_tarea_maestra(self):
        print("\n--- NUEVA TAREA MAESTRA ---")
        unidades = self.empresa.obtener_diccionario_unidades()
        
        if not unidades or not self.empresa.obtener_catalogo_habilidades():
            return print("ERROR: Debe cargar al menos una Unidad y una Habilidad primero.")
            
        nombre = input("Nombre del Tipo de Tarea: ")
        
        print("\nUnidades Disponibles:")
        for uid, u in unidades.items(): 
            print(f"  ID {uid}: {u.get_nombre()}")

        id_u = int(input("ID de la Unidad asociada: "))
        
        print("\nHabilidades Disponibles:")
        for hid, hnom in self.empresa.obtener_catalogo_habilidades().items(): 
            print(f"  ID {hid}: {hnom}")
        id_h = int(input("ID de la Habilidad requerida: "))
        
        if id_u in unidades and id_h in self.empresa.obtener_catalogo_habilidades():
            self.empresa.agregar_tarea_maestra(nombre, id_u, id_h)
            print("CONFIRMACIÓN: Tarea Maestra creada exitosamente.")
        else:
            print("ERROR: IDs no válidos.")



    def agregar_usuario(self):
        print("\n--- REGISTRO DE NUEVO USUARIO ---")
        try:
            contrasena = input("Ingrese la contraseña: ").strip()
            if not contrasena:
                return print(" ERROR: La contraseña no puede estar vacía.")
            nombre = input("Nombre: ").strip()
            apellido = input("Apellido: ").strip()
            dni = input("DNI: ").strip()
            if not dni:
                return print(" ERROR: El DNI es obligatorio.")

            proximo_id, es_duplicado = self.empresa.verificar_usuario_y_proximo_id(dni)
            if es_duplicado:
                return print(f" ERROR: Ya existe un usuario registrado con el DNI {dni}.")

            print("\nSeleccione el rol:")
            print("  1. Producción")
            print("  2. Administración")
            op_rol = input("Opción (1/2): ").strip()
            if op_rol == "1":
                rol = "produccion"
            elif op_rol == "2":
                rol = "administracion"
            else:
                return print(" ERROR: Opción de rol no válida.")

            self.empresa.guardar_nuevo_usuario(proximo_id, contrasena, rol, nombre, apellido, dni)
            print(f"\n-> Usuario '{nombre} {apellido}' registrado correctamente como '{rol}'.")
            print(f"-> AVISO IMPORTANTE: Su ID de acceso generado por el sistema es el número {proximo_id}.")
        except KeyError as e:
            print(f" ERROR: El archivo 'usuarios.csv' está dañado o no tiene los encabezados correctos.")
        except ValueError as e:
            print(f" ERROR: Hay un ID incorrecto en 'usuarios.csv' que no es un número")
        except OSError as e:
            print(f" ERROR: Falla al intentar guardar en 'usuarios.csv'")