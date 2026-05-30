import pytest
from unittest.mock import MagicMock, patch
from menu_prod import MenuProduccion

@pytest.fixture
def menu_setup():
    empresa_mock = MagicMock()
    menu = MenuProduccion(empresa_mock)
    return menu, empresa_mock

def test_ejecutar_opcion_cero_cierra_sesion(menu_setup):
    menu, _ = menu_setup
    assert menu.ejecutar_opcion("0") is False

def test_ejecutar_opcion_invalida_mantiene_menu_vivo(menu_setup):
    menu, _ = menu_setup
    assert menu.ejecutar_opcion("99") is True

def test_menu_produccion_hereda_empresa_correctamente(menu_setup):
    menu, empresa_mock = menu_setup
    assert menu.empresa == empresa_mock

@patch('builtins.input', side_effect=["letras_inválidas", "50"])
def test_captura_de_datos_falla_con_letras_y_se_protege(mock_input, menu_setup):
    menu, _ = menu_setup
    menu.ejecutar_opcion("1")
    assert mock_input.call_count == 1