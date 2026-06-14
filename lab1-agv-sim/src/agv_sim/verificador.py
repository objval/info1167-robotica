from .simulacion import SimulacionAGV


def verificar_requisitos(sim, resumen):
    colores_unicos = {r.color for r in sim.robots}
    cantidad_rutas = resumen.get("ejemplos_grafos", {}).get("cantidad_rutas", 0)

    checks = [
        {
            "id": "R1",
            "requisito": "Simular 4 robots AGV en mapa 2D",
            "ok": len(sim.robots) == 4 and sim.config.ancho > 0 and sim.config.alto > 0,
            "evidencia": {"robots": len(sim.robots), "grilla": [sim.config.ancho, sim.config.alto]},
        },
        {
            "id": "R2",
            "requisito": "Inicio en bases y busqueda de carrito asignado aleatoriamente",
            "ok": any("asignado a carrito" in e for e in sim.eventos),
            "evidencia": {"asignaciones": [e for e in sim.eventos if "asignado a carrito" in e][:4]},
        },
        {
            "id": "R3",
            "requisito": "Carrito adopta color unico del robot asignado",
            "ok": len(colores_unicos) == len(sim.robots),
            "evidencia": {"colores": sorted(colores_unicos)},
        },
        {
            "id": "R4",
            "requisito": "Rutas dadas por algoritmos de grafos",
            "ok": bool(resumen.get("ejemplos_grafos", {}).get("dijkstra"))
            and bool(resumen.get("ejemplos_grafos", {}).get("bfs"))
            and bool(resumen.get("ejemplos_grafos", {}).get("dfs")),
            "evidencia": {
                "dijkstra_len": len(resumen.get("ejemplos_grafos", {}).get("dijkstra", [])),
                "bfs_len": len(resumen.get("ejemplos_grafos", {}).get("bfs", [])),
                "dfs_len": len(resumen.get("ejemplos_grafos", {}).get("dfs", [])),
            },
        },
        {
            "id": "R5",
            "requisito": "Movimiento con variacion aleatoria hacia nodo final",
            "ok": sim.config.modo_ruta == "random_shortest",
            "evidencia": {"modo_ruta": sim.config.modo_ruta},
        },
        {
            "id": "R6",
            "requisito": "Rotaciones en pasos de 10 grados",
            "ok": abs(sim.config.paso_rotacion - 10.0) < 1e-9,
            "evidencia": {"paso_rotacion": sim.config.paso_rotacion},
        },
        {
            "id": "R7",
            "requisito": "Entrega y retorno a base para carga",
            "ok": resumen.get("entregas_totales", 0) > 0
            and any("llego a base y carga" in e for e in sim.eventos)
            and any("bateria 100% listo" in e for e in sim.eventos),
            "evidencia": {
                "entregas_totales": resumen.get("entregas_totales", 0),
                "eventos_carga": [e for e in sim.eventos if "llego a base y carga" in e][:4],
                "eventos_listos": [e for e in sim.eventos if "bateria 100% listo" in e][:4],
            },
        },
        {
            "id": "R8",
            "requisito": "Temas de grafos: profundidad, ruta corta, todas y al menos una ruta",
            "ok": bool(resumen.get("ejemplos_grafos", {}).get("dfs"))
            and bool(resumen.get("ejemplos_grafos", {}).get("dijkstra"))
            and cantidad_rutas > 0,
            "evidencia": {
                "cantidad_rutas": cantidad_rutas,
                "al_menos_una": resumen.get("ejemplos_grafos", {}).get("al_menos_una_ruta", False),
            },
        },
    ]

    aprobados = sum(1 for c in checks if c["ok"])
    return {
        "checks": checks,
        "aprobados": aprobados,
        "reprobados": len(checks) - aprobados,
        "porcentaje": round((aprobados / len(checks)) * 100.0, 2),
    }
