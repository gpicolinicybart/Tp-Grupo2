import pytest
from inventario import Inventario
from insumo_basico import InsumoBasico

@pytest.fixture 
def inv_setup():
    inv = Inventario()
    acero = InsumoBasico("Acero", 50.0)
    madera = InsumoBasico("Madera", 100.0)
    inv.ingresar_stock(acero, 100) 
    inv.ingresar_stock(madera, 50)  
    return inv, acero, madera

def test_reservar_disminuye_disponibilidad(inv_setup):
    inv, acero, madera = inv_setup
    inv.reservar_stock(acero, 30)
    
    assert inv.consultar_stock(acero) == 100
    assert inv.hay_disponibilidad(acero, 70) is True
    assert inv.consultar_stock(madera) == 50
    assert inv.hay_disponibilidad(madera, 50) is True

def test_descontar_stock_con_reserva(inv_setup):
    inv, acero, madera = inv_setup
    inv.reservar_stock(acero, 40)
    inv.descontar_stock(acero, 40)
    
    assert inv.consultar_stock(acero) == 60

def test_obtener_materiales_criticos(inv_setup): 
    inv, acero, madera = inv_setup
    necesidades = {acero: 1000, madera: 100}
    
    criticos_lista = inv.obtener_materiales_criticos(necesidades)
    criticos_dict = dict(criticos_lista)
    
    assert acero in criticos_dict
    assert madera not in criticos_dict

def test_ingresar_reservar_cant_negativas(inv_setup):
    inv, acero, _ = inv_setup
    with pytest.raises(ValueError):
        inv.ingresar_stock(acero, -10)
        
    with pytest.raises(ValueError):
        inv.reservar_stock(acero, -5)

def test_reservar_mas_stock_del_disponible_falla(inv_setup):
    inv, acero, _ = inv_setup
    inv.reservar_stock(acero, 200)
    assert inv.obtener_stock_disponible(acero) == 100

def test_descontar_mas_stock_del_reservado_falla(inv_setup):
    inv, acero, _ = inv_setup
    inv.reservar_stock(acero, 10)
    inv.descontar_stock(acero, 50)
    assert inv.consultar_stock(acero) == 100

def test_obtener_stock_disponible_hace_bien_la_resta(inv_setup):
    inv, acero, _ = inv_setup
    inv.reservar_stock(acero, 25)
    assert inv.obtener_stock_disponible(acero) == 75