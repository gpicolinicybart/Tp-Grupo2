import csv
import os
from datetime import datetime
from solicitud_fabricacion import SolicitudDeFabricacion
from itembom import ItemBOM
from lista_tareas import ListaEnlazadaTareas

class GestorArchivos:
    def __init__(self, empresa):
        self.empresa = empresa

    def _leer_csv(self, ruta, procesar_fila):
        """Abre un CSV y le pasa cada fila (dict) a procesar_fila. Centraliza el manejo de errores."""
        if not os.path.exists(ruta):
            return
        try:
            with open(ruta, mode='r', newline='', encoding='utf-8') as archivo:
                for fila in csv.DictReader(archivo):
                    procesar_fila(fila)
        except KeyError:
            print(f"-> [ERROR] Falta una columna en '{ruta}'")
        except ValueError:
            print(f"-> [ERROR] Dato numérico o fecha inválida en '{ruta}'")
        except OSError:
            print(f"-> [ERROR] Problema de lectura con '{ruta}'")

    def _guardar_csv(self, ruta, encabezados, filas):
        """Escribe encabezados + filas en un CSV nuevo. Centraliza el manejo de errores."""
        try:
            with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(encabezados)
                escritor.writerows(filas)
        except OSError:
            print(f"-> [ERROR] Falla al guardar '{ruta}'")

            
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
        filas = []
        for s in self.empresa.obtener_solicitudes().values():
            fila = [
                s.get_id(),
                s.get_item_solicitado().get_nombre(),
                s.get_cantidad(),
                s.get_estado(),
                s.get_fecha_creacion().strftime("%d/%m/%Y %H:%M"),
            ]
            filas.append(fila)
        encabezados = ["ID Solicitud", "Producto", "Cantidad", "Estado", "Fecha Creacion"]
        self._guardar_csv("csv/solicitudes_activas.csv", encabezados, filas)
    
    def guardar_catalogo_csv(self):
        inventario = self.empresa.obtener_inventario()
        filas = []
        for prod in self.empresa.obtener_elementos_catalogo():
            fisico = inventario.consultar_stock(prod)
            reservado = inventario.obtener_stock_reservado(prod)
            tipo = prod.get_tipo_elemento()
            if tipo == "Articulo Fabricado":
                bom_str_lista = []
                for bom_item in prod.get_bom():
                    for elemento, cantidad in bom_item.get_diccionario().items():
                        bom_str_lista.append(f"{elemento.get_id()}: {cantidad}")
                receta_str = ";".join(bom_str_lista)
                filas.append([prod.get_id(), prod.get_nombre(), tipo, 0.0, fisico, reservado, receta_str])
            elif tipo == "Insumo Básico":
                filas.append([prod.get_id(), prod.get_nombre(), tipo, prod.get_costo_fijo(), fisico, reservado, ""])
        encabezados = ["ID Producto", "Nombre Producto", "Tipo", "Costo Fijo",
                       "Stock Fisico", "Stock Reservado", "Receta BOM"]
        self._guardar_csv("csv/productos.csv", encabezados, filas)


    def guardar_unidades_csv(self):
        filas = []
        for u in self.empresa.obtener_unidades():
            fila = [u.get_id(), u.get_nombre(), u.get_capacidad_max_horas(), u.get_costo_operativo()]
            filas.append(fila)
        encabezados = ["ID Unidad", "Nombre", "Capacidad", "Costo Operativo"]
        self._guardar_csv("csv/unidades.csv", encabezados, filas)

    def guardar_colaboradores_csv(self):
        filas = []
        for c in self.empresa.obtener_diccionario_colaboradores().values():
            habilidades_str = ";".join(map(str, c.get_habilidades()))
            f_alta = c.get_fecha_alta().strftime("%Y-%m-%d %H:%M:%S")
            if c.get_fecha_baja() is not None:
                f_baja = c.get_fecha_baja().strftime("%Y-%m-%d %H:%M:%S")
            else:
                f_baja = ""
            fila = [c.get_id(), habilidades_str, c.get_horas_disponibles(),
                    c.get_salario_hora(), f_alta, f_baja]
            filas.append(fila)
        encabezados = ["ID Colaborador", "Habilidades_IDs", "Horas Disponibles",
                       "Salario Hora", "Fecha Alta", "Fecha Baja"]
        self._guardar_csv("csv/colaboradores.csv", encabezados, filas)


    def guardar_tareas_csv(self):
        filas = []
        for prod in self.empresa.obtener_elementos_catalogo():
            if hasattr(prod, 'get_lista_tareas'):
                for t in prod.get_lista_tareas():
                    fila = [
                        prod.get_id(),
                        t.get_id_tarea_maestra(),
                        t.get_unidad_requerida().get_id(),
                        t.get_cant_colaboradores_req(),
                        t.get_tiempo_por_unidad(),
                        t.get_id_habilidad_requerida(),
                        t.get_costo_mano_obra_hora(),
                    ]
                    filas.append(fila)
        encabezados = ["ID Producto", "ID_Tarea_M", "ID Unidad", "Cant Colab",
                       "Tiempo", "ID_Hab_Req", "Costo MO"]
        self._guardar_csv("csv/tareas.csv", encabezados, filas)

    def guardar_compras_csv(self):
        filas = []
        for compra in self.empresa.obtener_historial_compras():
            f_emision = compra.get_fecha_emision().strftime("%Y-%m-%d %H:%M:%S")
            if compra.get_fecha_recepcion() is not None:
                f_recepcion = compra.get_fecha_recepcion().strftime("%Y-%m-%d %H:%M:%S")
            else:
                f_recepcion = ""
            fila = [compra.get_id(), compra.get_insumo().get_id(), compra.get_cantidad(),
                    compra.get_estado(), f_emision, f_recepcion]
            filas.append(fila)
        encabezados = ["ID", "Insumo_ID", "Cantidad", "Estado", "Fecha_Emision", "Fecha_Recepcion"]
        self._guardar_csv("csv/compras.csv", encabezados, filas)

    def guardar_catalogos_maestros(self):
        filas_hab = []
        for id_h, nom in self.empresa.obtener_catalogo_habilidades().items():
            filas_hab.append([id_h, nom])
        self._guardar_csv("csv/habilidades.csv", ["ID", "Nombre"], filas_hab)

        filas_t = []
        for id_t, datos in self.empresa.obtener_catalogo_tareas().items():
            filas_t.append([id_t, datos["nombre"], datos["id_unidad"], datos["id_habilidad"]])
        self._guardar_csv("csv/tareas_maestras.csv", ["ID", "Nombre", "ID_Unidad", "ID_Habilidad"], filas_t)

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
        
        def procesar(fila):
            nombre_prod = fila["Producto"]
            resultados = list(filter(lambda p: p.get_nombre() == nombre_prod,
                                     self.empresa.obtener_elementos_catalogo()))
            if not resultados:
                return
            producto_obj = resultados[0]
            id_sol = int(fila["ID Solicitud"])
            cantidad = int(fila["Cantidad"])
            fecha_creacion = datetime.strptime(fila["Fecha Creacion"], "%d/%m/%Y %H:%M")
            nueva_sol = SolicitudDeFabricacion(producto_obj, cantidad, es_para_cliente=True,
                                               id=id_sol, fecha_creacion=fecha_creacion)
            nueva_sol.set_estado(fila["Estado"])
            self.empresa.agregar_solicitud(id_sol, nueva_sol)
        self._leer_csv("csv/solicitudes_activas.csv", procesar)

    
    def cargar_unidades_csv(self):
        from unidad_de_trabajo import UnidadDeTrabajo
        def procesar(fila):
            unidad = UnidadDeTrabajo(fila["Nombre"], float(fila["Capacidad"]),
                                     float(fila["Costo Operativo"]), id=int(fila["ID Unidad"]))
            self.empresa.agregar_unidad(unidad)
        self._leer_csv("csv/unidades.csv", procesar)

    def cargar_colaboradores_csv(self):
        from colaboradores import Colaborador
        def procesar(fila):
            ids_str = fila["Habilidades_IDs"].strip()
            h_ids = []
            if ids_str:
                for texto_id in ids_str.split(";"):
                    h_ids.append(int(texto_id.strip()))
            f_alta = None
            if fila.get("Fecha Alta"):
                f_alta = datetime.strptime(fila["Fecha Alta"], "%Y-%m-%d %H:%M:%S")
            f_baja = None
            if fila.get("Fecha Baja"):
                f_baja = datetime.strptime(fila["Fecha Baja"], "%Y-%m-%d %H:%M:%S")
            colab = Colaborador(h_ids, float(fila["Horas Disponibles"]), float(fila["Salario Hora"]),
                                id=int(fila["ID Colaborador"]), fecha_alta=f_alta, fecha_baja=f_baja)
            self.empresa.agregar_colaborador(colab)
        self._leer_csv("csv/colaboradores.csv", procesar)

    def cargar_tareas_csv(self):
        from tarea import Tarea
        productos_dict = self.empresa.obtener_diccionario_productos()
        unidades_dict = self.empresa.obtener_diccionario_unidades()
        def procesar(fila):
            prod = productos_dict.get(int(fila["ID Producto"]))
            unidad = unidades_dict.get(int(fila["ID Unidad"]))
            if prod and unidad:
                tarea = Tarea(
                    id_tarea_maestra=int(fila["ID_Tarea_M"]),
                    unidad_requerida=unidad,
                    cant_colaboradores_req=int(fila["Cant Colab"]),
                    tiempo_por_unidad=float(fila["Tiempo"]),
                    id_habilidad_requerida=int(fila["ID_Hab_Req"]),
                    costo_mano_obra_hora=float(fila["Costo MO"]),
                )
                prod.get_lista_tareas().agregar_al_final(tarea)
        self._leer_csv("csv/tareas.csv", procesar)
    
    def cargar_compras_csv(self):
        from compra_insumo import Compra_Insumo
        insumos_disp = self.empresa.obtener_diccionario_insumos()
        def procesar(fila):
            insumo = insumos_disp.get(int(fila["Insumo_ID"]))
            if not insumo:
                return
            orden = Compra_Insumo(insumo, int(fila["Cantidad"]), id=int(fila["ID"]), estado=fila["Estado"])
            f_emision = datetime.strptime(fila["Fecha_Emision"], "%Y-%m-%d %H:%M:%S")
            f_recepcion = None
            if fila["Fecha_Recepcion"]:
                f_recepcion = datetime.strptime(fila["Fecha_Recepcion"], "%Y-%m-%d %H:%M:%S")
            orden.set_fechas_historicas(f_emision, f_recepcion)
            self.empresa.cargar_compra_desde_archivo(orden)
        self._leer_csv("csv/compras.csv", procesar)


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
    
    def cargar_usuarios_csv(self) -> dict:
        usuarios = {}
        if not os.path.exists("csv/usuarios.csv"):
            print("Archivo 'usuarios.csv' no encontrado.")
            return usuarios
        try:
            with open("csv/usuarios.csv", mode="r", newline="", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                for fila in lector:
                    usuarios[fila["id"].strip()] = {
                        "clave": fila["clave"].strip(),
                        "rol": fila["rol"].strip(),
                        "nombre": fila.get("nombre", "").strip(),
                        "apellido": fila.get("apellido", "").strip(),
                        "dni": fila.get("dni", "").strip(),
                    }
        except KeyError:
            print(" El archivo 'usuarios.csv' está mal formateado.")
        except OSError:
            print(" Problema al leer 'usuarios.csv'.")
        return usuarios
    
    def guardar_usuario_csv(self, nuevo_usuario: list):
        try:
            filas = []
            if os.path.exists("csv/usuarios.csv"):
                with open("csv/usuarios.csv", "r", newline="", encoding="utf-8") as f:
                    filas = list(csv.reader(f))
            if not filas:
                filas = [["id", "clave", "rol", "nombre", "apellido", "dni"]]
            filas.append(nuevo_usuario)
            with open("csv/usuarios.csv", mode="w", newline="", encoding="utf-8") as archivo:
                csv.writer(archivo).writerows(filas)
        except OSError:
            print(" ERROR: Falla al guardar en 'usuarios.csv'.")

    def leer_historial_csv(self):
        nombre_archivo = "csv/historial_solicitudes.csv"
        if not os.path.isfile(nombre_archivo):
            return None, []
        try:
            with open(nombre_archivo, mode="r", newline="", encoding="utf-8") as archivo:
                lector = csv.reader(archivo)
                encabezados = next(lector, None)
                filas = list(lector)
            return encabezados, filas
        except OSError:
            print("[ERROR] No se pudo leer el archivo de historial")
            return None, []
        
    def cargar_inventario_csv(self, elementos_catalogo: list, archivo_csv="csv/inventario.csv"):
        inventario = self.empresa.obtener_inventario()
        elementos_por_id = {}
        elementos_por_nombre = {}
        for elemento in elementos_catalogo:
            if hasattr(elemento, 'get_id'):
                elementos_por_id[str(elemento.get_id())] = elemento
            if hasattr(elemento, 'get_nombre'):
                elementos_por_nombre[elemento.get_nombre()] = elemento

        def procesar(fila):
            id_elem = fila.get('id_elemento', '').strip()
            nombre = fila.get('nombre_referencia', '').strip()
            fisico = int(fila.get('stock_fisico', 0))
            reservado = int(fila.get('stock_reservado', 0))
            elemento = elementos_por_id.get(id_elem) or elementos_por_nombre.get(nombre)
            if elemento is not None:
                inventario.establecer_stock(elemento, fisico, reservado)
        self._leer_csv(archivo_csv, procesar)

    def guardar_inventario_csv(self, archivo_csv="csv/inventario.csv"):
        inventario = self.empresa.obtener_inventario()
        filas = []
        for elem, fisico, reservado in inventario.exportar_stock():
            if hasattr(elem, 'get_id'):
                id_elem = elem.get_id()
            else:
                id_elem = "N/A"
            if hasattr(elem, 'get_nombre'):
                nombre = elem.get_nombre()
            else:
                nombre = "Desconocido"
            filas.append([id_elem, nombre, fisico, reservado])
        encabezados = ["id_elemento", "nombre_referencia", "stock_fisico", "stock_reservado"]
        self._guardar_csv(archivo_csv, encabezados, filas)
    
    def guardar_todos_los_csv(self):
        
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
        
        self.cargar_inventario_csv(self.empresa.obtener_elementos_catalogo())
            
        self.cargar_tareas_csv()
        self.cargar_compras_csv()
        self.cargar_solicitudes_csv()
    