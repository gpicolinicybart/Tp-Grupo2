import pytest
from itembom import ItemBOM
from insumo_basico import InsumoBasico

def test_itembom_calculo_costo_basico():
    madera = InsumoBasico(101, "Madera", 100.0)  # creo un insumo real para probar el cálculo
    bom = ItemBOM(201, "BOM Tabla", {madera: 2}) # requiere 2 maderas
    assert bom.get_costo_total() == 200.0 # verifico q vale 200 (100*2)

def test_itembom_cantidades_invalidas_lanzan_error():
    madera = InsumoBasico(101, "Madera", 100.0)
# Test: Cantidad negativa debe lanzar ValueError
    with pytest.raises(ValueError):
        ItemBOM(201, "BOM Error", {madera: -1})
# Test: Cantidad no entera debe lanzar TypeError
    with pytest.raises(TypeError):
        ItemBOM(201, "BOM Error", {madera: 1.5})