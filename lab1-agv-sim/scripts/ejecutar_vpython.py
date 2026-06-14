#!/usr/bin/env python3
import argparse

from agv_sim.animacion_vpython import AnimadorVPython
from agv_sim.modelos import ConfigSimulacion
from agv_sim.simulacion import SimulacionAGV


def main():
    parser = argparse.ArgumentParser(description="Simulacion AGV con Visual Python")
    parser.add_argument("--ticks", type=int, default=600)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--ancho", type=int, default=10)
    parser.add_argument("--alto", type=int, default=8)
    parser.add_argument("--velocidad", type=int, default=10)
    parser.add_argument(
        "--modo-ruta",
        type=str,
        default="random_shortest",
        choices=["random_shortest", "dijkstra", "bfs"],
    )
    args = parser.parse_args()

    config = ConfigSimulacion(
        semilla=args.semilla,
        ancho=args.ancho,
        alto=args.alto,
        max_ticks=args.ticks,
        modo_ruta=args.modo_ruta,
    )
    sim = SimulacionAGV(config)
    animador = AnimadorVPython(sim)
    animador.animar(ticks=args.ticks, velocidad=args.velocidad)


if __name__ == "__main__":
    main()
