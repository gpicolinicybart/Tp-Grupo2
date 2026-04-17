from empresa import Empresa 
from inventario import Inventario
from compra_insumo import Compra_Insumo
from solicitud_fabricacion import SolicitudDeFabricacion
from insumo_basico import InsumoBasico
from colaboradores import Colaborador
from unidad_de_trabajo import UnidadDeTrabajo
from tarea import Tarea
from itembom import ItemBOM
from articulo_fabricado import ArticuloFabricadoInternamente

class SistemaGestion:
    def __init__(self):
        self.empresa = Empresa(Inventario())
        self.insumos = {}
        self.productos = {}
        self.unidades = {}
        self.colaboradores = {}
        self.solicitudes = {}
        self.contador_id = {
            "insumo": 100,
            "producto": 500,
            "unidad": 1,
            "colab": 700,
            "solicitud": 5000,
            "tarea": 2000
        }
    
    def mostrar_menu_principal(self):
        print("\n" + "="*60)
        print("     SISTEMA DE GESTIÓN DE MANUFACTURA - MENÚ PRINCIPAL")
        print("="*60)
        print("1. Crear Insumo Básico")
        print("2. Crear Producto (Artículo Fabricado)")
        print("3. Agregar Unidad de Trabajo (Máquina)")
        print("4. Agregar Colaborador (Operario)")
        print("5. Crear Solicitud de Fabricación")
        print("6. Procesar Solicitud")
        print("7. Ejecutar Solicitud")
        print("8. Finalizar Solicitud")
        print("9. Ver Estado del Sistema")
        print("10. Cargar Demo Completo")
        print("0. Salir")
        print("="*60)
    
    def crear_insumo(self):
        print("\n--- CREAR INSUMO BÁSICO ---")
        try:
            nombre = input("Nombre del insumo: ").strip()
            costo = float(input("Costo unitario: $"))
            id_insumo = self.contador_id["insumo"]
            self.contador_id["insumo"] += 1
            
            insumo = InsumoBasico(id_insumo, nombre, costo)
            self.insumos[id_insumo] = insumo
            self.empresa._catalogo_elementos.append(insumo)
            print(f"✓ Insumo '{nombre}' creado (ID: {id_insumo})")
        except ValueError:
            print("✗ Error: Ingresa valores válidos")
    
    def crear_producto(self):
        print("\n--- CREAR PRODUCTO FABRICADO ---")
        if not self.insumos:
            print("✗ Primero debes crear insumos")
            return
        
        try:
            nombre = input("Nombre del producto: ").strip()
            
            # Seleccionar insumos para BOM
            print("\nInsumos disponibles:")
            for id_ins, ins in self.insumos.items():
                print(f"  {id_ins}: {ins._nombre} (${ins._costo_unitario})")
            
            bom_dict = {}
            while True:
                id_ins = int(input("\nID del insumo (0 para terminar): "))
                if id_ins == 0:
                    break
                if id_ins in self.insumos:
                    cantidad = int(input(f"Cantidad de {self.insumos[id_ins]._nombre}: "))
                    bom_dict[self.insumos[id_ins]] = cantidad
                else:
                    print("✗ ID no válido")
            
            # Crear BOM
            id_bom = self.contador_id["tarea"]
            self.contador_id["tarea"] += 1
            bom = ItemBOM(id_bom, f"BOM {nombre}", bom_dict)
            
            # Crear lista de tareas vacía (se pueden agregar después)
            id_producto = self.contador_id["producto"]
            self.contador_id["producto"] += 1
            
            producto = ArticuloFabricadoInternamente(id_producto, nombre, [bom], [])
            self.productos[id_producto] = producto
            self.empresa._catalogo_elementos.append(producto)
            print(f"✓ Producto '{nombre}' creado (ID: {id_producto})")
        except (ValueError, KeyError):
            print("✗ Error en la creación del producto")
    
    def agregar_unidad_trabajo(self):
        print("\n--- AGREGAR UNIDAD DE TRABAJO ---")
        try:
            nombre = input("Nombre de la máquina: ").strip()
            horas_disponibles = float(input("Horas disponibles por mes: "))
            costo_operativo = float(input("Costo operativo por hora: $"))
            
            id_unidad = self.contador_id["unidad"]
            self.contador_id["unidad"] += 1
            
            unidad = UnidadDeTrabajo(id_unidad, nombre, horas_disponibles, costo_operativo)
            self.unidades[id_unidad] = unidad
            self.empresa.agregar_unidad_trabajo(unidad)
            print(f"✓ Unidad '{nombre}' agregada (ID: {id_unidad})")
        except ValueError:
            print("✗ Error: Ingresa valores válidos")
    
    def agregar_colaborador(self):
        print("\n--- AGREGAR COLABORADOR ---")
        try:
            nombre = input("Nombre del colaborador: ").strip()
            habilidades_str = input("Habilidades (separadas por coma): ").strip()
            habilidades = [h.strip() for h in habilidades_str.split(",")]
            horas_disponibles = float(input("Horas disponibles: "))
            salario_hora = float(input("Salario por hora: $"))
            
            id_colab = self.contador_id["colab"]
            self.contador_id["colab"] += 1
            
            colab = Colaborador(id_colab, habilidades, horas_disponibles, salario_hora)
            self.colaboradores[id_colab] = colab
            self.empresa.agregar_colaborador(colab)
            print(f"✓ Colaborador '{nombre}' agregado (ID: {id_colab})")
        except ValueError:
            print("✗ Error: Ingresa valores válidos")
    
    def crear_solicitud(self):
        print("\n--- CREAR SOLICITUD DE FABRICACIÓN ---")
        if not self.productos:
            print("✗ Primero debes crear productos")
            return
        
        try:
            print("\nProductos disponibles:")
            for id_prod, prod in self.productos.items():
                print(f"  {id_prod}: {prod._nombre}")
            
            id_producto = int(input("\nID del producto a fabricar: "))
            if id_producto not in self.productos:
                print("✗ Producto no encontrado")
                return
            
            cantidad = int(input("Cantidad a solicitar: "))
            id_solicitud = self.contador_id["solicitud"]
            self.contador_id["solicitud"] += 1
            
            solicitud = SolicitudDeFabricacion(id_solicitud, self.productos[id_producto], cantidad, True)
            self.solicitudes[id_solicitud] = solicitud
            self.empresa.crear_solicitud(solicitud)
            print(f"✓ Solicitud #{id_solicitud} creada")
        except ValueError:
            print("✗ Error en la solicitud")
    
    def procesar_solicitud(self):
        print("\n--- PROCESAR SOLICITUDES ---")
        if not self.solicitudes:
            print("✗ No hay solicitudes")
            return
        
        self.empresa.procesar_solicitud()
        
        for id_sol, sol in self.solicitudes.items():
            estado = sol.get_estado()
            print(f"Solicitud #{id_sol}: {estado}")
    
    def ejecutar_solicitud(self):
        print("\n--- EJECUTAR SOLICITUD ---")
        try:
            id_solicitud = int(input("ID de la solicitud a ejecutar: "))
            self.empresa.ejecutar_solicitud(id_solicitud)
        except ValueError:
            print("✗ ID inválido")
    
    def finalizar_solicitud(self):
        print("\n--- FINALIZAR SOLICITUD ---")
        try:
            id_solicitud = int(input("ID de la solicitud a finalizar: "))
            self.empresa.finalizar_solicitud(id_solicitud)
        except ValueError:
            print("✗ ID inválido")
    
    def ver_estado(self):
        print("\n" + "="*60)
        print("               ESTADO DEL SISTEMA")
        print("="*60)
        
        print(f"\n📦 Insumos registrados: {len(self.insumos)}")
        for id_ins, ins in self.insumos.items():
            stock = self.empresa._inventario.consultar_stock(ins)
            print(f"   {id_ins}: {ins._nombre} - Stock: {stock} unidades")
        
        print(f"\n🏭 Productos: {len(self.productos)}")
        for id_prod, prod in self.productos.items():
            print(f"   {id_prod}: {prod._nombre}")
        
        print(f"\n⚙️ Unidades de Trabajo: {len(self.unidades)}")
        for id_unit, unit in self.unidades.items():
            print(f"   {id_unit}: {unit._nombre}")
        
        print(f"\n👤 Colaboradores: {len(self.colaboradores)}")
        for id_col, col in self.colaboradores.items():
            print(f"   {id_col}: ID={id_col}, Habilidades={col._habilidades}")
        
        print(f"\n📋 Solicitudes activas: {len(self.empresa._solicitudes)}")
        self.empresa.mostrar_solicitudes()
    
    def cargar_demo(self):
        print("\n--- CARGANDO ESCENARIO DEMO ---")
        
        # Insumos
        acero = InsumoBasico(100, "Plancha de Acero", 500.0)
        tornillos = InsumoBasico(101, "Tornillo 10mm", 5.0)
        self.insumos[100] = acero
        self.insumos[101] = tornillos
        self.empresa._catalogo_elementos.extend([acero, tornillos])
        
        # Agregar stock inicial
        orden_acero = Compra_Insumo(1001, acero, 10)
        orden_tornillos = Compra_Insumo(1002, tornillos, 50)
        orden_acero.recibir_materiales(self.empresa._inventario)
        orden_tornillos.recibir_materiales(self.empresa._inventario)
        
        # Unidad de trabajo
        prensa = UnidadDeTrabajo(1, "Prensa Hidráulica", 40.0, 1500.0)
        self.unidades[1] = prensa
        self.empresa.agregar_unidad_trabajo(prensa)
        
        # Colaborador
        soldador = Colaborador(700, ["Soldadura"], 40.0, 1000.0)
        self.colaboradores[700] = soldador
        self.empresa.agregar_colaborador(soldador)
        
        # Tarea
        tarea = Tarea("Soldadura y Ensamblaje", prensa, 1, 2.0, "Soldadura", 1000.0)
        
        # Producto
        bom = ItemBOM(2000, "BOM Mesa", {acero: 1, tornillos: 4})
        mesa = ArticuloFabricadoInternamente(500, "Mesa Metálica", [bom], [tarea])
        self.productos[500] = mesa
        self.empresa._catalogo_elementos.append(mesa)
        
        # Solicitud
        solicitud = SolicitudDeFabricacion(5000, mesa, 2, True)
        self.solicitudes[5000] = solicitud
        self.empresa.crear_solicitud(solicitud)
        
        self.contador_id = {"insumo": 102, "producto": 501, "unidad": 2, "colab": 701, "solicitud": 5001, "tarea": 2001}
        
        print("✓ Demo cargada exitosamente")
        print("\nPuedes ahora:")
        print("  6. Procesar la solicitud")
        print("  7. Ejecutar la solicitud")
        print("  8. Finalizar la solicitud")
        print("  9. Ver Estado del Sistema")

def main():
    print("\n" + "="*60)
    print("  BIENVENIDO AL SISTEMA DE GESTIÓN DE MANUFACTURA")
    print("="*60)
    
    sistema = SistemaGestion()
    
    while True:
        sistema.mostrar_menu_principal()
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "1":
            sistema.crear_insumo()
        elif opcion == "2":
            sistema.crear_producto()
        elif opcion == "3":
            sistema.agregar_unidad_trabajo()
        elif opcion == "4":
            sistema.agregar_colaborador()
        elif opcion == "5":
            sistema.crear_solicitud()
        elif opcion == "6":
            sistema.procesar_solicitud()
        elif opcion == "7":
            sistema.ejecutar_solicitud()
        elif opcion == "8":
            sistema.finalizar_solicitud()
        elif opcion == "9":
            sistema.ver_estado()
        elif opcion == "10":
            sistema.cargar_demo()
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("✗ Opción no válida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrumpido por el usuario")
    except Exception as e:
        print(f"\n[ERROR CRÍTICO]: {e}")