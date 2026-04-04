

from inventario import Inventario
from compra_insumo import Compra_Insumo
from solicitud_fabricacion import SolicitudDeFabricacion
from colaboradores import Colaborador
from unidad_de_trabajo import UnidadDeTrabajo
from elemento import Elemento
from articulo_fabricado import ArticuloFabricadoInternamente
from insumo_basico import InsumoBasico


#-----------------------------------------------------------------------------------------------------------------------------
#IMPORTANTE NOTA: gemini me dijo que en solicitud de fabricacion no deberia ser quien planifica ejecuta y finaliza porque 
# le das el poder de hacer las cosas que en realidad maneja la empresa, por eso esta aca ahora todo: y solicitud 
#queda como un objeto que solo tiene la info de lo que se pidió, y la empresa es quien se encarga de procesar esa solicitud, 
# chequear stock, asignar tareas, etc.
#------------------------------------------------------------------------------------------------------------------------------


class Empresa:
    def __init__(self, inventario: Inventario):
        self._inventario = inventario
        self._catalogo_elementos = []
        self._solicitudes = []
        self._unidades = []
        self._habilidades = [] 
        self._colaboradores = []
        self._compras_pendientes = []
        
    def registrar_compra(self,orden: Compra_Insumo):
        self._compras_pendientes.append(orden)
        print(f"EMPRESA: Se registró la orden de compra {orden._id} por {orden._cantidad} unidades de '{orden._insumo._nombre}'.")
    def crear_solicitud (self,solicitud: SolicitudDeFabricacion):
          self._solicitudes.append(solicitud)
          print(f"EMPRESA: Se registró una nueva solicitud de fabricación (ID:{solicitud._id})")

    def procesar_solicitud(self):
        
        for solicitud in list(self._solicitudes): 
            # Solo procesamos las "Creada" o las que estaban demoradas
            estado = solicitud.get_estado()
            if estado == "Creada" or "Demorada" in estado:
                
                producto = solicitud.get_item_solicitado()
                cantidad_pedida = solicitud._cantidad 
                print(f"\nProcesando Solicitud {solicitud.get_id()} -> Fabricar: {cantidad_pedida}x '{producto.get_nombre()}'")
                
                # ==========================================
                # FASE 1: EXPLOSIÓN DE MATERIALES Y STOCK
                # ==========================================
                materiales_necesarios = {}
                for bom in producto.get_bom():
                    for componente, cant_unitaria in bom.get_diccionario().items():
                        total_necesario = cant_unitaria * cantidad_pedida
                        if componente in materiales_necesarios:
                            materiales_necesarios[componente] += total_necesario
                        else:
                            materiales_necesarios[componente] = total_necesario
                
                todo_disponible = True
                for componente, cant_necesaria in materiales_necesarios.items():
                    if not self._inventario.hay_disponibilidad(componente, cant_necesaria):
                        todo_disponible = False
                        stock_real = self._inventario.consultar_stock(componente) - self._inventario._stock_reservado.get(componente, 0)
                        faltante = cant_necesaria - stock_real
                        
                        print(f" [!] Faltan {faltante} unidades de '{componente.get_nombre()}'.")
                        
                        # Generación automática de órdenes
                        if isinstance(componente, InsumoBasico):
                            id_compra = len(self._compras_pendientes) + 1000
                            self.registrar_compra(Compra_Insumo(id_compra, componente, faltante))
                        elif isinstance(componente, ArticuloFabricadoInternamente):
                            id_solicitud_hija = len(self._solicitudes) + 5000
                            from solicitud_fabricacion import SolicitudDeFabricacion # Importación local para evitar ciclos
                            self.crear_solicitud(SolicitudDeFabricacion(id_solicitud_hija, componente, faltante, False))
                
                # Si faltan materiales, frenamos acá y pasamos a la siguiente solicitud
                if not todo_disponible:
                    solicitud._estado = "Demorada por falta de stock"
                    print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Stock).")
                    continue 

                # ==========================================
                # FASE 2: ASIGNACIÓN DE TIEMPO Y PERSONAL
                # ==========================================
                recursos_disponibles = True
                asignaciones_pendientes = [] # Guardamos a quién elegimos antes de confirmar

                for tarea in producto.get_lista_tareas():
                    horas_totales = tarea.get_tiempo_por_unidad() * solicitud.get_cantidad_pedida()
                    unidad = tarea._unidad_requerida

                    # 2A. Chequear Máquina (Unidad de Trabajo)
                    if not unidad.verificar_disponibilidad(horas_totales):
                        print(f" [!] Falta capacidad en la Unidad #{unidad.get_id()} para la tarea '{tarea.get_descripcion()}'.")
                        recursos_disponibles = False
                        break 

                    # 2B. Buscar Colaboradores
                    colabs_necesarios = tarea._cant_colaboradores_req
                    colabs_encontrados = []

                    for colab in self._colaboradores:
                        if colab.tiene_habilidad(tarea._habilidad_requerida) and colab.verificar_disponibilidad(horas_totales):
                            colabs_encontrados.append(colab)
                            if len(colabs_encontrados) == colabs_necesarios:
                                break # Ya encontramos a todos los necesarios para esta tarea

                    if len(colabs_encontrados) < colabs_necesarios:
                        print(f" [!] No hay suficientes colaboradores con la habilidad '{tarea._habilidad_requerida}' y {horas_totales}hs libres.")
                        recursos_disponibles = False
                        break
                    else:
                        asignaciones_pendientes.append((tarea, unidad, horas_totales, colabs_encontrados))

                # ==========================================
                # FASE 3: CONFIRMACIÓN Y RESERVA
                # ==========================================
                if recursos_disponibles:
                    print(f" -> Stock y Capacidad OK. Confirmando reservas...")
                    
                    # 1. Reservar Materiales
                    for componente, cant_necesaria in materiales_necesarios.items():
                        self._inventario.reservar_stock(componente, cant_necesaria)
                        
                    # 2. Reservar Máquinas y Asignar Tareas a Colaboradores
                    for tarea, unidad, horas, colabs in asignaciones_pendientes:
                        unidad.reservar_horas(horas) 
                        for colab in colabs:
                          colab.asignar_tarea(tarea._habilidad_requerida, horas)
                            
                    solicitud._estado = "Planificada"
                    print(f" -> Solicitud {solicitud.get_id()} PLANIFICADA CON ÉXITO.")
                else:
                    solicitud._estado = "Demorada por falta de capacidad"
                    print(f" -> Solicitud {solicitud.get_id()} DEMORADA (Falta Capacidad).")

    def ejecutar_solicitud(self, id_solicitud: int):
        # Buscamos la solicitud por su ID
        for solicitud in self._solicitudes:
            if solicitud.get_id() == id_solicitud:
                if solicitud.get_estado() == "Planificada":
                    print(f"\n[Empresa] Ejecutando solicitud {id_solicitud}. La producción arranca...")
                    producto = solicitud.get_item_solicitado()
                    cantidad_pedida = solicitud.get_cantidad()
                    
                    # Descontamos físicamente los materiales del inventario
                    for bom in producto.get_bom():
                        for componente, cant_unitaria in bom.get_diccionario().items():
                            total_a_descontar = cant_unitaria * cantidad_pedida
                            self._inventario.descontar_stock(componente, total_a_descontar)
                    
                    solicitud._estado = "En curso"
                    return True
                else:
                    print(f"\n[Error] No se puede ejecutar la solicitud {id_solicitud}. Estado actual: {solicitud.get_estado()}")
                    return False
                    
        print(f"[Error] Solicitud {id_solicitud} no encontrada.")
        return False

    def finalizar_solicitud(self, id_solicitud: int):
        # Buscamos la solicitud por su ID
        for solicitud in self._solicitudes:
            if solicitud.get_id() == id_solicitud:
                if solicitud.get_estado() == "En curso":
                    print(f"\n[Empresa] Finalizando solicitud {id_solicitud}. Producción terminada.")
                    producto = solicitud.get_item_solicitado()
                    cantidad_pedida = solicitud._cantidad
                    
                    # Ingresamos el producto terminado al inventario
                    self._inventario.ingresar_stock(producto, cantidad_pedida)
                    
                    solicitud._estado = "Terminada"
                    return True
                else:
                    print(f"\n[Error] No se puede finalizar la solicitud {id_solicitud}. Estado actual: {solicitud.get_estado()}")
                    return False
                    
        print(f"[Error] Solicitud {id_solicitud} no encontrada.")
        return False



    def detectar_cuello_botella(self):
        pass
#estos dos no estan en el diagrama 

    def agregar_colaborador(self, nuevo_colaborador: Colaborador):
        self._colaboradores.append(nuevo_colaborador)
        print(f"EMPRESA: Colaborador ID:{nuevo_colaborador._id} agregado al equipo.")

    def agregar_unidad_trabajo(self, nueva_unidad: UnidadDeTrabajo):
        self._unidades.append(nueva_unidad)
    def registrar_producto_nuevo(self, producto: Elemento):
        """
        Punto de entrada para agregar cosas al catálogo. 
        Aquí es donde usamos el 'validar_ciclos' como guardia de seguridad.
        """
        try:
            # Solo validamos ciclos si es algo que se fabrica
            if isinstance(producto, ArticuloFabricadoInternamente):
                producto.validar_ciclos() # Si hay ciclo, salta al except
            
            self._catalogo_elementos.append(producto)
            print(f"EMPRESA: '{producto._nombre}' registrado exitosamente en el catálogo.")
            
        except ValueError as e:
            print(f"EMPRESA - ERROR AL REGISTRAR: {e}")

    def obtener_presupuesto(self, producto: Elemento, cantidad: int) -> float:
        """
        Método para informarle al cliente cuánto le va a salir.
        Usa el 'get_costo_unitario' del producto.
        """
        costo_unitario = producto.get_costo_unitario()
        total = costo_unitario * cantidad
        print(f"PRESUPUESTO: Fabricar {cantidad} unidades de '{producto._nombre}' cuesta ${total:.2f}")
        return total



