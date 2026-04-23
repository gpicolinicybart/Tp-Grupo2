import pytest
from inventario import Inventario
from insumo_basico import InsumoBasico

@pytest.fixture # el fixture es para hacer un escenario y no tener q repetirlo en todos los test
def inv_setup():
    #Crea un inventario y le ingresa stock de dos materiales
    inv = Inventario()
    acero = InsumoBasico("Acero", 50.0)
    madera = InsumoBasico("Madera", 100.0)
    inv.ingresar_stock(acero, 100) # Ingresamos 100 unidades
    inv.ingresar_stock(madera, 50)  # Ingresamos 50 unidades
    return inv, acero, madera

def test_reservar_disminuye_disponibilidad(inv_setup):
    inv, acero, madera = inv_setup
    # Reservamos 30 unidades de acero
    inv.reservar_stock(acero, 30)
    
    # Comprobaciones del acero
    assert inv.consultar_stock(acero) == 100
    assert inv.hay_disponibilidad(acero, 70) is True
    assert inv.hay_disponibilidad(acero, 71) is False
    
    #  la madera sigue intacta 
    assert inv.consultar_stock(madera) == 50
    assert inv.hay_disponibilidad(madera, 50) is True

def test_descontar_stock_con_reserva(inv_setup):
    inv, acero, madera = inv_setup
    inv.reservar_stock(acero, 40)
    inv.descontar_stock(acero, 40)
    
    #  stock físico debe haber bajado 
    assert inv.consultar_stock(acero) == 60

def test_obtener_materiales_criticos(inv_setup): #Verifica que la regla del < 20% funcione correctamente 
    inv, acero, madera = inv_setup
    # llega un pedido que necesita 1000 de acero y 100 de madera.
    necesidades = {acero: 1000, madera: 100}
    # para el acero tenemos 100 y necesitamos 1000, el 20% es 200 asi que como solo hay 100 es critico
    #  la madera tenemos 50 y necesitamos 100, el 20% es 20 asi q tenemos mas (no es critico)
    
    criticos_lista = inv.obtener_materiales_criticos(necesidades)
    # la funcion devuelve tuplas asi q para q sea mas facil lo volvemos diccionario
    criticos_dict = dict(criticos_lista)
    assert acero in criticos_dict
    assert madera not in criticos_dict