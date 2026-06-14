"""
Animador Tkinter Profesional - INFO1167 Robotica Lab #1
========================================================
Tema oscuro, rutas visibles, controles de reproduccion,
efectos ripple y dashboard de metricas en vivo.
"""

import math
import random
import tkinter as tk
from tkinter import ttk

from .simulacion import SimulacionAGV, EstadoRobot
from .sprites import PALETA, crear_sprite_sheet, obtener_robot_mas_cercano

# Paleta oscura profesional (Catppuccin Mocha inspired)
DARK = {
    "bg": "#0f1117",
    "panel": "#1a1d27",
    "panel_light": "#232634",
    "border": "#2a2e3f",
    "text": "#cdd6f4",
    "text_dim": "#6c7086",
    "accent": "#89b4fa",
    "green": "#a6e3a1",
    "red": "#f38ba8",
    "orange": "#fab387",
    "yellow": "#f9e2af",
    "grid": "#313244",
    "canvas_bg": "#11131a",
}


def _color_from_hex(hex_color):
    """Convierte #RRGGBB a tuple (R, G, B) 0-255."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _hex_from_rgb(r, g, b):
    """Convierte (R, G, B) a #RRGGBB."""
    return f"#{r:02x}{g:02x}{b:02x}"


def _fade_color(hex1, hex2, t):
    """Interpola entre dos colores hex. t=0 -> hex1, t=1 -> hex2."""
    c1 = _color_from_hex(hex1)
    c2 = _color_from_hex(hex2)
    return _hex_from_rgb(
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


class AnimadorTkinter:
    def __init__(self, sim, reporte=None, resumen=None):
        self.sim = sim
        self.reporte = reporte or {}
        self.resumen = resumen or {}
        self.ventana = tk.Tk()
        self.ventana.title("INFO1167 Robotica | Lab #1 - Simulacion AGV")
        self.ventana.configure(bg=DARK["bg"])
        self.ventana.option_add("*background", DARK["bg"])
        self.ventana.option_add("*foreground", DARK["text"])

        # Estado de reproduccion
        self.pausado = False
        self.velocidad = 15
        self.ticks_totales = 0
        self.contador = 0
        self.en_ejecucion = True
        self.distancia_total = 0
        self.ultima_pos = {r.id: (r.nodo[0], r.nodo[1]) for r in sim.robots}

        # Sprites
        colores = [r.color for r in sim.robots]
        self.sprite_sheet = crear_sprite_sheet(
            robots_colores=colores,
            tam_robot=44,
            tam_carrito=30,
            tam_base=38,
            tam_destino=28,
        )

        # Layout
        self.ancho_ventana = 1350
        self.alto_ventana = 860
        self.ancho_mapa = 780
        self.ancho_panel = self.ancho_ventana - self.ancho_mapa - 30

        sw = self.ventana.winfo_screenwidth()
        sh = self.ventana.winfo_screenheight()
        x = (sw - self.ancho_ventana) // 2
        y = (sh - self.alto_ventana) // 2 - 30
        self.ventana.geometry(f"{self.ancho_ventana}x{self.alto_ventana}+{x}+{y}")
        self.ventana.minsize(1150, 700)

        self._crear_header()
        self._crear_panel_izquierdo()
        self._crear_panel_derecho()
        self._init_canvas_objects()

        self.ultimos_eventos = 0
        self.ripples = []  # lista de dicts: {id, x, y, r, alpha, color}
        self.rutas_canvas = {}  # robot_id -> list of canvas line ids

    # ------------------------------------------------------------------
    # HEADER: CONTROLES
    # ------------------------------------------------------------------
    def _crear_header(self):
        hdr = tk.Frame(self.ventana, bg=DARK["panel"], height=50)
        hdr.pack(fill="x", padx=12, pady=(10, 0))
        hdr.pack_propagate(False)

        # Titulo
        tk.Label(hdr, text="INFO1167  |  Simulacion AGV", font=("Segoe UI", 14, "bold"),
                 bg=DARK["panel"], fg=DARK["text"]).pack(side="left", padx=(14, 20))

        # Botones de control
        btn_cfg = {"font": ("Segoe UI", 10, "bold"), "bd": 0, "padx": 14, "pady": 4,
                   "cursor": "hand2", "activebackground": DARK["accent"]}

        self.btn_play = tk.Button(hdr, text="⏸ Pausar", bg=DARK["green"], fg=DARK["bg"],
                                  command=self._toggle_pausa, **btn_cfg)
        self.btn_play.pack(side="left", padx=4)

        tk.Button(hdr, text="⏪ Lento", bg=DARK["panel_light"], fg=DARK["text"],
                  command=lambda: self._cambiar_velocidad(-3), **btn_cfg).pack(side="left", padx=4)
        tk.Button(hdr, text="⏩ Rapido", bg=DARK["panel_light"], fg=DARK["text"],
                  command=lambda: self._cambiar_velocidad(3), **btn_cfg).pack(side="left", padx=4)
        tk.Button(hdr, text="↻ Reiniciar", bg=DARK["panel_light"], fg=DARK["text"],
                  command=self._reiniciar, **btn_cfg).pack(side="left", padx=4)

        # Velocidad actual
        self.lbl_vel = tk.Label(hdr, text=f"Vel: {self.velocidad} t/s",
                                font=("Segoe UI", 10), bg=DARK["panel"], fg=DARK["text_dim"])
        self.lbl_vel.pack(side="left", padx=(14, 0))

        # Tick actual / total
        self.lbl_tick_hdr = tk.Label(hdr, text="Tick: 0 / 600",
                                     font=("Segoe UI", 12, "bold"),
                                     bg=DARK["panel"], fg=DARK["accent"])
        self.lbl_tick_hdr.pack(side="right", padx=14)

    def _toggle_pausa(self):
        self.pausado = not self.pausado
        if self.pausado:
            self.btn_play.config(text="▶ Reanudar", bg=DARK["accent"], fg=DARK["bg"])
        else:
            self.btn_play.config(text="⏸ Pausar", bg=DARK["green"], fg=DARK["bg"])
            self._programar_siguiente()

    def _cambiar_velocidad(self, delta):
        self.velocidad = max(2, min(40, self.velocidad + delta))
        self.lbl_vel.config(text=f"Vel: {self.velocidad} t/s")

    def _reiniciar(self):
        self.en_ejecucion = False
        self.ventana.after(100, self._do_reiniciar)

    def _do_reiniciar(self):
        # Crear nueva simulacion desde cero
        self.sim = SimulacionAGV(self.sim.config)
        self.contador = 0
        self.pausado = False
        self.en_ejecucion = True
        self.distancia_total = 0
        self.ultima_pos = {r.id: (r.nodo[0], r.nodo[1]) for r in self.sim.robots}
        self.ultimos_eventos = 0
        self.ripples.clear()
        self.btn_play.config(text="⏸ Pausar", bg=DARK["green"], fg=DARK["bg"])
        self._limpiar_rutas()
        self._reiniciar_canvas()
        self._log("Simulacion reiniciada.", "success")
        self._programar_siguiente()

    # ------------------------------------------------------------------
    # PANEL IZQUIERDO: MAPA
    # ------------------------------------------------------------------
    def _crear_panel_izquierdo(self):
        self.frame_mapa = tk.Frame(self.ventana, bg=DARK["bg"], width=self.ancho_mapa)
        self.frame_mapa.pack(side="left", fill="both", expand=False, padx=(12, 0), pady=10)
        self.frame_mapa.pack_propagate(False)

        alto_c = self.alto_ventana - 110
        self.canvas = tk.Canvas(self.frame_mapa, width=self.ancho_mapa - 20,
                                height=alto_c, bg=DARK["canvas_bg"],
                                highlightthickness=1, highlightbackground=DARK["border"])
        self.canvas.pack()
        self.alto_canvas = alto_c

        w, h = self.sim.config.ancho, self.sim.config.alto
        margen = 50
        self.celda_w = (self.ancho_mapa - 20 - margen * 2) / w
        self.celda_h = (alto_c - margen * 2) / h
        self.offset_x = margen
        self.offset_y = margen

        self._dibujar_grilla(w, h)

    def _dibujar_grilla(self, w, h):
        for j in range(h):
            for i in range(w):
                x1 = i * self.celda_w + self.offset_x
                y1 = j * self.celda_h + self.offset_y
                x2 = x1 + self.celda_w
                y2 = y1 + self.celda_h
                color = "#161821" if (i + j) % 2 == 0 else "#1a1d27"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", width=0)

        for i in range(w + 1):
            x = i * self.celda_w + self.offset_x
            self.canvas.create_line(x, self.offset_y, x, h * self.celda_h + self.offset_y,
                                    fill=DARK["grid"], width=1)
        for j in range(h + 1):
            y = j * self.celda_h + self.offset_y
            self.canvas.create_line(self.offset_x, y, w * self.celda_w + self.offset_x, y,
                                    fill=DARK["grid"], width=1)

        self.canvas.create_rectangle(
            self.offset_x, self.offset_y,
            w * self.celda_w + self.offset_x, h * self.celda_h + self.offset_y,
            outline=DARK["border"], width=2
        )

        for i in range(w):
            x = i * self.celda_w + self.offset_x + self.celda_w / 2
            self.canvas.create_text(x, self.offset_y - 16, text=str(i),
                                    font=("Segoe UI", 9), fill=DARK["text_dim"])
        for j in range(h):
            y = j * self.celda_h + self.offset_y + self.celda_h / 2
            self.canvas.create_text(self.offset_x - 16, y, text=str(j),
                                    font=("Segoe UI", 9), fill=DARK["text_dim"])

    def _coord(self, gx, gy):
        x = gx * self.celda_w + self.celda_w / 2 + self.offset_x
        y = gy * self.celda_h + self.celda_h / 2 + self.offset_y
        return x, y

    # ------------------------------------------------------------------
    # PANEL DERECHO: METRICAS + LOG + REQUISITOS
    # ------------------------------------------------------------------
    def _crear_panel_derecho(self):
        self.frame_der = tk.Frame(self.ventana, bg=DARK["bg"], width=self.ancho_panel)
        self.frame_der.pack(side="right", fill="both", expand=True, padx=(0, 12), pady=10)
        self.frame_der.pack_propagate(False)

        # --- Metricas en vivo ---
        met = tk.LabelFrame(self.frame_der, text=" Metricas en Vivo ",
                            font=("Segoe UI", 11, "bold"),
                            bg=DARK["panel"], fg=DARK["text"],
                            highlightbackground=DARK["border"], highlightthickness=1)
        met.pack(fill="x", pady=(0, 8))

        self.metricas = {}
        metricas_data = [
            ("Throughput", "0.00 ent/tick", "throughput"),
            ("Distancia Total", "0 celdas", "distancia"),
            ("Bateria Promedio", "100%", "bateria_avg"),
            ("Algoritmo", self.sim.config.modo_ruta, "algo"),
        ]
        for titulo, val, key in metricas_data:
            row = tk.Frame(met, bg=DARK["panel"])
            row.pack(fill="x", padx=10, pady=3)
            tk.Label(row, text=titulo + ":", font=("Segoe UI", 9),
                     bg=DARK["panel"], fg=DARK["text_dim"]).pack(side="left")
            lbl = tk.Label(row, text=val, font=("Segoe UI", 10, "bold"),
                           bg=DARK["panel"], fg=DARK["accent"])
            lbl.pack(side="right")
            self.metricas[key] = lbl

        # --- Stats compactos ---
        stats = tk.Frame(self.frame_der, bg=DARK["panel"])
        stats.pack(fill="x", pady=(0, 8))
        stats.configure(highlightbackground=DARK["border"], highlightthickness=1)

        self._stat_box(stats, "Entregas", "0", DARK["green"], "entregas")
        self._stat_box(stats, "Robots", str(len(self.sim.robots)), DARK["accent"], "robots")
        self._stat_box(stats, "Ticks", "0", DARK["text"], "tick")

        # --- Baterias ---
        batt = tk.LabelFrame(self.frame_der, text=" Baterias ",
                             font=("Segoe UI", 10, "bold"),
                             bg=DARK["panel"], fg=DARK["text"],
                             highlightbackground=DARK["border"], highlightthickness=1)
        batt.pack(fill="x", pady=(0, 8))

        self.barras_bateria = {}
        for r in self.sim.robots:
            row = tk.Frame(batt, bg=DARK["panel"])
            row.pack(fill="x", padx=8, pady=3)

            tk.Label(row, image=self.sprite_sheet["robot"][r.color][0],
                     bg=DARK["panel"]).pack(side="left")
            tk.Label(row, text=f"R{r.id}", font=("Segoe UI", 10, "bold"),
                     bg=DARK["panel"], fg=DARK["text"], width=3).pack(side="left")

            bar = tk.Canvas(row, width=100, height=8, bg=DARK["grid"], highlightthickness=0)
            bar.pack(side="left", padx=(6, 0))
            fill_id = bar.create_rectangle(0, 0, 100, 8, fill=DARK["green"], width=0)

            lbl = tk.Label(row, text="100%", font=("Segoe UI", 9),
                           bg=DARK["panel"], fg=DARK["text"], width=5)
            lbl.pack(side="right")
            self.barras_bateria[r.id] = (bar, fill_id, lbl)

        # --- Estados ---
        est = tk.LabelFrame(self.frame_der, text=" Estados ",
                            font=("Segoe UI", 10, "bold"),
                            bg=DARK["panel"], fg=DARK["text"],
                            highlightbackground=DARK["border"], highlightthickness=1)
        est.pack(fill="x", pady=(0, 8))
        self.lbl_estados = tk.Label(est, text="Inicializando...",
                                     font=("Segoe UI", 9),
                                     bg=DARK["panel"], fg=DARK["text_dim"],
                                     justify="left", wraplength=self.ancho_panel - 40)
        self.lbl_estados.pack(padx=8, pady=6, anchor="w")

        # --- Requisitos ---
        if self.reporte.get("checks"):
            req_frame = tk.LabelFrame(self.frame_der, text=" Verificacion R1-R8 ",
                                      font=("Segoe UI", 10, "bold"),
                                      bg=DARK["panel"], fg=DARK["text"],
                                      highlightbackground=DARK["border"], highlightthickness=1)
            req_frame.pack(fill="x", pady=(0, 8))
            for c in self.reporte["checks"]:
                ok = c.get("ok", False)
                color = DARK["green"] if ok else DARK["red"]
                icono = "✓" if ok else "✗"
                lbl = tk.Label(req_frame, text=f"{icono} {c['id']}: {c['requisito'][:32]}",
                               font=("Segoe UI", 8), bg=DARK["panel"], fg=color)
                lbl.pack(anchor="w", padx=8, pady=1)
            pct = self.reporte.get("porcentaje", 0)
            tk.Label(req_frame, text=f"Aprobado: {pct}%",
                     font=("Segoe UI", 10, "bold"), bg=DARK["panel"],
                     fg=DARK["green"] if pct == 100 else DARK["orange"]).pack(anchor="w", padx=8, pady=(2, 6))

        # --- Grafos ---
        if self.resumen.get("ejemplos_grafos"):
            grafos = self.resumen["ejemplos_grafos"]
            gf = tk.LabelFrame(self.frame_der, text=" Algoritmos de Grafos ",
                               font=("Segoe UI", 10, "bold"),
                               bg=DARK["panel"], fg=DARK["text"],
                               highlightbackground=DARK["border"], highlightthickness=1)
            gf.pack(fill="x", pady=(0, 8))
            datos = [
                ("BFS (anchura)", f"{len(grafos.get('bfs', []))} nodos"),
                ("Dijkstra", f"{len(grafos.get('dijkstra', []))} nodos"),
                ("DFS (profundidad)", f"{len(grafos.get('dfs', []))} nodos"),
                ("Rutas posibles", str(grafos.get("cantidad_rutas", 0))),
            ]
            for titulo, val in datos:
                row = tk.Frame(gf, bg=DARK["panel"])
                row.pack(fill="x", padx=8, pady=1)
                tk.Label(row, text=f"• {titulo}:", font=("Segoe UI", 8),
                        bg=DARK["panel"], fg=DARK["text_dim"]).pack(side="left")
                tk.Label(row, text=val, font=("Segoe UI", 8, "bold"),
                        bg=DARK["panel"], fg=DARK["accent"]).pack(side="right")

        # --- Log ---
        log_frame = tk.LabelFrame(self.frame_der, text=" Eventos ",
                                   font=("Segoe UI", 10, "bold"),
                                   bg=DARK["panel"], fg=DARK["text"],
                                   highlightbackground=DARK["border"], highlightthickness=1)
        log_frame.pack(fill="both", expand=True)

        self.txt_log = tk.Text(log_frame, font=("Segoe UI", 9),
                               bg=DARK["panel_light"], fg=DARK["text"],
                               highlightthickness=0, relief="flat",
                               wrap="word", state="disabled",
                               padx=8, pady=6)
        self.txt_log.pack(fill="both", expand=True, padx=4, pady=4)

        sb = ttk.Scrollbar(self.txt_log, command=self.txt_log.yview)
        sb.pack(side="right", fill="y")
        self.txt_log.config(yscrollcommand=sb.set)

        self.txt_log.tag_configure("timestamp", foreground=DARK["text_dim"], font=("Segoe UI", 8))
        self.txt_log.tag_configure("dim", foreground=DARK["text_dim"])
        self.txt_log.tag_configure("info", foreground=DARK["accent"])
        self.txt_log.tag_configure("success", foreground=DARK["green"])
        self.txt_log.tag_configure("accent", foreground=DARK["orange"])
        self.txt_log.tag_configure("warning", foreground=DARK["yellow"])
        self.txt_log.tag_configure("danger", foreground=DARK["red"])

        self._log("Sistema iniciado. Bodega AGV lista.", "success")
        self._log("4 robots activos. 8 carritos en almacen.", "info")

    def _stat_box(self, parent, title, value, color, attr_name):
        box = tk.Frame(parent, bg=DARK["panel"], padx=10, pady=6)
        box.pack(side="left", fill="x", expand=True)
        tk.Label(box, text=title, font=("Segoe UI", 8),
                bg=DARK["panel"], fg=DARK["text_dim"]).pack(anchor="w")
        lbl = tk.Label(box, text=value, font=("Segoe UI", 18, "bold"),
                      bg=DARK["panel"], fg=color)
        lbl.pack(anchor="w")
        setattr(self, f"val_{attr_name}", lbl)

    def _log(self, mensaje, tag="dim"):
        self.txt_log.config(state="normal")
        ts = f"[{self.sim.ticks:04d}] "
        self.txt_log.insert("end", ts, "timestamp")
        self.txt_log.insert("end", mensaje + "\n", tag)
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    # ------------------------------------------------------------------
    # CANVAS OBJECTS
    # ------------------------------------------------------------------
    def _init_canvas_objects(self):
        self.obj_bases = {}
        self.obj_robots = {}
        self.obj_carritos = {}
        self.obj_destinos = {}
        self.obj_rutas = {}  # robot_id -> lista de line ids

        for r in self.sim.robots:
            bx, by = self._coord(r.base[0], r.base[1])
            sprite = self.sprite_sheet["base"].get(r.color, list(self.sprite_sheet["base"].values())[0])
            self.obj_bases[r.id] = self.canvas.create_image(bx, by, image=sprite)
            self.canvas.create_text(bx, by + 24, text=f"B{r.id}",
                                    font=("Segoe UI", 8), fill=DARK["text_dim"])

        for c in self.sim.carritos:
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.obj_destinos[c.id] = self.canvas.create_image(dx, dy - 6,
                image=self.sprite_sheet["destino"])

        for c in self.sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            color = c.color_original if c.color_original in self.sprite_sheet["carrito"] else "gris"
            self.obj_carritos[c.id] = self.canvas.create_image(x, y,
                image=self.sprite_sheet["carrito"][color])

        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])
            sprite = obtener_robot_mas_cercano(self.sprite_sheet, r.color, r.angulo)
            self.obj_robots[r.id] = self.canvas.create_image(x, y, image=sprite)

    def _reiniciar_canvas(self):
        for oid in list(self.obj_robots.values()) + list(self.obj_carritos.values()) + list(self.obj_destinos.values()):
            self.canvas.coords(oid, -1000, -1000)
        for lines in self.obj_rutas.values():
            for lid in lines:
                self.canvas.delete(lid)
        self.obj_rutas.clear()
        self._limpiar_rutas()
        self.canvas.delete("ripple")

    def _limpiar_rutas(self):
        for lines in self.obj_rutas.values():
            for lid in lines:
                self.canvas.delete(lid)
        self.obj_rutas.clear()

    def _dibujar_rutas(self):
        """Dibuja las rutas planificadas de cada robot como lineas punteadas."""
        self._limpiar_rutas()
        for r in self.sim.robots:
            ruta = r.ruta
            if not ruta or len(ruta) < 2:
                continue
            color = PALETA.get(r.color, PALETA["azul"])
            line_ids = []
            for i in range(len(ruta) - 1):
                x1, y1 = self._coord(ruta[i][0], ruta[i][1])
                x2, y2 = self._coord(ruta[i + 1][0], ruta[i + 1][1])
                lid = self.canvas.create_line(x1, y1, x2, y2,
                                              fill=color, width=2, dash=(4, 4),
                                              stipple="gray25")
                line_ids.append(lid)
            self.obj_rutas[r.id] = line_ids

    def _crear_ripple(self, gx, gy, color):
        """Crea un efecto de onda expansiva en el canvas."""
        x, y = self._coord(gx, gy)
        rid = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5,
                                      outline=color, width=2, tags="ripple")
        self.ripples.append({"id": rid, "x": x, "y": y, "r": 5, "alpha": 1.0, "color": color})

    def _actualizar_ripples(self):
        """Actualiza y elimina ripples expirados."""
        nuevos = []
        for rip in self.ripples:
            rip["r"] += 3
            rip["alpha"] -= 0.05
            if rip["alpha"] <= 0:
                self.canvas.delete(rip["id"])
                continue
            # Simular alpha cambiando el color
            hex_color = PALETA.get(rip["color"], "#89b4fa")
            faded = _fade_color(hex_color, DARK["canvas_bg"], 1 - rip["alpha"])
            self.canvas.coords(rip["id"],
                               rip["x"] - rip["r"], rip["y"] - rip["r"],
                               rip["x"] + rip["r"], rip["y"] + rip["r"])
            self.canvas.itemconfig(rip["id"], outline=faded)
            nuevos.append(rip)
        self.ripples = nuevos

    # ------------------------------------------------------------------
    # ACTUALIZACION
    # ------------------------------------------------------------------
    def actualizar(self):
        # Robots
        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])
            self.canvas.coords(self.obj_robots[r.id], x, y)
            sprite = obtener_robot_mas_cercano(self.sprite_sheet, r.color, r.angulo)
            self.canvas.itemconfig(self.obj_robots[r.id], image=sprite)

        # Carritos
        for c in self.sim.carritos:
            x, y = self._coord(c.nodo[0], c.nodo[1])
            self.canvas.coords(self.obj_carritos[c.id], x, y)
            color = c.color_original if c.color_original in self.sprite_sheet["carrito"] else "gris"
            self.canvas.itemconfig(self.obj_carritos[c.id],
                                   image=self.sprite_sheet["carrito"][color])

        # Destinos
        for c in self.sim.carritos:
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.canvas.coords(self.obj_destinos[c.id], dx, dy - 6)

        # Rutas
        self._dibujar_rutas()

        # Ripples
        self._actualizar_ripples()

        # Stats
        entregas = sum(r.entregas_completadas for r in self.sim.robots)
        self.val_tick.config(text=str(self.sim.ticks))
        self.val_entregas.config(text=str(entregas))
        self.lbl_tick_hdr.config(text=f"Tick: {self.sim.ticks} / {self.ticks_totales}")

        # Metricas
        ticks = max(1, self.sim.ticks)
        throughput = entregas / ticks
        self.metricas["throughput"].config(text=f"{throughput:.3f} ent/tick")

        bateria_avg = sum(r.bateria for r in self.sim.robots) / len(self.sim.robots)
        self.metricas["bateria_avg"].config(text=f"{bateria_avg:.0f}%")

        self.metricas["distancia"].config(text=f"{self.distancia_total} celdas")

        # Baterias
        for r in self.sim.robots:
            bar, fill_id, lbl = self.barras_bateria[r.id]
            pct = max(0, min(100, int(r.bateria)))
            w = int(100 * (pct / 100))
            bar.coords(fill_id, 0, 0, w, 8)
            if pct < 20:
                bar.itemconfig(fill_id, fill=DARK["red"])
            elif pct < 50:
                bar.itemconfig(fill_id, fill=DARK["orange"])
            else:
                bar.itemconfig(fill_id, fill=DARK["green"])
            lbl.config(text=f"{pct}%")

        # Estados
        partes = []
        for r in self.sim.robots:
            estado = r.estado.value.replace("_", " ").title()
            partes.append(f"R{r.id}: {estado}")
        self.lbl_estados.config(text="  |  ".join(partes))

        # Eventos
        nuevos = self.sim.eventos[self.ultimos_eventos:]
        self.ultimos_eventos = len(self.sim.eventos)
        for ev in nuevos:
            tag = "dim"
            if "asignado" in ev:
                tag = "info"
            elif "recogio" in ev:
                tag = "success"
                rid = int(ev.split("robot ")[1].split()[0])
                r = self.sim.robots[rid]
                self._crear_ripple(r.nodo[0], r.nodo[1], r.color)
            elif "entrego" in ev:
                tag = "accent"
                rid = int(ev.split("robot ")[1].split()[0])
                r = self.sim.robots[rid]
                self._crear_ripple(r.nodo[0], r.nodo[1], r.color)
            elif "llego a base" in ev:
                tag = "warning"
            elif "bateria 100%" in ev:
                tag = "success"
            self._log(ev, tag)

        # Distancia
        for r in self.sim.robots:
            pos_actual = (r.nodo[0], r.nodo[1])
            if pos_actual != self.ultima_pos[r.id]:
                self.distancia_total += 1
                self.ultima_pos[r.id] = pos_actual

    # ------------------------------------------------------------------
    # LOOP
    # ------------------------------------------------------------------
    def _programar_siguiente(self):
        if not self.en_ejecucion or self.pausado:
            return
        if self.contador >= self.ticks_totales:
            self.val_tick.config(fg=DARK["green"])
            self.lbl_tick_hdr.config(text=f"COMPLETADO: {self.sim.ticks} ticks")
            self._log("=" * 35, "dim")
            self._log("Simulacion completada", "success")
            self._log(f"Entregas totales: {sum(r.entregas_completadas for r in self.sim.robots)}", "accent")
            self.btn_play.config(text="▶ Reanudar", bg=DARK["accent"], fg=DARK["bg"])
            self.en_ejecucion = False
            return
        self.sim.paso()
        self.actualizar()
        self.contador += 1
        delay = int(1000 / self.velocidad)
        self.ventana.after(delay, self._programar_siguiente)

    def animar(self, ticks=None, velocidad=15):
        self.ticks_totales = ticks if ticks is not None else self.sim.config.max_ticks
        self.velocidad = velocidad
        self.lbl_vel.config(text=f"Vel: {self.velocidad} t/s")
        self.lbl_tick_hdr.config(text=f"Tick: 0 / {self.ticks_totales}")
        self._programar_siguiente()
        self.ventana.mainloop()
