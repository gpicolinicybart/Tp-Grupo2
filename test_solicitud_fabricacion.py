import pytest
from unittest.mock import MagicMock
from solicitud_fabricacion import SolicitudDeFabricacion
from itembom import ItemBOM

@pytest.fixture
def bom_mock():
    mock = MagicMock(spec=ItemBOM)
    mock._nombre = "Silla de Oficina"
    return mock

def test_solicitud_estado_inicial_y_getters(bom_mock):
    solicitud = SolicitudDeFabricacion(bom_mock, 50, True)
    
    assert solicitud.get_estado() == "Creada"
    assert solicitud.get_cantidad() == 50
    assert solicitud.get_id() == 1

def test_solicitud_rechaza_cantidades_invalidas(bom_mock):
    # Falla si es negativo (ValueError)
    with pytest.raises(ValueError):
        SolicitudDeFabricacion(bom_mock, -5, True)
        
    # Falla si es texto (TypeError)
    with pytest.raises(TypeError):
        SolicitudDeFabricacion(bom_mock, "veinte", True)