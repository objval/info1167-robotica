#!/usr/bin/env python3
"""
INFO1167 Robotica Lab #1 - Demo completa para la defensa
==========================================================
Corre esto para mostrarle al profe. Output minimal en consola.
Todo el detalle esta en la ventana Tkinter.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from agv_sim.animacion_tkinter import AnimadorTkinter
from agv_sim.modelos import ConfigSimulacion
from agv_sim.simulacion import SimulacionAGV
from agv_sim.verificador import verificar_requisitos


def paso_tests(verbose=False):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        capture_output=True, text=True,
    )
    passed = result.stdout.count("PASSED")
    failed = result.stdout.count("FAILED")
    if verbose:
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    return passed, failed


def paso_simulacion(cfg):
    sim = SimulacionAGV(cfg)
    for _ in range(cfg.max_ticks):
        sim.paso()
    return sim


def paso_archivos(sim, resumen):
    Path("outputs").mkdir(exist_ok=True)
    with open("outputs/resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    reporte = verificar_requisitos(sim, resumen)
    with open("outputs/reporte_requisitos.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    return reporte


def main():
    parser = argparse.ArgumentParser(description="Demo INFO1167 Lab #1")
    parser.add_argument("--tkinter", action="store_true", default=True, help="Usar Tkinter (default)")
    parser.add_argument("--sin-animacion", action="store_true", help="Solo reportes, sin GUI")
    parser.add_argument("--verbose", action="store_true", help="Output completo en consola")
    parser.add_argument("--ticks", type=int, default=600)
    parser.add_argument("--velocidad", type=int, default=15)
    parser.add_argument("--semilla", type=int, default=123)
    parser.add_argument("--modo-ruta", default="random_shortest")
    args = parser.parse_args()

    # Tests
    passed, failed = paso_tests(verbose=args.verbose)
    if failed > 0:
        print(f"Tests: {passed} passed, {failed} FAILED")
        return
    print(f"Tests: {passed}/{passed} PASSED")

    # Config
    cfg = ConfigSimulacion(
        semilla=args.semilla,
        ancho=10,
        alto=8,
        max_ticks=args.ticks,
        modo_ruta=args.modo_ruta,
    )

    # Simulacion
    sim = paso_simulacion(cfg)
    entregas = sum(r.entregas_completadas for r in sim.robots)
    resumen = sim.resumen()
    print(f"Simulacion: {entregas} entregas en {cfg.max_ticks} ticks")

    # Reporte
    reporte = paso_archivos(sim, resumen)
    pct = reporte.get("porcentaje", 0)
    ok = reporte.get("aprobados", 0)
    print(f"Requisitos: {ok}/8 OK ({pct}%)")

    # Animacion
    if args.sin_animacion:
        print("Animacion: omitida (--sin-animacion)")
    else:
        print("Abriendo animacion Tkinter...")
        AnimadorTkinter(sim, reporte=reporte, resumen=resumen).animar(
            ticks=args.ticks, velocidad=args.velocidad
        )

    print(f"Archivos: {Path.cwd() / 'outputs'}")


if __name__ == "__main__":
    main()
