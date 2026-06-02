from solicitud_fabricacion import SolicitudDeFabricacion, ESTADOS_VALIDOS

class GestorSolicitudes:
    def __init__(self, empresa):
        self._empresa = empresa
        self._solicitudes = {}

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
                print(f"-> AVISO: No se pudo completar la Solicitud {solicitud.get_id()} por falta de recursos/validación")
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
        materiales_faltantes = list(filter(lambda item: not self._empresa.obtener_inventario().hay_disponibilidad(item[0], item[1]), materiales_necesarios.items()))
        
        if not materiales_faltantes:
            return True

        # Evitar procesar demoradas que ya han generado compras
        if solicitud.get_estado().startswith("Demorada"):
            return False

        for componente, cant_necesaria in materiales_faltantes:
            stock_disponible = self._empresa.obtener_inventario().obtener_stock_disponible(componente)
            faltante = int(cant_necesaria) - int(stock_disponible)
            print(f" [!] Faltan {faltante} unidades de '{componente.get_nombre()}'.")
            # la empresa ejecuta metodo de reabastecimiento
            componente.gestionar_reabastecimiento(self._empresa, faltante)
        
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
                datos_tarea=self._empresa.obtener_catalogo_tareas().get(id_tarea_maestra)
                if isinstance(datos_tarea, dict):
                    nombre_tarea=datos_tarea["nombre"]
                else:
                    print(f"Tarea ID {id_tarea_maestra} no encontrada en catálogo de tareas.")
                print (f" [!] Falta capacidad en la unidad #{unidad.get_id()} para la tarea '{nombre_tarea}'.")
                return False, [], "capacidad"
            colabs_necesarios=tarea.get_cant_colaboradores_req()
            colabs_aptos=tarea.filtrar_colaboradores_aptos(self._empresa.obtener_diccionario_colaboradores(), horas_totales)
            if len(colabs_aptos)<colabs_necesarios:
                id_hab=tarea.get_id_habilidad_requerida()
                nombre_hab=self._empresa.obtener_catalogo_habilidades().get(id_hab, f"Habilidad ID {id_hab}")
                print (f" [!] Falta personal con habilidad '{nombre_hab}' ")
                return False, [], "personal"
            colabs_encontrados=colabs_aptos[:colabs_necesarios]
            asignaciones_pendientes.append((tarea, horas_totales, colabs_encontrados))
        return True, asignaciones_pendientes, None

    def confirmar_reservas(self, solicitud, materiales_necesarios, asignaciones_pendientes):
            print(" -> Stock y Capacidad OK. Confirmando reservas...")
            for componente, cant_necesaria in materiales_necesarios.items():
                self._empresa.obtener_inventario().reservar_stock(componente, cant_necesaria)
                
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
                        self._empresa.obtener_inventario().descontar_stock(componente, cant_necesaria)

                    solicitud.set_estado(ESTADOS_VALIDOS[2])  # En Ejecución
                    print(f"-> ÉXITO: Solicitud #{id_solicitud} ('{producto.get_nombre()}') enviada a producción.")
                    contador_ejecutadas += 1
                    
                except Exception as e:
                    print(f"-> ERROR CRÍTICO en Solicitud #{id_solicitud}")
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
                    self._empresa.obtener_inventario().ingresar_stock(producto, cantidad_pedida)
                    solicitud.marcar_como_terminada()
                    print(f"-> ÉXITO: Solicitud #{id_solicitud} terminada. {cantidad_pedida}x '{producto.get_nombre()}' sumados al stock.")
                    solicitudes_a_archivar.append(solicitud)
                    contador_finalizadas += 1
                except Exception as e:
                    print(f"-> ERROR al finalizar Solicitud #{id_solicitud}")
                                    
        if contador_finalizadas > 0:
            self._empresa.obtener_gestor_archivos().guardar_historial_csv(solicitudes_a_archivar)
            self._solicitudes = dict(filter(lambda item: item[1].get_estado() != ESTADOS_VALIDOS[3], self._solicitudes.items()))
            print(f"-> SISTEMA: Limpieza de memoria. {contador_finalizadas} solicitudes históricas archivadas/borradas.")
        else:
            print("-> AVISO: No hay solicitudes en producción para finalizar.")
    
    def mostrar_solicitudes(self):
        print("\n--- RESUMEN DE SOLICITUDES ---")
        if not self._solicitudes:
            print("No hay solicitudes registradas.")
            return
            
        for solicitud in self._solicitudes.values():
            print(solicitud)
        print("-----------------------------\n")

    def agregar_solicitud(self, id_solicitud, solicitud):
        self._solicitudes[id_solicitud] = solicitud
    
    def obtener_solicitudes(self):
        return self._solicitudes