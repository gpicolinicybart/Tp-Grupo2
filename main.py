#importamos todas las clases para poder hacer el script de prueba (aunque no se usen todas)
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


if __name__ == "__main__":
    try:
        print(" --------INICIANDO SISTEMA TECNOMECÁNICA ITBA--------")
        
        mi_inventario = Inventario()
        tecno_mecanica = Empresa(mi_inventario)
            
        print("\n--- 1. CATÁLOGO DE INSUMOS ---")
        acero = InsumoBasico(101, "Plancha de Acero", 500.0)
        tornillos = InsumoBasico(102, "Tornillo 10mm", 5.0)
        pintura = InsumoBasico(103, "Pintura Industrial Azul", 200.0)
        print(acero)
        print(tornillos)
        print(pintura)
            
        print("\n--- 2. GESTIÓN DE COMPRAS Y STOCK ---")
        orden_1 = Compra_Insumo(1001, acero, 10)
        orden_2 = Compra_Insumo(1002, tornillos, 20)
        orden_3 = Compra_Insumo(1003, pintura, 5)

        tecno_mecanica.registrar_compra(orden_1)
        tecno_mecanica.registrar_compra(orden_2)
        tecno_mecanica.registrar_compra(orden_3)

        print(orden_1)
        print(orden_2)
        print(orden_3)
        
        orden_1.recibir_materiales(mi_inventario)
        orden_2.recibir_materiales(mi_inventario)

        print(f"-> Stock físico de '{acero._nombre}': {mi_inventario.consultar_stock(acero)} unidades.")
        print(f"-> Stock físico de '{tornillos._nombre}': {mi_inventario.consultar_stock(tornillos)} unidades.")
        print(f"-> Stock físico de '{pintura._nombre}': {mi_inventario.consultar_stock(pintura)} unidades.")
            

        # Producto ya definido en el sistema
        bom_mesa = ItemBOM(2001, "BOM Mesa Simple", {acero: 1, tornillos: 4})

        mesa = ArticuloFabricadoInternamente(
            3001,
            "Mesa Metálica",
            [bom_mesa],
            []
        )


        print("\n--- 3. SOLICITUD DE FABRICACIÓN ---")
        solicitud_mesa = SolicitudDeFabricacion(5001, mesa, 2, True)

        tecno_mecanica.crear_solicitud(solicitud_mesa)
        
        print("Estado inicial:", solicitud_mesa)
        
        solicitud_mesa.planificar(mi_inventario)
        solicitud_mesa.ejecutar(mi_inventario)
        solicitud_mesa.finalizar(mi_inventario)
        
        print("\nEstado final tras la producción:")
        print(solicitud_mesa)


        print("\n--- 4. GESTIÓN DE COLABORADORES ---")
        operario_1 = Colaborador(
            701,
            ["Soldadura", "Ensamblaje"],
            8.0,
            3500.0
        )

        tecno_mecanica.agregar_colaborador(operario_1)
        print(operario_1)
        
        tarea, duracion = "Soldadura", 5.0
        operario_1.asignar_tarea(tarea, duracion)
        print(operario_1)

        print("-----------------------------FIN-------------------------------------")

    except ValueError as e:
        print(f"Se detectó un errror del tipo: -> {e}")
    except TypeError as e:
        print(f"Se detectó un error del tipo: -> {e}")
