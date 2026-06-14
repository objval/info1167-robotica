from pathlib import Path

import matplotlib.pyplot as plt

from .simulacion import SimulacionAGV


def guardar_captura(sim, ruta_salida):
    p = Path(ruta_salida)
    p.parent.mkdir(parents=True, exist_ok=True)

    traducir_color = {
        "rojo": "red",
        "azul": "blue",
        "verde": "green",
        "naranja": "orange",
        "gris": "gray",
    }

    def color(c):
        return traducir_color.get(c, c)

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_title(f"Simulacion AGV (tick={sim.ticks})")
    ax.set_xlim(-1, sim.config.ancho)
    ax.set_ylim(-1, sim.config.alto)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)

    for c in sim.carritos:
        ax.scatter(c.nodo[0], c.nodo[1], marker="s", s=120, color=color(c.color_original), edgecolors="black")
        ax.scatter(c.destino[0], c.destino[1], marker="x", s=100, color="black")

    for r in sim.robots:
        ax.scatter(r.base[0], r.base[1], marker="^", s=160, color=color(r.color), alpha=0.3)
        ax.scatter(r.nodo[0], r.nodo[1], marker="o", s=180, color=color(r.color), edgecolors="black")
        ax.text(r.nodo[0] + 0.1, r.nodo[1] + 0.1, f"R{r.id}", fontsize=9)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    fig.tight_layout()
    fig.savefig(p, dpi=180)
    plt.close(fig)
    return str(p)
