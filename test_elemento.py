import pytest

from elemento import Elemento
def test_elemento_nombre_no_puede_ser_vacio_tira_value_error():
        with pytest.raises(ValueError):
            elem = Elemento(1, "Nombre")
            elem.set_nombre("") # trato poner un nombre vacío  