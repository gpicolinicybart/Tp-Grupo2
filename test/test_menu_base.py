import pytest
from unittest.mock import MagicMock, patch
from menu_base import MenuBase

class Menu(MenuBase):
    def mostrar_menu(self):
        pass
    
    def ejecutar_opcion(self, opcion):
        pass

@pytest.fixture
def menu_setup():
    empresa_mock = MagicMock()
    menu = Menu(empresa_mock)
    return menu, empresa_mock

@patch('builtins.print')
def test_ver_estado_imprime_reporte(mock_print, menu_setup):
    menu, _ = menu_setup
    menu.ver_estado()
    assert mock_print.call_count >= 5
    texto_impreso = str(mock_print.call_args_list)
    assert "ESTADO ACTUAL" in texto_impreso
    assert "INSUMOS" in texto_impreso
    assert "COLABORADORES" in texto_impreso