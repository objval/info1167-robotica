import math
import random
from dataclasses import asdict

import networkx as nx

from .grafos import (
    bfs,
    crear_grafo_cuadricula,
    dfs,
    dijkstra,
    ruta_corta_aleatoria,
    todas_las_rutas,
)
from .modelos import Carrito, ConfigSimulacion, EstadoRobot, Robot


class SimulacionAGV:
    COLORES = ["rojo", "azul", "verde", "naranja"]

    def __init__(self, config=None):
        self.config = config or ConfigSimulacion()
        self.rng = random.Random(self.config.semilla)
        self.grafo = crear_grafo_cuadricula(self.config.ancho, self.config.alto)
        self.robots = []
        self.carritos = []
        self.ticks = 0
        self.eventos = []
        self._iniciar_entidades()

    def _iniciar_entidades(self):
        esquinas = [
            (0, 0),
            (self.config.ancho - 1, 0),
            (0, self.config.alto - 1),
            (self.config.ancho - 1, self.config.alto - 1),
        ]
        bases = esquinas[: self.config.cantidad_robots]
        for i in range(self.config.cantidad_robots):
            base = bases[i % len(bases)]
            self.robots.append(
                Robot(id=i, color=self.COLORES[i], base=base, nodo=base)
            )

        ocupados = {r.base for r in self.robots}
        for i in range(self.config.cantidad_carritos):
            nodo = self._nodo_aleatorio(excluir=ocupados)
            ocupados.add(nodo)
            destino = self._nodo_aleatorio(excluir=ocupados)
            self.carritos.append(
                Carrito(id=i, color_original="gris", nodo=nodo, destino=destino)
            )

    def _nodo_aleatorio(self, excluir):
        while True:
            n = (self.rng.randrange(self.config.ancho), self.rng.randrange(self.config.alto))
            if n not in excluir:
                return n

    def _normalizar_angulo(self, angulo):
        while angulo > 180:
            angulo -= 360
        while angulo < -180:
            angulo += 360
        return angulo

    def _angulo_deseado(self, actual, siguiente):
        dx = siguiente[0] - actual[0]
        dy = siguiente[1] - actual[1]
        return math.degrees(math.atan2(dy, dx))

    def _rotar_y_mover(self, robot):
        if len(robot.ruta) <= 1:
            return False
        objetivo = robot.ruta[1]
        deseado = self._angulo_deseado(robot.nodo, objetivo)
        delta = self._normalizar_angulo(deseado - robot.angulo)
        paso = self.config.paso_rotacion
        if abs(delta) > paso:
            robot.angulo = self._normalizar_angulo(robot.angulo + (paso if delta > 0 else -paso))
            return False

        robot.angulo = deseado
        robot.nodo = objetivo
        robot.ruta = robot.ruta[1:]
        robot.bateria = max(0.0, robot.bateria - self.config.gasto_bateria)
        return True

    def _obtener_ruta(self, origen, destino):
        modo = self.config.modo_ruta
        if modo == "dijkstra":
            return dijkstra(self.grafo, origen, destino)
        if modo == "bfs":
            return bfs(self.grafo, origen, destino)
        if modo == "random_shortest":
            return ruta_corta_aleatoria(self.grafo, origen, destino, self.rng)
        raise ValueError(f"modo_ruta no soportado: {modo}")

    def _asignar_robots_libres(self):
        carritos_libres = [c for c in self.carritos if c.robot_asignado is None]
        self.rng.shuffle(carritos_libres)

        for r in self.robots:
            if r.estado not in {EstadoRobot.EN_BASE, EstadoRobot.CARGANDO}:
                continue
            if r.estado == EstadoRobot.CARGANDO and r.bateria < 100.0:
                continue
            if r.carrito_asignado is not None:
                continue
            if not carritos_libres:
                break

            carrito = carritos_libres.pop()
            carrito.robot_asignado = r.id
            carrito.color_original = r.color
            r.carrito_asignado = carrito.id
            r.estado = EstadoRobot.BUSCANDO_CARRITO
            r.ruta = self._obtener_ruta(r.nodo, carrito.nodo)
            self.eventos.append(f"tick={self.ticks}: robot {r.id} asignado a carrito {carrito.id}")

    def _carrito_por_id(self, cid):
        return next(c for c in self.carritos if c.id == cid)

    def _avanzar_robot(self, r):
        if r.estado == EstadoRobot.CARGANDO:
            r.bateria = min(100.0, r.bateria + self.config.carga_bateria)
            if r.bateria >= 100.0:
                r.estado = EstadoRobot.EN_BASE
                self.eventos.append(f"tick={self.ticks}: robot {r.id} bateria 100% listo")
            return

        if r.estado == EstadoRobot.EN_BASE:
            return

        self._rotar_y_mover(r)

        if r.estado == EstadoRobot.BUSCANDO_CARRITO:
            carrito = self._carrito_por_id(r.carrito_asignado)
            if r.nodo == carrito.nodo:
                r.estado = EstadoRobot.LLEVANDO_CARRITO
                r.ruta = self._obtener_ruta(r.nodo, carrito.destino)
                self.eventos.append(f"tick={self.ticks}: robot {r.id} recogio carrito {carrito.id}")

        elif r.estado == EstadoRobot.LLEVANDO_CARRITO:
            carrito = self._carrito_por_id(r.carrito_asignado)
            carrito.nodo = r.nodo
            if r.nodo == carrito.destino:
                carrito.entregas += 1
                r.entregas_completadas += 1
                self.eventos.append(f"tick={self.ticks}: robot {r.id} entrego carrito {carrito.id}")

                ocupados = {rb.nodo for rb in self.robots}
                carrito.nodo = self._nodo_aleatorio(excluir=ocupados)
                carrito.destino = self._nodo_aleatorio(excluir=ocupados | {carrito.nodo})
                carrito.robot_asignado = None
                carrito.color_original = "gris"

                r.carrito_asignado = None
                r.estado = EstadoRobot.VOLVIENDO_BASE
                r.ruta = self._obtener_ruta(r.nodo, r.base)

        elif r.estado == EstadoRobot.VOLVIENDO_BASE:
            if r.nodo == r.base:
                r.estado = EstadoRobot.CARGANDO
                self.eventos.append(f"tick={self.ticks}: robot {r.id} llego a base y carga")

    def paso(self):
        self._asignar_robots_libres()
        for r in self.robots:
            self._avanzar_robot(r)
        self.ticks += 1

    def correr(self, ticks=None):
        limite = ticks if ticks is not None else self.config.max_ticks
        for _ in range(limite):
            self.paso()
        return self.resumen()

    def resumen(self):
        origen = (0, 0)
        destino = (min(3, self.config.ancho - 1), min(2, self.config.alto - 1))
        ej_bfs = bfs(self.grafo, origen, destino)
        ej_dijkstra = dijkstra(self.grafo, origen, destino)
        ej_dfs = dfs(self.grafo, origen, destino)
        rutas = todas_las_rutas(self.grafo, origen, destino, max_caminos=12, limite=6)

        return {
            "ticks": self.ticks,
            "config": asdict(self.config),
            "robots": [asdict(r) for r in self.robots],
            "carritos": [asdict(c) for c in self.carritos],
            "entregas_totales": sum(r.entregas_completadas for r in self.robots),
            "ultimos_eventos": self.eventos[-20:],
            "seniales_requisitos": {
                "cantidad_robots": len(self.robots),
                "colores_unicos": len({r.color for r in self.robots}),
                "paso_rotacion": self.config.paso_rotacion,
                "baterias_ok": all(0.0 <= r.bateria <= 100.0 for r in self.robots),
                "modo_ruta": self.config.modo_ruta,
            },
            "ejemplos_grafos": {
                "origen": origen,
                "destino": destino,
                "bfs": ej_bfs,
                "dijkstra": ej_dijkstra,
                "dfs": ej_dfs,
                "todas_las_rutas": rutas,
                "cantidad_rutas": len(rutas),
                "al_menos_una_ruta": len(rutas) > 0,
            },
        }
