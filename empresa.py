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
        """Itera sobre las solicitudes pendientes y llama al procesador individual"""
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
            accion = componente.get_tipo_reabastecimiento()
            
            if accion == "COMPRAR":
                id_compra = self._contador_id_compras
                self._contador_id_compras += 1
                self.registrar_compra(Compra_Insumo(id_compra, componente, faltante))
            elif accion == "FABRICAR":
                id_solicitud_hija = self._contador_id_solicitudes_hijas
                self._contador_id_solicitudes_hijas += 1
                self.crear_solicitud(SolicitudDeFabricacion(id_solicitud_hija, componente, faltante, False))
        
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
    def ejecutar_solicitud(self, id_solicitud: int):
        solicitud = self._solicitudes.get(id_solicitud)
        
        if not solicitud:
            print(f"[Error] Solicitud {id_solicitud} no encontrada.")
            return False

        if solicitud.get_estado() == "Procesada y Planificada" or solicitud.get_estado() == "Planificada":
            print(f"\n[Empresa] Ejecutando solicitud {id_solicitud}. La producción arranca...")
            producto = solicitud.get_item_solicitado()
            cantidad_pedida = solicitud.get_cantidad()
            
            for bom in producto.get_bom():
                for componente, cant_unitaria in bom.get_diccionario().items():
                    total_a_descontar = float(cant_unitaria) * float(cantidad_pedida)
                    self._inventario.descontar_stock(componente, int(total_a_descontar))
            
            solicitud.set_estado("En curso")
            return True
        else:
            print(f"\n[Error] No se puede ejecutar la solicitud {id_solicitud}. Estado actual: {solicitud.get_estado()}")
            return False

    def finalizar_solicitud(self, id_solicitud: int):
        solicitud = self._solicitudes.get(id_solicitud)
        
        if not solicitud:
            print(f"[Error] Solicitud {id_solicitud} no encontrada.")
            return False

        if solicitud.get_estado() == "En curso":
            print(f"\n[Empresa] Finalizando solicitud {id_solicitud}. Producción terminada.")
            producto = solicitud.get_item_solicitado()
            cantidad_pedida = float(solicitud.get_cantidad())
            
            self._inventario.ingresar_stock(producto, cantidad_pedida)
            solicitud.set_estado("Terminada")
            
            # FUNCION DE ALTO ORDEN: Limpiar el diccionario eliminando las solicitudes "Terminadas"
            self._solicitudes = dict(filter(lambda item: item[1].get_estado() != "Terminada", self._solicitudes.items()))
            print(f"[Sistema] Limpieza: Solicitud {id_solicitud} borrada de la memoria activa.")
            
            return True
        else:
            print(f"\n[Error] No se puede finalizar la solicitud {id_solicitud}. Estado actual: {solicitud.get_estado()}")
            return False

    # ==========================================
    # REPORTES Y OTROS MÉTODOS
    # ==========================================
    def detectar_cuello_botella(self):
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
        print("="*45 + "\n")

    def mostrar_solicitudes(self):
        print("\n--- RESUMEN DE SOLICITUDES ---")
        if not self._solicitudes:
            print("No hay solicitudes registradas.")
            return
            
        for solicitud in self._solicitudes.values():
            print(solicitud)
        print("-----------------------------\n")

    def mostrar_colaboradores(self):
        print("\n--- NÓMINA DE EMPLEADOS ---")
        if not self._colaboradores:
            print("No hay colaboradores registrados.")
            return
            
        for colab in self._colaboradores.values():
            print(colab) 
        print("---------------------------\n")

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

    def obtener_presupuesto(self, producto: Elemento, cantidad: int) -> float:
        costo_unitario = producto.get_costo_unitario()
        total = costo_unitario * cantidad
        print(f"PRESUPUESTO: Fabricar {cantidad} unidades de '{producto.get_nombre()}' cuesta ${total:.2f}")
        return total