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


#script de prueba (para mostrar si quieren)

if __name__ == "__main__":
    try:
        print(" --------INICIANDO SISTEMA TECNOMECÁNICA ITBA--------")
        
        mi_inventario = Inventario()
        tecno_mecanica = Empresa(mi_inventario)
            
        print("\n--- 1. CATÁLOGO DE INSUMOS ---")
        acero = InsumoBasico(id_elemento=101, nombre="Plancha de Acero", costo_fijo=500.0)
        tornillos = InsumoBasico(id_elemento=102, nombre="Caja de Tornillos 10mm", costo_fijo=50.0)
        print(acero)
        print(tornillos)
            
        print("\n--- 2. GESTIÓN DE COMPRAS Y STOCK ---")
        orden_1 = Compra_Insumo(id_orden=1001, insumo=acero, cantidad=10)
        tecno_mecanica.registrar_compra(orden_1)
        print(orden_1) 
        
        orden_1.recibir_materiales(mi_inventario)
        print(f"-> Stock físico de '{acero._nombre}': {mi_inventario.consultar_stock(acero)} unidades.")
            
        print("\n--- 3. SOLICITUD DE FABRICACIÓN  ---")
        
        solicitud_mesa = SolicitudDeFabricacion(id_solicitud=5001, item_solicitado=acero, cantidad=2, es_para_cliente=True)
        tecno_mecanica.crear_solicitud(solicitud_mesa)
        
        print("Estado inicial:", solicitud_mesa)
        
        solicitud_mesa.planificar(mi_inventario)
        solicitud_mesa.ejecutar(mi_inventario)
        solicitud_mesa.finalizar(mi_inventario)
        
        print("\nEstado final tras la producción:")
        print(solicitud_mesa)

        print("\n--- 4. GESTIÓN DE COLABORADORES ---")
        operario_1 = Colaborador(id_colaborador=701, habilidades=["Soldadura", "Ensamblaje"], horas_disponibles=8.0, salario_hora=3500.0)
        tecno_mecanica.agregar_colaborador(operario_1)
        print(operario_1)
        
        tarea,duracion= "Soldadura", 5.0

        print(f"\nEvaluando asignación de tarea (Requiere {tarea}, {duracion}hs)...")
        if operario_1.tiene_habilidad(tarea) and operario_1.verificar_disponibilidad(duracion):
            print("-> CHECK: El colaborador cumple los requisitos. Asignando tarea...")
            operario_1._horas_asignadas += duracion
            print(operario_1) 
        else:
            print("-> ERROR: El colaborador no cumple con los requisitos.")

        print("-----------------------------FIN-------------------------------------")

    except ValueError as e:
        print(f"Se detectó un errror del tipo: -> {e}")
    except TypeError as e:
        print(f"Se detectó un error del tipo: -> {e}")

