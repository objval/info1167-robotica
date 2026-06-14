#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ejecutar(cmd, cwd=ROOT):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def etapa_setup(python):
    ejecutar([python, "-m", "pip", "install", "-e", ".[dev]"])


def etapa_test(python):
    ejecutar([python, "-m", "pytest", "-q"])


def etapa_simular(python, ticks, semilla, ancho, alto, salida, modo_ruta):
    ejecutar([
        python,
        "scripts/ejecutar_simulacion.py",
        "--ticks", str(ticks),
        "--semilla", str(semilla),
        "--ancho", str(ancho),
        "--alto", str(alto),
        "--salida", salida,
        "--modo-ruta", modo_ruta,
    ])


def etapa_verificar(salida, estricto):
    out = ROOT / salida
    req_path = out / "reporte_requisitos.json"
    sum_path = out / "resumen.json"

    if not req_path.exists():
        raise SystemExit(f"Falta reporte: {req_path}")
    if not sum_path.exists():
        raise SystemExit(f"Falta resumen: {sum_path}")

    reporte = json.loads(req_path.read_text(encoding="utf-8"))
    resumen = json.loads(sum_path.read_text(encoding="utf-8"))

    print("\n=== VERIFICACION DE REQUISITOS ===")
    for c in reporte["checks"]:
        status = "OK" if c["ok"] else "FAIL"
        print(f"[{status}] {c['id']} - {c['requisito']}")

    print("\n=== RESUMEN ===")
    print(f"Ticks: {resumen['ticks']}")
    print(f"Entregas: {resumen['entregas_totales']}")
    print(f"Modo ruta: {resumen['seniales_requisitos']['modo_ruta']}")
    print(f"Aprobado: {reporte['porcentaje']}% ({reporte['aprobados']}/{len(reporte['checks'])})")

    if estricto and reporte["reprobados"] > 0:
        raise SystemExit(2)

    return reporte


def main():
    parser = argparse.ArgumentParser(description="Pipeline INFO1167 AGV Lab #1")
    parser.add_argument("etapa", choices=["setup", "test", "simular", "verificar", "todo"])
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--ticks", type=int, default=1000)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--ancho", type=int, default=10)
    parser.add_argument("--alto", type=int, default=8)
    parser.add_argument("--salida", default="outputs")
    parser.add_argument("--modo-ruta", default="random_shortest", choices=["random_shortest", "dijkstra", "bfs"])
    parser.add_argument("--sin-setup", action="store_true", help="Saltar instalacion cuando etapa=todo")
    parser.add_argument("--no-estricto", action="store_true", help="No fallar si hay checks reprobados")
    args = parser.parse_args()

    estricto = not args.no_estricto

    if args.etapa == "setup":
        etapa_setup(args.python)
        return
    if args.etapa == "test":
        etapa_test(args.python)
        return
    if args.etapa == "simular":
        etapa_simular(args.python, args.ticks, args.semilla, args.ancho, args.alto, args.salida, args.modo_ruta)
        return
    if args.etapa == "verificar":
        etapa_verificar(args.salida, estricto)
        return

    # etapa = todo
    if not args.sin_setup:
        etapa_setup(args.python)
    etapa_test(args.python)
    etapa_simular(args.python, args.ticks, args.semilla, args.ancho, args.alto, args.salida, args.modo_ruta)
    etapa_verificar(args.salida, estricto)


if __name__ == "__main__":
    main()
