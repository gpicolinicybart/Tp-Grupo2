class Elemento: #Gemini, revisa tambien encapsulamiento
    def __init__(self, id_elemento: int, nombre: str):
    #esto es un constructor, se llama igual que la clase y se ejecuta cada vez que se crea un nuevo objeto de esta clase

        self._id = id_elemento
        self._nombre = nombre
        
    def get_costo_unitario(self) -> float:
        pass

#le pregunte a gemini como se hacia, lo vemos cuando veamos herencia
class InsumoBasico(Elemento):
    def __init__(self, id_elemento: int, nombre: str, costo_fijo: float):
        super().__init__(id_elemento, nombre) 
        # Llama al constructor del padre, herada los atributos id y nombre 
        self._costo_fijo = costo_fijo
        
    def get_costo_unitario(self) -> float:
        return self._costo_fijo


class ArticuloFabricadoInternamente(Elemento):
    def __init__(self, id_elemento: int, nombre: str, bom: list, lista_tareas: list):
        super().__init__(id_elemento, nombre)
        self._bom = bom # Lista de elementos
        self._lista_tareas = lista_tareas 

    def get_costo_unitario(self) -> float:
        costo_total = 0.0
        
        # 1. Sumamos materiales (Recursivo)
        for elemento, cantidad in self._bom.items():
            costo_total += elemento.get_costo_unitario() * cantidad
            
        # 2. Sumamos tareas (Delegamos el cálculo a cada tarea)
        for tarea in self._lista_tareas:
            costo_total += tarea.get_costo()
            
        return costo_total
    #Arriba se define el metodo para calcular el costo total del artículo sumando el costo de los materiales (usando get_costo_unitario de cada elemento) y el costo de las tareas (usando get_costo de cada tarea).
    #respeta encapsulamiento porque cada clase se encarga de calcular su propio costo, no accede directamente a los atributos de otras clases, sino que llama a sus métodos públicos para obtener la información necesaria.




        #Empezar en el producto actual.
        #Mirar todos sus componentes en la BOM.
        #Si alguno de esos componentes es el producto original, tira error de ciclo.
        #Si no, revisar los componentes de los componentes (recursión profunda)
    def validar_ciclos(self, visitados=None) -> bool:
        if visitados is None:
            visitados = []
        
        # Si el ID ya está en la lista, lanzamos la excepción
        if self._id in visitados:
            raise ValueError(f"ERROR DE DISEÑO: Ciclo detectado. El artículo '{self._nombre}' (ID: {self._id}) se requiere a sí mismo en su propia cadena de producción.")
        
        nuevo_camino = visitados + [self._id]
        
        for elemento in self._bom.keys():
            if isinstance(elemento, ArticuloFabricadoInternamente):
                # La recursión sigue, y si un hijo lanza el raise, 
                # este "sube" automáticamente hasta el nivel más alto.
                elemento.validar_ciclos(nuevo_camino)
        
        return False # Si llega acá, es que todo está OK
    


class ItemBOM:
    def __init__(self, id_item: int, nombre: str, diccionario_elementos: dict):
        self._id = id_item
        self._nombre = nombre
        self._diccionario = diccionario_elementos # Formato esperado: {Elemento: cantidad}
        
    def validar_entero_positivo(self):
        pass
        
    def get_costo_total(self) -> float:
        pass

class UnidadDeTrabajo:
    def __init__(self, id_unidad: int, capacidad_max_horas: float, limite_de_colab: int, costo_operativo_por_hora: float):
        self._id = id_unidad
        self._capacidad_max_horas = capacidad_max_horas
        self._limite_de_colab = limite_de_colab
        self._horas_reservadas = 0.0 # arranca en 0
        self._costo_operativo_por_hora = costo_operativo_por_hora # deberiamos calcularlo y q se actualice?
        
    def verificar_disponibilidad(self, horas_necesarias: float) -> bool:
        # La máquina sabe cuánto le queda libre
        return (self._capacidad_max_horas - self._horas_reservadas) >= horas_necesarias

    def reservar_horas(self, horas: float):
        # La máquina se encarga de anotar su propia reserva
        self._horas_reservadas += horas

class Colaborador:
    def __init__(self, id_colaborador: int, habilidades: list, horas_disponibles: float, salario_hora: float):
        self._id = id_colaborador
        self._habilidades = habilidades
        self._horas_disponibles = horas_disponibles
        self._horas_asignadas = 0.0 # arranca en 0
        self._salario_hora = salario_hora
        
    def tiene_habilidad(self, habilidad: str) -> bool:
        #se revisa que la habilidad q se pide esta dentro de su lista
        if habilidad in self._habilidades:
            return True
        else:
            return False
        
    def verificar_disponibilidad(self, horas_necesarias: float) -> bool:
        #cuantas horas libres le quedan
        horas_libres=self._horas_disponibles-self._horas_asignadas
        #da true si las horas libres le dan para la tarea q se quiere hacer
        if horas_libres>=horas_necesarias:
            return True
        else:
            return False



class Tarea:
    def __init__(self, descripcion: str, unidad_requerida: UnidadDeTrabajo, cant_colaboradores_req: int, tiempo_por_unidad: float, habilidad_requerida: str):
        self._descripcion = descripcion
        self._unidad_requerida = unidad_requerida
        self._cant_colaboradores_req = cant_colaboradores_req
        self._tiempo_por_unidad = tiempo_por_unidad
        self._habilidad_requerida = habilidad_requerida
        
    def get_costo(self) -> float:
        
        # La tarea sabe cuánto tiempo lleva y qué máquina usa
        costo_maquina = self._tiempo_por_unidad * self._unidad_requerida._costo_operativo_por_hora
        
        # También sabe cuánta gente necesita
        # Usamos el valor base de 3500 por ahora
        costo_mano_obra = self._tiempo_por_unidad * self._cant_colaboradores_req * 3500.0
        
        return costo_maquina + costo_mano_obra

class Compra_Insumo:
    def __init__(self, id_orden: int, insumo: InsumoBasico, cantidad: int):
        self._id = id_orden
        self._insumo = insumo
        self._cantidad = cantidad
        
        
    def recibir_materiales(self, inventario): 
        #directamente ingresa el stock al inventario, dsp si hay que ponerlo como pendiente o hacerlo mas complejo vemos, por ahora simple.
        inventario.ingresar_stock(self._insumo,self._cantidad)
        print(f"Se ingresaron  con éxito {self._cantidad} unidades de {self._insumo._nombre} al inventario (Orden: {self._id}).")
        


class SolicitudDeFabricacion:
    def __init__(self, id_solicitud: int, item_solicitado: ItemBOM, cantidad: int, es_para_cliente: bool):
        self._id = id_solicitud
        self._item_solicitado = item_solicitado
        self._cantidad = cantidad
        self._estado = "Creada" # estado inicial, despues tendria q variar entre en proceso, demorada, entregada,etc
        self._es_para_cliente = es_para_cliente #esto tenemos q hablarlo si cuando se solicita una mesa se generan automaticamente solicitudes de patas
        #o el programa internamente avanza con la creacion de patas sin que se generen solicitudes
        self._colaboradores_asignados = [] # es necesario?#guille: yo no creo.#nico: es necesario para mostrar la info de los colabs y pasarle la info a las tareas.

    def mostrar_info (self):
        print(f"-> SOLICITUD: ID {self._id} | Estado:{self._estado} | Fabricar: {self._cantidad} unidades de '{self._item_solicitado._nombre} colaboradores'{self._colaboradores_asignados} ")
    def planificar (self, inventario):#saque esto, duda, no rompe encapsulamiento?(self, inventario, unidades: list, colaboradores: list) -> bool:
        print(f"\n--- PLANIFICACIÓN ID: {self._id} ---")
        errores = []
        producto = self._item_solicitado # El ArticuloFabricado
        
        # 1. Preguntamos al Inventario (Encapsulado)
        for elem, cant in producto._bom.items():
            total = cant * self._cantidad
            if not inventario.hay_disponibilidad(elem, total):
                errores.append(f"Falta stock de {elem._nombre}")

        # 2. Preguntamos a las Unidades (Encapsulado)
        for tarea in producto._lista_tareas:
            horas = tarea._tiempo_por_unidad * self._cantidad
            if not tarea._unidad_requerida.verificar_disponibilidad(horas):
                errores.append(f"Sobrecarga en Unidad {tarea._unidad_requerida._id}")

        if errores:
            self._estado = "Fallida"
            for e in errores: 
                print(f" [!] {e}")
            return False

        # 3. Si todo OK, damos la orden de reservar (Delegación)
        for elem, cant in producto._bom.items():
            inventario.reservar_stock(elem, cant * self._cantidad)
            
        for tarea in producto._lista_tareas:
            tarea._unidad_requerida.reservar_horas(tarea._tiempo_por_unidad * self._cantidad)
            
        self._estado = "Planificada"
        return True
        
    def ejecutar(self, inventario):
        pass
        
    def finalizar(self, inventario): #ejecutar y finalizar no es lo mismo?
        pass


class Inventario:
    def __init__(self):
        # Usamos diccionarios vacíos al instanciar el inventario
        #usamos el objeto elemento como clave y la cantidad como valor
        self._stock_fisico = {} 
        self._stock_reservado = {}
        
    def consultar_stock(self, elem: Elemento) -> int:
        return self._stock_fisico.get(elem,0) #el get va a devolver la cantidad o 0 si el elemento no existe en el dict
        
    def reservar_stock(self, elem: Elemento, cant: int):
        stock_actual=self.consultar_stock(elem)
        reservado_actual=self._stock_reservado.get(elem,0)
        stock_disponible=stock_actual-reservado_actual
        if stock_disponible>=cant:
            self._stock_reservado[elem]=reservado_actual+cant
            print(f"-> RESERVA: Se reservaron {cant} unidades de '{elem._nombre}'.")
        else:
            print(f"->ALERTA: No hay stock suficiente para reservar {cant} de '{elem._nombre}'.")
    def descontar_stock(self, elem: Elemento, cant: int):
        # se descuenta el fisico y la reserva cuando se arranca a producir
        if elem in self._stock_reservado and self._stock_reservado[elem]>=cant:
            self._stock_fisico[elem]-=cant 
            self._stock_reservado[elem]-=cant 
            print(f"->CONSUMO: Se utilizaron {cant} unidades de '{elem._nombre}'.")
        else:
            print(f"->ERROR: Intentando consumir '{elem._nombre} sin reserva previa.")
        
    def ingresar_stock(self, elem: Elemento, cant: int):#si lo hacemos con una tarea me parece q esto vuela
        if elem in self._stock_fisico:
            self._stock_fisico[elem]+=cant
        else: 
            self._stock_fisico[elem]=cant
    
    def hay_disponibilidad(self, elem: Elemento, cant_pedida: int) -> bool:
        # El inventario hace su propia cuenta interna
        stock_real = self.consultar_stock(elem)
        reservado = self._stock_reservado.get(elem, 0)
        return (stock_real - reservado) >= cant_pedida

#aca en lo de ingresar stock que me ddecias que vuela , gemini me dijo q es mejor mantenerlo separado , pero lo vemos cuando lo hagamos 

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
        pass
        
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








#print("--- INICIANDO SISTEMA TECNOMECÁNICA ITBA ---")
    
#mi_inventario = Inventario()
#tecno_mecanica = Empresa(mi_inventario)
    
#algunos ejs de insumos basicos para mostrar
#acero = InsumoBasico(id_elemento=101, nombre="Plancha de Acero", costo_fijo=500.0)
#tornillos = InsumoBasico(id_elemento=102, nombre="Caja de Tornillos 10mm", costo_fijo=50.0)
    
#print("\n--- CONSULTA DE STOCK INICIAL ---")
#print(f"Stock de '{acero._nombre}': {mi_inventario.consultar_stock(acero)} unidades.")
    
#print("\n--- SIMULANDO COMPRA DE INSUMOS ---")
#creamos algunas ordenes de compra
#orden_1 = Compra_Insumo(id_orden=1001, insumo=acero, cantidad=10)
#orden_2 = Compra_Insumo(id_orden=1002, insumo=tornillos, cantidad=20)
    
#la "empresa" registra lass compras
#tecno_mecanica.registrar_compra(orden_1)
#tecno_mecanica.registrar_compra(orden_2)
    
#print("\n--- RECIBIENDO MATERIALES EN FÁBRICA ---")
    
#orden_1.recibir_materiales(mi_inventario)
#haciendo de cuenta q la orden1 llegó del "camion" y la orden2 todavia no
    
#print("\n--- CONSULTA DE STOCK ACTUALIZADA ---")
#print(f"Stock de '{acero._nombre}': {mi_inventario.consultar_stock(acero)} unidades.")
#print(f"Stock de '{tornillos._nombre}': {mi_inventario.consultar_stock(tornillos)} unidades (Aún no recibimos la orden 1002).")
    
#print("\n--- CREANDO SOLICITUD DE FABRICACIÓN ---")
#hacemos que creamos una solicitud de mesa pero usamos solo el acero para q no sea toda la fabricacion compleja
#solicitud_mesa = SolicitudDeFabricacion(id_solicitud=5001, item_solicitado=acero, cantidad=2, es_para_cliente=True)
    
#se registra la solicitud y se muestra
#tecno_mecanica.crear_solicitud(solicitud_mesa)
#solicitud_mesa.mostrar_info()

#print("\n--- GESTIÓN DE COLABORADORES ---")
   
#operario_1 = Colaborador(id_colaborador=701, habilidades=["Soldadura", "Ensamblaje"], horas_disponibles=8.0, salario_hora=3500.0)
    
#tecno_mecanica.agregar_colaborador(operario_1)
    
#print(f"\nVerificando habilidades del Colaborador ID {operario_1._id}...")
#habilidad_requerida = "Soldadura"
    
#if operario_1.tiene_habilidad(habilidad_requerida):
    #print(f"-> CHECK: El colaborador tiene la habilidad '{habilidad_requerida}'.")
#else:
 #   print(f"-> ERROR: El colaborador NO sabe hacer '{habilidad_requerida}'.")

#horas_tarea = 5.0      
#print(f"\nVerificando disponibilidad de tiempo (La tarea requiere {horas_tarea} horas)...")
    
#if operario_1.verificar_disponibilidad(horas_tarea):
    #print(f"-> CHECK: El colaborador tiene tiempo suficiente. (Disponibles: {operario_1._horas_disponibles}hs | Necesarias: {horas_tarea}hs)")
    # Simulamos que le asignamos la tarea
    #operario_1._horas_asignadas += horas_tarea
    #print(f"-> ACTUALIZACIÓN: Se le asignaron {horas_tarea}hs. Le quedan {operario_1._horas_disponibles - operario_1._horas_asignadas}hs libres.")
#else:
    #print(f"-> ALERTA: El colaborador no tiene horas suficientes.")


#print("\n--- DETENIENDO SISTEMA TECNOMECÁNICA ITBA ---")
# --- 1. CONFIGURACIÓN DEL ENTORNO ---
mi_inventario = Inventario()
tecno_mecanica = Empresa(mi_inventario)

# --- 2. DEFINICIÓN DE RECURSOS (MÁQUINAS Y PERSONAS) ---
# Unidad de trabajo con un costo de $5000 por hora
prensa = UnidadDeTrabajo(id_unidad=1, capacidad_max_horas=100.0, limite_de_colab=2, costo_operativo_por_hora=5000.0)
tecno_mecanica.agregar_unidad_trabajo(prensa)

# Colaborador (Usamos su salario_hora para el cálculo)
juan = Colaborador(id_colaborador=701, habilidades=["Operador"], horas_disponibles=40.0, salario_hora=3500.0)
tecno_mecanica.agregar_colaborador(juan)

# --- 3. DEFINICIÓN DE PRODUCTOS ---
# Insumo Básico (Costo fijo)
chapa = InsumoBasico(id_elemento=101, nombre="Chapa de Aluminio", costo_fijo=1200.0)

# Tarea para fabricar un Panel (Lleva 2 horas de prensa y 1 operario)
tarea_panel = Tarea(
    descripcion="Prensado de chapa",
    unidad_requerida=prensa,
    cant_colaboradores_req=1,
    tiempo_por_unidad=2.0,
    habilidad_requerida="Operador"
)

# Artículo Fabricado: Panel Reforzado
# Receta (BOM): 1 Chapa
# Proceso: 1 Tarea de prensado
panel = ArticuloFabricadoInternamente(
    id_elemento=201, 
    nombre="Panel Reforzado", 
    bom={chapa: 1}, 
    lista_tareas=[tarea_panel]
)

# --- 4. PROBANDO EL SISTEMA ---

print("\n--- TEST 1: REGISTRO Y VALIDACIÓN ---")
# Esto debería funcionar bien porque no hay ciclos
tecno_mecanica.registrar_producto_nuevo(panel)

print("\n--- TEST 2: CÁLCULO DE COSTOS (DELEGACIÓN) ---")
# Debería sumar: $1200 (chapa) + $10000 (2hs prensa) + $7000 (2hs de operario a $3500)
# Total esperado: $18200.00
tecno_mecanica.obtener_presupuesto(panel, cantidad=1)

print("\n--- TEST 3: DETECCIÓN DE CICLOS (EL CUIDADO) ---")
# Vamos a crear un error a propósito: Un Panel que necesita otro Panel
ciclo_error = ArticuloFabricadoInternamente(
    id_elemento=202, 
    nombre="Panel Infinito", 
    bom={panel: 1}, 
    lista_tareas=[]
)
# Cerramos el círculo: el 'panel' original ahora necesita al 'ciclo_error'
panel._bom[ciclo_error] = 1 

print("Intentando registrar producto con ciclo...")
tecno_mecanica.registrar_producto_nuevo(panel)

print("\n--- FIN DE LAS PRUEBAS ---") 