import pytest
from unittest.mock import MagicMock
from articulo_fabricado import ArticuloFabricadoInternamente
from itembom import ItemBOM
from tarea import Tarea

def test_costo_unitario_articulo_fabricado():
    # simulo que los materiales cuestan $500 y la mano de obra 300
    bom_mock = MagicMock(spec=ItemBOM)
    bom_mock.get_costo_total.return_value = 500.0
    tarea_mock = MagicMock(spec=Tarea)
    tarea_mock.get_costo.return_value = 300.0
    
    #Creamos el artículo con esos mocks
    mesa = ArticuloFabricadoInternamente(
        "Mesa", [bom_mock], [tarea_mock])
    assert mesa.get_costo_unitario() == 800.0 # Verificación: Costo Total = 500 (BOM) + 300 (Tarea) = 800

def test_detectar_ciclo_infinito():
    item_a = ArticuloFabricadoInternamente("Parte A", [], []) # q no se requiera a si mismo
    bom_ciclico = ItemBOM(202, "BOM Ciclo", {item_a: 1}) # hago un BOM que contiene al mismo item_a (circulo vicioso)
    item_a._bom = [bom_ciclico]
    
    with pytest.raises(ValueError, match="CICLO DETECTADO"):  # al validar ciclos, debe saltar el error
        item_a.validar_ciclos()

def test_articulo_fabricado_id_autoincremental():
    art1 = ArticuloFabricadoInternamente("Producto A", [], [])
    art2 = ArticuloFabricadoInternamente("Producto B", [], [])
    assert art1.get_id() < art2.get_id()