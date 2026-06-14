from agv_sim.modelos import ConfigSimulacion, EstadoRobot
from agv_sim.simulacion import SimulacionAGV
from agv_sim.verificador import verificar_requisitos


def test_simulacion_entrega_carritos():
    sim = SimulacionAGV(ConfigSimulacion(semilla=7, max_ticks=900))
    out = sim.correr(900)
    assert out["entregas_totales"] > 0


def test_estados_robots_validos():
    sim = SimulacionAGV(ConfigSimulacion(semilla=1, max_ticks=100))
    sim.correr(100)
    validos = {s.value for s in EstadoRobot}
    for r in sim.robots:
        assert r.estado.value in validos


def test_baterias_en_rango():
    sim = SimulacionAGV(ConfigSimulacion(semilla=3, max_ticks=500))
    sim.correr(500)
    for r in sim.robots:
        assert 0.0 <= r.bateria <= 100.0


def test_carrito_cambia_color_al_asignar():
    sim = SimulacionAGV(ConfigSimulacion(semilla=11, max_ticks=5))
    sim.paso()
    asignados = [c for c in sim.carritos if c.robot_asignado is not None]
    assert asignados, "Esperaba al menos un carrito asignado"
    for c in asignados:
        robot = next(r for r in sim.robots if r.id == c.robot_asignado)
        assert c.color_original == robot.color


def test_resumen_incluye_grafos_y_config():
    sim = SimulacionAGV(ConfigSimulacion(semilla=13, max_ticks=200, modo_ruta="random_shortest"))
    resumen = sim.correr(200)

    assert resumen["config"]["modo_ruta"] == "random_shortest"
    assert resumen["seniales_requisitos"]["paso_rotacion"] == 10.0

    grafos = resumen["ejemplos_grafos"]
    assert len(grafos["dfs"]) >= 1
    assert len(grafos["dijkstra"]) >= 1
    assert grafos["cantidad_rutas"] >= 1
    assert grafos["al_menos_una_ruta"] is True


def test_reporte_requisitos_aprueba_todo():
    sim = SimulacionAGV(ConfigSimulacion(semilla=21, max_ticks=800, modo_ruta="random_shortest"))
    resumen = sim.correr(800)
    reporte = verificar_requisitos(sim, resumen)

    assert reporte["reprobados"] == 0
    assert reporte["aprobados"] == len(reporte["checks"])
