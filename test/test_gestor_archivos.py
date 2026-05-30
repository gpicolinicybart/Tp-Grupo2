#Si tu test ejecuta guardar_unidades_csv(), te va a crear un archivo unidades.csv real en tu computadora. 
#Si el test falla por la mitad, te deja basura en el disco duro. Y si lo corrés en otra computadora que 
# no tiene permisos de administrador, el test explota.
#Para testear gestor_archivos.py sin crear archivos reales, usamos una herramienta avanzada de Python 
# llamada patch y mock_open. Básicamente, engañamos a Python haciéndole creer que abrió y guardó 
# un archivo, pero todo ocurre de forma virtual en la memoria RAM.

from unittest.mock import MagicMock, patch, mock_open
from gestor_archivos import GestorArchivos

def test_guardar_unidades_csv_simulado():
    empresa_mock = MagicMock()
    unidad_mock = MagicMock()
    unidad_mock.get_id.return_value = 1
    unidad_mock.get_nombre.return_value = "Cortadora"
    unidad_mock.get_capacidad_max_horas.return_value = 100.0
    unidad_mock.get_costo_operativo.return_value = 500.0
    
    empresa_mock.obtener_unidades.return_value = [unidad_mock]
    
    gestor = GestorArchivos(empresa_mock)
    
    # 'mock_open()' crea un archivo virtual 
    m_open = mock_open()
    
    with patch('builtins.open', m_open): # 'patch()' reemplaza la función 'open' 'mock_open()'
        gestor.guardar_unidades_csv()
        
    # Comprobamos que el gestor intentó abrir el archivo con el nombre y modo correcto
    m_open.assert_called_once_with("unidades.csv", mode='w', newline='', encoding='utf-8')
    
    # Rescatamos todo el texto que el gestor intentó escribir en nuestro archivo virtual
    handle = m_open()
    texto_escrito = ""
    for llamada in handle.write.call_args_list:
        texto_escrito += llamada[0][0]
        
    # Verificamos que haya escrito los encabezados
    assert "ID Unidad" in texto_escrito
    assert "Nombre" in texto_escrito
    
    # Verificamos que haya guardado los datos de nuestra unidad falsa (Cortadora)
    assert "1" in texto_escrito
    assert "Cortadora" in texto_escrito
    assert "100.0" in texto_escrito