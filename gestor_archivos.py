import csv
import os
from datetime import datetime
from solicitud_fabricacion import SolicitudDeFabricacion
from itembom import ItemBOM
from lista_tareas import ListaEnlazadaTareas

class GestorArchivos:
    def __init__(self, empresa):
        self.empresa = empresa

    def guardar_historial_csv (self,solicitudes_terminadas: list):
        nombre_archivo = "csv/historial_solicitudes.csv"
        archivo_existe=os.path.isfile(nombre_archivo)
        try:
            with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                if not archivo_existe:
                    escritor_csv.writerow(["ID Solicitud", "Producto", "Cantidad", "Fecha Creación", "Fecha Finalización", "Tiempo Transcurrido (horas)"])
                for solicitud in solicitudes_terminadas:
                    id_sol= solicitud.get_id()
                    producto= solicitud.get_item_solicitado().get_nombre()
                    cantidad= solicitud.get_cantidad()
                    fecha_creacion= solicitud.get_fecha_creacion().strftime("%d/%m/%Y %H:%M")
                    if solicitud.get_fecha_finalizacion():
                        fecha_finalizacion= solicitud.get_fecha_finalizacion().strftime("%d/%m/%Y %H:%M")
                        tiempo_hs=round((solicitud.get_fecha_finalizacion() - solicitud.get_fecha_creacion()).total_seconds()/3600,2)
                    else:
                        fecha_finalizacion="N/A"
                        tiempo_hs="N/A"
                    escritor_csv.writerow([id_sol, producto, cantidad, fecha_creacion, fecha_finalizacion, tiempo_hs])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado del historial CSV")

    def guardar_solicitudes_csv(self):
        try: 
            with open("csv/solicitudes_activas.csv", mode='w', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                escritor_csv.writerow(["ID Solicitud", "Producto", "Cantidad", "Estado", "Fecha Creacion"])
                for solicitud in self.empresa.obtener_solicitudes().values():
                    escritor_csv.writerow([
                        solicitud.get_id(),
                        solicitud.get_item_solicitado().get_nombre(),
                        solicitud.get_cantidad(),
                            solicitud.get_estado(),
                            solicitud.get_fecha_creacion().strftime("%d/%m/%Y %H:%M")])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado de solicitudes activas CSV")

    def guardar_catalogo_csv(self):
        try:
            with open("csv/productos.csv", mode='w', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                escritor_csv.writerow(["ID Producto", "Nombre Producto","Tipo", "Costo Fijo","Stock Fisico", "Stock Reservado", "Receta BOM"])
                for prod in self.empresa.obtener_elementos_catalogo():
                    fisico=self.empresa.obtener_inventario().consultar_stock(prod)
                    reservado=self.empresa.obtener_inventario().obtener_stock_reservado(prod)
                    tipo=prod.get_tipo_elemento()
                    
                    if tipo=="Articulo Fabricado":
                        bom_str_lista=[]
                        for bom_item in prod.get_bom():
                            for elemento,cantidad in bom_item.get_diccionario().items():
                                bom_str_lista.append(f"{elemento.get_id()}: {cantidad}")
                        receta_str=";".join(bom_str_lista)
                        escritor_csv.writerow([prod.get_id(), prod.get_nombre(), tipo, 0.0, fisico, reservado, receta_str])
                        
                    elif tipo=="Insumo Básico": # El insumo SÍ tiene get_costo_fijo()
                        escritor_csv.writerow([prod.get_id(), prod.get_nombre(), tipo, prod.get_costo_fijo(), fisico, reservado, ""])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado del catálogo CSV")

    def guardar_inventario_csv(self):
        inventario = self.empresa.obtener_inventario()
        if hasattr(inventario, 'guardar_en_csv'):
            inventario.guardar_en_csv()
        else:
            print(f"[AVISO] Falta implementar guardar_en_csv() en la clase Inventario.")

    def guardar_unidades_csv(self):
        try:
            with open("csv/unidades.csv", mode='w', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                escritor_csv.writerow(["ID Unidad", "Nombre", "Capacidad", "Costo Operativo"])
                for unidad in self.empresa.obtener_unidades():
                    escritor_csv.writerow([unidad.get_id(), unidad.get_nombre(), unidad.get_capacidad_max_horas(), unidad.get_costo_operativo()])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado de unidades CSV")

    def guardar_colaboradores_csv(self):
        try:
            with open("csv/colaboradores.csv", mode='w', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                escritor_csv.writerow(["ID Colaborador", "Habilidades_IDs", "Horas Disponibles", "Salario Hora", "Fecha Alta", "Fecha Baja"])
                for colaborador in self.empresa.obtener_diccionario_colaboradores().values():
                    habilidades_str = ";".join(map(str, colaborador.get_habilidades()))
                    f_alta = colaborador.get_fecha_alta().strftime("%Y-%m-%d %H:%M:%S")
                    if colaborador.get_fecha_baja() is not None:
                        f_baja = colaborador.get_fecha_baja().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        f_baja = ""
                    escritor_csv.writerow([colaborador.get_id(), habilidades_str, colaborador.get_horas_disponibles(), colaborador.get_salario_hora(), f_alta, f_baja])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado de colaboradores CSV")

    def guardar_tareas_csv(self):
            try:
                with open("csv/tareas.csv", mode='w', newline='', encoding='utf-8') as archivo:
                    writer = csv.writer(archivo)
                    writer.writerow(["ID Producto", "ID_Tarea_M", "ID Unidad", "Cant Colab", "Tiempo", "ID_Hab_Req", "Costo MO"])
                    for prod in self.empresa.obtener_elementos_catalogo():
                        if hasattr(prod, 'get_lista_tareas'):
                            for t in prod.get_lista_tareas():
                                writer.writerow([
                                    prod.get_id(), t.get_id_tarea_maestra(), # Guardamos ID numérico
                                    t.get_unidad_requerida().get_id(), t.get_cant_colaboradores_req(),
                                    t.get_tiempo_por_unidad(), t.get_id_habilidad_requerida(), # Guardamos ID numérico
                                    t.get_costo_mano_obra_hora()
                                ])
            except IOError as e:
                print(f"-> [ERROR] Falla en el guardado de tareas CSV")

    def guardar_compras_csv(self):
        try:
            with open("csv/compras.csv", mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID", "Insumo_ID", "Cantidad", "Estado", "Fecha_Emision", "Fecha_Recepcion"])
                for compra in self.empresa.obtener_historial_compras(): 
                    f_emision = compra.get_fecha_emision().strftime("%Y-%m-%d %H:%M:%S")
                    if compra.get_fecha_recepcion() is not None:
                        f_recepcion = compra.get_fecha_recepcion().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        f_recepcion = ""
            
                    writer.writerow([compra.get_id(), compra.get_insumo().get_id(), compra.get_cantidad(), compra.get_estado(), f_emision, f_recepcion])
        except IOError as e:
            print(f"-> [ERROR] Falla al guardar compras CSV")

    def guardar_catalogos_maestros(self):
        try:
            with open("csv/habilidades.csv", mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Nombre"])
                # Usamos el getter
                for id_h, nom in self.empresa.obtener_catalogo_habilidades().items():
                    writer.writerow([id_h, nom])    
            with open("csv/tareas_maestras.csv", mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Nombre", "ID_Unidad", "ID_Habilidad"])
                for id_t, datos in self.empresa.obtener_catalogo_tareas().items():
                    writer.writerow([id_t, datos["nombre"], datos["id_unidad"], datos["id_habilidad"]])
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura de catálogos maestros CSV")

    def guardar_reporte_criticos_csv(self, producto, criticos):
        nombre_archivo = f"csv/criticos_{producto.get_id()}.csv"
        inventario = self.empresa.obtener_inventario()
        try:
            with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID Insumo", "Nombre", "Cant. Necesaria", "Stock Actual", "Cobertura"])
                if not criticos:
                    print(f"-> [INFO] Reporte: NO hay materiales críticos para '{producto.get_nombre()}'. Stock en niveles aceptables.")
                else:
                    for insumo, cant_nec in criticos:
                        stock = inventario.consultar_stock(insumo)
                        porcentaje = (stock / cant_nec) * 100
                        cobertura = f"{porcentaje:.1f}%"
                        writer.writerow([insumo.get_id(), insumo.get_nombre(), cant_nec, stock, cobertura])
            print(f"-> Reporte de críticos generado en: '{nombre_archivo}'.")
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura del archivo")

    def cargar_catalogo_csv(self):
            """Reconstruye los objetos Elemento al arrancar el programa"""
            nombre_archivo = "csv/productos.csv"
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
                        valor_id = fila.get("ID Producto")
                        if valor_id:
                            id_prod = int(valor_id)
                        else:
                            id_prod = None
                        nombre = fila["Nombre Producto"]
                        tipo = fila["Tipo"]
                        costo = float(fila.get("Costo Fijo", 0.0))
                        
                        if tipo == "Articulo Fabricado":
                            nuevo_prod = ArticuloFabricadoInternamente(nombre=nombre, bom=[], lista_tareas=ListaEnlazadaTareas(), id=id_prod)
                            self.empresa.agregar_elemento_al_catalogo(nuevo_prod)
                        elif tipo == "Insumo Básico":
                            nuevo_insumo = InsumoBasico(nombre=nombre, costo_fijo=costo, id=id_prod)
                            self.empresa.agregar_elemento_al_catalogo(nuevo_insumo)
                # Reconstruimos el BOM utilizando IDs
                elementos_por_id = {}
                for elem in self.empresa.obtener_elementos_catalogo():
                    elementos_por_id[elem.get_id()] = elem

                for fila in filas_csv:
                    if fila.get("Tipo") == "Articulo Fabricado" and fila.get("Receta BOM"):
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
                            prod_obj.set_bom([ItemBOM(f"Receta {prod_obj.get_nombre()}", dict(bom_items))])
            except KeyError as e:
                print(f"-> [ERROR] El archivo 'productos.csv' está mal formateado. Falta la columna")
            except ValueError as e:
                print(f"-> [ERROR] Datos numéricos corruptos en 'productos.csv'")
            except OSError as e:
                print(f"-> [ERROR] Problema de lectura en el disco duro con 'productos.csv'")

    def cargar_solicitudes_csv(self):
            """Carga las solicitudes activas para retomar la producción"""
            nombre_archivo = "csv/solicitudes_activas.csv"
            if not os.path.exists(nombre_archivo):
                return
            try:
                with open(nombre_archivo, mode='r', encoding='utf-8') as archivo:
                    reader = csv.DictReader(archivo)
                    
                    for fila in reader:
                        nombre_prod = fila["Producto"]
                        # Filtramos el catálogo dejando solo los que coinciden con el nombre.
                        resultados = list(filter(lambda p: p.get_nombre() == nombre_prod, self.empresa.obtener_elementos_catalogo()))
                        
                        if len(resultados) > 0:
                            producto_obj = resultados[0] 
                            
                            id_sol = int(fila["ID Solicitud"])
                            cantidad = int(fila["Cantidad"])
                            estado = fila["Estado"]
                            fecha_creacion_str = fila["Fecha Creacion"]
                            
                            fecha_creacion= datetime.strptime(fecha_creacion_str, "%d/%m/%Y %H:%M")
                            nueva_sol= SolicitudDeFabricacion(producto_obj, cantidad, es_para_cliente=True, id=id_sol, fecha_creacion=fecha_creacion)
                            nueva_sol.set_estado(estado)
                            self.empresa.agregar_solicitud(id_sol, nueva_sol)
            except KeyError as e:
                print(f"-> [ERROR] El archivo 'solicitudes_activas.csv' está mal formateado. Falta la columna")
            except ValueError as e:
                print(f"-> [ERROR] Datos corruptos o formato de fecha inválido en 'solicitudes_activas.csv'")
            except OSError as e:
                print(f"-> [ERROR] Problema de lectura en el disco duro con 'solicitudes_activas.csv'")
    
    def cargar_unidades_csv(self):
        if not os.path.exists("csv/unidades.csv"): return
        from unidad_de_trabajo import UnidadDeTrabajo
        try:
            with open("csv/unidades.csv", mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    nueva_unidad = UnidadDeTrabajo(fila["Nombre"], float(fila["Capacidad"]), float(fila["Costo Operativo"]),id=int(fila["ID Unidad"]))
                    self.empresa.agregar_unidad(nueva_unidad)
        except KeyError as e:
            print(f"-> [ERROR] El archivo 'unidades.csv' está mal formateado. Falta la columna")
        except ValueError as e:
            print(f"-> [ERROR] Datos numéricos corruptos en 'unidades.csv'")
        except OSError as e:
            print(f"-> [ERROR] Problema de lectura en el disco duro con 'unidades.csv'")

    def cargar_colaboradores_csv(self):
            if not os.path.exists("csv/colaboradores.csv"): 
                return
            from colaboradores import Colaborador
            try:
                with open("csv/colaboradores.csv", mode='r', encoding='utf-8') as archivo:
                    reader = csv.DictReader(archivo)
                    for fila in reader:
                        ids_str = fila["Habilidades_IDs"].strip()
                        h_ids = []
                        if ids_str:
                            lista_textos = ids_str.split(";")
                            for texto_id in lista_textos:
                                numero_id = int(texto_id.strip())
                                h_ids.append(numero_id)
                        f_alta = None
                        if fila.get("Fecha Alta"):
                            f_alta = datetime.strptime(fila["Fecha Alta"], "%Y-%m-%d %H:%M:%S")
                        f_baja = None
                        if fila.get("Fecha Baja"):
                            f_baja = datetime.strptime(fila["Fecha Baja"], "%Y-%m-%d %H:%M:%S")
                        nuevo_colaborador = Colaborador(h_ids, float(fila["Horas Disponibles"]), float(fila["Salario Hora"]), id=int(fila["ID Colaborador"]), fecha_alta=f_alta, fecha_baja=f_baja  )
                        self.empresa.agregar_colaborador(nuevo_colaborador)
            except IOError as e:
                print(f"-> [ERROR] Falla en la carga de colaboradores CSV")
            except KeyError as e:
                print(f"-> [ERROR] Falla en la carga de colaboradores CSV")
            except ValueError as e:
                print(f"-> [ERROR] Falla en la carga de colaboradores CSV") 

    def cargar_tareas_csv(self):
        if not os.path.exists("csv/tareas.csv"):
            return
        from tarea import Tarea
        try:
            productos_dict = self.empresa.obtener_diccionario_productos()
            unidades_dict = self.empresa.obtener_diccionario_unidades()

            with open("csv/tareas.csv", mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for fila in reader:
                    id_p = int(fila["ID Producto"])
                    id_u = int(fila["ID Unidad"])
                    prod = productos_dict.get(id_p)
                    unidad = unidades_dict.get(id_u)
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
            print(f"-> [ERROR] Falla de lectura en tareas CSV")
        except KeyError as e:
            print(f"-> [ERROR] Columna faltante en tareas CSV")
        except ValueError as e:
            print(f"-> [ERROR] Dato numérico corrupto en tareas CSV")
    
    def cargar_compras_csv(self):
        if not os.path.exists("csv/compras.csv"): return
        from compra_insumo import Compra_Insumo
        from datetime import datetime
        try:
            with open("csv/compras.csv", mode='r', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                insumos_disp = self.empresa.obtener_diccionario_insumos()

                for fila in reader:
                    insumo = insumos_disp.get(int(fila["Insumo_ID"]))
                    if insumo:
                        orden = Compra_Insumo(insumo, int(fila["Cantidad"]), id=int(fila["ID"]), estado=fila["Estado"]) 
                        
                        f_emision = datetime.strptime(fila["Fecha_Emision"], "%Y-%m-%d %H:%M:%S")
                        f_recepcion = None
                        if fila["Fecha_Recepcion"]:
                            f_recepcion = datetime.strptime(fila["Fecha_Recepcion"], "%Y-%m-%d %H:%M:%S")
                        orden.set_fechas_historicas(f_emision, f_recepcion)
                        self.empresa.cargar_compra_desde_archivo(orden)
        except KeyError as e:
            print(f"-> [ERROR] El archivo 'compras.csv' está mal formateado.")
        except ValueError as e:
            print(f"-> [ERROR] Dato numérico o fecha inválida en 'compras.csv'")
        except OSError as e:
            print(f"-> [ERROR] Problema de lectura en el disco con 'compras.csv'")


    def cargar_catalogos_maestros(self):
        if os.path.exists("csv/habilidades.csv"):
            with open("csv/habilidades.csv", mode='r', encoding='utf-8') as f:
                for fila in csv.DictReader(f):
                    # Usamos el método de la empresa para inyectar el dato
                    self.empresa.registrar_habilidad_desde_archivo(int(fila["ID"]), fila["Nombre"])
                    
        if os.path.exists("csv/tareas_maestras.csv"):
            with open("csv/tareas_maestras.csv", mode='r', encoding='utf-8') as f:
                for fila in csv.DictReader(f):
                    datos_tarea = {"nombre": fila["Nombre"],"id_unidad": int(fila["ID_Unidad"]),"id_habilidad": int(fila["ID_Habilidad"]) }
                    # Usamos el método de la empresa para inyectar el dato
                    self.empresa.registrar_tarea_desde_archivo(int(fila["ID"]), datos_tarea)
    
    def guardar_todos_los_csv(self):
        """Centraliza el guardado de todos los archivos del sistema"""
        self.guardar_unidades_csv()
        self.guardar_colaboradores_csv()
        self.guardar_tareas_csv()
        self.guardar_catalogo_csv()
        self.guardar_compras_csv()
        self.guardar_solicitudes_csv()
        self.guardar_catalogos_maestros()
        self.guardar_inventario_csv()

    def cargar_todos_los_csv(self):
        self.cargar_catalogos_maestros()
        self.cargar_unidades_csv()
        self.cargar_colaboradores_csv()
        self.cargar_catalogo_csv()
        
        self.empresa.cargar_inventario_desde_archivo()
            
        self.cargar_tareas_csv()
        self.cargar_compras_csv()
        self.cargar_solicitudes_csv()
    