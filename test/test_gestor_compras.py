import pytest
from unittest.mock import MagicMock
from gestor_compras import GestorCompras

@pytest.fixture
def gestor_setup():
    gestor = GestorCompras()
    gestor._arbol_historico = MagicMock()
    return gestor

def test_agregar_compra_solicitada_va_a_cola_y_arbol(gestor_setup):
    compra_mock = MagicMock()
    compra_mock.get_estado.return_value = "Solicitada"
    gestor_setup._arbol_historico = MagicMock()    
    gestor_setup.agregar_compra(compra_mock)
    # Verificamos que se haya guardado en el historial
    gestor_setup._arbol_historico.insertar.assert_called_once_with(compra_mock)
    # Verificamos que haya entrado a la cola de pendientes
    assert len(gestor_setup._compras_pendientes) == 1
    assert gestor_setup._compras_pendientes[0] == compra_mock

# si viene del historial CSV y ya está "Recibida", no va a la cola
def test_agregar_compra_no_solicitada_solo_va_al_arbol(gestor_setup):
    compra_mock = MagicMock()
    compra_mock.get_estado.return_value = "Recibida" 
    gestor_setup.agregar_compra(compra_mock)
    # No debería haber entrado a la cola de pendientes
    assert len(gestor_setup._compras_pendientes) == 0

def test_recibir_proxima_compra_respeta_fifo(gestor_setup):
    compra_mock_1 = MagicMock()
    compra_mock_1.get_estado.return_value = "Solicitada"

    compra_mock_2 = MagicMock()
    compra_mock_2.get_estado.return_value = "Solicitada"
    
    inventario_mock = MagicMock()

    # Ingresan en orden: primero la 1, luego la 2
    gestor_setup.agregar_compra(compra_mock_1)
    gestor_setup.agregar_compra(compra_mock_2)

    compra_procesada = gestor_setup.recibir_proxima_compra(inventario_mock)
    
    assert compra_procesada == compra_mock_1
    
    compra_mock_1.recibir_materiales.assert_called_once_with(inventario_mock)

    assert len(gestor_setup._compras_pendientes) == 1

def test_recibir_proxima_compra_cola_vacia_devuelve_none(gestor_setup):
    inventario_mock = MagicMock()
    resultado = gestor_setup.recibir_proxima_compra(inventario_mock)
    assert resultado is None