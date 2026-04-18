import pytest

from elemento import Elemento
def test_elemento_nombre_no_puede_ser_vacio_tira_value_error():
        with pytest.raises(ValueError):
            elem = Elemento("Nombre")
            elem.set_nombre("") # trato poner un nombre vacío

def test_elemento_id_autoincremental():
    elem1 = Elemento("Elemento1")
    elem2 = Elemento("Elemento2")
    elem3 = Elemento("Elemento3")
    assert elem1.get_id() == 1
    assert elem2.get_id() == 2
    assert elem3.get_id() == 3  