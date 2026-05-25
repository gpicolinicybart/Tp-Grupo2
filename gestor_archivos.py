import csv
import os
from datetime import datetime
from solicitud_fabricacion import SolicitudDeFabricacion
from itembom import ItemBOM
from lista_tareas import ListaEnlazadaTareas

class GestorArchivos:
    def __init__(self, empresa):
        self.empresa = empresa


    #Guardar----------------------------
    def guardar_historial_csv (self,solicitudes_terminadas: list):
        nombre_archivo = "historial_solicitudes.csv"
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
                    fecha_creacion= solicitud._fecha_creacion.strftime("%d/%m/%Y %H:%M")
                    if solicitud._fecha_finalizacion:
                        fecha_finalizacion= solicitud._fecha_finalizacion.strftime("%d/%m/%Y %H:%M")
                        tiempo_hs=round((solicitud._fecha_finalizacion - solicitud._fecha_creacion).total_seconds()/3600,2)
                    else:
                        fecha_finalizacion="N/A"
                        tiempo_hs="N/A"
                    escritor_csv.writerow([id_sol, producto, cantidad, fecha_creacion, fecha_finalizacion, tiempo_hs])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado del historial CSV")


    def guardar_solicitudes_csv(self):
        try: 
            with open("solicitudes_activas.csv", mode='w', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                escritor_csv.writerow(["ID Solicitud", "Producto", "Cantidad", "Estado", "Fecha Creacion"])
                for solicitud in self.empresa._solicitudes.values():
                    escritor_csv.writerow([
                        solicitud.get_id(),
                        solicitud.get_item_solicitado().get_nombre(),
                        solicitud.get_cantidad(),
                            solicitud.get_estado(),
                            solicitud._fecha_creacion.strftime("%d/%m/%Y %H:%M")])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado de solicitudes activas CSV")

    def guardar_catalogo_csv(self):
        try:
            with open("productos.csv", mode='w', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                escritor_csv.writerow(["ID Producto", "Nombre Producto","Tipo", "Costo Fijo","Stock Fisico", "Stock Reservado", "Receta BOM"])
                for prod in self.empresa._catalogo_elementos:
                    fisico=self.empresa._inventario.consultar_stock(prod)
                    reservado=self.empresa._inventario.obtener_stock_reservado(prod)
                    tipo=prod.get_tipo_elemento()
                    if tipo=="Articulo Fabricado":
                        bom_str_lista=[]
                        for bom_item in prod.get_bom():
                            for elemento,cantidad in bom_item.get_diccionario().items():
                                bom_str_lista.append(f"{elemento.get_id()}: {cantidad}")
                        receta_str=";".join(bom_str_lista)
                        escritor_csv.writerow([prod.get_id(), prod.get_nombre(), tipo, prod.get_costo_fijo(), fisico, reservado, receta_str])
                    elif tipo=="Insumo Básico":
                        escritor_csv.writerow([prod.get_id(), prod.get_nombre(), tipo, prod.get_costo_fijo(), fisico, reservado, ""])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado del catálogo CSV")

    def guardar_inventario_csv(self):
        if hasattr(self.empresa._inventario, 'guardar_en_csv'):
            self.empresa._inventario.guardar_en_csv()
        else:
            print(f"[AVISO] Falta implementar guardar_en_csv() en la clase Inventario.")

    def guardar_unidades_csv(self):
        try:
            with open("unidades.csv", mode='w', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                escritor_csv.writerow(["ID Unidad", "Nombre", "Capacidad", "Costo Operativo"])
                for unidad in self.empresa._unidades:
                    escritor_csv.writerow([unidad.get_id(), unidad.get_nombre(), unidad.get_capacidad_max_horas(), unidad.get_costo_operativo()])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado de unidades CSV")

    def guardar_colaboradores_csv(self):
        try:
            with open("colaboradores.csv", mode='w', newline='', encoding='utf-8') as archivo:
                escritor_csv = csv.writer(archivo)
                escritor_csv.writerow(["ID Colaborador", "Habilidades_IDs", "Horas Disponibles", "Salario Hora"])
                for colaborador in self.empresa._colaboradores.values():
                    habilidades_str = ";".join(map(str, colaborador.get_habilidades()))
                    escritor_csv.writerow([colaborador.get_id(), habilidades_str, colaborador.get_horas_disponibles(), colaborador.get_salario_hora()])
        except IOError as e:
            print(f"->[ERROR] Falla en el guardado de colaboradores CSV")

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
                print(f"-> [ERROR] Falla en el guardado de tareas CSV")

    def guardar_compras_csv(self):
                try:
                    with open("compras.csv", mode='w', newline='', encoding='utf-8') as archivo:
                        writer = csv.writer(archivo)
                        writer.writerow(["ID", "Insumo_ID", "Cantidad", "Estado", "Fecha_Emision", "Fecha_Recepcion"])
            
                        for compra in self._gestor_compras.obtener_historial(): 
                            f_emision = compra._fecha_emision.strftime("%Y-%m-%d %H:%M:%S")
                            if compra._fecha_recepcion is not None:
                                f_recepcion = compra._fecha_recepcion.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                f_recepcion = ""
                    
                            writer.writerow([compra.get_id(), compra._insumo.get_id(), compra._cantidad, compra._estado, f_emision, f_recepcion])
                        
                except IOError as e:
                    print(f"-> [ERROR] Falla al guardar compras CSV")

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
                print(f"-> [ERROR] Falló la escritura de catálogos")

    #-----------Cargar----------------------------

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
                            self._catalogo_elementos.append(nuevo_prod)
                        elif tipo == "Insumo Básico":
                            nuevo_insumo = InsumoBasico(nombre=nombre, costo_fijo=costo, id=id_prod)
                            self._catalogo_elementos.append(nuevo_insumo)

                # Reconstruimos el BOM utilizando IDs
                elementos_por_id = {}
                for elem in self._catalogo_elementos:
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
                            prod_obj._bom = [ItemBOM(f"Receta {prod_obj.get_nombre()}", dict(bom_items))]

            except KeyError as e:
                print(f"-> [ERROR] El archivo 'productos.csv' está mal formateado. Falta la columna")
            except ValueError as e:
                print(f"-> [ERROR] Datos numéricos corruptos en 'productos.csv'")
            except OSError as e:
                print(f"-> [ERROR] Problema de lectura en el disco duro con 'productos.csv'")

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
                            nueva_sol._fecha_creacion = datetime.strptime(fecha_creacion_str, "%d/%m/%Y %H:%M")
                            
                            self._solicitudes[id_sol] = nueva_sol
                            
                            if id_sol > SolicitudDeFabricacion.id_solicitud:
                                SolicitudDeFabricacion.id_solicitud = id_sol
                                
            except KeyError as e:
                print(f"-> [ERROR] El archivo 'solicitudes_activas.csv' está mal formateado. Falta la columna")
            except ValueError as e:
                print(f"-> [ERROR] Datos corruptos o formato de fecha inválido en 'solicitudes_activas.csv'")
            except OSError as e:
                print(f"-> [ERROR] Problema de lectura en el disco duro con 'solicitudes_activas.csv'")
    
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
        except KeyError as e:
            print(f"-> [ERROR] El archivo 'unidades.csv' está mal formateado. Falta la columna")
        except ValueError as e:
            print(f"-> [ERROR] Datos numéricos corruptos en 'unidades.csv'")
        except OSError as e:
            print(f"-> [ERROR] Problema de lectura en el disco duro con 'unidades.csv'")

    def cargar_colaboradores_csv(self):
            if not os.path.exists("colaboradores.csv"): 
                return
            from colaboradores import Colaborador
            try:
                with open("colaboradores.csv", mode='r', encoding='utf-8') as archivo:
                    reader = csv.DictReader(archivo)
                    for fila in reader:
                        ids_str = fila["Habilidades_IDs"].strip()
                        h_ids = []
                        if ids_str:
                            lista_textos = ids_str.split(";")
                            for texto_id in lista_textos:
                                numero_id = int(texto_id.strip())
                                h_ids.append(numero_id)
                        nuevo_colaborador = Colaborador(h_ids, float(fila["Horas Disponibles"]), float(fila["Salario Hora"]))
                        nuevo_colaborador._id = int(fila["ID Colaborador"])
                        if hasattr(Colaborador, 'id_colaborador') and nuevo_colaborador._id > Colaborador.id_colaborador:
                            Colaborador.id_colaborador = nuevo_colaborador._id
                        self._colaboradores[nuevo_colaborador.get_id()] = nuevo_colaborador
            except IOError as e:
                print(f"-> [ERROR] Falla en la carga de colaboradores CSV")
            except KeyError as e:
                print(f"-> [ERROR] Falla en la carga de colaboradores CSV")
            except ValueError as e:
                print(f"-> [ERROR] Falla en la carga de colaboradores CSV") 

    def cargar_tareas_csv(self):
        if not os.path.exists("tareas.csv"):
            return
        from tarea import Tarea
        try:
            productos_dict = {}
            for p in self._catalogo_elementos:
                productos_dict[p.get_id()] = p
                
            unidades_dict = {}
            for u in self._unidades:
                unidades_dict[u.get_id()] = u

            with open("tareas.csv", mode='r', encoding='utf-8') as archivo:
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
            if not os.path.exists("compras.csv"):
                return
            from compra_insumo import Compra_Insumo
            try:
                with open("compras.csv", mode='r', encoding='utf-8') as archivo:
                    reader = csv.DictReader(archivo)
                    elementos_id = {}
                    for e in self._catalogo_elementos:
                        elementos_id[e.get_id()] = e

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
                                self._compras_pendientes.append(orden)
            except IOError as e:
                print(f"-> [ERROR] Falla en la carga de compras CSV")
            except KeyError as e:
                print(f"-> [ERROR] Falla en la carga de compras CSV")
            except ValueError as e:
                print(f"-> [ERROR] Falla en la carga de compras CSV")

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
    
    #--------------------centralizacion--------------------------------------

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
        """Centraliza la carga en el orden correcto para evitar dependencias rotas"""
        self.cargar_catalogos_maestros()
        self.cargar_unidades_csv()
        self.cargar_colaboradores_csv()
        self.cargar_catalogo_csv()
        self._inventario.cargar_desde_csv(self._catalogo_elementos)
            
        self.cargar_tareas_csv()
        self.cargar_compras_csv()
        self.cargar_solicitudes_csv()