import pytest
from unittest.mock import MagicMock, patch
from menu_admin import MenuAdministrativo

@pytest.fixture
def menu_setup():
    empresa_mock = MagicMock()
    menu = MenuAdministrativo(empresa_mock)
    return menu, empresa_mock

def test_ejecutar_opcion_cero_cierra_sesion(menu_setup):
    menu, _ = menu_setup
    assert menu.ejecutar_opcion("0") is False

def test_ejecutar_opcion_invalida_no_cierra_sesion(menu_setup):
    menu, _ = menu_setup
    assert menu.ejecutar_opcion("99") is True

# Simulamos que el usuario tipea "Madera" en el primer input y "150.0" en el segundo
@patch('builtins.input', side_effect=["Madera", "150.0"])
def test_crear_insumo_exitoso(mock_input, menu_setup):
    menu, empresa_mock = menu_setup
    insumo_mock = MagicMock()
    insumo_mock.get_id.return_value = 1
    empresa_mock.crear_insumo_basico.return_value = insumo_mock

    menu.crear_insumo()

    empresa_mock.crear_insumo_basico.assert_called_once_with("Madera", 150.0)

# Testeamos otra opción del menú simulando 3 tipeos del usuario
@patch('builtins.input', side_effect=["Soldadora", "100.0", "500.0"])
def test_agregar_unidad_trabajo_exitoso(mock_input, menu_setup):
    menu, empresa_mock = menu_setup
    menu.agregar_unidad_trabajo()
    # Comprobamos que el menú tradujo los inputs de texto a los floats correctos
    empresa_mock.crear_unidad_trabajo.assert_called_once_with("Soldadora", 100.0, 500.0)

# Simulamos que el usuario intenta poner letras en un campo numérico
@patch('builtins.input', side_effect=["Pintura", "letras_en_vez_de_numeros"])
def test_crear_insumo_falla_con_letras_pero_no_crashea(mock_input, menu_setup):
    menu, empresa_mock = menu_setup    
# El float() interno va a fallar. Verificamos q el try-except lo ataje y el programa termine la ejecución sin explotar.
    menu.crear_insumo()
    # Como falló antes de llegar a la lógica, aseguramos que la empresa NUNCA recibió la orden
    empresa_mock.crear_insumo_basico.assert_not_called()
    
#Que son los @patch? Son decoradores que nos permiten simular la función 'input'
#Con 'side_effect' le decimos qué respuestas queremos que devuelva cada vez que el menú le pregunte algo al usuario. 
#Así, podemos probar cómo reacciona el menú a diferentes tipos de entradas sin tener que escribirlas 
# manualmente cada vez que corremos el test.