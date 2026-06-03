
from gestor_compras import GestorCompras
from inventario import Inventario
from tarea import Tarea
from compra_insumo import Compra_Insumo
from unidad_de_trabajo import UnidadDeTrabajo
from elemento import Elemento
from articulo_fabricado import ArticuloFabricadoInternamente
from insumo_basico import InsumoBasico
from colaboradores import Colaborador
from itembom import ItemBOM
from lista_tareas import ListaEnlazadaTareas
from gestor_archivos import GestorArchivos
from gestor_solicitudes import GestorSolicitudes
from solicitud_fabricacion import SolicitudDeFabricacion, ESTADOS_VALIDOS

class Empresa:
    def __init__(self, inventario: Inventario):
        self._inventario = inventario
        self._insumos_basicos = {}
        self._productos_fabricados = {}        
        self._unidades = {}
        self._colaboradores = {}
        self._catalogo_habilidades = {}  
        self._catalogo_tareas = {}       
        self._gestor_compras = GestorCompras()
        self._gestor_archivos = GestorArchivos(self)
        self._gestor_solicitudes = GestorSolicitudes(self) 

    def crear_solicitud(self, solicitud: SolicitudDeFabricacion):
        self._gestor_solicitudes.crear_solicitud(solicitud)

    def generar_solicitud_desde_menu(self, producto, cantidad):
        return self._gestor_solicitudes.generar_solicitud_desde_menu(producto, cantidad)

    def procesar_solicitud(self):
        self._gestor_solicitudes.procesar_solicitud()

    def ejecutar_solicitud(self):
        self._gestor_solicitudes.ejecutar_solicitud()

    def finalizar_solicitud(self):
        self._gestor_solicitudes.finalizar_solicitud()

    def mostrar_solicitudes(self):
        self._gestor_solicitudes.mostrar_solicitudes()


    def registrar_compra(self, orden: Compra_Insumo):
        self._gestor_compras.agregar_compra(orden)
        print(f"EMPRESA: Se registró la orden de compra {orden.get_id()}...")
        self._gestor_archivos.guardar_compras_csv()
        
            
    def recibir_compras(self) -> int:
        compra = self._gestor_compras.recibir_proxima_compra(self._inventario)
        
        if compra:
            # Hubo una recepción exitosa, persistimos los datos
            self._gestor_archivos.guardar_compras_csv()  
            self._gestor_archivos.guardar_inventario_csv()
            return 1 # Avisamos al menú que se recibió 1 orden
            
        return 0 
#==============================================================================================================

    def generar_reporte_materiales_criticos(self, producto, cantidad_pedida: int):
        necesidades = producto.calcular_materiales_necesarios(cantidad_pedida)
        criticos = self._inventario.obtener_materiales_criticos(necesidades)
        self._gestor_archivos.guardar_reporte_criticos_csv(producto, criticos)

    
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
        solicitudes=self._gestor_solicitudes.obtener_solicitudes()
        d_stock = len(list(filter(lambda t: t.get_estado() == ESTADOS_VALIDOS[4],solicitudes.values())))
        d_capacidad = len(list(filter(lambda t: t.get_estado() == ESTADOS_VALIDOS[5],solicitudes.values())))
        d_personal = len(list(filter(lambda t: t.get_estado() == ESTADOS_VALIDOS[6],solicitudes.values())))        
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


    def agregar_colaborador(self, nuevo_colaborador):
            id_nuevo = nuevo_colaborador.get_id()
            if id_nuevo in self._colaboradores:
                raise ValueError("ID repetido")
            self._colaboradores[id_nuevo] = nuevo_colaborador
            self._gestor_archivos.guardar_colaboradores_csv()

    def agregar_unidad_trabajo(self, nueva_unidad: UnidadDeTrabajo):
        self._unidades[nueva_unidad.get_id()] = nueva_unidad
        self._gestor_archivos.guardar_unidades_csv()
        
    
    def registrar_producto_nuevo(self, producto: Elemento) -> bool:
            nombre_nuevo = producto.get_nombre().strip().lower()
            for ins in self._insumos_basicos.values():
                if ins.get_nombre().strip().lower() == nombre_nuevo:
                    print(f"-> [ERROR] Ya existe '{ins.get_nombre()}' en insumos. Cancelado.")
                    return False
            for prod in self._productos_fabricados.values():
                if prod.get_nombre().strip().lower() == nombre_nuevo:
                    print(f"-> [ERROR] Ya existe '{prod.get_nombre()}' en productos. Cancelado.")
                    return False
            try:
                producto.validar_ciclos() 
                if producto.get_tipo_elemento() == "Insumo Básico":
                    self._insumos_basicos[producto.get_id()] = producto
                else:
                    self._productos_fabricados[producto.get_id()] = producto
                print(f"EMPRESA: '{producto.get_nombre()}' registrado exitosamente en el catálogo.")
                self._gestor_archivos.guardar_catalogo_csv() 
                self._gestor_archivos.guardar_tareas_csv()  
                return True
            except ValueError as e:
                print(f"No se pudo registrar '{producto.get_nombre()}' por un ciclo en el BOM")
                return False
                
    def consultar_stock_insumo(self, insumo):
        return self._inventario.obtener_stock_disponible(insumo)

   

    def agregar_habilidad(self, nombre: str):
            if self._catalogo_habilidades:
                nuevo_id = len(self._catalogo_habilidades) + 1
            else:
                nuevo_id = 1
            self._catalogo_habilidades[nuevo_id] = nombre.strip().title()
            self._gestor_archivos.guardar_catalogos_maestros()
            return nuevo_id

    def agregar_tarea_maestra(self, nombre: str, id_unidad: int, id_habilidad: int):
        if self._catalogo_tareas:
            nuevo_id = len(self._catalogo_tareas) + 1
        else:
            nuevo_id = 1
        self._catalogo_tareas[nuevo_id] = {
            "nombre": nombre.strip().title(),
            "id_unidad": id_unidad,
            "id_habilidad": id_habilidad
        }
        self._gestor_archivos.guardar_catalogos_maestros()
        return nuevo_id
   
    def obtener_diccionario_insumos(self):
        return self._insumos_basicos

    def obtener_diccionario_productos(self):
        return self._productos_fabricados

    def obtener_diccionario_unidades(self):
        return self._unidades

    def obtener_diccionario_colaboradores(self):
        return self._colaboradores

    def crear_insumo_basico(self, nombre, costo):
        if not nombre: 
            raise ValueError("El nombre no puede estar vacío.")
        if costo <= 0: 
            raise ValueError("El costo debe ser positivo.")
        
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
        self._gestor_archivos.guardar_colaboradores_csv()
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

        if len(tareas_producto) == 0:
            raise ValueError("No se puede fabricar sin tareas.")

        
        producto = ArticuloFabricadoInternamente(nombre, [bom], tareas_producto)
        self.registrar_producto_nuevo(producto)
        return producto

    def cargar_demo_completa(self):
        print("\n=== CARGANDO DEMO}===")

        # 1) Habilidades
        id_corte = self.agregar_habilidad("Corte")
        id_ensamblaje = self.agregar_habilidad("Ensamblaje")
        id_pintura = self.agregar_habilidad("Pintura")

        # 2) Unidades de trabajo (capacidad en horas, costo operativo por hora)
        sierra = UnidadDeTrabajo("Sierra de Corte", 200.0, 500.0)
        linea = UnidadDeTrabajo("Linea de Ensamblaje", 200.0, 800.0)
        cabina = UnidadDeTrabajo("Cabina de Pintura", 150.0, 400.0)
        for u in (sierra, linea, cabina):
            self.agregar_unidad_trabajo(u)

        # 3) Tareas maestras (nombre, id_unidad, id_habilidad)
        id_t_corte = self.agregar_tarea_maestra("Corte de Madera", sierra.get_id(), id_corte)
        id_t_ensamble = self.agregar_tarea_maestra("Ensamblaje General", linea.get_id(), id_ensamblaje)
        id_t_pintado = self.agregar_tarea_maestra("Pintado y Acabado", cabina.get_id(), id_pintura)

        # 4) Insumos basicos + stock inicial
        madera = InsumoBasico("Tablon de Madera", 5000.0)
        tornillos = InsumoBasico("Tornillos 10mm", 5.0)
        barniz = InsumoBasico("Barniz", 1200.0)
        pegamento = InsumoBasico("Pegamento", 300.0)
        for insumo in (madera, tornillos, barniz, pegamento):
            self.registrar_producto_nuevo(insumo)
            self._inventario.ingresar_stock(insumo, 2000)

        # 5) Colaboradores (habilidades, horas disponibles, salario/hora)
        colaboradores = [
            Colaborador([id_corte], 40.0, 2500.0),
            Colaborador([id_corte], 40.0, 2300.0),
            Colaborador([id_ensamblaje], 40.0, 2800.0),
            Colaborador([id_ensamblaje], 40.0, 2600.0),
            Colaborador([id_pintura], 40.0, 2400.0),
            Colaborador([id_corte, id_ensamblaje], 40.0, 3000.0),  # multi-habilidad
        ]
        for c in colaboradores:
            self.agregar_colaborador(c)

        # 6) Productos fabricados (BOM multinivel)
        # --- Pata de Mesa ---
        lista_pata = ListaEnlazadaTareas()
        lista_pata.agregar_al_final(Tarea(id_t_corte, sierra, 1, 0.5, id_corte, 1000.0))
        pata = ArticuloFabricadoInternamente("Pata de Mesa", [ItemBOM("Receta Pata", {madera: 1, tornillos: 4})], lista_pata)
        self.registrar_producto_nuevo(pata)

        # --- Tablero ---
        lista_tablero = ListaEnlazadaTareas()
        lista_tablero.agregar_al_final(Tarea(id_t_corte, sierra, 1, 0.8, id_corte, 1000.0))
        tablero = ArticuloFabricadoInternamente("Tablero", [ItemBOM("Receta Tablero", {madera: 2, pegamento: 1})], lista_tablero)
        self.registrar_producto_nuevo(tablero)

        # --- Mesa Completa (usa tablero + patas) ---
        lista_mesa = ListaEnlazadaTareas()
        lista_mesa.agregar_al_final(Tarea(id_t_ensamble, linea, 1, 1.5, id_ensamblaje, 2500.0))
        lista_mesa.agregar_al_final(Tarea(id_t_pintado, cabina, 1, 1.0, id_pintura, 2200.0))
        mesa = ArticuloFabricadoInternamente("Mesa Completa", [ItemBOM("Receta Mesa", {tablero: 1, pata: 4, tornillos: 8})], lista_mesa)
        self.registrar_producto_nuevo(mesa)

        # --- Silla ---
        lista_silla = ListaEnlazadaTareas()
        lista_silla.agregar_al_final(Tarea(id_t_ensamble, linea, 1, 1.0, id_ensamblaje, 2500.0))
        lista_silla.agregar_al_final(Tarea(id_t_pintado, cabina, 1, 0.8, id_pintura, 2200.0))
        silla = ArticuloFabricadoInternamente("Silla", [ItemBOM("Receta Silla", {madera: 2, tornillos: 8, barniz: 1})], lista_silla)
        self.registrar_producto_nuevo(silla)

        print("=== DEMO CARGADA: 3 habilidades, 3 unidades, 4 insumos, 6 colaboradores, 4 productos ===\n")

    # GETTERS para lectura
    def obtener_catalogo_habilidades(self) -> dict:
        return self._catalogo_habilidades

    def obtener_catalogo_tareas(self) -> dict:
        return self._catalogo_tareas

    def obtener_historial_compras(self) -> list:
        # La empresa le delega al gestor la obtención del historial
        return self._gestor_compras.obtener_historial()

    # MÉTODOS para cargar datos desde los CSV sin pisar la lógica de negocio
    def registrar_habilidad_desde_archivo(self, id_hab: int, nombre: str):
        self._catalogo_habilidades[id_hab] = nombre

    def registrar_tarea_desde_archivo(self, id_tarea: int, datos: dict):
        self._catalogo_tareas[id_tarea] = datos

    def agregar_elemento_al_catalogo(self, elemento):
        """Agrega un elemento al catálogo desde GestorArchivos"""
        if elemento.get_tipo_elemento() == "Insumo Básico":
            self._insumos_basicos[elemento.get_id()] = elemento
        else:
            self._productos_fabricados[elemento.get_id()] = elemento
    
    def obtener_elementos_catalogo(self):
        """Retorna la lista de elementos combinada para guardar en el CSV"""
        return list(self._insumos_basicos.values()) + list(self._productos_fabricados.values())
    
    def agregar_unidad(self, unidad):
        """Agrega una unidad de trabajo al registro desde GestorArchivos"""
        self._unidades[unidad.get_id()] = unidad    
        
    def obtener_unidades(self):
        """Retorna la lista de unidades de trabajo"""
        return list(self._unidades.values())
    
    def agregar_solicitud(self, id_solicitud, solicitud):
        self._gestor_solicitudes.agregar_solicitud(id_solicitud, solicitud)

    def obtener_solicitudes(self):
        return self._gestor_solicitudes.obtener_solicitudes()
    
    def obtener_inventario(self):
        """Retorna el inventario de la empresa"""
        return self._inventario
    
    def obtener_gestor_archivos(self):
        return self._gestor_archivos
    
        
    def cargar_compra_desde_archivo(self, orden):
        self._gestor_compras.agregar_compra(orden)

    def cargar_todos_los_datos(self):
        self._gestor_archivos.cargar_todos_los_csv()
        
    def guardar_todos_los_datos(self):
        self._gestor_archivos.guardar_todos_los_csv()
    
    def guardar_inventario(self):
        self._gestor_archivos.guardar_inventario_csv()
    
    def guardar_solicitudes(self):
        self._gestor_archivos.guardar_solicitudes_csv()
    
    def obtener_producciones_terminadas_lifo(self):
        return self._gestor_solicitudes.obtener_terminadas_lifo()