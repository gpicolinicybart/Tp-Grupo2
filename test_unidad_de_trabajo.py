import pytest
from unidad_de_trabajo import UnidadDeTrabajo

@pytest.fixture
def fresadora():
    #Prepara una unidad con 20 horas de capacidad máxima
    return UnidadDeTrabajo(501, "Fresadora", 20.0, 1500.0)
def test_reserva_de_horas_correcta(fresadora):
    # reservo 15hs
    reserva = fresadora.reservar_horas(15.0)
    assert reserva is True
    #verifico que solo queden 5 libres
    assert fresadora.verificar_disponibilidad(5.0) is True
    assert fresadora.verificar_disponibilidad(5.1) is False

def test_reserva_excedida_falla(fresadora):
    #trato de reservar 25 horas en una máquina de 20
    reserva = fresadora.reservar_horas(25.0)
    assert reserva is False
    # la capacidad debería seguir intacta (20 libres)
    assert fresadora.verificar_disponibilidad(20.0) is True

def test_costo_operativo_no_negativo(fresadora):
    # trato de setear un costo negativo
    fresadora.set_costo_operativo(-100.0)
    # tendria q haber ignorado el cambio (mantiene el original de 1500.0)
    assert fresadora.get_costo_operativo() == 1500.0