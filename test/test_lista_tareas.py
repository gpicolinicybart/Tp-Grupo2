import pytest
from unittest.mock import MagicMock
from lista_tareas import ListaEnlazadaTareas

@pytest.fixture
def lista_vacia():
    return ListaEnlazadaTareas()

def test_lista_enlazada_vacia_comportamiento_base(lista_vacia):
    assert lista_vacia.get_costo_total() == 0.0
    elementos = list(lista_vacia)
    assert len(elementos) == 0

def test_agregar_tarea_mantiene_el_orden_de_insercion(lista_vacia):
    tarea_1 = MagicMock()
    tarea_2 = MagicMock()
    
    lista_vacia.agregar_al_final(tarea_1)
    lista_vacia.agregar_al_final(tarea_2)
    
    elementos = list(lista_vacia)
    
    assert len(elementos) == 2
    assert elementos[0] == tarea_1
    assert elementos[1] == tarea_2

def test_get_costo_total_suma_correctamente_los_nodos(lista_vacia):
    tarea_1 = MagicMock()
    tarea_1.get_costo.return_value = 150.0
    
    tarea_2 = MagicMock()
    tarea_2.get_costo.return_value = 50.0
    
    lista_vacia.agregar_al_final(tarea_1)
    lista_vacia.agregar_al_final(tarea_2)
    
    assert lista_vacia.get_costo_total() == 200.0