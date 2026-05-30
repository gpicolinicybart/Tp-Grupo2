from unittest.mock import MagicMock
from articulo_fabricado import ArticuloFabricadoInternamente
from itembom import ItemBOM
from tarea import Tarea
from insumo_basico import InsumoBasico
from lista_tareas import ListaEnlazadaTareas

def test_costo_unitario_articulo_fabricado():
    # Simulamos que los materiales cuestan $500
    bom_mock = MagicMock(spec=ItemBOM)
    bom_mock.get_costo_total.return_value = 500.0
    
    # Simulamos que la Lista Enlazada de tareas cuesta $300 (NUEVO)
    lista_tareas_mock = MagicMock(spec=ListaEnlazadaTareas)
    lista_tareas_mock.get_costo_total.return_value = 300.0
    
    # Creamos el artículo con esos mocks
    mesa = ArticuloFabricadoInternamente("Mesa", [bom_mock], lista_tareas_mock)
    
    # Verificación: Costo Total = 500 (BOM) + 300 (Tareas) = 800
    assert mesa.get_costo_unitario() == 800.0

def test_detectar_ciclo_infinito():
    # Inyectamos MagicMock en la lista de tareas para que no moleste
    item_a = ArticuloFabricadoInternamente("Parte A", [], MagicMock()) 
    bom_ciclico = ItemBOM("BOM Ciclo", {item_a: 1}) # Círculo vicioso
    
    item_a.set_bom([bom_ciclico])
    
    # NUEVO: Ahora validar_ciclos atrapa el error (try-except) y devuelve False
    assert item_a.validar_ciclos() is False

def test_articulo_fabricado_id_autoincremental():
    art1 = ArticuloFabricadoInternamente("Producto A", [], MagicMock())
    art2 = ArticuloFabricadoInternamente("Producto B", [], MagicMock())
    assert art1.get_id() < art2.get_id()

def test_calcular_materiales_necesarios_recursivo():
    madera = InsumoBasico("Madera", 100.0)
    tornillo = InsumoBasico("Tornillo", 5.0)
    
    # Sub-ensamble: Pata (1 madera, 4 tornillos)
    bom_pata = ItemBOM("Receta Pata", {madera: 1, tornillo: 4})
    pata = ArticuloFabricadoInternamente("Pata", [bom_pata], MagicMock())
    
    # Producto Final: Mesa (1 madera, 4 patas)
    bom_mesa = ItemBOM("Receta Mesa", {madera: 1, pata: 4})
    mesa = ArticuloFabricadoInternamente("Mesa", [bom_mesa], MagicMock())
    
    # Necesidades para fabricar 2 MESAS
    necesidades = mesa.calcular_materiales_necesarios(2)
    
    # Verificaciones:
    # Maderas = 2 mesas * (1 base + 4 patas * 1 madera) = 10 maderas
    assert necesidades[madera] == 10
    # Tornillos = 2 mesas * (4 patas * 4 tornillos) = 32 tornillos
    assert necesidades[tornillo] == 32
    # Verificamos que la pata no esté en la lista (se explotó exitosamente a insumo puro)
    assert pata not in necesidades

def test_calcular_horas_en_unidad_funcional():
    unidad_corte = MagicMock()
    unidad_corte.get_id.return_value = 1
    
    unidad_pintura = MagicMock()
    unidad_pintura.get_id.return_value = 2

    tarea_corte_1 = MagicMock()
    tarea_corte_1.get_unidad_requerida.return_value = unidad_corte
    tarea_corte_1.get_tiempo_por_unidad.return_value = 2.0  

    tarea_corte_2 = MagicMock()
    tarea_corte_2.get_unidad_requerida.return_value = unidad_corte
    tarea_corte_2.get_tiempo_por_unidad.return_value = 1.5  

    # Esta es la tramposa que deberia ignorar el sistema
    tarea_pintura = MagicMock()
    tarea_pintura.get_unidad_requerida.return_value = unidad_pintura
    tarea_pintura.get_tiempo_por_unidad.return_value = 5.0  

    # NUEVO: Configuramos el mock de la lista para que se pueda iterar en el bucle 'for'
    lista_tareas_mock = MagicMock()
    lista_tareas_mock.__iter__.return_value = iter([tarea_corte_1, tarea_corte_2, tarea_pintura])

    articulo = ArticuloFabricadoInternamente("Mueble", [], lista_tareas_mock)

    # Solo queremos horas en la unidad 1 (corte)
    horas_totales = articulo.calcular_horas_en_unidad(unidad_corte, 10)

    # 10 muebles * (2.0 + 1.5 hs) = 35.0 hs
    assert horas_totales == 35.0

def test_gestionar_reabastecimiento_crea_solicitud_hija():
    pata = ArticuloFabricadoInternamente("Pata de Mesa", [], MagicMock())
    empresa_mock = MagicMock()

    # Simulamos que faltan 50 patas
    mensaje_alerta = pata.gestionar_reabastecimiento(empresa_mock, 50)
    
    # NUEVO: Le preguntamos al mock de empresa cuántas veces se llamó a crear_solicitud
    cantidad_llamadas = empresa_mock.crear_solicitud.call_count 
    
    assert cantidad_llamadas == 1
    assert "50" in mensaje_alerta
    assert "Pata de Mesa" in mensaje_alerta