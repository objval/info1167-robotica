"""
Animador Pygame - INFO1167 Robotica Lab #1
===========================================
Visualizacion profesional con tema oscuro, rutas visibles,
controles de reproduccion, efectos ripple y dashboard de metricas.
Funciona en Windows, macOS y Linux.
"""

import math
from pathlib import Path

import pygame

from agv_sim.modelos import ConfigSimulacion, EstadoRobot
from agv_sim.simulacion import SimulacionAGV
from agv_sim.sprites import crear_sprite_sheet


# ============================================================
# PALETA OSCURA PROFESIONAL
# ============================================================
PALETA = {
    "bg": (15, 17, 23),           # #0f1117
    "panel": (26, 29, 39),        # #1a1d27
    "panel_border": (45, 49, 66), # #2d3142
    "text": (226, 232, 240),      # #e2e8f0
    "text_dim": (148, 163, 184),  # #94a3b8
    "grid": (38, 42, 58),         # #262a3a
    "grid_alt": (22, 25, 35),     # #161923
    "accent": (56, 189, 248),     # #38bdf8
    "success": (74, 222, 128),    # #4ade80
    "warning": (251, 191, 36),    # #fbbf24
    "danger": (248, 113, 113),    # #f87171
    "robot_colors": {
        "rojo": (239, 68, 68),
        "azul": (59, 130, 246),
        "verde": (34, 197, 94),
        "naranja": (249, 115, 22),
    },
}


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


# ============================================================
# RIPPLE EFFECT
# ============================================================
class Ripple:
    def __init__(self, x, y, color, max_radius=40, duration=30):
        self.x = x
        self.y = y
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.age = 0
        self.alive = True

    def update(self):
        self.age += 1
        if self.age >= self.duration:
            self.alive = False

    def draw(self, surface):
        progress = self.age / self.duration
        radius = int(self.max_radius * progress)
        alpha = int(255 * (1 - progress))
        if radius > 0 and alpha > 0:
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (radius, radius), radius, 2)
            surface.blit(s, (self.x - radius, self.y - radius))


# ============================================================
# ANIMADOR PYGAME
# ============================================================
class AnimadorPygame:
    def __init__(self, sim: SimulacionAGV, reporte=None, resumen=None):
        self.sim = sim
        self.cfg: ConfigSimulacion = sim.config
        self.reporte = reporte or {}
        self.resumen = resumen or {}
        self.ancho, self.alto = self.cfg.ancho, self.cfg.alto

        pygame.init()
        pygame.display.set_caption("INFO1167 Robotica | Lab #1 - Simulacion AGV")

        self.cell = 64
        self.map_w = self.ancho * self.cell
        self.map_h = self.alto * self.cell
        self.header_h = 50
        self.panel_w = 380
        self.footer_h = 40
        self.screen_w = self.map_w + self.panel_w
        self.screen_h = self.map_h + self.header_h + self.footer_h

        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        self.clock = pygame.time.Clock()

        # Fuentes
        self.font = pygame.font.SysFont("sfprodisplay", 16)
        self.font_bold = pygame.font.SysFont("sfprodisplay", 16, bold=True)
        self.font_large = pygame.font.SysFont("sfprodisplay", 22, bold=True)
        self.font_small = pygame.font.SysFont("sfprodisplay", 13)
        self.font_mono = pygame.font.SysFont("menlo", 12)

        # Sprites
        self.sprites = crear_sprite_sheet(tam=48)
        self.surf_robots = {}
        self.surf_carrito = None
        self.surf_base = None
        self.surf_destino = None
        self._preparar_sprites()

        # Estado
        self.paused = False
        self.velocidad = 15
        self.ticks_target = self.cfg.max_ticks
        self.ripples = []
        self.log_lines = []
        self.max_log = 20
        self.total_distancia = 0.0
        self.ultimas_posiciones = {r.id: (r.nodo[0], r.nodo[1]) for r in sim.robots}

        # Botones de control
        self.btn_pause = pygame.Rect(self.map_w + 20, 8, 70, 34)
        self.btn_slow = pygame.Rect(self.map_w + 100, 8, 50, 34)
        self.btn_fast = pygame.Rect(self.map_w + 160, 8, 50, 34)
        self.btn_reset = pygame.Rect(self.map_w + 220, 8, 60, 34)

    def _preparar_sprites(self):
        from PIL import Image
        def pil_to_pygame(img):
            mode = img.mode
            data = img.tobytes("raw", mode)
            if mode == "RGBA":
                return pygame.image.fromstring(data, img.size, "RGBA")
            return pygame.image.fromstring(data, img.size, "RGB")

        for color in ["rojo", "azul", "verde", "naranja"]:
            self.surf_robots[color] = pil_to_pygame(self.sprites["robot"][color])
        self.surf_carrito = pil_to_pygame(self.sprites["carrito"])
        self.surf_base = pil_to_pygame(self.sprites["base"])
        self.surf_destino = pil_to_pygame(self.sprites["destino"])

    def _coord(self, gx, gy):
        x = gx * self.cell + self.cell // 2
        y = gy * self.cell + self.cell // 2 + self.header_h
        return x, y

    def _agregar_log(self, mensaje, tipo="info"):
        tick = self.sim.tick if hasattr(self.sim, 'tick') else 0
        self.log_lines.append((tick, mensaje, tipo))
        if len(self.log_lines) > self.max_log:
            self.log_lines.pop(0)

    def _procesar_eventos(self):
        for ev in self.sim.eventos_del_tick:
            tipo = ev.get("tipo", "")
            r = ev.get("robot", "?")
            if tipo == "asignar":
                c = ev.get("carrito", "?")
                self._agregar_log(f"R{r} -> mision: carrito {c}", "info")
            elif tipo == "recoger":
                c = ev.get("carrito", "?")
                self._agregar_log(f"R{r} recogio carrito {c}", "success")
                # Ripple verde en carrito
                carrito = next((car for car in self.sim.carritos if car.id == int(c)), None)
                if carrito:
                    x, y = self._coord(carrito.nodo[0], carrito.nodo[1])
                    self.ripples.append(Ripple(x, y, PALETA["success"], max_radius=35, duration=25))
            elif tipo == "entregar":
                c = ev.get("carrito", "?")
                self._agregar_log(f"R{r} entrego carrito {c}", "accent")
                carrito = next((car for car in self.sim.carritos if car.id == int(c)), None)
                if carrito:
                    x, y = self._coord(carrito.destino[0], carrito.destino[1])
                    self.ripples.append(Ripple(x, y, PALETA["accent"], max_radius=40, duration=30))
            elif tipo == "llegar_base":
                self._agregar_log(f"R{r} en base (cargando)", "warning")
                robot = next((rob for rob in self.sim.robots if rob.id == int(r)), None)
                if robot:
                    x, y = self._coord(robot.base[0], robot.base[1])
                    self.ripples.append(Ripple(x, y, PALETA["warning"], max_radius=30, duration=20))
            elif tipo == "carga_completa":
                self._agregar_log(f"R{r} listo (100%)", "success")

    def _actualizar_metricas(self):
        for r in self.sim.robots:
            nueva = (r.nodo[0], r.nodo[1])
            anterior = self.ultimas_posiciones.get(r.id, nueva)
            dx = nueva[0] - anterior[0]
            dy = nueva[1] - anterior[1]
            self.total_distancia += math.sqrt(dx*dx + dy*dy)
            self.ultimas_posiciones[r.id] = nueva

    # ============================================================
    # DIBUJO
    # ============================================================
    def _dibujar_header(self):
        pygame.draw.rect(self.screen, PALETA["panel"], (0, 0, self.screen_w, self.header_h))
        pygame.draw.line(self.screen, PALETA["panel_border"], (0, self.header_h - 1), (self.screen_w, self.header_h - 1), 1)

        # Titulo
        titulo = self.font_large.render("INFO1167  |  Lab #1  |  Simulacion AGV", True, PALETA["text"])
        self.screen.blit(titulo, (16, 12))

        # Botones
        self._dibujar_boton(self.btn_pause, "PAUSA" if not self.paused else "PLAY", PALETA["accent"])
        self._dibujar_boton(self.btn_slow, "-", PALETA["text_dim"])
        self._dibujar_boton(self.btn_fast, "+", PALETA["text_dim"])
        self._dibujar_boton(self.btn_reset, "RESET", PALETA["danger"])

        # Velocidad
        vel_txt = self.font.render(f"{self.velocidad} tick/s", True, PALETA["text_dim"])
        self.screen.blit(vel_txt, (self.map_w + 290, 16))

        # Estado
        status = "PAUSADO" if self.paused else "EN CURSO" if self.sim.tick < self.ticks_target else "COMPLETADO"
        color = PALETA["warning"] if self.paused else PALETA["success"] if status == "COMPLETADO" else PALETA["accent"]
        st = self.font_bold.render(status, True, color)
        self.screen.blit(st, (self.screen_w - 140, 16))

    def _dibujar_boton(self, rect, texto, color):
        pygame.draw.rect(self.screen, PALETA["panel_border"], rect, border_radius=6)
        pygame.draw.rect(self.screen, color, rect, width=1, border_radius=6)
        txt = self.font.render(texto, True, color)
        tx = rect.x + (rect.width - txt.get_width()) // 2
        ty = rect.y + (rect.height - txt.get_height()) // 2
        self.screen.blit(txt, (tx, ty))

    def _dibujar_mapa(self):
        for j in range(self.alto):
            for i in range(self.ancho):
                rect = pygame.Rect(i * self.cell, j * self.cell + self.header_h, self.cell, self.cell)
                color = PALETA["grid_alt"] if (i + j) % 2 == 0 else PALETA["bg"]
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, PALETA["grid"], rect, 1)

        # Ejes
        for i in range(self.ancho):
            lbl = self.font_small.render(str(i), True, PALETA["text_dim"])
            self.screen.blit(lbl, (i * self.cell + self.cell // 2 - 4, self.header_h - 18))
        for j in range(self.alto):
            lbl = self.font_small.render(str(j), True, PALETA["text_dim"])
            self.screen.blit(lbl, (4, j * self.cell + self.cell // 2 + self.header_h - 6))

    def _dibujar_rutas(self):
        for r in self.sim.robots:
            if not r.ruta or len(r.ruta) < 2:
                continue
            color = PALETA["robot_colors"].get(r.color, (128, 128, 128))
            # Dibujar linea punteada a lo largo de la ruta restante
            puntos = [self._coord(n[0], n[1]) for n in r.ruta[r.paso_ruta:]]
            if len(puntos) >= 2:
                for i in range(len(puntos) - 1):
                    self._dibujar_linea_punteada(puntos[i], puntos[i+1], color, 2)

    def _dibujar_linea_punteada(self, p1, p2, color, width=2, dash_len=6, gap_len=4):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0:
            return
        dx, dy = dx / dist, dy / dist
        pos = 0
        dibujando = True
        while pos < dist:
            long = dash_len if dibujando else gap_len
            if pos + long > dist:
                long = dist - pos
            start = (p1[0] + dx * pos, p1[1] + dy * pos)
            end = (p1[0] + dx * (pos + long), p1[1] + dy * (pos + long))
            if dibujando:
                pygame.draw.line(self.screen, color, start, end, width)
            pos += long
            dibujando = not dibujando

    def _dibujar_elementos(self):
        # Bases
        for r in self.sim.robots:
            bx, by = self._coord(r.base[0], r.base[1])
            self.screen.blit(self.surf_base, (bx - 24, by - 24))
            # Label
            lbl = self.font_small.render(f"B{r.id}", True, PALETA["text_dim"])
            self.screen.blit(lbl, (bx - 8, by + 20))

        # Destinos
        for c in self.sim.carritos:
            if c.entregado:
                continue
            dx, dy = self._coord(c.destino[0], c.destino[1])
            self.screen.blit(self.surf_destino, (dx - 20, dy - 20))
            # Parpadeo sutil si esta siendo buscado
            robot_asignado = next((r for r in self.sim.robots if r.carrito_asignado == c.id), None)
            if robot_asignado:
                alpha = int(60 + 40 * math.sin(pygame.time.get_ticks() / 300))
                s = pygame.Surface((44, 44), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 255, alpha), (22, 22), 22, 2)
                self.screen.blit(s, (dx - 22, dy - 22))

        # Carritos
        for c in self.sim.carritos:
            if c.entregado:
                continue
            x, y = self._coord(c.nodo[0], c.nodo[1])
            # Borde de color si esta asignado
            if c.color_original:
                ccolor = PALETA["robot_colors"].get(c.color_original, (128, 128, 128))
                pygame.draw.circle(self.screen, ccolor, (x, y), 18, 2)
            self.screen.blit(pygame.transform.scale(self.surf_carrito, (32, 32)), (x - 16, y - 16))

        # Robots
        for r in self.sim.robots:
            x, y = self._coord(r.nodo[0], r.nodo[1])
            surf = self.surf_robots.get(r.color, self.surf_robots["rojo"])
            rot = -math.degrees(r.angulo)
            rot_surf = pygame.transform.rotate(surf, rot)
            rect = rot_surf.get_rect(center=(x, y))
            self.screen.blit(rot_surf, rect.topleft)

            # Glow de estado
            estado_color = {
                EstadoRobot.EN_BASE: PALETA["text_dim"],
                EstadoRobot.BUSCANDO_CARRITO: PALETA["accent"],
                EstadoRobot.LLEVANDO_CARRITO: PALETA["success"],
                EstadoRobot.VOLVIENDO_BASE: PALETA["warning"],
                EstadoRobot.CARGANDO: PALETA["danger"],
            }.get(r.estado, (128, 128, 128))
            pygame.draw.circle(self.screen, estado_color, (x, y), 26, 2)

            # ID del robot
            id_surf = self.font_small.render(f"R{r.id}", True, PALETA["text"])
            self.screen.blit(id_surf, (x - 8, y - 36))

    def _dibujar_ripples(self):
        for rip in self.ripples:
            rip.draw(self.screen)

    def _dibujar_panel(self):
        x0 = self.map_w
        pygame.draw.rect(self.screen, PALETA["panel"], (x0, self.header_h, self.panel_w, self.map_h + self.footer_h))
        pygame.draw.line(self.screen, PALETA["panel_border"], (x0, self.header_h), (x0, self.screen_h), 2)

        x = x0 + 16
        y = self.header_h + 12

        # --- Stats principales ---
        stats = [
            ("Tick", f"{self.sim.tick}/{self.ticks_target}", PALETA["accent"]),
            ("Entregas", str(self.sim.entregas_completadas), PALETA["success"]),
            ("Throughput", f"{self.sim.entregas_completadas / max(1, self.sim.tick):.3f} e/tick", PALETA["warning"]),
        ]
        for label, val, col in stats:
            pygame.draw.rect(self.screen, PALETA["bg"], (x, y, 100, 44), border_radius=6)
            pygame.draw.rect(self.screen, PALETA["panel_border"], (x, y, 100, 44), 1, border_radius=6)
            l = self.font_small.render(label, True, PALETA["text_dim"])
            v = self.font_bold.render(val, True, col)
            self.screen.blit(l, (x + 8, y + 4))
            self.screen.blit(v, (x + 8, y + 20))
            x += 110
        x = x0 + 16
        y += 56

        # --- Metricas adicionales ---
        pygame.draw.rect(self.screen, PALETA["bg"], (x, y, 334, 80), border_radius=6)
        pygame.draw.rect(self.screen, PALETA["panel_border"], (x, y, 334, 80), 1, border_radius=6)

        avg_batt = sum(r.bateria for r in self.sim.robots) / max(1, len(self.sim.robots))
        metricas = [
            ("Distancia total", f"{self.total_distancia:.1f} celdas"),
            ("Bateria promedio", f"{avg_batt:.1f}%"),
            ("Algoritmo", str(self.cfg.modo_ruta)),
        ]
        my = y + 8
        for label, val in metricas:
            l = self.font_small.render(label + ":", True, PALETA["text_dim"])
            v = self.font.render(val, True, PALETA["text"])
            self.screen.blit(l, (x + 10, my))
            self.screen.blit(v, (x + 160, my))
            my += 22
        y += 92

        # --- Baterias ---
        pygame.draw.rect(self.screen, PALETA["bg"], (x, y, 334, 110), border_radius=6)
        pygame.draw.rect(self.screen, PALETA["panel_border"], (x, y, 334, 110), 1, border_radius=6)
        self.screen.blit(self.font_bold.render("Baterias", True, PALETA["text"]), (x + 10, y + 6))
        by = y + 26
        for r in self.sim.robots:
            c = PALETA["robot_colors"].get(r.color, (128, 128, 128))
            pygame.draw.rect(self.screen, c, (x + 10, by, 8, 8), border_radius=2)
            txt = self.font.render(f"R{r.id}", True, PALETA["text"])
            self.screen.blit(txt, (x + 22, by - 2))
            pct = max(0, min(100, int(r.bateria)))
            bar_w = 120
            pygame.draw.rect(self.screen, PALETA["panel_border"], (x + 55, by + 2, bar_w, 8), border_radius=3)
            bc = PALETA["success"] if pct >= 50 else PALETA["warning"] if pct >= 20 else PALETA["danger"]
            pygame.draw.rect(self.screen, bc, (x + 55, by + 2, int(bar_w * pct / 100), 8), border_radius=3)
            ptxt = self.font_small.render(f"{pct}%", True, PALETA["text_dim"])
            self.screen.blit(ptxt, (x + 55 + bar_w + 8, by - 2))
            by += 20
        y += 120

        # --- Estados ---
        pygame.draw.rect(self.screen, PALETA["bg"], (x, y, 334, 70), border_radius=6)
        pygame.draw.rect(self.screen, PALETA["panel_border"], (x, y, 334, 70), 1, border_radius=6)
        self.screen.blit(self.font_bold.render("Estados", True, PALETA["text"]), (x + 10, y + 6))
        estados = []
        for r in self.sim.robots:
            e = r.estado.value.replace("_", " ").title()
            c = PALETA["robot_colors"].get(r.color, (128, 128, 128))
            estados.append((f"R{r.id}: {e}", c))
        ey = y + 26
        for i, (texto, col) in enumerate(estados):
            pygame.draw.rect(self.screen, col, (x + 10 + (i % 2) * 160, ey + (i // 2) * 22, 6, 6), border_radius=1)
            self.screen.blit(self.font_small.render(texto, True, PALETA["text"]), (x + 20 + (i % 2) * 160, ey + (i // 2) * 22 - 3))
        y += 82

        # --- Requisitos (si hay reporte) ---
        if self.reporte.get("checks"):
            pygame.draw.rect(self.screen, PALETA["bg"], (x, y, 334, 110), border_radius=6)
            pygame.draw.rect(self.screen, PALETA["panel_border"], (x, y, 334, 110), 1, border_radius=6)
            self.screen.blit(self.font_bold.render("Requisitos", True, PALETA["text"]), (x + 10, y + 6))
            ry = y + 26
            for c in self.reporte["checks"]:
                ok = c.get("ok", False)
                col = PALETA["success"] if ok else PALETA["danger"]
                icono = "✓" if ok else "✗"
                txt = self.font_small.render(f"{icono} {c['id']}", True, col)
                self.screen.blit(txt, (x + 10, ry))
                ry += 16
            pct = self.reporte.get("porcentaje", 0)
            ptxt = self.font_bold.render(f"Aprobado: {pct}%", True, PALETA["success"] if pct == 100 else PALETA["warning"])
            self.screen.blit(ptxt, (x + 10, ry + 2))
            y += 118

        # --- Log ---
        log_h = self.screen_h - y - self.footer_h - 8
        if log_h > 60:
            pygame.draw.rect(self.screen, PALETA["bg"], (x, y, 334, log_h), border_radius=6)
            pygame.draw.rect(self.screen, PALETA["panel_border"], (x, y, 334, log_h), 1, border_radius=6)
            self.screen.blit(self.font_bold.render("Eventos", True, PALETA["text"]), (x + 10, y + 6))
            ly = y + 26
            for tick, msg, tipo in self.log_lines[-12:]:
                colores = {
                    "info": PALETA["accent"],
                    "success": PALETA["success"],
                    "accent": PALETA["accent"],
                    "warning": PALETA["warning"],
                    "dim": PALETA["text_dim"],
                }
                c = colores.get(tipo, PALETA["text_dim"])
                ts = self.font_mono.render(f"[{tick:04d}]", True, PALETA["text_dim"])
                m = self.font_small.render(msg, True, c)
                self.screen.blit(ts, (x + 10, ly))
                self.screen.blit(m, (x + 65, ly))
                ly += 16

    def _dibujar_footer(self):
        y = self.screen_h - self.footer_h
        pygame.draw.rect(self.screen, PALETA["panel"], (0, y, self.screen_w, self.footer_h))
        pygame.draw.line(self.screen, PALETA["panel_border"], (0, y), (self.screen_w, y), 1)
        txt = self.font_small.render("[ESPACIO] Pausa/Play  |  [+] Mas rapido  |  [-] Mas lento  |  [R] Reset  |  [ESC] Salir", True, PALETA["text_dim"])
        self.screen.blit(txt, (16, y + 12))

    def _manejar_click(self, pos):
        if self.btn_pause.collidepoint(pos):
            self.paused = not self.paused
        elif self.btn_slow.collidepoint(pos):
            self.velocidad = max(5, self.velocidad - 3)
        elif self.btn_fast.collidepoint(pos):
            self.velocidad = min(60, self.velocidad + 3)
        elif self.btn_reset.collidepoint(pos):
            self._reset()

    def _reset(self):
        self.sim = SimulacionAGV(self.cfg)
        self.ripples.clear()
        self.log_lines.clear()
        self.total_distancia = 0.0
        self.ultimas_posiciones = {r.id: (r.nodo[0], r.nodo[1]) for r in self.sim.robots}
        self.paused = False

    # ============================================================
    # LOOP PRINCIPAL
    # ============================================================
    def animar(self, ticks=None, velocidad=None):
        if ticks is not None:
            self.ticks_target = ticks
        if velocidad is not None:
            self.velocidad = velocidad

        running = True
        tick_delay = int(1000 / self.velocidad)
        last_tick = pygame.time.get_ticks()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_UP or event.key == pygame.K_PLUS:
                        self.velocidad = min(60, self.velocidad + 3)
                        tick_delay = int(1000 / self.velocidad)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_MINUS:
                        self.velocidad = max(5, self.velocidad - 3)
                        tick_delay = int(1000 / self.velocidad)
                    elif event.key == pygame.K_r:
                        self._reset()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._manejar_click(event.pos)

            now = pygame.time.get_ticks()
            if not self.paused and now - last_tick >= tick_delay and self.sim.tick < self.ticks_target:
                self.sim.paso()
                self._procesar_eventos()
                self._actualizar_metricas()
                last_tick = now

            # Actualizar ripples
            for rip in self.ripples:
                rip.update()
            self.ripples = [r for r in self.ripples if r.alive]

            # Render
            self.screen.fill(PALETA["bg"])
            self._dibujar_header()
            self._dibujar_mapa()
            self._dibujar_rutas()
            self._dibujar_elementos()
            self._dibujar_ripples()
            self._dibujar_panel()
            self._dibujar_footer()
            pygame.display.flip()
            self.clock.tick(60)

            if self.sim.tick >= self.ticks_target and not self.paused:
                self.paused = True
                self._agregar_log("=== Simulacion completada ===", "success")

        pygame.quit()
