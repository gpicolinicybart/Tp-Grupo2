import pytest
from unittest.mock import MagicMock
from articulo_fabricado import ArticuloFabricadoInternamente
from itembom import ItemBOM
from tarea import Tarea
from insumo_basico import InsumoBasico

def test_costo_unitario_articulo_fabricado():
    # simulo que los materiales cuestan $500 y la mano de obra 300
    bom_mock = MagicMock(spec=ItemBOM)
    bom_mock.get_costo_total.return_value = 500.0
    tarea_mock = MagicMock(spec=Tarea)
    tarea_mock.get_costo.return_value = 300.0
    
    #Creamos el artículo con esos mocks
    mesa = ArticuloFabricadoInternamente("Mesa", [bom_mock], [tarea_mock])
    assert mesa.get_costo_unitario() == 800.0 # Verificación: Costo Total = 500 (BOM) + 300 (Tarea) = 800
    #el assert "afirma" q tiene q ser verdadero si llega a ser Falso, hace fallar el test y tira error

def test_detectar_ciclo_infinito():
    item_a = ArticuloFabricadoInternamente("Parte A", [], []) # q no se requiera a si mismo
    bom_ciclico = ItemBOM("BOM Ciclo", {item_a: 1}) # hago un BOM que contiene al mismo item_a (circulo vicioso)
    item_a._bom = [bom_ciclico]
    
    with pytest.raises(ValueError, match="CICLO DETECTADO"):  # al validar ciclos, debe saltar el error
        item_a.validar_ciclos()

def test_articulo_fabricado_id_autoincremental():
    art1 = ArticuloFabricadoInternamente("Producto A", [], [])
    art2 = ArticuloFabricadoInternamente("Producto B", [], [])
    assert art1.get_id() < art2.get_id()

def test_calcular_materiales_necesarios_recursivo():
    #Verifica que la explosión del BOM baje correctamente por todos los niveles
    #hasta llegar a los insumos básicos, acumulando las cantidades exactas.
    # Insumos básicos
    madera = InsumoBasico("Madera", 100.0)
    tornillo = InsumoBasico("Tornillo", 5.0)
    # Sub-ensamble: Pata (1 madera, 4 tornillos)
    bom_pata = ItemBOM("Receta Pata", {madera: 1, tornillo: 4})
    pata = ArticuloFabricadoInternamente("Pata", [bom_pata], [])
    #  Prod Mesa (1 madera, 4 patas)
    bom_mesa = ItemBOM("Receta Mesa", {madera: 1, pata: 4})
    mesa = ArticuloFabricadoInternamente("Mesa", [bom_mesa], [])
    #  necesidades para fabricar 2 MESAS
    necesidades = mesa.calcular_materiales_necesarios(2)
    # verificaion
    # Maderas = 2 mesas * (1 base + 4 patas * 1 madera) = 2 * 5 = 10 maderas
    assert necesidades[madera] == 10
    # Tornillos = 2 mesas * (4 patas * 4 tornillos) = 2 * 16 = 32 tornillos
    assert necesidades[tornillo] == 32
    # y verificamos que la pata no esté en la lista final, para ver si se explotó el componente
    assert pata not in necesidades
    #conviene separarlos xq si falla alguno es mas facil identificar donde esta el problema

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

    # esta es la tramposa que deberia ignorar el sistema porque no es de la unidad de corte, sino de pintura
    tarea_pintura = MagicMock()
    tarea_pintura.get_unidad_requerida.return_value = unidad_pintura
    tarea_pintura.get_tiempo_por_unidad.return_value = 5.0  

    # el arituclo tiene as 3 mezcladas
    articulo = ArticuloFabricadoInternamente("Mueble", [], [tarea_corte_1, tarea_corte_2, tarea_pintura])

    # quiero saber la cantidad de horass en la unidad de corte solamente 
    horas_totales = articulo.calcular_horas_en_unidad(unidad_corte, 10)

    # Verificamos que el sistema haya filtrado y sumado correctamente
    assert horas_totales == 35.0


def test_gestionar_reabastecimiento_crea_solicitud_hija():
    pata = ArticuloFabricadoInternamente("Pata de Mesa", [], [])
    empresa_mock = MagicMock()

    # simulamos que faltan 50 patas para cumplir un pedido y queremos generar una solicitud de fabricación para reabastecer ese faltante
    mensaje_alerta = pata.gestionar_reabastecimiento(empresa_mock, 50)
    # Le preguntamos al mock exactamente cuántas veces se ejecutó su método 'crear_solicitud'
    cantidad_llamadas = empresa_mock.crear_solicitud.call_count 
    #verificamos que se haya llamado una vez a crear solicitud en empresa, y que el mensaje tenga los datos correctos
    assert cantidad_llamadas == 1
    assert "50" in mensaje_alerta
    assert "Pata de Mesa" in mensaje_alerta