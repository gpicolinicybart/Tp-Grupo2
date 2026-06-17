import csv
import os
from datetime import datetime

class GestorArchivos:
    def __init__(self, empresa):
        self.empresa = empresa

    def _leer_csv(self, ruta, procesar_fila):
        if not os.path.exists(ruta):
            return
        try:
            with open(ruta, mode='r', newline='', encoding='utf-8') as archivo:
                for fila in csv.DictReader(archivo):
                    try:
                        procesar_fila(fila)
                    except (KeyError, ValueError, TypeError) as e:
                        print(f"[Aviso] Fila con error en {ruta} ignorada: {e}")
                        continue 
        except OSError:
            pass

    def _guardar_csv(self, ruta, encabezados, filas): #escribe encabezados + filas en un CSV nuevo
        try:
            with open(ruta, mode='w', newline='', encoding='utf-8') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(encabezados)
                escritor.writerows(filas)
            return True
        except OSError:
            return False

    def _guardar_objetos(self, ruta, columnas, objetos):
        filas = []
        for obj in objetos:
            filas.append(obj.serialize())
        return self._guardar_csv(ruta, columnas, filas)

    def _cargar_objetos(self, ruta, clase):
        objetos = []
        def procesar(fila):
            obj = clase.deserialize(fila)
            if obj is not None:
                objetos.append(obj)
        self._leer_csv(ruta, procesar)
        return objetos

    def _cargar_objetos_con_contexto(self, ruta, clase, contexto):
        objetos = []
        def procesar(fila):
            obj = clase.deserialize(fila, contexto)
            if obj is not None:
                objetos.append(obj)
        self._leer_csv(ruta, procesar)
        return objetos
    
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

    def guardar_solicitudes_csv(self):
        from solicitud_fabricacion import SolicitudDeFabricacion
        return self._guardar_objetos(SolicitudDeFabricacion.ARCHIVO, SolicitudDeFabricacion.COLUMNAS,
                                     self.empresa.obtener_solicitudes().values())

    def cargar_solicitudes_csv(self):
        from solicitud_fabricacion import SolicitudDeFabricacion
        productos_por_nombre = {}
        for prod in self.empresa.obtener_elementos_catalogo():
            productos_por_nombre[prod.get_nombre()] = prod
        solicitudes = self._cargar_objetos_con_contexto(
            SolicitudDeFabricacion.ARCHIVO, SolicitudDeFabricacion, productos_por_nombre)
        for sol in solicitudes:
            self.empresa.agregar_solicitud(sol.get_id(), sol)
    
    def guardar_colaboradores_csv(self):
        from colaboradores import Colaborador
        return self._guardar_objetos(Colaborador.ARCHIVO, Colaborador.COLUMNAS,
                                     self.empresa.obtener_diccionario_colaboradores().values())

    def cargar_colaboradores_csv(self):
        from colaboradores import Colaborador
        for colab in self._cargar_objetos(Colaborador.ARCHIVO, Colaborador):
            self.empresa.agregar_colaborador(colab)

    def guardar_tareas_csv(self):
        from tarea import Tarea
        filas = []
        for prod in self.empresa.obtener_elementos_catalogo():
            for tarea in prod.get_lista_tareas():
                filas.append([prod.get_id()] + tarea.serialize())
        encabezados = ["ID Producto"] + Tarea.COLUMNAS
        return self._guardar_csv("csv/tareas.csv", encabezados, filas)

    def cargar_tareas_csv(self):
        from tarea import Tarea
        productos = self.empresa.obtener_diccionario_productos()
        unidades = self.empresa.obtener_diccionario_unidades()
        def procesar(fila):
            prod = productos.get(int(fila["ID Producto"]))
            tarea = Tarea.deserialize(fila, unidades)
            if prod is not None and tarea is not None:
                prod.get_lista_tareas().agregar_al_final(tarea)
        self._leer_csv("csv/tareas.csv", procesar)

    def guardar_reporte_criticos_csv(self, producto, criticos):
        nombre_archivo = f"csv/criticos_{producto.get_id()}.csv"
        try:
            with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["ID Insumo", "Nombre", "Cant. Necesaria", "Stock Actual", "Cobertura"])
                if not criticos:
                    print(f"-> [INFO] Reporte: NO hay materiales críticos para '{producto.get_nombre()}'. Stock en niveles aceptables.")
                else:
                    for insumo, cant_nec in criticos:
                        stock = self.empresa.consultar_stock_elemento(insumo)
                        porcentaje = (stock / cant_nec) * 100
                        cobertura = f"{porcentaje:.1f}%"
                        writer.writerow([insumo.get_id(), insumo.get_nombre(), cant_nec, stock, cobertura])
            print(f"-> Reporte de críticos generado en: '{nombre_archivo}'.")
        except IOError as e:
            print(f"-> [ERROR] Falló la escritura del archivo")
    COLUMNAS_CATALOGO = ["ID Producto", "Nombre Producto", "Tipo", "Costo Fijo", "Receta BOM"]

    def guardar_catalogo_csv(self):
        filas = []
        for prod in self.empresa.obtener_elementos_catalogo():
            filas.append(prod.serialize())
        return self._guardar_csv("csv/productos.csv", self.COLUMNAS_CATALOGO, filas)

    def cargar_catalogo_csv(self):
        from articulo_fabricado import ArticuloFabricadoInternamente
        from insumo_basico import InsumoBasico
        ruta = "csv/productos.csv"
        if not os.path.exists(ruta):
            return
        filas_articulos = []
        # creamos cada elemento (sin receta todavía)
        def procesar(fila):
            tipo = fila["Tipo"]
            if tipo == "Insumo Básico":
                self.empresa.agregar_elemento_al_catalogo(InsumoBasico.deserialize(fila))
            elif tipo == "Articulo Fabricado":
                self.empresa.agregar_elemento_al_catalogo(ArticuloFabricadoInternamente.deserialize(fila))
                filas_articulos.append(fila)
        self._leer_csv(ruta, procesar)

        #  reconstruimos el BOM usando los IDs ya cargados
        elementos_por_id = {}
        for elem in self.empresa.obtener_elementos_catalogo():
            elementos_por_id[elem.get_id()] = elem
        for fila in filas_articulos:
            prod = elementos_por_id.get(int(fila["ID Producto"]))
            if prod is not None:
                ArticuloFabricadoInternamente.reconstruir_bom(prod, fila.get("Receta BOM", ""), elementos_por_id)
    
    def guardar_unidades_csv(self):
        from unidad_de_trabajo import UnidadDeTrabajo
        return self._guardar_objetos(UnidadDeTrabajo.ARCHIVO, UnidadDeTrabajo.COLUMNAS,
                                     self.empresa.obtener_unidades())

    def cargar_unidades_csv(self):
        from unidad_de_trabajo import UnidadDeTrabajo
        for unidad in self._cargar_objetos(UnidadDeTrabajo.ARCHIVO, UnidadDeTrabajo):
            self.empresa.agregar_unidad(unidad)

    def guardar_compras_csv(self):
        from compra_insumo import Compra_Insumo
        return self._guardar_objetos(Compra_Insumo.ARCHIVO, Compra_Insumo.COLUMNAS,
                                     self.empresa.obtener_historial_compras())

    def cargar_compras_csv(self):
        from compra_insumo import Compra_Insumo
        insumos = self.empresa.obtener_diccionario_insumos()
        compras = self._cargar_objetos_con_contexto(Compra_Insumo.ARCHIVO, Compra_Insumo, insumos)
        for compra in compras:
            self.empresa.cargar_compra_desde_archivo(compra)

    def guardar_habilidades_csv(self):
        from habilidad import Habilidad
        return self._guardar_objetos(Habilidad.ARCHIVO, Habilidad.COLUMNAS,
                                     self.empresa.obtener_habilidades())

    def cargar_habilidades_csv(self):
        from habilidad import Habilidad
        for hab in self._cargar_objetos(Habilidad.ARCHIVO, Habilidad):
            self.empresa.registrar_habilidad(hab)

    def guardar_tareas_maestras_csv(self):
        from tarea_maestra import TareaMaestra
        return self._guardar_objetos(TareaMaestra.ARCHIVO, TareaMaestra.COLUMNAS,
                                     self.empresa.obtener_tareas_maestras())

    def cargar_tareas_maestras_csv(self):
        from tarea_maestra import TareaMaestra
        for tm in self._cargar_objetos(TareaMaestra.ARCHIVO, TareaMaestra):
            self.empresa.registrar_tarea_maestra(tm)
    
    def cargar_usuarios_csv(self):
        from usuario import Usuario
        usuarios = {}
        for u in self._cargar_objetos(Usuario.ARCHIVO, Usuario):
            usuarios[u.get_id()] = u
        return usuarios

    def guardar_usuario_csv(self, nuevo_usuario):
        from usuario import Usuario
        existentes = list(self.cargar_usuarios_csv().values())
        existentes.append(nuevo_usuario)
        return self._guardar_objetos(Usuario.ARCHIVO, Usuario.COLUMNAS, existentes)

    def guardar_inventario_csv(self, archivo_csv="csv/inventario.csv"):
        inventario = self.empresa.obtener_inventario()
        return self._guardar_csv(archivo_csv, inventario.COLUMNAS_STOCK,
                                 inventario.serializar_stock())

    def cargar_inventario_csv(self, elementos_catalogo, archivo_csv="csv/inventario.csv"):
        elementos_por_id = {}
        elementos_por_nombre = {}
        for elemento in elementos_catalogo:
            elementos_por_id[str(elemento.get_id())] = elemento
            elementos_por_nombre[elemento.get_nombre()] = elemento

        def procesar(fila):
            id_elem = fila.get('id_elemento', '').strip()
            nombre = fila.get('nombre_referencia', '').strip()
            fisico = int(fila.get('stock_fisico', 0))
            reservado = int(fila.get('stock_reservado', 0))
            elemento = elementos_por_id.get(id_elem) or elementos_por_nombre.get(nombre)
            if elemento is not None:
                self.empresa.establecer_stock(elemento, fisico, reservado)
        self._leer_csv(archivo_csv, procesar)
    
    def guardar_todos_los_csv(self):
        resultados = []
        resultados.append(self.guardar_unidades_csv())
        resultados.append(self.guardar_colaboradores_csv())
        resultados.append(self.guardar_tareas_csv())
        resultados.append(self.guardar_catalogo_csv())
        resultados.append(self.guardar_compras_csv())
        resultados.append(self.guardar_solicitudes_csv())
        resultados.append(self.guardar_habilidades_csv())
        resultados.append(self.guardar_tareas_maestras_csv())
        resultados.append(self.guardar_inventario_csv())
        return all(resultados)

    def cargar_todos_los_csv(self):
        self.cargar_habilidades_csv()
        self.cargar_tareas_maestras_csv()
        self.cargar_unidades_csv()
        self.cargar_colaboradores_csv()
        self.cargar_catalogo_csv()
        self.cargar_inventario_csv(self.empresa.obtener_elementos_catalogo())
        self.cargar_tareas_csv()
        self.cargar_compras_csv()
        self.cargar_solicitudes_csv()