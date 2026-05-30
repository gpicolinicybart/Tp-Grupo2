import pytest
from elemento import Elemento

def test_elem_nombre_no_vacio_tira_value_error():
    elem = Elemento("Nombre")
    with pytest.raises(ValueError, match="El nombre no puede estar vacío"):
        elem.set_nombre("") 

def test_elemento_id_autoincremental():
    elem1 = Elemento("Elemento A")
    elem2 = Elemento("Elemento B")
    assert elem1.get_id() < elem2.get_id()


def test_elemento_id_explicito_actualiza_contador():
    elem_csv = Elemento("Elemento del Archivo", id=500)
    elem_nuevo = Elemento("Elemento Nuevo del Menú")
    
    # verificamos que el sistema haya respetado el ID del archivo
    assert elem_csv.get_id() == 500
    
    # verificamos que el contador global haya saltado a 500, 
    # haciendo que el nuevo elemento nazca con el ID 501
    assert elem_nuevo.get_id() == 501

def test_get_y_set_nombre():
    elem = Elemento("Original")
    assert elem.get_nombre() == "Original"
    elem.set_nombre("Modificado")
    assert elem.get_nombre() == "Modificado"