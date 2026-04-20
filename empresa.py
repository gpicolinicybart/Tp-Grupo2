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

# como la empresa confia en lo que colaboradores y insumo basico le devuelven al preguntar por su tipo de reabastecimiento, no es necesario importar la clase de cada uno, con importar el padre (Elemento) alcanza para que la empresa pueda preguntar por el tipo de reabastecimiento sin necesidad de saber si es un insumo o un articulo fabricado. Esto es polimorfismo puro.
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

    # ==========================================
    # PROCESAMIENTO MODULARIZADO
    # ==========================================
    def procesar_solicitud(self):
        print("\n--- PROCESANDO PLANIFICACIÓN DE PRODUCCIÓN ---")
        for solicitud in list(self._solicitudes.values()): 
            estado = solicitud.get_estado()
            if estado == "Creada" or estado.startswith("Demorada"):
                self._procesar_solicitud_individual(solicitud)

    def _procesar_solicitud_individual(self, solicitud):
        producto = solicitud.get_item_solicitado()
        cantidad_pedida = float(solicitud.get_cantidad()) 
        print(f"\nProcesando Solicitud {solicitud.get_id()} -> Fabricar: {cantidad_pedida}x '{producto.get_nombre()}'")
        
        # 1: EXPLOSIÓN DE MATERIALES
        materiales_necesarios = self._explotar_bom(producto, cantidad_pedida)
        
        # 2: VERIFICAR STOCK (Si falta stock, frena y retorna)
        if not self._gestionar_stock(solicitud, materiales_necesarios):
            return 

        # 3: VERIFICAR CAPACIDAD (Delegación a Tarea)
        exito_capacidad, asignaciones_pendientes = self._gestionar_capacidad(producto, cantidad_pedida)
        if not exito_capacidad:
            solicitud.set_estado("Demorada por falta de capacidad")
            print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Capacidad).")
            return

        # 4: CONFIRMACIÓN Y RESERVA
        self._confirmar_reservas(solicitud, materiales_necesarios, asignaciones_pendientes)

    def _explotar_bom(self, producto, cantidad_pedida) -> dict:
        materiales_necesarios = {}
        for bom in producto.get_bom():
            for componente, cant_unitaria in bom.get_diccionario().items():
                total_necesario = float(cant_unitaria) * float(cantidad_pedida)
                materiales_necesarios[componente] = materiales_necesarios.get(componente, 0) + total_necesario
        return materiales_necesarios

    def _gestionar_stock(self, solicitud, materiales_necesarios) -> bool:
        # Función de alto orden para filtrar faltantes
        materiales_faltantes = list(filter(lambda item: not self._inventario.hay_disponibilidad(item[0], item[1]), materiales_necesarios.items()))
        
        if not materiales_faltantes:
            return True

        # Evitar procesar demoradas que ya han generado compras
        if solicitud.get_estado().startswith("Demorada"):
            return False

        for componente, cant_necesaria in materiales_faltantes:
            stock_disponible = self._inventario.obtener_stock_disponible(componente)
            faltante = cant_necesaria - stock_disponible
            print(f" [!] Faltan {faltante} unidades de '{componente.get_nombre()}'.")
            
            # POLIMORFISMO PURO: La empresa no pregunta qué es, solo ejecuta su método de reabastecimiento
            componente.gestionar_reabastecimiento(self, faltante)
        
        solicitud.set_estado("Demorada por falta de stock")
        print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Stock).")
        return False

    def _gestionar_capacidad(self, producto, cantidad_pedida) -> tuple:
        asignaciones_pendientes = [] 
        for tarea in producto.get_lista_tareas():
            # DELEGACIÓN: La tarea hace sus propios cálculos
            horas_totales = tarea.calcular_horas_totales(cantidad_pedida)
            unidad = tarea.get_unidad_requerida()

            if not unidad.verificar_disponibilidad(horas_totales):
                print(f" [!] Falta capacidad en la Unidad #{unidad.get_id()} para la tarea '{tarea.get_descripcion()}'.")
                return False, []

            colabs_necesarios = tarea.get_cant_colaboradores_req()
            # DELEGACIÓN Y ALTA ORDEN: La tarea filtra a los empleados aptos
            colabs_aptos = tarea.filtrar_colaboradores_aptos(self._colaboradores, horas_totales)

            if len(colabs_aptos) < colabs_necesarios:
                print(f" [!] No hay suficientes colaboradores con la habilidad '{tarea.get_habilidad_requerida()}' y {horas_totales}hs libres.")
                return False, []
            
            colabs_encontrados = colabs_aptos[:colabs_necesarios]
            asignaciones_pendientes.append((tarea, horas_totales, colabs_encontrados))
            
        return True, asignaciones_pendientes

    def _confirmar_reservas(self, solicitud, materiales_necesarios, asignaciones_pendientes):
        print(" -> Stock y Capacidad OK. Confirmando reservas...")
        for componente, cant_necesaria in materiales_necesarios.items():
            self._inventario.reservar_stock(componente, cant_necesaria)
            
        for tarea, horas, colabs in asignaciones_pendientes:
            # DELEGACIÓN: La tarea ejecuta sus reservas internamente
            tarea.ejecutar_reservas(horas, colabs)
                
        solicitud.set_estado("Procesada y Planificada")
        print(f" -> Solicitud {solicitud.get_id()} PROCESADA CON ÉXITO.")

    # ==========================================
    # EJECUCIÓN Y FINALIZACIÓN
    # ==========================================
    def ejecutar_solicitud(self):
        print("\n--- EJECUTANDO ÓRDENES PLANIFICADAS ---")
        contador_ejecutadas = 0
        
        for id_solicitud, solicitud in self._solicitudes.items():
            
            # Solo actuamos sobre las que están listas
            if solicitud.get_estado() == "Procesada y Planificada":
                try:
                    producto = solicitud.get_item_solicitado()
                    cantidad_pedida = solicitud.get_cantidad()

                    materiales_necesarios = self._explotar_bom(producto, cantidad_pedida)
                    
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
        
        for id_solicitud, solicitud in list(self._solicitudes.items()):
            
            if solicitud.get_estado() == "En Ejecución": 
                try:
                    producto = solicitud.get_item_solicitado()
                    cantidad_pedida = int(solicitud.get_cantidad())
                    
                    self._inventario.ingresar_stock(producto, cantidad_pedida)
                    
                    solicitud.marcar_como_terminada()
                    print(f"-> ÉXITO: Solicitud #{id_solicitud} terminada. {cantidad_pedida}x '{producto.get_nombre()}' sumados al stock.")
                    contador_finalizadas += 1
                except Exception as e:
                    print(f"-> ERROR al finalizar Solicitud #{id_solicitud}: {e}")

        
        if contador_finalizadas > 0:
            self._solicitudes = dict(filter(lambda item: item[1].get_estado() != "Terminada", self._solicitudes.items()))
            print(f"-> SISTEMA: Limpieza de memoria. {contador_finalizadas} solicitudes históricas archivadas/borradas.")
        else:
            print("-> AVISO: No hay solicitudes en producción para finalizar.")
            
    # ==========================================
    # REPORTES Y OTROS MÉTODOS
    # ==========================================



    #consigna de implementacion 

    def generar_reporte_materiales_criticos(self, producto, cantidad_pedida: int):
        necesidades = producto.calcular_materiales_necesarios(cantidad_pedida)
        criticos = self._inventario.obtener_materiales_criticos(necesidades)
        
        if not criticos:
            print(f"-> [INFO] Reporte : NO hay materiales críticos para '{producto.get_nombre()}'. El stock se encuentra en niveles aceptables.")
            return
            
        nombre_archivo = f"criticos_{producto.get_id()}.csv"
        try:
            with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID Insumo", "Nombre", "Cant. Necesaria", "Stock Actual", "Cobertura"])
                
                for insumo, cant_nec in criticos:
                    stock = self._inventario.consultar_stock(insumo)
                    
                    if cant_nec > 0:
                        porcentaje = (stock / cant_nec) * 100    #el porcentaje es el porcentaje de la cantidad necesaria que nuestro stock actual cubre
                        cobertura = f"{porcentaje:.1f}%"
                    else:
                        cobertura = "0%"
                        
                    writer.writerow([insumo.get_id(), insumo.get_nombre(), cant_nec, stock, cobertura])
                    
            print(f"-> [CSV OK] Reporte de críticos generado en: '{nombre_archivo}'.")
                
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura del archivo: {e}")

    
    def generar_reporte_estado_planta(self, lista_unidades: list):
        print("\n" + "="*55)
        print("   REPORTE GLOBAL DE ESTADO DE PLANTA Y CUELLOS DE BOTELLA")
        print("="*55)
        
        print("\n[1] ESTADO DE MÁQUINAS:")
        if not lista_unidades:
            print("  No hay unidades registradas.")
        else:
            unidad_critica = max(lista_unidades, key=lambda x: x.get_porcentaje_uso())
            for x in lista_unidades:
                print(f"  - Unidad #{x.get_id()} ({x.get_nombre()}): {x.get_porcentaje_uso():.1f}% de ocupación.")
            
            if unidad_critica.get_porcentaje_uso() > 0:
                print(f"  >>> MÁQUINA MÁS EXIGIDA: {unidad_critica.get_nombre()}")

       
        print("\n[2] ANÁLISIS DE DEMORAS (CUELLOS DE BOTELLA):")
        
        d_stock = len(list(filter(lambda t: t.get_estado() == "Demorada por falta de stock", self._solicitudes.values())))
        d_capacidad = len(list(filter(lambda t: t.get_estado() == "Demorada por falta de capacidad", self._solicitudes.values())))
        d_personal = len(list(filter(lambda t: t.get_estado() == "Demorada por falta de colaboradores", self._solicitudes.values())))
        
        print(f"  - Frenadas por FALTA DE INSUMOS: {d_stock}")
        print(f"  - Frenadas por CAPACIDAD DE MÁQUINA: {d_capacidad}")
        print(f"  - Frenadas por ESCASEZ DE COLABORADORES: {d_personal}")
        
        demoras = {
            "FALTA DE INSUMOS": d_stock,
            "SOBRECARGA DE MÁQUINAS": d_capacidad,
            "ESCASEZ DE COLABORADORES": d_personal
        }
        
        cuello_principal = max(demoras, key=demoras.get)
        
        if demoras[cuello_principal] > 0:
            print(f"\n>>> CONCLUSIÓN: El cuello de botella principal del sistema es {cuello_principal}.")
        else:
            print("\n>>> CONCLUSIÓN: Flujo perfecto. No hay cuellos de botella activos.")
        
    def calcular_sobrecarga_maquina(self, unidad, producto, cantidad: int):
        carga_necesaria = producto.calcular_horas_en_unidad(unidad, cantidad)
        capacidad_max = unidad.get_capacidad_max_horas()

        print(f"\n--- CÁLCULO DE SOBRECARGA PREDICTIVA: {unidad.get_nombre()} ---")
        print(f"Carga requerida: {carga_necesaria:.2f} hs | Capacidad instalada: {capacidad_max:.2f} hs")

        if carga_necesaria > capacidad_max:
            sobrecarga = carga_necesaria - capacidad_max
            print(f">>> ALERTA: Sobrecarga detectada. La máquina colapsará por un exceso de {sobrecarga:.2f} hs.")
        else:
            print(">>> OK: La máquina tiene capacidad suficiente para absorber este pedido.")


    #codigo de detectar cuello de botella que estaba antes (lo dejo por las dudas por ahora despues veanlo y decidan si lo dejamos o no)
    #yo trate de combinarlo con lo nuevo  de arriba pero por las dudas no lo borre, lo dejo comentado 

    '''def detectar_cuello_botella(self):
        print("\n" + "="*45)
        print("   REPORTE DE ESTADO DE PLANTA Y CUELLOS")
        print("="*45)
        
        if not self._unidades:
            print("No hay unidades de trabajo registradas para analizar.")
        else:
            unidad_critica = None
            max_porcentaje = -1.0

            for unidad in self._unidades:
                try:
                    porcentaje = unidad.get_porcentaje_uso() 
                    print(f"Unidad #{unidad.get_id()}: {porcentaje:.1f}% de ocupación.")

                    if porcentaje > max_porcentaje:
                        max_porcentaje = porcentaje
                        unidad_critica = unidad
                except AttributeError:
                    print(f"Unidad #{unidad.get_id()}: (Falta método get_porcentaje_uso)")

            if unidad_critica and max_porcentaje > 0:
                print(f"\n>>> ALERTA CAPACIDAD MÁQUINA: Unidad #{unidad_critica.get_id()} al {max_porcentaje:.1f}%")
            else:
                print("\nLa planta se encuentra sin carga de trabajo en las máquinas.")

        print("\n--- DIAGNÓSTICO DE DEMORAS GLOBALES ---")
        demoras_stock = 0
        demoras_capacidad = 0
        
        for solicitud in self._solicitudes.values():
            estado = solicitud.get_estado()
            if estado == "Demorada por falta de stock":
                demoras_stock += 1
            elif estado == "Demorada por falta de capacidad":
                demoras_capacidad += 1
                
        print(f"  - Solicitudes frenadas por STOCK: {demoras_stock}")
        print(f"  - Solicitudes frenadas por CAPACIDAD: {demoras_capacidad}")
        
        if demoras_stock > demoras_capacidad and demoras_stock > 0:
            print("\n>>> CONCLUSIÓN: El cuello de botella principal es la GESTIÓN DE COMPRAS/STOCK.")
        elif demoras_capacidad > demoras_stock and demoras_capacidad > 0:
            print("\n>>> CONCLUSIÓN: El cuello de botella principal es la CAPACIDAD OPERATIVA (Invertir en máquinas/personal).")
        elif demoras_stock == demoras_capacidad and demoras_stock > 0:
            print("\n>>> CONCLUSIÓN: Hay demoras críticas tanto en stock como en capacidad operativa.")
        else:
            print("\n>>> CONCLUSIÓN: Flujo perfecto. No hay demoras detectadas.")
        print("="*45 + "\n")'''

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
