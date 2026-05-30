import pytest
from unittest.mock import MagicMock
from itembom import ItemBOM

def test_itembom_calculo_costo_multiple():
    insumo_1 = MagicMock()
    insumo_1.get_costo_unitario.return_value = 100.0
    
    insumo_2 = MagicMock()
    insumo_2.get_costo_unitario.return_value = 50.0

    bom = ItemBOM("BOM Silla", {insumo_1: 2, insumo_2: 3}) # necesito 2 de insumo_1 y 3 de insumo_2 tiene q dar 350
    
    assert bom.get_costo_total() == 350.0

def test_itembom_cantidades_invalidas_lanzan_error():
    insumo_mock = MagicMock()
    
    with pytest.raises(ValueError, match="La cantidad en una receta debe ser mayor a cero"):
        ItemBOM("BOM Error Negativo", {insumo_mock: -1})
        
    with pytest.raises(TypeError, match="La cantidad debe ser un número entero"):
        ItemBOM("BOM Error Flotante", {insumo_mock: 1.5})

def test_itembom_id_autoincremental():
    bom1 = ItemBOM("Receta 1", {})
    bom2 = ItemBOM("Receta 2", {})
    assert bom1.get_id() < bom2.get_id()

def test_itembom_metodos_magicos_y_getters():
    insumo_mock = MagicMock()
    diccionario_receta = {insumo_mock: 5}
    bom = ItemBOM("Receta Prueba", diccionario_receta)
    
    assert bom.get_nombre() == "Receta Prueba"
    assert bom.get_diccionario() == diccionario_receta    
    assert len(bom) == 1