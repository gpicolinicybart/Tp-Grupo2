import pytest
from unittest.mock import MagicMock
from empresa import Empresa
from inventario import Inventario
from articulo_fabricado import ArticuloFabricadoInternamente

@pytest.fixture
def empresa_setup():
    inv_mock = MagicMock(spec=Inventario)
    empresa = Empresa(inv_mock)
    # mock del gestor de archivos 
    empresa._gestor_archivos = MagicMock()
    return empresa

def test_registrar_producto_llama_validar_ciclos_y_guarda_en_diccionario(empresa_setup):
    producto_mock = MagicMock(spec=ArticuloFabricadoInternamente)
    producto_mock.get_nombre.return_value = "Mesa Ratona"
    producto_mock.get_id.return_value = 99
    producto_mock.get_tipo_elemento.return_value = "Articulo Fabricado"
    
    empresa_setup.registrar_producto_nuevo(producto_mock)
    
    # Verificamos que se guardó en el diccionario de productos usando su ID
    assert 99 in empresa_setup._productos_fabricados
    assert empresa_setup._productos_fabricados[99] == producto_mock
    producto_mock.validar_ciclos.assert_called_once()

def test_crear_insumo_basico_invalido(empresa_setup):
    # con un nombre vacío tiene q explotar
    with pytest.raises(ValueError, match="El nombre no puede estar vacío."):
        empresa_setup.crear_insumo_basico("", 500)
        
    # Si le paso costo negativo o cero tiene q explotar
    with pytest.raises(ValueError, match="El costo debe ser positivo."):
        empresa_setup.crear_insumo_basico("Madera", -10)

def test_generar_solicitud_menu_rechaza_cantidad_invalida(empresa_setup):
    producto_mock = MagicMock()
    with pytest.raises(ValueError, match="La cantidad a fabricar debe ser mayor a cero."):
        empresa_setup.generar_solicitud_desde_menu(producto_mock, 0)
        
def test_crear_colaborador_valida_habilidades_existentes(empresa_setup):
    empresa_setup._catalogo_habilidades = {1: "Soldadura"}
    # Tratamos de crear un colaborador con la habilidad 1 y la 99 q no existe
    with pytest.raises(ValueError, match="La habilidad con ID 99 no existe."):
        empresa_setup.crear_colaborador([1, 99], 40.0, 1000.0)