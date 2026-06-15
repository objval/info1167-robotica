import pygame, sys, random, numpy as np

from mapa import GRID, ROWS, COLS, ACTIONS, get_goal, get_states, move, get_random_start

CELDA = 78

GAP = 3

MARGEN_SUP = 48

MARGEN_INF = 36

PANEL_LATERAL = 260

ANCHO_GRILLA = COLS * (CELDA + GAP) + GAP

ALTO_GRILLA = ROWS * (CELDA + GAP) + GAP

ANCHO = ANCHO_GRILLA + PANEL_LATERAL + 4

ALTO = MARGEN_SUP + ALTO_GRILLA + MARGEN_INF

C = {

    'fondo':      (18, 18, 24),

    'panel':      (22, 22, 32),

    'borde':      (45, 45, 60),

    'celda':      (50, 55, 75),

    'vacio':      (30, 30, 40),

    'muro':       (25, 25, 32),

    'meta':       (30, 140, 50),

    'robot':      (210, 55, 55),

    'flecha':     (200, 200, 80),

    'rastro':     (70, 50, 120),

    'inicio':     (100, 80, 30),

    'val_bajo':   (40, 45, 80),

    'val_alto':   (85, 165, 250),

    'texto':      (210, 210, 215),

    'dim':        (120, 120, 135),

    'accent':     (80, 140, 255),

    'ok':         (80, 220, 80),

    'warn':       (255, 200, 50),

    'barra_bg':   (35, 35, 48),

    'barra_fg':   (70, 150, 240),

    'slider_bg':  (40, 40, 55),

    'slider_fg':  (80, 140, 255),

    'slider_knob':(120, 180, 255),

    'btn':        (45, 50, 70),

    'btn_hover':  (60, 65, 90),

    'btn_active': (70, 80, 120),

}

class Slider:

    def __init__(self, x, y, w, h, min_val, max_val, valor_ini, label, fmt="{:.2f}"):

        self.rect = pygame.Rect(x, y, w, h)

        self.min_val = min_val

        self.max_val = max_val

        self.valor = valor_ini

        self.label = label

        self.fmt = fmt

        self.arrastrando = False

    def handle_event(self, ev):

        if ev.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(ev.pos):

            self.arrastrando = True

            self._update(ev.pos[0])

        elif ev.type == pygame.MOUSEBUTTONUP:

            self.arrastrando = False

        elif ev.type == pygame.MOUSEMOTION and self.arrastrando:

            self._update(ev.pos[0])

    def _update(self, mx):

        ratio = (mx - self.rect.x) / self.rect.w

        ratio = max(0, min(1, ratio))

        self.valor = self.min_val + ratio * (self.max_val - self.min_val)

    def draw(self, surf):

        f = pygame.font.SysFont('consolas', 12)

        txt = f"{self.label}: {self.fmt.format(self.valor)}"

        surf.blit(f.render(txt, True, C['texto']), (self.rect.x, self.rect.y - 16))

        pygame.draw.rect(surf, C['slider_bg'], self.rect, border_radius=3)

        ratio = (self.valor - self.min_val) / (self.max_val - self.min_val)

        fill_w = int(self.rect.w * ratio)

        if fill_w > 0:

            pygame.draw.rect(surf, C['slider_fg'], (self.rect.x, self.rect.y, fill_w, self.rect.h), border_radius=3)

        knob_x = self.rect.x + fill_w

        knob_rect = pygame.Rect(knob_x - 5, self.rect.y - 3, 10, self.rect.h + 6)

        pygame.draw.rect(surf, C['slider_knob'], knob_rect, border_radius=4)

class Boton:

    def __init__(self, x, y, w, h, texto, accion=None):

        self.rect = pygame.Rect(x, y, w, h)

        self.texto = texto

        self.accion = accion

        self.hover = False

    def handle_event(self, ev):

        if ev.type == pygame.MOUSEMOTION:

            self.hover = self.rect.collidepoint(ev.pos)

        elif ev.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(ev.pos):

            if self.accion:

                self.accion()

    def draw(self, surf):

        color = C['btn_hover'] if self.hover else C['btn']

        pygame.draw.rect(surf, color, self.rect, border_radius=5)

        pygame.draw.rect(surf, C['borde'], self.rect, 1, border_radius=5)

        f = pygame.font.SysFont('consolas', 13, bold=True)

        txt = f.render(self.texto, True, C['texto'])

        surf.blit(txt, (self.rect.x + self.rect.w//2 - txt.get_width()//2,

                        self.rect.y + self.rect.h//2 - txt.get_height()//2))

class Toggle:

    def __init__(self, x, y, label, valor_ini=True):

        self.x = x

        self.y = y

        self.label = label

        self.activo = valor_ini

        self.rect = pygame.Rect(x, y, 36, 18)

    def handle_event(self, ev):

        if ev.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(ev.pos):

            self.activo = not self.activo

    def draw(self, surf):

        f = pygame.font.SysFont('consolas', 12)

        surf.blit(f.render(self.label, True, C['texto']), (self.x + 42, self.y + 1))

        bg = C['ok'] if self.activo else C['slider_bg']

        pygame.draw.rect(surf, bg, self.rect, border_radius=9)

        knob_x = self.rect.x + (20 if self.activo else 4)

        pygame.draw.circle(surf, (220, 220, 230), (knob_x, self.rect.y + 9), 6)

def coords_pixel(fila, col):

    x = GAP + col * (CELDA + GAP)

    y = MARGEN_SUP + GAP + fila * (CELDA + GAP)

    return x, y

def dibujar_flecha(sup, fila, col, accion):

    cx, cy = coords_pixel(fila, col)

    cx += CELDA // 2; cy += CELDA // 2

    s = CELDA // 3

    formas = {

        'Norte': [(cx, cy-s), (cx-s//2, cy+s//3), (cx+s//2, cy+s//3)],

        'Sur':   [(cx, cy+s), (cx-s//2, cy-s//3), (cx+s//2, cy-s//3)],

        'Este':  [(cx+s, cy), (cx-s//3, cy-s//2), (cx-s//3, cy+s//2)],

        'Oeste': [(cx-s, cy), (cx+s//3, cy-s//2), (cx+s//3, cy+s//2)],

    }

    if accion in formas:

        pygame.draw.polygon(sup, C['flecha'], formas[accion])

def dibujar_grilla(sup, valores, politica, pos_robot, rastro, pos_ini,

                   mostrar_valores=True, mostrar_flechas=True):

    meta = get_goal()

    if valores:

        vmin = min(valores.values())

        vmax = max(valores.values())

        vran = vmax - vmin if vmax != vmin else 1

    else:

        vmin, vmax, vran = 0, 1, 1

    f_ch = pygame.font.SysFont('consolas', 12)

    f_gr = pygame.font.SysFont('consolas', 15, bold=True)

    for r in range(ROWS):

        for c in range(COLS):

            x, y = coords_pixel(r, c)

            celda = GRID[r][c]

            est = (r, c)

            if celda == 'X':

                color = C['muro']

            elif celda == 'M':

                color = C['meta']

            elif est == pos_robot:

                color = C['robot']

            elif est in rastro:

                idx = len(rastro) - list(rastro).index(est)

                fade = max(0.25, 1.0 - idx * 0.1)

                color = tuple(int(v * fade) for v in C['rastro'])

            elif est == pos_ini and est != pos_robot:

                color = C['inicio']

            elif celda == 'S' and valores:

                norm = max(0, min(1, (valores.get(est, 0) - vmin) / vran))

                color = tuple(int(C['val_bajo'][i] + (C['val_alto'][i] - C['val_bajo'][i]) * norm) for i in range(3))

            else:

                color = C['vacio']

            pygame.draw.rect(sup, color, (x, y, CELDA, CELDA), border_radius=4)

            if mostrar_valores and celda in ('S', 'M') and est in valores:

                txt = f_ch.render(f"{valores[est]:.1f}", True, (170, 170, 185))

                sup.blit(txt, (x + CELDA//2 - txt.get_width()//2, y + 4))

            if mostrar_flechas and celda == 'S' and politica and est in politica and politica[est] != 'META':

                dibujar_flecha(sup, r, c, politica[est])

            if celda == 'M':

                txt = f_gr.render("META", True, (255, 255, 255))

                sup.blit(txt, (x + CELDA//2 - txt.get_width()//2, y + CELDA//2 - 7))

            elif est == pos_ini and celda == 'S' and est != pos_robot:

                txt = f_gr.render("INI", True, (255, 255, 200))

                sup.blit(txt, (x + CELDA//2 - txt.get_width()//2, y + CELDA//2 - 7))

    if pos_robot:

        rx, ry = pos_robot

        cx, cy = coords_pixel(rx, ry)

        cx += CELDA // 2; cy += CELDA // 2

        rad = CELDA // 3

        pygame.draw.circle(sup, C['robot'], (cx, cy), rad)

        pygame.draw.circle(sup, (255, 255, 255), (cx, cy), rad, 2)

        pygame.draw.circle(sup, (255, 255, 255), (cx - 8, cy - 5), 4)

        pygame.draw.circle(sup, (255, 255, 255), (cx + 8, cy - 5), 4)

def dibujar_header(sup, titulo):

    f = pygame.font.SysFont('consolas', 18, bold=True)

    sup.blit(f.render(titulo, True, C['texto']), (8, 14))

def dibujar_footer(sup, linea):

    f = pygame.font.SysFont('consolas', 11)

    sup.blit(f.render(linea, True, C['dim']), (8, ALTO - MARGEN_INF + 8))

def dibujar_grafico(sup, x, y, w, h, datos, color=C['barra_fg']):

    pygame.draw.rect(sup, C['barra_bg'], (x, y, w, h), border_radius=3)

    if len(datos) < 2:

        return

    n = min(len(datos), 200)

    d = datos[-n:]

    ventana = max(1, len(d) // 30)

    suav = [np.mean(d[max(0, i-ventana):i+1]) for i in range(len(d))]

    rmin, rmax = min(suav), max(suav)

    rran = rmax - rmin if rmax != rmin else 1

    puntos = []

    for i, v in enumerate(suav):

        px = x + 2 + int(i / max(1, len(suav)-1) * (w - 4))

        py = y + h - 3 - int((v - rmin) / rran * (h - 6))

        puntos.append((px, py))

    if len(puntos) > 1:

        pygame.draw.lines(sup, color, False, puntos, 2)
