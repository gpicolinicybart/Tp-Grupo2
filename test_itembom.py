import pytest
from itembom import ItemBOM
from insumo_basico import InsumoBasico

def test_itembom_calculo_costo_basico():
    madera = InsumoBasico("Madera", 100.0)  # creamos un insumo real para probar el cálculo
    bom = ItemBOM("BOM Tabla", {madera: 2}) # requiere 2 maderas
    assert bom.get_costo_total() == 200.0   # verificamos que vale 200 (100*2)

def test_itembom_cantidades_invalidas_lanzan_error():
    madera = InsumoBasico("Madera", 100.0)
    # Cantidad negativa debe lanzar ValueError
    with pytest.raises(ValueError):
        ItemBOM("BOM Error Negativo", {madera: -1})
    # Cantidad no entera debe lanzar TypeError
    with pytest.raises(TypeError):
        ItemBOM("BOM Error Flotante", {madera: 1.5})

def test_itembom_id_autoincremental():
    # aca pruebo si el id autoincremental funciona bien
    bom1 = ItemBOM("Receta 1", {})
    bom2 = ItemBOM("Receta 2", {})
    assert bom1.get_id() < bom2.get_id()
