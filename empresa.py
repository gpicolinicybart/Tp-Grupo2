#------------------------------------------------------------------------------------------------------------------------------
# IMPORTANTE NOTA: La empresa centraliza el procesamiento (revisa stock, asigna tareas).
# La solicitud queda como un objeto de datos puro.
#------------------------------------------------------------------------------------------------------------------------------
from datetime import datetime
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
from cola import Cola
import csv
import os

# como la empresa confia en lo que colaboradores y insumo basico le devuelven al preguntar por 
# su tipo de reabastecimiento, no es necesario importar la clase de cada uno, con importar el padre (Elemento)
# alcanza para que la empresa pueda preguntar por el tipo de reabastecimiento sin necesidad de saber si es un 
# insumo o un articulo fabricado.
class Empresa:
    def __init__(self, inventario: Inventario):
        self._inventario = inventario
        self._catalogo_elementos = []
        self._solicitudes = {}
        self._unidades = []
        self._colaboradores = {}
        self._registro_compras = []  # Para guardar el historial en el CSV
        self._cola_entregas = Cola() # Para procesar las que van llegando en orden (FIFO)
        self._catalogo_habilidades = {}  # Formato -> ID: Nombre
        self._catalogo_tareas = {}       # Formato -> ID: Nombre
        
    def registrar_compra(self, orden: Compra_Insumo):
        self._registro_compras.append(orden)
        self._cola_entregas.encolar(orden)
        print(f"EMPRESA: Se registró la orden de compra {orden.get_id()}...")
        self.guardar_compras_csv()
        
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
        materiales_necesarios =self.explotar_bom(producto, cantidad_pedida)
        
        # 2: VERIFICAR STOCK (Si falta stock, frena y retorna)
        if not self.gestionar_stock(solicitud, materiales_necesarios):
            return 

        # 3: VERIFICAR CAPACIDAD (Delegación a Tarea)
        exito_capacidad, asignaciones_pendientes = self.gestionar_capacidad(producto, cantidad_pedida)
        if not exito_capacidad:
            solicitud.set_estado(ESTADOS_VALIDOS[5])  # Demorada por falta de capacidad
            print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Capacidad).")
            return

        # 4: CONFIRMACIÓN Y RESERVA
        self.confirmar_reservas(solicitud, materiales_necesarios, asignaciones_pendientes)


    def explotar_bom(self, producto, cantidad_pedida) -> dict:
        materiales_necesarios = {}
        for bom in producto.get_bom():
            for componente, cant_unitaria in bom.get_diccionario().items():
                total_necesario = int(cant_unitaria) * int(cantidad_pedida)
                materiales_necesarios[componente] = materiales_necesarios.get(componente, 0) + total_necesario
        return materiales_necesarios

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
        lista_tareas = producto.get_lista_tareas() # Esto es una ListaEnlazadaTareas

        if not lista_tareas.cabecera:
            print(f" [!] ERROR: El producto '{producto.get_nombre()}' no tiene tareas asignadas.")
            return False, []

        nodo_actual = lista_tareas.cabecera
        while nodo_actual is not None:
            tarea = nodo_actual.tarea
            horas_totales = tarea.calcular_horas_totales(cantidad_pedida)
            unidad = tarea.get_unidad_requerida()
            
            # Verificamos Disponibilidad de Máquina
            if not unidad.verificar_disponibilidad(horas_totales):
                id_tarea_maestra = tarea.get_id_tarea_maestra()
                # Accedemos al diccionario maestro que ahora tiene el formato {"nombre": "...", ...}
                datos_tarea = self._catalogo_tareas.get(id_tarea_maestra)
                nombre_tarea = datos_tarea["nombre"] if isinstance(datos_tarea, dict) else f"Tarea ID {id_tarea_maestra}"
                print(f" [!] Falta capacidad en la Unidad #{unidad.get_id()} para la tarea '{nombre_tarea}'.")
                return False, [] 
                
            colabs_necesarios = tarea.get_cant_colaboradores_req()
            colabs_aptos = tarea.filtrar_colaboradores_aptos(self._colaboradores, horas_totales)
            
            # Verificamos Disponibilidad de Personal
            if len(colabs_aptos) < colabs_necesarios:
                id_hab = tarea.get_id_habilidad_requerida()
                nombre_hab = self._catalogo_habilidades.get(id_hab, f"Habilidad ID {id_hab}")
                print(f" [!] No hay suficientes colaboradores con la habilidad '{nombre_hab}'.")
                return False, []
                
            colabs_encontrados = colabs_aptos[:colabs_necesarios]
            asignaciones_pendientes.append((tarea, horas_totales, colabs_encontrados))
            nodo_actual = nodo_actual.siguiente # Avanzamos en la lista enlazada
            
        return True, asignaciones_pendientes

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
            self.guardar_historial_csv(solicitudes_a_archivar) # archivo las solicitudes que voy a borrar
            self._solicitudes = dict(filter(lambda item: item[1].get_estado() != ESTADOS_VALIDOS[3], self._solicitudes.items()))
            print(f"-> SISTEMA: Limpieza de memoria. {contador_finalizadas} solicitudes históricas archivadas/borradas.")
        else:
            print("-> AVISO: No hay solicitudes en producción para finalizar.")


    def guardar_historial_csv(self, solicitudes_terminadas: list): #agarra la lista de solicitudes terminadas y las appendea al historial CSV
        nombre_archivo = "historial_solicitudes.csv"
        # veo si el archivo ya existe para sobreescribirle
        archivo_existe = os.path.isfile(nombre_archivo) # Devuelve True si el archivo existe en el disco, False si no existe
        
        try:
            with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                # Si es la primera vez que se crea el archivo, le ponemos los títulos a las columnas
                if not archivo_existe:
                    writer.writerow(["ID Solicitud", "Producto", "Cantidad", "Fecha Creacion", "Fecha Finalizacion", "Tiempo Transcurrido (Horas)"])
                # Escribimos una fila por cada solicitud terminada
                for sol in solicitudes_terminadas:
                    id_sol = sol.get_id()
                    producto = sol.get_item_solicitado().get_nombre()
                    cantidad = sol.get_cantidad()
                    
                    # no hace falta pero formateo las fechas para que se vean bien, si no queda en un formato raro
                    fecha_creacion = sol._fecha_creacion.strftime("%d/%m/%Y %H:%M")
                    if sol._fecha_finalizacion:
                        fecha_fin = sol._fecha_finalizacion.strftime("%d/%m/%Y %H:%M")
                        # Calculamos las horas que tardó en producirse
                        tiempo_hs = round((sol._fecha_finalizacion - sol._fecha_creacion).total_seconds() / 3600, 2)
                    else:
                        fecha_fin = "N/A"
                        tiempo_hs = "N/A"
                        
                    writer.writerow([id_sol, producto, cantidad, fecha_creacion, fecha_fin, tiempo_hs])
                    
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura del historial CSV: {e}")
            
    def recibir_compras(self):
        if self._cola_entregas.esta_vacia():
            return 0
        cantidad_recibida = 0
        # Desencolamos una a una 
        while not self._cola_entregas.esta_vacia():
            orden = self._cola_entregas.desencolar()
            if orden._estado == "Solicitada":
                orden.recibir_materiales(self._inventario) 
                orden._estado = "Recibida"
                orden._fecha_recepcion = datetime.now()
                cantidad_recibida += 1
        self.guardar_compras_csv() 
        self.guardar_catalogo_csv() 
        return cantidad_recibida
        
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
            self.guardar_colaboradores_csv()

    def agregar_unidad_trabajo(self, nueva_unidad: UnidadDeTrabajo):
        self._unidades.append(nueva_unidad)
        self.guardar_unidades_csv()  
        
    
    def registrar_producto_nuevo(self, producto: Elemento) -> bool:
            # --- NUEVO: Validación de duplicados por nombre ---
            nombre_nuevo = producto.get_nombre().strip().lower()
            for elem in self._catalogo_elementos:
                if elem.get_nombre().strip().lower() == nombre_nuevo:
                    print(f"-> [ERROR] Ya existe un elemento llamado '{elem.get_nombre()}' en el catálogo. Acción cancelada.")
                    return False
                    
            try:
                producto.validar_ciclos() 
                self._catalogo_elementos.append(producto)
                print(f"EMPRESA: '{producto.get_nombre()}' registrado exitosamente en el catálogo.")
                
                # --- PERSISTENCIA ---
                self.guardar_catalogo_csv()
                self.guardar_tareas_csv() # <--- ¡ACÁ VA EL CAMBIO!
                return True
            except ValueError as e:
                print(f"No se pudo registrar '{producto.get_nombre()}' por un ciclo en el BOM: {e}")
                return False
                
    def consultar_stock_insumo(self, insumo):
        return self._inventario.obtener_stock_disponible(insumo)

    # =====================================================================
    # MÉTODOS DE PERSISTENCIA (Sincronización con archivos CSV)
    # =====================================================================

    def guardar_solicitudes_csv(self):
        """Guarda las solicitudes activas (en cola, en proceso) para no perder el estado de la fábrica"""
        nombre_archivo = "solicitudes_activas.csv"
        try:
            with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID Solicitud", "Producto", "Cantidad", "Estado", "Fecha Creacion"])
                for sol in self._solicitudes.values():
                    id_sol = sol.get_id()
                    producto = sol.get_item_solicitado().get_nombre()
                    cantidad = sol.get_cantidad()
                    estado = sol.get_estado()
                    fecha_creacion = sol._fecha_creacion.strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([id_sol, producto, cantidad, estado, fecha_creacion])
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura de solicitudes activas CSV: {e}")

    def guardar_catalogo_csv(self):
        """Guarda modelos, recetas y stock físico actual en un solo archivo"""
        nombre_archivo = "productos.csv"
        try:
            with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                # Una sola tabla con TODO
                writer.writerow(["ID Producto", "Nombre Producto", "Tipo", "Costo Fijo", "Stock Fisico", "Stock Reservado", "Receta BOM"])
                
                for prod in self._catalogo_elementos:
                    # Obtenemos los datos del inventario para este producto
                    fisico = self._inventario.consultar_stock(prod)
                    reservado = self._inventario.obtener_stock_reservado(prod)
                    
                    if isinstance(prod, ArticuloFabricadoInternamente):
                        # Serializamos el BOM por IDs: "123:2;456:5"
                        bom_str_list = []
                        for bom_item in prod.get_bom():
                            for elemento, cantidad in bom_item.get_diccionario().items():
                                bom_str_list.append(f"{elemento.get_id()}:{cantidad}")
                        receta_str = ";".join(bom_str_list)
                        
                        writer.writerow([prod.get_id(), prod.get_nombre(), "ArticuloFabricado", "0.0", fisico, reservado, receta_str])
                    else: 
                        costo = prod.get_costo_fijo() if hasattr(prod, 'get_costo_fijo') else 0.0
                        writer.writerow([prod.get_id(), prod.get_nombre(), "Insumo", costo, fisico, reservado, ""])
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura centralizada: {e}")
    def guardar_inventario_csv(self):
        """Le pide al inventario que guarde su stock físico actual respetando el encapsulamiento"""
        if hasattr(self._inventario, 'guardar_en_csv'):
            self._inventario.guardar_en_csv()
        else:
            print("-> [AVISO] Falta implementar guardar_en_csv() en la clase Inventario.")
    def cargar_catalogo_csv(self):
        """Reconstruye los objetos Elemento al arrancar el programa"""
        nombre_archivo = "productos.csv"
        if not os.path.exists(nombre_archivo):
            return
            
        from articulo_fabricado import ArticuloFabricadoInternamente
        from insumo_basico import InsumoBasico

        try:
            filas_csv = []
            with open(nombre_archivo, mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    filas_csv.append(fila)
                    id_prod = int(fila.get("ID Producto", 0)) if fila.get("ID Producto") else None
                    nombre = fila["Nombre Producto"]
                    tipo = fila["Tipo"]
                    costo = float(fila.get("Costo Fijo", 0.0))
                    
                    if tipo == "ArticuloFabricado":
                        nuevo_prod = ArticuloFabricadoInternamente(nombre=nombre, bom=[], lista_tareas=ListaEnlazadaTareas(), id=id_prod)
                        self._catalogo_elementos.append(nuevo_prod)
                    elif tipo == "Insumo":
                        nuevo_insumo = InsumoBasico(nombre=nombre, costo_fijo=costo, id=id_prod)
                        self._catalogo_elementos.append(nuevo_insumo)

            # Reconstruimos el BOM utilizando IDs
            elementos_por_id = {elem.get_id(): elem for elem in self._catalogo_elementos}
            for fila in filas_csv:
                if fila.get("Tipo") == "ArticuloFabricado" and fila.get("Receta BOM"):
                    prod_id = int(fila.get("ID Producto", 0))
                    prod_obj = elementos_por_id.get(prod_id)
                    if not prod_obj:
                        continue

                    receta_str = fila.get("Receta BOM", "")
                    bom_items = []
                    if receta_str:
                        for item in receta_str.split(";"):
                            if not item.strip():
                                continue
                            componente_id_str, cantidad_str = item.split(":")
                            componente_id = int(componente_id_str)
                            cantidad = int(cantidad_str)
                            componente = elementos_por_id.get(componente_id)
                            if componente is not None:
                                bom_items.append((componente, cantidad))
                    if bom_items:
                        prod_obj._bom = [ItemBOM(f"Receta {prod_obj.get_nombre()}", dict(bom_items))]

        except Exception as e:
            print(f"-> [ERROR] Falló la lectura del catálogo CSV: {e}")

    def cargar_solicitudes_csv(self):
        """Carga las solicitudes activas para retomar la producción"""
        nombre_archivo = "solicitudes_activas.csv"
        if not os.path.exists(nombre_archivo):
            return
    
        try:
            with open(nombre_archivo, mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                
                for fila in reader:
                    nombre_prod = fila["Producto"]
                    
                    # Filtramos el catálogo dejando solo los que coinciden con el nombre.
                    resultados = list(filter(lambda p: p.get_nombre() == nombre_prod, self._catalogo_elementos))
                    
                    if len(resultados) > 0:
                        producto_obj = resultados[0] 
                        
                        id_sol = int(fila["ID Solicitud"])
                        cantidad = int(fila["Cantidad"])
                        estado = fila["Estado"]
                        fecha_creacion_str = fila["Fecha Creacion"]
                        
                        nueva_sol = SolicitudDeFabricacion(producto_obj, cantidad, True)
                        
                        nueva_sol._id = id_sol
                        nueva_sol.set_estado(estado)
                        nueva_sol._fecha_creacion = datetime.strptime(fecha_creacion_str, "%Y-%m-%d %H:%M:%S")
                        
                        self._solicitudes[id_sol] = nueva_sol
                        
                        if id_sol > SolicitudDeFabricacion.id_solicitud:
                            SolicitudDeFabricacion.id_solicitud = id_sol
                            
        except Exception as e:
            print(f"-> [ERROR] Falló la lectura de solicitudes activas CSV: {e}")
            

#================================= CAMBIOS LUCAS ==================================
# =====================================================================
    # NUEVOS MÉTODOS DE PERSISTENCIA (Múltiples CSVs)
    # =====================================================================

    def guardar_unidades_csv(self):
        try:
            with open("unidades.csv", mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID Unidad", "Nombre", "Capacidad", "Costo Operativo"])
                for unidad in self._unidades:
                    writer.writerow([unidad.get_id(), unidad.get_nombre(), unidad.get_capacidad_max_horas(), unidad.get_costo_operativo()])
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura de unidades: {e}")

    def cargar_unidades_csv(self):
        if not os.path.exists("unidades.csv"): return
        from unidad_de_trabajo import UnidadDeTrabajo
        try:
            with open("unidades.csv", mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    nueva_unidad = UnidadDeTrabajo(fila["Nombre"], float(fila["Capacidad"]), float(fila["Costo Operativo"]))
                    nueva_unidad._id = int(fila["ID Unidad"])
                    if hasattr(UnidadDeTrabajo, 'id_unidad') and nueva_unidad._id > UnidadDeTrabajo.id_unidad:
                        UnidadDeTrabajo.id_unidad = nueva_unidad._id
                    self._unidades.append(nueva_unidad)
        except Exception as e:
            print(f"-> [ERROR] Falló la carga de unidades: {e}")

# CORRECCIÓN PARA COLABORADORES (Guarda y lee IDs numéricos)
    def guardar_colaboradores_csv(self):
        try:
            with open("colaboradores.csv", mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID Colaborador", "Habilidades_IDs", "Horas Disponibles", "Salario Hora"])
                for colaborador in self._colaboradores.values():
                    ids_str = ";".join(map(str, colaborador.get_habilidades()))
                    writer.writerow([colaborador.get_id(), ids_str, colaborador.get_horas_disponibles(), colaborador.get_salario_hora()])
        except IOError as e:
            print(f"-> [ERROR] Falla en el guardado de colaboradores CSV: {e}")
        except KeyError as e:
            print(f"-> [ERROR] Falla en el guardado de colaboradores CSV: {e}")
        except ValueError as e:
            print(f"-> [ERROR] Falla en el guardado de colaboradores CSV: {e}")

    def cargar_colaboradores_csv(self):
        if not os.path.exists("colaboradores.csv"): return
        from colaboradores import Colaborador
        try:
            with open("colaboradores.csv", mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    ids_str = fila["Habilidades_IDs"]
                    h_ids = [int(id_habilidad) for id_habilidad in ids_str.split(";")] if ids_str else []
                    nuevo_colaborador = Colaborador(h_ids, float(fila["Horas Disponibles"]), float(fila["Salario Hora"]))
                    nuevo_colaborador._id = int(fila["ID Colaborador"])
                    if hasattr(Colaborador, 'id_colaborador') and nuevo_colaborador._id > Colaborador.id_colaborador:
                        Colaborador.id_colaborador = nuevo_colaborador._id
                    self._colaboradores[nuevo_colaborador.get_id()] = nuevo_colaborador
        except IOError as e:
            print(f"-> [ERROR] Falla en la carga de colaboradores CSV: {e}")
        except KeyError as e:
            print(f"-> [ERROR] Falla en la carga de colaboradores CSV: {e}")
        except ValueError as e:
            print(f"-> [ERROR] Falla en la carga de colaboradores CSV: {e}")

    # CORRECCIÓN PARA TAREAS (Relaciona el ID de tarea y habilidad maestra)
    def guardar_tareas_csv(self):
        try:
            with open("tareas.csv", mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID Producto", "ID_Tarea_M", "ID Unidad", "Cant Colab", "Tiempo", "ID_Hab_Req", "Costo MO"])
                for prod in self._catalogo_elementos:
                    if hasattr(prod, 'get_lista_tareas'):
                        for t in prod.get_lista_tareas():
                            writer.writerow([
                                prod.get_id(), t.get_id_tarea_maestra(), # Guardamos ID numérico
                                t.get_unidad_requerida().get_id(), t.get_cant_colaboradores_req(),
                                t.get_tiempo_por_unidad(), t.get_id_habilidad_requerida(), # Guardamos ID numérico
                                getattr(t, '_costo_mano_obra_hora', 0.0)
                            ])
        except IOError as e:
            print(f"-> [ERROR] Falla en el guardado de tareas CSV: {e}")
        except KeyError as e:
            print(f"-> [ERROR] Falla en el guardado de tareas CSV: {e}")
        except ValueError as e:
            print(f"-> [ERROR] Falla en el guardado de tareas CSV: {e}")

    def cargar_tareas_csv(self):
        if not os.path.exists("tareas.csv"): return
        from tarea import Tarea
        try:
            with open("tareas.csv", mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    id_p, id_u = int(fila["ID Producto"]), int(fila["ID Unidad"])
                    prod = next((p for p in self._catalogo_elementos if p.get_id() == id_p), None)
                    unidad = next((unidad for unidad in self._unidades if unidad.get_id() == id_u), None)
                    if prod and unidad:
                        nueva_tarea = Tarea(
                            id_tarea_maestra=int(fila["ID_Tarea_M"]),
                            unidad_requerida=unidad,
                            cant_colaboradores_req=int(fila["Cant Colab"]),
                            tiempo_por_unidad=float(fila["Tiempo"]),
                            id_habilidad_requerida=int(fila["ID_Hab_Req"]),
                            costo_mano_obra_hora=float(fila["Costo MO"])
                        )
                        prod.get_lista_tareas().agregar_al_final(nueva_tarea)
        except IOError as e:
            print(f"-> [ERROR] Falla en la carga de tareas CSV: {e}")
        except KeyError as e:
            print(f"-> [ERROR] Falla en la carga de tareas CSV: {e}")
        except ValueError as e:
            print(f"-> [ERROR] Falla en la carga de tareas CSV: {e}")
    
    def guardar_compras_csv(self):
            try:
                with open("compras.csv", mode='w', newline='', encoding='utf-8') as archivo:
                    writer = csv.writer(archivo)
                    writer.writerow(["ID", "Insumo_ID", "Cantidad", "Estado", "Fecha_Emision", "Fecha_Recepcion"])
                    for compra in self._registro_compras:
                        f_emision = compra._fecha_emision.strftime("%Y-%m-%d %H:%M:%S")
                        f_recepcion = compra._fecha_recepcion.strftime("%Y-%m-%d %H:%M:%S") if compra._fecha_recepcion else ""
                        writer.writerow([compra.get_id(), compra._insumo.get_id(), compra._cantidad, compra._estado, f_emision, f_recepcion])
            except IOError as e:
                print(f"-> [ERROR] Falla en el guardado de compras CSV: {e}")
            except KeyError as e:
                print(f"-> [ERROR] Falla en el guardado de compras CSV: {e}")
            except ValueError as e:
                print(f"-> [ERROR] Falla en el guardado de compras CSV: {e}")

    def cargar_compras_csv(self):
            if not os.path.exists("compras.csv"): return
            from compra_insumo import Compra_Insumo
            try:
                with open("compras.csv", mode='r', encoding='utf-8') as archivo:
                    reader = csv.DictReader(archivo)
                    elementos_id = {e.get_id(): e for e in self._catalogo_elementos}
                    for fila in reader:
                        insumo = elementos_id.get(int(fila["Insumo_ID"]))
                        if insumo:
                            orden = Compra_Insumo(insumo, int(fila["Cantidad"]),id=int(fila["ID"]), estado=fila["Estado"]) 
                            # ponemos manualmente la fecha vieja para no perder el historial
                            orden._fecha_emision = datetime.strptime(fila["Fecha_Emision"], "%Y-%m-%d %H:%M:%S")
                            if fila["Fecha_Recepcion"]:
                                orden._fecha_recepcion = datetime.strptime(fila["Fecha_Recepcion"], "%Y-%m-%d %H:%M:%S")
                            self._registro_compras.append(orden)
                            if orden._estado == "Solicitada":
                                self._cola_entregas.encolar(orden)
            except IOError as e:
                print(f"-> [ERROR] Falla en la carga de compras CSV: {e}")
            except KeyError as e:
                print(f"-> [ERROR] Falla en la carga de compras CSV: {e}")
            except ValueError as e:
                print(f"-> [ERROR] Falla en la carga de compras CSV: {e}")

    def agregar_habilidad(self, nombre: str):
            nuevo_id = len(self._catalogo_habilidades) + 1 if self._catalogo_habilidades else 1
            self._catalogo_habilidades[nuevo_id] = nombre.strip().title()
            self.guardar_catalogos_maestros()
            return nuevo_id

    def agregar_tarea_maestra(self, nombre: str, id_unidad: int, id_habilidad: int):
        nuevo_id = len(self._catalogo_tareas) + 1 if self._catalogo_tareas else 1
        self._catalogo_tareas[nuevo_id] = {
            "nombre": nombre.strip().title(),
            "id_unidad": id_unidad,
            "id_habilidad": id_habilidad
        }
        self.guardar_catalogos_maestros()
        return nuevo_id

    def guardar_catalogos_maestros(self):
        try:
            with open("habilidades.csv", mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Nombre"])
                for id_h, nom in self._catalogo_habilidades.items():
                    writer.writerow([id_h, nom])
                    
            with open("tareas_maestras.csv", mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Nombre", "ID_Unidad", "ID_Habilidad"])
                for id_t, datos in self._catalogo_tareas.items():
                    writer.writerow([id_t, datos["nombre"], datos["id_unidad"], datos["id_habilidad"]])
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura de catálogos: {e}")

    def cargar_catalogos_maestros(self):
        if os.path.exists("habilidades.csv"):
            with open("habilidades.csv", mode='r', encoding='utf-8') as f:
                for fila in csv.DictReader(f):
                    self._catalogo_habilidades[int(fila["ID"])] = fila["Nombre"]
                    
        if os.path.exists("tareas_maestras.csv"):
            with open("tareas_maestras.csv", mode='r', encoding='utf-8') as f:
                for fila in csv.DictReader(f):
                    self._catalogo_tareas[int(fila["ID"])] = {
                        "nombre": fila["Nombre"],
                        "id_unidad": int(fila["ID_Unidad"]),
                        "id_habilidad": int(fila["ID_Habilidad"])
                    }

    # ==========================================================
    # PERSISTENCIA MAESTRA EN CSV
    # ==========================================================
    def guardar_todos_los_csv(self):
        """Centraliza el guardado de todos los archivos del sistema"""
        self.guardar_unidades_csv()
        self.guardar_colaboradores_csv()
        self.guardar_tareas_csv()
        self.guardar_catalogo_csv()
        self.guardar_compras_csv()
        self.guardar_solicitudes_csv()
        self.guardar_catalogos_maestros()
        
        if hasattr(self._inventario, 'guardar_en_csv'):
            self._inventario.guardar_en_csv()

    def cargar_todos_los_csv(self):
        """Centraliza la carga en el orden correcto para evitar dependencias rotas"""
        self.cargar_catalogos_maestros()
        self.cargar_unidades_csv()
        self.cargar_colaboradores_csv()
        self.cargar_catalogo_csv()
        
        if hasattr(self._inventario, 'cargar_desde_csv'):
            self._inventario.cargar_desde_csv(self._catalogo_elementos)
            
        self.cargar_tareas_csv()
        self.cargar_compras_csv()
        self.cargar_solicitudes_csv()
    # ==========================================================
    # metodos que cargan los datos en los menus
    # ==========================================================
    def obtener_diccionario_insumos(self):
        # creo un diccionario nuevo con solo los insumos basicos, filtrando el catalogo por tipo de elemento
        insumos = {}
        for elemento in self._catalogo_elementos:
            if elemento.get_tipo_elemento() == "Insumo Básico":
                insumos[elemento.get_id()] = elemento
        return insumos

    def obtener_diccionario_productos(self):
        #lo mismo que el de insumos pero filtrando por Articulo Fabricado
        productos = {}
        for elemento in self._catalogo_elementos:
            if elemento.get_tipo_elemento() == "Articulo Fabricado":
                productos[elemento.get_id()] = elemento
        return productos

    def obtener_diccionario_unidades(self):
        unidades_dict = {}
        for u in self._unidades:
            unidades_dict[u.get_id()] = u
        return unidades_dict

    def obtener_diccionario_colaboradores(self):
        return self._colaboradores 

    # ==========================================================
    # los metodos que estaban en los menus
    # ==========================================================

    def crear_insumo_basico(self, nombre, costo):
        if not nombre: raise ValueError("El nombre no puede estar vacío.")
        if costo <= 0: raise ValueError("El costo debe ser positivo.")
        
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

        if not tareas_producto.cabecera:
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