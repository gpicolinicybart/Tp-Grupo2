import pytest
from datetime import datetime
from unittest.mock import MagicMock
from solicitud_fabricacion import SolicitudDeFabricacion, ESTADOS_VALIDOS

@pytest.fixture
def producto_mock():
    producto = MagicMock()
    producto.get_nombre.return_value = "Silla"
    return producto

def test_creacion_solicitud_exitosa(producto_mock):
    fecha_prueba = datetime(2026, 5, 20, 10, 0)
    solicitud = SolicitudDeFabricacion(producto_mock, 50, True, fecha_creacion=fecha_prueba)
    
    assert solicitud.get_item_solicitado() == producto_mock
    assert solicitud.get_cantidad() == 50
    assert solicitud.get_estado() == ESTADOS_VALIDOS[0]  
    assert solicitud.get_fecha_creacion() == fecha_prueba
    assert solicitud.get_fecha_finalizacion() is None
    assert solicitud.get_id() > 0

def test_solicitud_rechaza_cantidades_invalidas(producto_mock):
    with pytest.raises(ValueError, match="La cantidad debe ser mayor a cero"):
        SolicitudDeFabricacion(producto_mock, 0, True)
    
    with pytest.raises(ValueError):
        SolicitudDeFabricacion(producto_mock, -5, True)
        
    with pytest.raises(TypeError, match="La cantidad debe ser un número entero"):
        SolicitudDeFabricacion(producto_mock, "veinte", True)

def test_modificacion_de_estados_valida_y_rechaza(producto_mock):
    solicitud = SolicitudDeFabricacion(producto_mock, 10, True)
    
    solicitud.set_estado("En Ejecución")
    assert solicitud.get_estado() == "En Ejecución"
    
    with pytest.raises(ValueError, match="Estado inválido"):
        solicitud.set_estado("Estado Inventado Inexistente")

def test_agregar_colaboradores_evita_duplicados(producto_mock):
    solicitud = SolicitudDeFabricacion(producto_mock, 10, True)
    
    solicitud.agregar_colaborador(5)
    solicitud.agregar_colaborador(8)
    
    solicitud.agregar_colaborador(5)
    
    assert solicitud._colaboradores_asignados == [5, 8]

def test_marcar_como_terminada_actualiza_estado_y_fecha(producto_mock):
    solicitud = SolicitudDeFabricacion(producto_mock, 10, True)
    
    assert solicitud.get_fecha_finalizacion() is None
    
    solicitud.marcar_como_terminada()
    
    assert solicitud.get_estado() == "Terminada"
    assert solicitud.get_fecha_finalizacion() is not None