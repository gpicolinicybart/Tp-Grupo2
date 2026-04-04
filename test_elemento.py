from elemento import Elemento

def test_elemento_nombre_no_puede_ser_vacio():
    elem = Elemento(1, "Nombre")
    elem.set_nombre("") # trato poner un nombre vacío
    assert elem.get_nombre() == "Nombre" # "afirmamos" que el nombre NO cambió
