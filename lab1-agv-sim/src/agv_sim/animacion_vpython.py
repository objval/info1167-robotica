import math

from .simulacion import SimulacionAGV


def _color_vp(nombre):
    from vpython import color

    colores = {
        "rojo": color.red,
        "azul": color.blue,
        "verde": color.green,
        "naranja": color.orange,
        "gris": color.gray(0.5),
    }
    return colores.get(nombre, color.white)


class AnimadorVPython:
    def __init__(self, sim):
        from vpython import box, canvas, color, curve, cylinder, ring, vector

        self.sim = sim
        w, h = sim.config.ancho, sim.config.alto

        self.escena = canvas(
            title="INFO1167 AGV Lab #1 - Visual Python",
            width=900,
            height=700,
        )
        self.escena.background = color.white
        self.escena.camera.pos = vector(w / 2, max(w, h) * 1.2, h / 2)
        self.escena.camera.axis = vector(0, -max(w, h) * 1.2, 0)

        for x in range(w + 1):
            curve(pos=[vector(x, 0, 0), vector(x, 0, h)], color=color.gray(0.7), radius=0.02)
        for y in range(h + 1):
            curve(pos=[vector(0, 0, y), vector(w, 0, y)], color=color.gray(0.7), radius=0.02)

        box(pos=vector(w / 2, -0.05, h / 2), size=vector(w, 0.1, h), color=color.gray(0.95))

        self.obj_robots = {}
        self.obj_direcciones = {}
        self.obj_bases = {}
        self.obj_carritos = {}
        self.obj_destinos = {}

        for r in sim.robots:
            self.obj_bases[r.id] = cylinder(
                pos=vector(r.base[0], 0.01, r.base[1]),
                axis=vector(0, 0.3, 0),
                radius=0.35,
                color=_color_vp(r.color),
                opacity=0.3,
            )
            self.obj_robots[r.id] = cylinder(
                pos=vector(r.nodo[0], 0.2, r.nodo[1]),
                axis=vector(0, 0.4, 0),
                radius=0.25,
                color=_color_vp(r.color),
            )
            self.obj_direcciones[r.id] = cylinder(
                pos=vector(r.nodo[0], 0.35, r.nodo[1]),
                axis=vector(0.3, 0, 0),
                radius=0.04,
                color=color.black,
            )

        for c in sim.carritos:
            self.obj_carritos[c.id] = box(
                pos=vector(c.nodo[0], 0.15, c.nodo[1]),
                size=vector(0.35, 0.3, 0.35),
                color=_color_vp(c.color_original),
            )
            self.obj_destinos[c.id] = ring(
                pos=vector(c.destino[0], 0.01, c.destino[1]),
                axis=vector(0, 1, 0),
                radius=0.3,
                thickness=0.05,
                color=color.black,
            )

    def actualizar(self):
        from vpython import vector

        for r in self.sim.robots:
            self.obj_robots[r.id].pos = vector(r.nodo[0], 0.2, r.nodo[1])
            rad = math.radians(r.angulo)
            self.obj_direcciones[r.id].pos = vector(r.nodo[0], 0.35, r.nodo[1])
            self.obj_direcciones[r.id].axis = vector(math.cos(rad) * 0.4, 0, math.sin(rad) * 0.4)

        for c in self.sim.carritos:
            self.obj_carritos[c.id].pos = vector(c.nodo[0], 0.15, c.nodo[1])
            self.obj_carritos[c.id].color = _color_vp(c.color_original)
            self.obj_destinos[c.id].pos = vector(c.destino[0], 0.01, c.destino[1])

    def animar(self, ticks=None, velocidad=10):
        from vpython import rate

        limite = ticks if ticks is not None else self.sim.config.max_ticks
        for _ in range(limite):
            rate(velocidad)
            self.sim.paso()
            self.actualizar()
