import pytest
from unittest.mock import MagicMock
from arbol_compras import ArbolBinarioCompras

@pytest.fixture
def arbol_setup():
    arbol = ArbolBinarioCompras()
    compra_50 = MagicMock()
    compra_50.get_id.return_value = 50
    
    compra_30 = MagicMock()
    compra_30.get_id.return_value = 30
    
    compra_70 = MagicMock()
    compra_70.get_id.return_value = 70
    
#50 raíz, 30 a la izq y 70 a la derecha.
    arbol.insertar(compra_50)
    arbol.insertar(compra_30)
    arbol.insertar(compra_70)
    
    return arbol, compra_50, compra_30, compra_70

def test_insercion_y_busqueda(arbol_setup):
    arbol, c_50, c_30, c_70 = arbol_setup
    
    # Verificamos que las búsquedas exitosas devuelvan el objeto correcto
    assert arbol.buscar_por_id(50) == c_50
    assert arbol.buscar_por_id(30) == c_30
    assert arbol.buscar_por_id(70) == c_70
    
    # Verificamos que buscar un ID que no existe devuelva None
    assert arbol.buscar_por_id(99) is None

def test_recorrido_inorden_ordena_correctamente(arbol_setup):
    arbol, c_50, c_30, c_70 = arbol_setup
    
    # Agregamos un par de compras más mezcladas para hacer el test más robusto
    compra_40 = MagicMock()
    compra_40.get_id.return_value = 40
    arbol.insertar(compra_40)
    
    compra_20 = MagicMock()
    compra_20.get_id.return_value = 20
    arbol.insertar(compra_20)

    # inorden debería devolver los objetos ordenados por ID: 20, 30, 40, 50, 70
    lista_ordenada = arbol.obtener_lista_inorden()
    
    # Verificamos que no se haya perdido ninguna compra (deben ser 5)
    assert len(lista_ordenada) == 5
    
    # Verificamos matemáticamente que el orden de los IDs sea estrictamente ascendente
    assert lista_ordenada[0].get_id() == 20
    assert lista_ordenada[1].get_id() == 30
    assert lista_ordenada[2].get_id() == 40
    assert lista_ordenada[3].get_id() == 50
    assert lista_ordenada[4].get_id() == 70