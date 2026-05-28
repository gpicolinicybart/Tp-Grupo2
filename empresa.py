import csv
from gestor_compras import GestorCompras
from inventario import Inventario
from tarea import Tarea
from compra_insumo import Compra_Insumo
from solicitud_fabricacion import SolicitudDeFabricacion, ESTADOS_VALIDOS
from unidad_de_trabajo import UnidadDeTrabajo
from elemento import Elemento
from articulo_fabricado import ArticuloFabricadoInternamente
from insumo_basico import InsumoBasico
from colaboradores import Colaborador
from itembom import ItemBOM
from lista_tareas import ListaEnlazadaTareas
from gestor_archivos import GestorArchivos

class Empresa:
    def __init__(self, inventario: Inventario):
        self._inventario = inventario
        self._insumos_basicos = {}
        self._productos_fabricados = {}        
        self._solicitudes = {}
        self._unidades = {}
        self._colaboradores = {}
        self._catalogo_habilidades = {}  
        self._catalogo_tareas = {}       
        self._gestor_compras = GestorCompras()
        self._gestor_archivos = GestorArchivos(self)

    def registrar_compra(self, orden: Compra_Insumo):
        self._gestor_compras.agregar_compra(orden)
        print(f"EMPRESA: Se registró la orden de compra {orden.get_id()}...")
        self._gestor_archivos.guardar_compras_csv()
        
    def crear_solicitud(self, solicitud: SolicitudDeFabricacion):
        self._solicitudes[solicitud.get_id()] = solicitud
        print(f"EMPRESA: Se registró una nueva solicitud de fabricación (ID:{solicitud.get_id()})")

    def generar_solicitud_desde_menu(self, producto, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad a fabricar debe ser mayor a cero.")
        
        solicitud = SolicitudDeFabricacion(producto, cantidad, True)
        self.crear_solicitud(solicitud)
        return solicitud
    
    def procesar_solicitud(self):
        print("\n--- PROCESANDO PLANIFICACIÓN DE PRODUCCIÓN ---")
        
        elegibles = []
        for solicitud in self._solicitudes.values():
            if solicitud.get_estado() == ESTADOS_VALIDOS[0] or solicitud.get_estado().startswith("Demorada"):
                elegibles.append(solicitud)
    
        if not elegibles:
            print("-> AVISO: No hay solicitudes para procesar. Creá una con la opción 5 o esperá a que lleguen insumos (opción 14) si hay demoradas.")
            return
        
        for solicitud in elegibles:
            try:
                self.procesar_solicitud_individual(solicitud)
            except ValueError as e:
                print(f"-> AVISO: No se pudo completar la Solicitud {solicitud.get_id()} por falta de recursos/validación: {e}")
                solicitud.set_estado(ESTADOS_VALIDOS[7])  # Demorada por falta de recursos/validación
    
    def procesar_solicitud_individual(self, solicitud):
        producto = solicitud.get_item_solicitado()
        cantidad_pedida = int(solicitud.get_cantidad()) 
        print(f"\nProcesando Solicitud {solicitud.get_id()} -> Fabricar: {cantidad_pedida}x '{producto.get_nombre()}'")
        
        # 1: EXPLOSIÓN DE MATERIALES
        materiales_necesarios = self.explotar_bom(producto, cantidad_pedida)
        
        # 2: VERIFICAR STOCK (Si falta stock, frena y retorna)
        if not self.gestionar_stock(solicitud, materiales_necesarios):
            return 

        # 3: VERIFICAR CAPACIDAD (Delegación a Tarea)
        # Ahora desempaquetamos 3 variables
        exito_capacidad, asignaciones_pendientes, motivo_fallo = self.gestionar_capacidad(producto, cantidad_pedida)
        
        if not exito_capacidad:
            if motivo_fallo == "capacidad":
                solicitud.set_estado(ESTADOS_VALIDOS[5])  # Demorada por falta de capacidad
                print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Capacidad Máquina).")
            elif motivo_fallo == "personal":
                solicitud.set_estado(ESTADOS_VALIDOS[6])  # Demorada por falta de colaboradores
                print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Personal).")
            return

        # 4: CONFIRMACIÓN Y RESERVA
        self.confirmar_reservas(solicitud, materiales_necesarios, asignaciones_pendientes)

    def explotar_bom(self, producto, cantidad_pedida) -> dict:
        return producto.calcular_materiales_necesarios(cantidad_pedida)

    def gestionar_stock(self, solicitud, materiales_necesarios) -> bool:
        # filtrar faltantes
        materiales_faltantes = list(filter(lambda item: not self._inventario.hay_disponibilidad(item[0], item[1]), materiales_necesarios.items()))
        
        if not materiales_faltantes:
            return True

        # Evitar procesar demoradas que ya han generado compras
        if solicitud.get_estado().startswith("Demorada"):
            return False

        for componente, cant_necesaria in materiales_faltantes:
            stock_disponible = self._inventario.obtener_stock_disponible(componente)
            faltante = int(cant_necesaria) - int(stock_disponible)
            print(f" [!] Faltan {faltante} unidades de '{componente.get_nombre()}'.")
            # la empresa ejecuta metodo de reabastecimiento
            componente.gestionar_reabastecimiento(self, faltante)
        
        solicitud.set_estado(ESTADOS_VALIDOS[4])  # Demorada por falta de stock
        print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Stock).")
        return False

    def gestionar_capacidad(self, producto, cantidad_pedida) -> tuple:
        asignaciones_pendientes = [] 
        lista_tareas = producto.get_lista_tareas() 

        if len(lista_tareas) == 0:
            print(f"[!]ERROR: el producto '{producto.get_nombre()}' no tiene tareas asignadas en su receta. No se puede procesar la solicitud.")
            return False, [], "eror_configuracion"
        for tarea in lista_tareas:
            horas_totales=tarea.calcular_horas_totales(cantidad_pedida)
            unidad=tarea.get_unidad_requerida()

            if not unidad.verificar_disponibilidad(horas_totales):
                id_tarea_maestra=tarea.get_id_tarea_maestra()
                datos_tarea=self._catalogo_tareas.get(id_tarea_maestra)
                if isinstance(datos_tarea, dict):
                    nombre_tarea=datos_tarea["nombre"]
                else:
                    print(f"Tarea ID {id_tarea_maestra} no encontrada en catálogo de tareas.")
                print (f" [!] Falta capacidad en la unidad #{unidad.get_id()} para la tarea '{nombre_tarea}'.")
                return False, [], "capacidad"
            colabs_necesarios=tarea.get_cant_colaboradores_req()
            colabs_aptos=tarea.filtrar_colaboradores_aptos(self._colaboradores, horas_totales)
            if len(colabs_aptos)<colabs_necesarios:
                id_hab=tarea.get_id_habilidad_requerida()
                nombre_hab=self._catalogo_habilidades.get(id_hab, f"Habilidad ID {id_hab}")
                print (f" [!] Falta personal con habilidad '{nombre_hab}' ")
                return False, [], "personal"
            colabs_encontrados=colabs_aptos[:colabs_necesarios]
            asignaciones_pendientes.append((tarea, horas_totales, colabs_encontrados))
        return True, asignaciones_pendientes, None

    def confirmar_reservas(self, solicitud, materiales_necesarios, asignaciones_pendientes):
            print(" -> Stock y Capacidad OK. Confirmando reservas...")
            for componente, cant_necesaria in materiales_necesarios.items():
                self._inventario.reservar_stock(componente, cant_necesaria)
                
            for tarea, horas, colabs in asignaciones_pendientes:
                # la tarea ejecuta sus reservas internamente
                tarea.ejecutar_reservas(horas, colabs)
                
                # anoto a los colaboradores en la solicitud 
                for colab in colabs:
                    solicitud.agregar_colaborador(colab.get_id())
                    
            solicitud.set_estado(ESTADOS_VALIDOS[1])  # Procesada y Planificada
            print(f" -> Solicitud {solicitud.get_id()} PROCESADA CON ÉXITO.")

   
    def ejecutar_solicitud(self):
        print("\n--- EJECUTANDO ÓRDENES PLANIFICADAS ---")
        contador_ejecutadas = 0
        
        for id_solicitud, solicitud in self._solicitudes.items():
            
            # Solo actuamos sobre las que están listas
            if solicitud.get_estado() == ESTADOS_VALIDOS[1]:
                try:
                    producto = solicitud.get_item_solicitado()
                    cantidad_pedida = solicitud.get_cantidad()

                    materiales_necesarios = self.explotar_bom(producto, cantidad_pedida)
                    
                    for componente, cant_necesaria in materiales_necesarios.items():
                        self._inventario.descontar_stock(componente, cant_necesaria)

                    solicitud.set_estado(ESTADOS_VALIDOS[2])  # En Ejecución
                    print(f"-> ÉXITO: Solicitud #{id_solicitud} ('{producto.get_nombre()}') enviada a producción.")
                    contador_ejecutadas += 1
                    
                except Exception as e:
                    print(f"-> ERROR CRÍTICO en Solicitud #{id_solicitud}: {e}")
                    solicitud.set_estado(ESTADOS_VALIDOS[8])  # Demorada por Error Interno

        
        if contador_ejecutadas == 0:
            print("-> AVISO: No se encontraron solicitudes en estado 'Procesada y Planificada' para ejecutar.")
        else:
            print(f"-> RESUMEN: {contador_ejecutadas} solicitudes han iniciado su producción.")

    
    def finalizar_solicitud(self):
            
        print("\n--- FINALIZANDO ÓRDENES EN PRODUCCIÓN ---")
        contador_finalizadas = 0
        solicitudes_a_archivar = []
            
        for id_solicitud, solicitud in list(self._solicitudes.items()):
                
            if solicitud.get_estado() == ESTADOS_VALIDOS[2]:  # En Ejecución
                try:
                    producto = solicitud.get_item_solicitado()
                    cantidad_pedida = int(solicitud.get_cantidad())
                    self._inventario.ingresar_stock(producto, cantidad_pedida)
                    solicitud.marcar_como_terminada()
                    print(f"-> ÉXITO: Solicitud #{id_solicitud} terminada. {cantidad_pedida}x '{producto.get_nombre()}' sumados al stock.")
                    solicitudes_a_archivar.append(solicitud)
                    contador_finalizadas += 1
                except Exception as e:
                    print(f"-> ERROR al finalizar Solicitud #{id_solicitud}: {e}")
                                    
        if contador_finalizadas > 0:
            self._gestor_archivos.guardar_historial_csv(solicitudes_a_archivar)
            self._solicitudes = dict(filter(lambda item: item[1].get_estado() != ESTADOS_VALIDOS[3], self._solicitudes.items()))
            print(f"-> SISTEMA: Limpieza de memoria. {contador_finalizadas} solicitudes históricas archivadas/borradas.")
        else:
            print("-> AVISO: No hay solicitudes en producción para finalizar.")

            
    def recibir_compras(self) -> int:
        compra = self._gestor_compras.recibir_proxima_compra(self._inventario)
        
        if compra:
            # Hubo una recepción exitosa, persistimos los datos
            self._gestor_archivos.guardar_compras_csv()  
            self._gestor_archivos.guardar_inventario_csv()
            return 1 # Avisamos al menú que se recibió 1 orden
            
        return 0 
#==============================================================================================================
    #consigna de implementacion 

    def generar_reporte_materiales_criticos(self, producto, cantidad_pedida: int):
        necesidades = producto.calcular_materiales_necesarios(cantidad_pedida)
        criticos = self._inventario.obtener_materiales_criticos(necesidades)
        nombre_archivo = f"criticos_{producto.get_id()}.csv"
        try:

            with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID Insumo", "Nombre", "Cant. Necesaria", "Stock Actual", "Cobertura"])
                if not criticos:
                #si no hay críticos, solo avisamos por consola y dejamos el archivo con solo el encabezado.
                    print(f"-> [INFO] Reporte: NO hay materiales críticos para '{producto.get_nombre()}'. Stock en niveles aceptables.")
                else:
                    for insumo, cant_nec in criticos:
                        stock = self._inventario.consultar_stock(insumo)
                        porcentaje = (stock / cant_nec) * 100  # se puede calcular directo xq cant_nec siempre es > 0 ya esta validado
                        cobertura = f"{porcentaje:.1f}%"
                        writer.writerow([insumo.get_id(), insumo.get_nombre(), cant_nec, stock, cobertura])
            print(f"-> Reporte de críticos generado en: '{nombre_archivo}'.")
                
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura del archivo: {e}")

    
    def generar_reporte_estado_planta(self, lista_unidades: list):
        print("\n" + "="*55)
        print("   REPORTE GLOBAL DE ESTADO DE PLANTA Y CUELLOS DE BOTELLA")
        print("="*55)
        
        print("\n[1] ESTADO DE UNIDADES DE TRABAJO:")
        if not lista_unidades:
            print("  No hay unidades registradas.")
        else: # para encontrar la maquina más saturada de la planta uso max() y lambda como clave (key)
            # busco el objeto mas grande de la lista ejecutando get_porcentaje_uso()
            unidad_critica = max(lista_unidades, key=lambda unidad: unidad.get_porcentaje_uso())
            for unidad in lista_unidades:
                print(f"  - Unidad #{unidad.get_id()} ({unidad.get_nombre()}): {unidad.get_porcentaje_uso():.1f}% de ocupación.")
            
            if unidad_critica.get_porcentaje_uso() > 0:
                print(f"  >>> UNIDAD DE TRABAJO MÁS EXIGIDA: {unidad_critica.get_nombre()}")

       
        print("\n[2] ANÁLISIS DE DEMORAS (CUELLOS DE BOTELLA):")
        #ponemos en listas las solicitudes que estan demoradas por cada tipo de cuello de botella
        # y contamos cuantas hay de c/u
        d_stock = len(list(filter(lambda t: t.get_estado() == ESTADOS_VALIDOS[4], self._solicitudes.values())))
        d_capacidad = len(list(filter(lambda t: t.get_estado() == ESTADOS_VALIDOS[5], self._solicitudes.values())))
        d_personal = len(list(filter(lambda t: t.get_estado() == ESTADOS_VALIDOS[6], self._solicitudes.values())))        
        print(f"  - Frenadas por FALTA DE INSUMOS: {d_stock}")
        print(f"  - Frenadas por CAPACIDAD DE UNIDADES DE TRABAJO: {d_capacidad}")
        print(f"  - Frenadas por ESCASEZ DE COLABORADORES: {d_personal}")
        
        demoras = {
            "FALTA DE INSUMOS": d_stock,
            "SOBRECARGA DE UNIDADES DE TRABAJO": d_capacidad,
            "ESCASEZ DE COLABORADORES": d_personal
        }
        
        cuello_principal = max(demoras, key=demoras.get)
        
        if demoras[cuello_principal] > 0:
            print(f"\n>>> CONCLUSIÓN: El cuello de botella principal del sistema es {cuello_principal}.")
        else:
            print("\n>>> CONCLUSIÓN: Flujo perfecto. No hay cuellos de botella activos.")
        
    def calcular_sobrecarga_unidad_trabajo(self, unidad, producto, cantidad: int):
        carga_necesaria = producto.calcular_horas_en_unidad(unidad, cantidad)
        capacidad_max = unidad.get_capacidad_max_horas()

        print(f"\n--- CÁLCULO DE SOBRECARGA PREDICTIVA: {unidad.get_nombre()} ---")
        print(f"Carga requerida: {carga_necesaria:.2f} hs | Capacidad instalada: {capacidad_max:.2f} hs")

        if carga_necesaria > capacidad_max:
            sobrecarga = carga_necesaria - capacidad_max
            print(f">>> ALERTA: Sobrecarga detectada. La unidad colapsará por un exceso de {sobrecarga:.2f} hs.")
        else:
            print(">>> OK: La unidad tiene capacidad suficiente para absorber este pedido.")

    def mostrar_solicitudes(self):
        print("\n--- RESUMEN DE SOLICITUDES ---")
        if not self._solicitudes:
            print("No hay solicitudes registradas.")
            return
            
        for solicitud in self._solicitudes.values():
            print(solicitud)
        print("-----------------------------\n")

    def agregar_colaborador(self, nuevo_colaborador):
            id_nuevo = nuevo_colaborador.get_id()
            if id_nuevo in self._colaboradores:
                raise ValueError("ID repetido")
            self._colaboradores[id_nuevo] = nuevo_colaborador
            self._gestor_archivos.guardar_colaboradores_csv()

    def agregar_unidad_trabajo(self, nueva_unidad: UnidadDeTrabajo):
        self._unidades[nueva_unidad.get_id()] = nueva_unidad
        self._gestor_archivos.guardar_unidades_csv()
        
    
    def registrar_producto_nuevo(self, producto: Elemento) -> bool:
            nombre_nuevo = producto.get_nombre().strip().lower()
            for ins in self._insumos_basicos.values():
                if ins.get_nombre().strip().lower() == nombre_nuevo:
                    print(f"-> [ERROR] Ya existe '{ins.get_nombre()}' en insumos. Cancelado.")
                    return False
            for prod in self._productos_fabricados.values():
                if prod.get_nombre().strip().lower() == nombre_nuevo:
                    print(f"-> [ERROR] Ya existe '{prod.get_nombre()}' en productos. Cancelado.")
                    return False
            try:
                producto.validar_ciclos() 
                if producto.get_tipo_elemento() == "Insumo Básico":
                    self._insumos_basicos[producto.get_id()] = producto
                else:
                    self._productos_fabricados[producto.get_id()] = producto
                print(f"EMPRESA: '{producto.get_nombre()}' registrado exitosamente en el catálogo.")
                self._gestor_archivos.guardar_catalogo_csv() 
                self._gestor_archivos.guardar_tareas_csv()  
                return True
            except ValueError as e:
                print(f"No se pudo registrar '{producto.get_nombre()}' por un ciclo en el BOM")
                return False
                
    def consultar_stock_insumo(self, insumo):
        return self._inventario.obtener_stock_disponible(insumo)

   

    def agregar_habilidad(self, nombre: str):
            if self._catalogo_habilidades:
                nuevo_id = len(self._catalogo_habilidades) + 1
            else:
                nuevo_id = 1
            self._catalogo_habilidades[nuevo_id] = nombre.strip().title()
            self._gestor_archivos.guardar_catalogos_maestros()
            return nuevo_id

    def agregar_tarea_maestra(self, nombre: str, id_unidad: int, id_habilidad: int):
        if self._catalogo_tareas:
            nuevo_id = len(self._catalogo_tareas) + 1
        else:
            nuevo_id = 1
        self._catalogo_tareas[nuevo_id] = {
            "nombre": nombre.strip().title(),
            "id_unidad": id_unidad,
            "id_habilidad": id_habilidad
        }
        self._gestor_archivos.guardar_catalogos_maestros()
        return nuevo_id
   
    def obtener_diccionario_insumos(self):
        return self._insumos_basicos

    def obtener_diccionario_productos(self):
        return self._productos_fabricados

    def obtener_diccionario_unidades(self):
        return self._unidades

    def obtener_diccionario_colaboradores(self):
        return self._colaboradores

    def crear_insumo_basico(self, nombre, costo):
        if not nombre: 
            raise ValueError("El nombre no puede estar vacío.")
        if costo <= 0: 
            raise ValueError("El costo debe ser positivo.")
        
        insumo = InsumoBasico(nombre, costo)
        self.registrar_producto_nuevo(insumo)
        return insumo

    def crear_unidad_trabajo(self, nombre, capacidad, costo):

        unidad = UnidadDeTrabajo(nombre, capacidad, costo)
        self.agregar_unidad_trabajo(unidad)
        return unidad

    def crear_colaborador(self, habilidades_ids, horas, salario):
        # Validar que las habilidades existan en el catálogo maestro
        for h in habilidades_ids:
            if h not in self._catalogo_habilidades:
                raise ValueError(f"La habilidad con ID {h} no existe.")
                
        colab = Colaborador(habilidades_ids, horas, salario)
        self.agregar_colaborador(colab)
        return colab

    def dar_baja_colaborador_por_id(self, id_colab):
        if id_colab not in self._colaboradores:
            raise ValueError("ID de colaborador no encontrado.")
        
        colab = self._colaboradores[id_colab]
        colab.dar_de_baja()
        return colab

    def comprar_insumo_manual(self, id_insumo, cantidad):
        insumos_disp = self.obtener_diccionario_insumos()
        if id_insumo not in insumos_disp:
            raise ValueError("ID de insumo no válido.")
            
        insumo = insumos_disp[id_insumo]
        insumo.gestionar_reabastecimiento(self, cantidad)
        return insumo

    def crear_producto_completo(self, nombre, dict_bom_cantidades, lista_datos_tareas):
        insumos_disp = self.obtener_diccionario_insumos()

        #  Armar Receta BOM
        bom_dict = {}
        for id_ins, cant in dict_bom_cantidades.items():
            bom_dict[insumos_disp[id_ins]] = cant
        bom = ItemBOM(f"Receta {nombre}", bom_dict)

        tareas_producto = ListaEnlazadaTareas() 
        
        for dt in lista_datos_tareas:
            id_t_maestra = dt['id_maestra']
            datos_maestros = self._catalogo_tareas[id_t_maestra]
            id_unidad = datos_maestros["id_unidad"]
            id_hab = datos_maestros["id_habilidad"]

            # colaboradores aptos para esta tarea
            aptos = []
            for colaborador in self._colaboradores.values():
                if colaborador.tiene_habilidad(id_hab):
                    aptos.append(colaborador)

            # calculo del costo de mano de obra promedio
            if len(aptos) > 0:
                suma_salarios = 0.0
                for colaborador in aptos:
                    suma_salarios += colaborador.get_salario_hora()
                
                costo_mo = suma_salarios / len(aptos)
            else:
                costo_mo = 0.0
            unidades_disp = self.obtener_diccionario_unidades()
            unidad_obj = unidades_disp[id_unidad]
            nueva_tarea = Tarea(id_t_maestra, unidad_obj, dt['cant_colabs'], dt['tiempo'], id_hab, costo_mo)
            
            tareas_producto.agregar_al_final(nueva_tarea) 

        if len(tareas_producto) == 0:
            raise ValueError("No se puede fabricar sin tareas.")

        
        producto = ArticuloFabricadoInternamente(nombre, [bom], tareas_producto)
        self.registrar_producto_nuevo(producto)
        return producto

    def cargar_demo_completa(self):
        

        id_hab_armado = self.agregar_habilidad("Armado General")
        ensambladora = UnidadDeTrabajo("Mesa de Ensamblaje", 80.0, 500.0)
        self.agregar_unidad_trabajo(ensambladora)
        
        id_tarea_ensamble = self.agregar_tarea_maestra("Ensamblaje Manual", ensambladora.get_id(), id_hab_armado)
        id_tarea_corte = self.agregar_tarea_maestra("Corte de Madera", ensambladora.get_id(), id_hab_armado)
        
        madera = InsumoBasico("Tablón de Madera", 5000.0)
        tornillos = InsumoBasico("Tornillos 10mm", 5.0)
        for insumo in [madera, tornillos]:
            self.registrar_producto_nuevo(insumo)
            self._inventario.ingresar_stock(insumo, 1000)
            
        carpintero = Colaborador([id_hab_armado], 40.0, 2500.0)
        self.agregar_colaborador(carpintero)

        # Pata
        tarea_pata = Tarea(id_tarea_corte, ensambladora, 1, 0.5, id_hab_armado, 1000.0)
        bom_pata = ItemBOM("Receta Pata", {madera: 1, tornillos: 4})
        lista_pata = ListaEnlazadaTareas()
        lista_pata.agregar_al_final(tarea_pata)
        pata = ArticuloFabricadoInternamente("Pata de Mesa", [bom_pata], lista_pata)
        self.registrar_producto_nuevo(pata)

        # Mesa
        tarea_mesa = Tarea(id_tarea_ensamble, ensambladora, 1, 1.5, id_hab_armado, 2500.0)
        bom_mesa = ItemBOM("Receta Mesa", {madera: 1, pata: 4})
        lista_mesa = ListaEnlazadaTareas()
        lista_mesa.agregar_al_final(tarea_mesa)
        mesa = ArticuloFabricadoInternamente("Mesa Completa", [bom_mesa], lista_mesa)
        self.registrar_producto_nuevo(mesa)
        # GETTERS para lectura
    def obtener_catalogo_habilidades(self) -> dict:
        return self._catalogo_habilidades

    def obtener_catalogo_tareas(self) -> dict:
        return self._catalogo_tareas

    def obtener_historial_compras(self) -> list:
        # La empresa le delega al gestor la obtención del historial
        return self._gestor_compras.obtener_historial()

    # MÉTODOS para cargar datos desde los CSV sin pisar la lógica de negocio
    def registrar_habilidad_desde_archivo(self, id_hab: int, nombre: str):
        self._catalogo_habilidades[id_hab] = nombre

    def registrar_tarea_desde_archivo(self, id_tarea: int, datos: dict):
        self._catalogo_tareas[id_tarea] = datos

    def agregar_elemento_al_catalogo(self, elemento):
        """Agrega un elemento al catálogo desde GestorArchivos"""
        if elemento.get_tipo_elemento() == "Insumo Básico":
            self._insumos_basicos[elemento.get_id()] = elemento
        else:
            self._productos_fabricados[elemento.get_id()] = elemento
    
    def obtener_elementos_catalogo(self):
        """Retorna la lista de elementos combinada para guardar en el CSV"""
        return list(self._insumos_basicos.values()) + list(self._productos_fabricados.values())
    
    def agregar_solicitud(self, id_solicitud, solicitud):
        """Agrega una solicitud al registro desde GestorArchivos"""
        self._solicitudes[id_solicitud] = solicitud
    
    def obtener_solicitudes(self):
        """Retorna el diccionario de solicitudes"""
        return self._solicitudes
    
    def agregar_unidad(self, unidad):
        """Agrega una unidad de trabajo al registro desde GestorArchivos"""
        self._unidades[unidad.get_id()] = unidad    
        
    def obtener_unidades(self):
        """Retorna la lista de unidades de trabajo"""
        return list(self._unidades.values())
    
    def obtener_inventario(self):
        """Retorna el inventario de la empresa"""
        return self._inventario
    
    def cargar_inventario_desde_archivo(self):
        self._inventario.cargar_desde_csv(self.obtener_elementos_catalogo())
        
    def cargar_compra_desde_archivo(self, orden):
        self._gestor_compras.agregar_compra(orden)

    def cargar_todos_los_datos(self):
        self._gestor_archivos.cargar_todos_los_csv()
        
    def guardar_todos_los_datos(self):
        self._gestor_archivos.guardar_todos_los_csv()
    
    def guardar_inventario(self):
        self._gestor_archivos.guardar_inventario_csv()
    
    def guardar_solicitudes(self):
        self._gestor_archivos.guardar_solicitudes_csv()