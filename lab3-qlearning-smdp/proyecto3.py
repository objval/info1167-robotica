import pygame, sys, random
import numpy as np
from collections import defaultdict
from mapa import GRID, ROWS, COLS, ACTIONS, get_goal, get_states, move, get_random_start
from framework import *

class AgenteQLearning:
    def __init__(self):
        self.q = defaultdict(float)
        self.estados = get_states()
        self.meta = get_goal()
        self.episodios = 0
        self.recompensas = []

    def mejor_accion(self, s):
        mejor, mejor_q = None, float("-inf")
        for a in ACTIONS:
            if self.q[(s, a)] > mejor_q:
                mejor_q, mejor = self.q[(s, a)], a
        return mejor

    def max_q(self, s):
        return max((self.q[(s, a)] for a in ACTIONS), default=0.0)

    def elegir(self, s, epsilon):
        if random.random() < epsilon:
            return random.choice(ACTIONS)
        return self.mejor_accion(s)

    def mover(self, s, a):
        if random.random() < 0.9:
            return move(s, a)
        return s

    def tiempo_accion(self, a):
        mu, sigma = {
            "Norte": (2, 0.2),
            "Sur": (2, 0.2),
            "Este": (3, 0.3),
            "Oeste": (3, 0.3),
        }[a]
        return max(0.1, np.random.normal(mu, sigma))

    def entrenar_episodio(self, gamma, alpha, epsilon):
        s = get_random_start()
        total = 0
        for _ in range(200):
            a = self.elegir(s, epsilon)
            sig = self.mover(s, a)
            r = -1.0 + (10.0 if sig == self.meta else 0.0)
            tau = self.tiempo_accion(a)
            desc = gamma**tau
            viejo = self.q[(s, a)]
            self.q[(s, a)] = viejo + alpha * (r + desc * self.max_q(sig) - viejo)
            total += r
            s = sig
            if s == self.meta:
                break
        self.episodios += 1
        self.recompensas.append(total)

    def politica(self):
        return {
            s: ("META" if s == self.meta else self.mejor_accion(s))
            for s in self.estados
        }

    def valores(self):
        return {s: self.max_q(s) for s in self.estados}

    def promedio(self, n=30):
        return np.mean(self.recompensas[-n:]) if self.recompensas else 0

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Proyecto #3 — Q-Learning SMDP")
    reloj = pygame.time.Clock()
    agente = AgenteQLearning()
    pos_ini = get_random_start()
    robot = pos_ini
    rastro = []
    pausado = False
    entrenando = False
    meta_entreno = 0
    pasos = 0
    tiempo = 0.0
    tick_anim = 0
    sx = ANCHO_GRILLA + 15
    sy = MARGEN_SUP + 10
    slider_gamma = Slider(sx, sy, 230, 14, 0.5, 0.99, 0.97, "Gamma", "{:.2f}")
    sy += 42
    slider_alpha = Slider(
        sx, sy, 230, 14, 0.01, 0.5, 0.10, "Alpha (aprendizaje)", "{:.2f}"
    )
    sy += 42
    slider_epsilon = Slider(
        sx, sy, 230, 14, 0.01, 1.0, 0.30, "Epsilon (exploracion)", "{:.2f}"
    )
    sy += 42
    slider_velocidad = Slider(
        sx, sy, 230, 14, 100, 800, 350, "Velocidad (ms)", "{:.0f}"
    )
    sy += 42
    toggle_valores = Toggle(sx, sy, "Valores", True)
    toggle_flechas = Toggle(sx + 120, sy, "Flechas", True)
    sy += 35

    def reiniciar():
        nonlocal agente, robot, rastro, pasos, tiempo, pausado, entrenando, pos_ini
        agente = AgenteQLearning()
        pos_ini = get_random_start()
        robot = pos_ini
        rastro = []
        pasos = 0
        tiempo = 0.0
        pausado = False
        entrenando = False

    def entrenar(n):
        nonlocal entrenando, meta_entreno
        entrenando = True
        meta_entreno = agente.episodios + n

    def animar():
        nonlocal robot, rastro, pasos, tiempo, pausado, entrenando, tick_anim, pos_ini
        pos_ini = get_random_start()
        robot = pos_ini
        rastro = []
        pasos = 0
        tiempo = 0.0
        pausado = False
        entrenando = False
        tick_anim = 0

    btn_entreno = Boton(sx, sy, 90, 28, "Entrenar", lambda: entrenar(500))
    btn_auto = Boton(sx + 100, sy, 70, 28, "Auto", lambda: entrenar(50000))
    btn_reset = Boton(sx + 180, sy, 65, 28, "Reset", reiniciar)
    sy += 35
    btn_animar = Boton(sx, sy, 90, 28, "Animar", animar)
    widgets = [
        slider_gamma,
        slider_alpha,
        slider_epsilon,
        slider_velocidad,
        toggle_valores,
        toggle_flechas,
        btn_entreno,
        btn_auto,
        btn_reset,
        btn_animar,
    ]
    corriendo = True
    while corriendo:
        dt = reloj.tick(30)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                corriendo = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                    corriendo = False
                elif ev.key == pygame.K_RETURN:
                    entrenar(500)
                elif ev.key == pygame.K_t:
                    entrenar(50000)
                elif ev.key == pygame.K_a:
                    animar()
                elif ev.key == pygame.K_SPACE:
                    pausado = not pausado
                elif ev.key == pygame.K_r:
                    reiniciar()
            for w in widgets:
                w.handle_event(ev)
        if entrenando and agente.episodios < meta_entreno:
            eps = slider_epsilon.valor
            for _ in range(20):
                if agente.episodios < meta_entreno:
                    agente.entrenar_episodio(
                        slider_gamma.valor, slider_alpha.valor, eps
                    )
                else:
                    break
            if (
                meta_entreno > 40000
                and agente.episodios > 300
                and len(agente.recompensas) > 60
            ):
                rec = np.mean(agente.recompensas[-30:])
                ant = np.mean(agente.recompensas[-60:-30])
                if abs(rec - ant) < 0.5:
                    entrenando = False
                    print(f"Convergio en {agente.episodios} ep, recompensa={rec:.1f}")
        elif entrenando and agente.episodios >= meta_entreno:
            entrenando = False
        if not entrenando and not pausado and robot != get_goal():
            tick_anim += dt
            if tick_anim >= slider_velocidad.valor:
                tick_anim = 0
                pi = agente.politica()
                accion = pi.get(robot)
                if accion and accion != "META":
                    nueva = agente.mover(robot, accion)
                    if nueva != robot:
                        rastro.append(robot)
                        if len(rastro) > 25:
                            rastro.pop(0)
                        pasos += 1
                        tau = agente.tiempo_accion(accion)
                        tiempo += tau
                    robot = nueva
        pantalla.fill(C["fondo"])
        pygame.draw.rect(
            pantalla, C["panel"], (ANCHO_GRILLA + 2, 0, PANEL_LATERAL, ALTO)
        )
        pygame.draw.line(
            pantalla, C["borde"], (ANCHO_GRILLA + 2, 0), (ANCHO_GRILLA + 2, ALTO), 1
        )
        dibujar_header(
            pantalla, f"Proyecto #3 — Q-Learning SMDP (alpha={slider_alpha.valor:.2f})"
        )
        val = agente.valores()
        pol = agente.politica()
        dibujar_grilla(
            pantalla,
            val,
            pol,
            robot,
            rastro,
            pos_ini,
            toggle_valores.activo,
            toggle_flechas.activo,
        )
        for w in widgets:
            w.draw(pantalla)
        f = pygame.font.SysFont("consolas", 13)
        fb = pygame.font.SysFont("consolas", 13, bold=True)
        y = sy + 40
        for label, valor in [
            ("Episodios", str(agente.episodios)),
            ("Recompensa", f"{agente.promedio():.1f}"),
            ("Pasos", str(pasos)),
            ("Tiempo", f"{tiempo:.1f}s"),
            ("Inicio", str(pos_ini)),
        ]:
            pantalla.blit(f.render(label, True, C["dim"]), (sx, y))
            pantalla.blit(fb.render(valor, True, C["texto"]), (sx + 100, y))
            y += 20
        if entrenando:
            eclr, etxt = C["warn"], "ENTRENANDO..."
        elif pausado:
            eclr, etxt = C["warn"], "PAUSADO"
        else:
            eclr, etxt = C["ok"], "LISTO"
        pantalla.blit(fb.render(etxt, True, eclr), (sx, y + 5))
        y += 25
        if entrenando:
            bw = 230
            pygame.draw.rect(pantalla, C["barra_bg"], (sx, y, bw, 12), border_radius=3)
            prog = min(1.0, agente.episodios / max(1, 500))
            if prog > 0:
                pygame.draw.rect(
                    pantalla,
                    C["barra_fg"],
                    (sx, y, int(bw * prog), 12),
                    border_radius=3,
                )
            pantalla.blit(
                f.render(f"{agente.episodios} ep", True, C["texto"]), (sx, y + 15)
            )
            y += 30
        y += 8
        dibujar_grafico(pantalla, sx, y, 230, 60, agente.recompensas)
        dibujar_footer(
            pantalla,
            "ENTER=Entrenar  T=Auto  A=Animar  R=Reset  Q=Salir  |  Sliders ajustables",
        )
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
