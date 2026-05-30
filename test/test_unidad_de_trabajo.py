import pytest
from unidad_de_trabajo import UnidadDeTrabajo

@pytest.fixture
def maquina_setup():
    return UnidadDeTrabajo("Fresadora", 40.0, 1500.0)

def test_creacion_y_getters_correctos(maquina_setup):
    assert maquina_setup.get_nombre() == "Fresadora"
    assert maquina_setup.get_capacidad_max_horas() == 40.0
    assert maquina_setup.get_costo_operativo() == 1500.0
    assert maquina_setup.get_id() > 0
    # Al nacer, el porcentaje de uso debe ser exacto 0.0%
    assert maquina_setup.get_porcentaje_uso() == 0.0

def test_validaciones_de_creacion():
    with pytest.raises(ValueError, match="El nombre de la unidad de trabajo no puede estar vacío."):
        UnidadDeTrabajo("", 40.0, 100.0)
        
    with pytest.raises(ValueError, match="La capacidad máxima de horas debe ser un valor positivo."):
        UnidadDeTrabajo("Torno", 0.0, 100.0)
        
    with pytest.raises(ValueError, match="La capacidad máxima de horas debe ser un valor positivo."):
        UnidadDeTrabajo("Torno", -10.0, 100.0)
        
    with pytest.raises(ValueError, match="El costo operativo por hora debe ser un valor no negativo."):
        UnidadDeTrabajo("Torno", 40.0, -50.0)

def test_reserva_de_horas_y_calculo_de_porcentaje_uso(maquina_setup):
    exito_reserva = maquina_setup.reservar_horas(10.0)
    
    assert exito_reserva is True
    assert maquina_setup.get_porcentaje_uso() == 25.0
    
    assert maquina_setup.verificar_disponibilidad(30.0) is True
    
    assert maquina_setup.verificar_disponibilidad(31.0) is False
    reserva_rebotada = maquina_setup.reservar_horas(31.0)
    
    assert reserva_rebotada is False
    assert maquina_setup.get_porcentaje_uso() == 25.0

def test_set_costo_operativo_ignora_valores_negativos(maquina_setup):
    maquina_setup.set_costo_operativo(2000.0)
    assert maquina_setup.get_costo_operativo() == 2000.0
    
    maquina_setup.set_costo_operativo(-500.0)
    
    assert maquina_setup.get_costo_operativo() == 2000.0

def test_id_autoincremental():
    unidad1 = UnidadDeTrabajo("Sector Soldadura", 20.0, 100.0)
    unidad2 = UnidadDeTrabajo("Sector Pintura", 20.0, 100.0)
    assert unidad1.get_id() < unidad2.get_id()