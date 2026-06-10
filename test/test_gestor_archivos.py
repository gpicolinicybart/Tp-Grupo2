
from unittest.mock import MagicMock, patch, mock_open
from gestor_archivos import GestorArchivos

def test_guardar_unidades_csv_simulado():
    empresa_mock = MagicMock()
    unidad_mock = MagicMock()
    unidad_mock.get_id.return_value = 1
    unidad_mock.get_nombre.return_value = "Cortadora"
    unidad_mock.get_capacidad_max_horas.return_value = 100.0
    unidad_mock.get_costo_operativo.return_value = 500.0
    unidad_mock.serialize.return_value = [1, "Cortadora", 100.0, 500.0]

    empresa_mock.obtener_unidades.return_value = [unidad_mock]
    
    gestor = GestorArchivos(empresa_mock)
    
    
    m_open = mock_open()
    
    with patch('builtins.open', m_open): 
        gestor.guardar_unidades_csv()
        
    
    m_open.assert_called_once_with("csv/unidades.csv", mode='w', newline='', encoding='utf-8')
    
    
    handle = m_open()
    texto_escrito = ""
    for llamada in handle.write.call_args_list:
        texto_escrito += llamada[0][0]
        
    
    assert "ID Unidad" in texto_escrito
    assert "Nombre" in texto_escrito
    
    assert "1" in texto_escrito
    assert "Cortadora" in texto_escrito
    assert "100.0" in texto_escrito