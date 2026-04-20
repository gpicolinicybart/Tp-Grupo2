import pytest
from inventario import Inventario
from insumo_basico import InsumoBasico

@pytest.fixture
def inv_con_acero():
    inv = Inventario()
    acero = InsumoBasico("Acero", 50.0)
    inv.ingresar_stock(acero, 100) # Ingresamos 100 unidades al inventario
    return inv, acero

def test_reservar_disminuye_disponibilidad(inv_con_acero):
    inv, acero = inv_con_acero
    
    # Reservamos 30 unidades
    inv.reservar_stock(acero, 30)
    
    # El stock físico sigue siendo 100
    assert inv.consultar_stock(acero) == 100
    # Pero solo hay disponibilidad para 70 (o menos)
    assert inv.hay_disponibilidad(acero, 70) is True
    assert inv.hay_disponibilidad(acero, 71) is False

def test_descontar_stock_con_reserva(inv_con_acero):
    inv, acero = inv_con_acero
    
    inv.reservar_stock(acero, 40)
    inv.descontar_stock(acero, 40)
    
    # Ahora sí el stock físico debe ser 60
    assert inv.consultar_stock(acero) == 60