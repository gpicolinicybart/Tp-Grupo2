import pytest
from colaboradores import Colaborador

@pytest.fixture
def operario_soldador():
    return Colaborador([1, 2], 10.0, 3000.0)

def test_verificar_habilidades(operario_soldador):
    # Verificamos que detecte los IDs correctos
    assert operario_soldador.tiene_habilidad(1) is True
    # Verificamos con un ID que no tiene (Ej: 3 = Pintura)
    assert operario_soldador.tiene_habilidad(3) is False

def test_asignar_tarea_exito(operario_soldador):
    exito = operario_soldador.asignar_tarea(1, 4.0)
    assert exito is True
    # Miro disponibilidad (10 - 4 = 6)
    assert operario_soldador.verificar_disponibilidad(6.0) is True
    assert operario_soldador.verificar_disponibilidad(6.1) is False

def test_asignar_tarea_sin_habilidad(operario_soldador):
    exito = operario_soldador.asignar_tarea(99, 1.0)
    assert exito is False
    # No debería haberle restado tiempo
    assert operario_soldador.verificar_disponibilidad(10.0) is True

def test_asignar_tarea_sin_tiempo(operario_soldador):
    # Trato de asignar 11 horas cuando solo tiene 10
    exito = operario_soldador.asignar_tarea(1, 11.0)
    assert exito is False
    
def test_colaborador_id_autoincremental():
    c1 = Colaborador([3], 40.0, 1000.0)
    c2 = Colaborador([4], 40.0, 1200.0)
    assert c1.get_id() < c2.get_id()

# test para la baja, hay q revisarlo cuando lo arreglemos
def test_asignar_tarea_a_colaborador_de_baja_falla(operario_soldador):
    # Lo despedimos
    operario_soldador.dar_de_baja()
    
    # Verificamos que se haya registrado la fecha de baja
    assert operario_soldador.get_fecha_baja() is not None
    
    # Tratamos de asignarle una tarea que SÍ sabe hacer (ID 1) y para la que SÍ tiene tiempo
    exito = operario_soldador.asignar_tarea(1, 2.0)
    
    # Como está dado de baja, tiene que fallar
    assert exito is False