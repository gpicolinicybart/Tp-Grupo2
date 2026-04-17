#!/usr/bin/env python3
import traceback
from empresa import Empresa
from inventario import Inventario
from insumo_basico import InsumoBasico
from colaboradores import Colaborador
from unidad_de_trabajo import UnidadDeTrabajo
from tarea import Tarea
from itembom import ItemBOM
from articulo_fabricado import ArticuloFabricadoInternamente
from solicitud_fabricacion import SolicitudDeFabricacion
from compra_insumo import Compra_Insumo

try:
    # Setup
    inventario = Inventario()
    empresa = Empresa(inventario)

    # Insumos
    acero = InsumoBasico(100, "Acero", 500.0)
    tornillos = InsumoBasico(101, "Tornillos", 5.0)

    # Stock
    orden_acero = Compra_Insumo(1001, acero, 10)
    orden_tornillos = Compra_Insumo(1002, tornillos, 50)
    orden_acero.recibir_materiales(inventario)
    orden_tornillos.recibir_materiales(inventario)

    # Máquina
    prensa = UnidadDeTrabajo(1, "Prensa", 40.0, 1500.0)
    empresa.agregar_unidad_trabajo(prensa)

    # Operario
    soldador = Colaborador(700, ["Soldadura"], 40.0, 1000.0)
    empresa.agregar_colaborador(soldador)

    # Tarea
    tarea = Tarea("Soldadura", prensa, 1, 2.0, "Soldadura", 1000.0)

    # BOM y Producto
    bom = ItemBOM(2000, "BOM", {acero: 1, tornillos: 4})
    mesa = ArticuloFabricadoInternamente(500, "Mesa", [bom], [tarea])

    # Solicitud
    solicitud = SolicitudDeFabricacion(5000, mesa, 2, True)
    empresa.crear_solicitud(solicitud)

    print("Procesando solicitud...")
    # Procesar
    empresa.procesar_solicitud()
    print("Éxito!")
    
except Exception as e:
    print(f"ERROR ENCONTRADO:")
    traceback.print_exc()
