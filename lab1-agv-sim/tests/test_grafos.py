from agv_sim.grafos import (
    bfs,
    crear_grafo_cuadricula,
    dfs,
    dijkstra,
    ruta_corta_aleatoria,
    todas_las_rutas,
)


def _ruta_valida(camino):
    for a, b in zip(camino, camino[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            return False
    return True


def test_dijkstra_en_grilla():
    g = crear_grafo_cuadricula(4, 4)
    p = dijkstra(g, (0, 0), (3, 3))
    assert p[0] == (0, 0)
    assert p[-1] == (3, 3)
    assert len(p) == 7


def test_bfs_y_dfs_devuelven_caminos():
    g = crear_grafo_cuadricula(4, 3)
    p1 = bfs(g, (0, 0), (3, 2))
    p2 = dfs(g, (0, 0), (3, 2))
    assert p1[0] == (0, 0) and p1[-1] == (3, 2)
    assert p2[0] == (0, 0) and p2[-1] == (3, 2)


def test_ruta_aleatoria_es_corta_y_valida():
    import random

    g = crear_grafo_cuadricula(5, 5)
    rng = random.Random(42)
    camino = ruta_corta_aleatoria(g, (0, 0), (4, 4), rng)
    assert camino[0] == (0, 0)
    assert camino[-1] == (4, 4)
    assert len(camino) == 9
    assert _ruta_valida(camino)


def test_ruta_aleatoria_explora_varias_opciones():
    import random

    g = crear_grafo_cuadricula(4, 4)
    rng = random.Random(99)
    observados = set()
    for _ in range(15):
        p = tuple(ruta_corta_aleatoria(g, (0, 0), (3, 3), rng))
        observados.add(p)
    assert len(observados) >= 2


def test_todas_las_rutas_devuelve_al_menos_una():
    g = crear_grafo_cuadricula(4, 3)
    rutas = todas_las_rutas(g, (0, 0), (3, 2), max_caminos=12, limite=6)
    assert len(rutas) >= 1
    for r in rutas:
        assert r[0] == (0, 0)
        assert r[-1] == (3, 2)
        assert _ruta_valida(r)
