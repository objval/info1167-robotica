from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EstadoRobot(str, Enum):
    EN_BASE = "en_base"
    BUSCANDO_CARRITO = "buscando_carrito"
    LLEVANDO_CARRITO = "llevando_carrito"
    VOLVIENDO_BASE = "volviendo_base"
    CARGANDO = "cargando"


@dataclass
class Carrito:
    id: int
    color_original: str
    nodo: tuple
    destino: tuple
    robot_asignado: int | None = None
    entregas: int = 0


@dataclass
class Robot:
    id: int
    color: str
    base: tuple
    nodo: tuple
    angulo: float = 0.0
    bateria: float = 100.0
    estado: EstadoRobot = EstadoRobot.EN_BASE
    carrito_asignado: int | None = None
    ruta: list = field(default_factory=list)
    entregas_completadas: int = 0


@dataclass
class ConfigSimulacion:
    ancho: int = 10
    alto: int = 8
    cantidad_robots: int = 4
    cantidad_carritos: int = 4
    paso_rotacion: float = 10.0
    gasto_bateria: float = 0.8
    carga_bateria: float = 5.0
    semilla: int = 42
    max_ticks: int = 1500
    modo_ruta: str = "random_shortest"
