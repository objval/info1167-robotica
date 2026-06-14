#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from agv_sim.modelos import ConfigSimulacion
from agv_sim.simulacion import SimulacionAGV
from agv_sim.verificador import verificar_requisitos
from agv_sim.visualizador import guardar_captura


def main():
    parser = argparse.ArgumentParser(description="Ejecutar simulacion AGV Lab #1")
    parser.add_argument("--ticks", type=int, default=600)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--ancho", type=int, default=10)
    parser.add_argument("--alto", type=int, default=8)
    parser.add_argument("--salida", type=str, default="outputs")
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
    resumen = sim.correr(args.ticks)

    outdir = Path(args.salida)
    outdir.mkdir(parents=True, exist_ok=True)

    resumen_path = outdir / "resumen.json"
    resumen_path.write_text(json.dumps(resumen, indent=2), encoding="utf-8")

    reporte = verificar_requisitos(sim, resumen)
    req_path = outdir / "reporte_requisitos.json"
    req_path.write_text(json.dumps(reporte, indent=2), encoding="utf-8")

    img_path = outdir / "captura.png"
    guardar_captura(sim, str(img_path))

    print(f"Simulacion completa. Entregas={resumen['entregas_totales']}")
    print(f"Checks: {reporte['aprobados']}/{len(reporte['checks'])}")
    print(f"Resumen: {resumen_path}")
    print(f"Requisitos: {req_path}")
    print(f"Captura: {img_path}")


if __name__ == "__main__":
    main()
