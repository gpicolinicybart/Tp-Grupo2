#------------------------------------------------------------------------------------------------------------------------------
# IMPORTANTE NOTA: La empresa centraliza el procesamiento (revisa stock, asigna tareas).
# La solicitud queda como un objeto de datos puro.
#------------------------------------------------------------------------------------------------------------------------------
from inventario import Inventario
from compra_insumo import Compra_Insumo
from solicitud_fabricacion import SolicitudDeFabricacion
from unidad_de_trabajo import UnidadDeTrabajo
from elemento import Elemento
from articulo_fabricado import ArticuloFabricadoInternamente
from datetime import datetime
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
        self._habilidades = [] 
        self._colaboradores = {}
        self._compras_pendientes = []
        self._contador_id_compras = 1000
        self._contador_id_solicitudes_hijas = 5000
        
    def registrar_compra(self, orden: Compra_Insumo):
        self._compras_pendientes.append(orden)
        print(f"EMPRESA: Se registró la orden de compra {orden.get_id()}...")

    def crear_solicitud(self, solicitud: SolicitudDeFabricacion):
        self._solicitudes[solicitud.get_id()] = solicitud
        print(f"EMPRESA: Se registró una nueva solicitud de fabricación (ID:{solicitud.get_id()})")

    def procesar_solicitud(self):
        print("\n--- PROCESANDO PLANIFICACIÓN DE PRODUCCIÓN ---")
        elegibles = [s for s in self._solicitudes.values() 
                 if s.get_estado() == "Creada" or s.get_estado().startswith("Demorada")]
    
        if not elegibles:
            print("-> AVISO: No hay solicitudes para procesar. Creá una con la opción 5 o esperá a que lleguen insumos (opción 14) si hay demoradas.")
            return
    
        for solicitud in elegibles:
            self.procesar_solicitud_individual(solicitud)


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
            solicitud.set_estado("Demorada por falta de capacidad")
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
        
        solicitud.set_estado("Demorada por falta de stock")
        print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Stock).")
        return False

    def gestionar_capacidad(self, producto, cantidad_pedida) -> tuple:
        asignaciones_pendientes = [] 
        lista_tareas = producto.get_lista_tareas()

        #Si no hay tareas, frena la planificación
        if not lista_tareas:
            print(f" [!] ERROR: El producto '{producto.get_nombre()}' no tiene tareas asignadas para su fabricación.")
            return False, []

        for tarea in lista_tareas:
            # la tarea hace sus propios calculos
            horas_totales = tarea.calcular_horas_totales(cantidad_pedida)
            unidad = tarea.get_unidad_requerida()
            if not unidad.verificar_disponibilidad(horas_totales):
                print(f" [!] Falta capacidad en la Unidad #{unidad.get_id()} para la tarea '{tarea.get_descripcion()}'.")
                return False, [] # hay q poner esa lista vacia xq es tuple y tiene q tener si o si 2 variables de retorno aunque no se usen
            colabs_necesarios = tarea.get_cant_colaboradores_req()
            colabs_aptos = tarea.filtrar_colaboradores_aptos(self._colaboradores, horas_totales)
            if len(colabs_aptos) < colabs_necesarios:
                print(f" [!] No hay suficientes colaboradores con la habilidad '{tarea.get_habilidad_requerida()}' y {horas_totales}hs libres.")
                return False, []
            colabs_encontrados = colabs_aptos[:colabs_necesarios]
            asignaciones_pendientes.append((tarea, horas_totales, colabs_encontrados))
        return True, asignaciones_pendientes

    def confirmar_reservas(self, solicitud, materiales_necesarios, asignaciones_pendientes):
            print(" -> Stock y Capacidad OK. Confirmando reservas...")
            for componente, cant_necesaria in materiales_necesarios.items():
                self._inventario.reservar_stock(componente, cant_necesaria)
                
            for tarea, horas, colabs in asignaciones_pendientes:
                # la tarea ejecuta sus reservas internamente
                tarea.ejecutar_reservas(horas, colabs)
                
                # anoto a los colaboradores en la solicitud ---
                for colab in colabs:
                    solicitud.agregar_colaborador(colab.get_id())
                    
            solicitud.set_estado("Procesada y Planificada")
            print(f" -> Solicitud {solicitud.get_id()} PROCESADA CON ÉXITO.")

   
    def ejecutar_solicitud(self):
        print("\n--- EJECUTANDO ÓRDENES PLANIFICADAS ---")
        contador_ejecutadas = 0
        
        for id_solicitud, solicitud in self._solicitudes.items():
            
            # Solo actuamos sobre las que están listas
            if solicitud.get_estado() == "Procesada y Planificada":
                try:
                    producto = solicitud.get_item_solicitado()
                    cantidad_pedida = solicitud.get_cantidad()

                    materiales_necesarios = self.explotar_bom(producto, cantidad_pedida)
                    
                    for componente, cant_necesaria in materiales_necesarios.items():
                        self._inventario.descontar_stock(componente, cant_necesaria)

                    solicitud.set_estado("En Ejecución")
                    print(f"-> ÉXITO: Solicitud #{id_solicitud} ('{producto.get_nombre()}') enviada a producción.")
                    contador_ejecutadas += 1
                    
                except Exception as e:
                    print(f"-> ERROR CRÍTICO en Solicitud #{id_solicitud}: {e}")
                    solicitud.set_estado("Demorada por Error Interno")

        
        if contador_ejecutadas == 0:
            print("-> AVISO: No se encontraron solicitudes en estado 'Procesada y Planificada' para ejecutar.")
        else:
            print(f"-> RESUMEN: {contador_ejecutadas} solicitudes han iniciado su producción.")

    
    def finalizar_solicitud(self):
            
            print("\n--- FINALIZANDO ÓRDENES EN PRODUCCIÓN ---")
            contador_finalizadas = 0
            solicitudes_a_archivar = []
            
            for id_solicitud, solicitud in list(self._solicitudes.items()):
                
                if solicitud.get_estado() == "En Ejecución": 
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
                self._solicitudes = dict(filter(lambda item: item[1].get_estado() != "Terminada", self._solicitudes.items()))
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
            #recorre las órdenes y actualiza el inventario
            pendientes = list(filter(lambda orden: orden._fecha_recepcion is None, self._compras_pendientes))
            if not pendientes:
                return 0
            for orden in pendientes:
                orden.recibir_materiales(self._inventario)
                
            return len(pendientes)  
        
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
    #si no hay críticos, solo avisamos por consola (la consigna pide q se cree igual el archivo)
                    print(f"-> [INFO] Reporte: NO hay materiales críticos para '{producto.get_nombre()}'. Stock en niveles aceptables.")
                else:
                    for insumo, cant_nec in criticos:
                        stock = self._inventario.consultar_stock(insumo)
                        porcentaje = (stock / cant_nec) * 100  # se puede calcular directo xq cant_nec siempre es > 0
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
        else:
            unidad_critica = max(lista_unidades, key=lambda x: x.get_porcentaje_uso())
            for x in lista_unidades:
                print(f"  - Unidad #{x.get_id()} ({x.get_nombre()}): {x.get_porcentaje_uso():.1f}% de ocupación.")
            
            if unidad_critica.get_porcentaje_uso() > 0:
                print(f"  >>> UNIDAD DE TRABAJO MÁS EXIGIDA: {unidad_critica.get_nombre()}")

       
        print("\n[2] ANÁLISIS DE DEMORAS (CUELLOS DE BOTELLA):")
        
        d_stock = len(list(filter(lambda t: t.get_estado() == "Demorada por falta de stock", self._solicitudes.values())))
        d_capacidad = len(list(filter(lambda t: t.get_estado() == "Demorada por falta de capacidad", self._solicitudes.values())))
        d_personal = len(list(filter(lambda t: t.get_estado() == "Demorada por falta de colaboradores", self._solicitudes.values())))
        
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

    def agregar_unidad_trabajo(self, nueva_unidad: UnidadDeTrabajo):
        self._unidades.append(nueva_unidad)

    def registrar_producto_nuevo(self, producto: Elemento):
        try:
            if isinstance(producto, ArticuloFabricadoInternamente):
                producto.validar_ciclos() 
            self._catalogo_elementos.append(producto)
            print(f"EMPRESA: '{producto.get_nombre()}' registrado exitosamente en el catálogo.")
        except ValueError as e:
            print(f"EMPRESA - ERROR AL REGISTRAR: {e}")