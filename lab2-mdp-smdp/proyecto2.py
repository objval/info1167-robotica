import pygame, sys, random
import numpy as np
from mapa import GRID, ROWS, COLS, ACTIONS, get_goal, get_states, move, get_random_start
from framework import *

def calcular_politica(gamma, modo="MDP"):
    estados = get_states()
    meta = get_goal()
    V = {s: 0.0 for s in estados}
    for _ in range(500):
        max_cambio = 0
        nuevos = {}
        for s in estados:
            if s == meta:
                nuevos[meta] = 10.0
                continue
            mejor = float("-inf")
            for acc in ACTIONS:
                sig = move(s, acc)
                r = -1.0 + (10.0 if sig == meta else 0.0)
                if modo == "SMDP":
                    mu, sigma = {
                        "Norte": (2, 0.2),
                        "Sur": (2, 0.2),
                        "Este": (3, 0.3),
                        "Oeste": (3, 0.3),
                    }[acc]
                    desc = np.mean(
                        [
                            gamma ** max(0.1, np.random.normal(mu, sigma))
                            for _ in range(20)
                        ]
                    )
                else:
                    desc = gamma
                val = 0.9 * (r + desc * V[sig]) + 0.1 * (-1.0 + desc * V[s])
                mejor = max(mejor, val)
            nuevos[s] = mejor
            max_cambio = max(max_cambio, abs(nuevos[s] - V[s]))
        V = nuevos
        if max_cambio < 0.001:
            break
    pi = {}
    for s in estados:
        if s == meta:
            pi[s] = "META"
            continue
        ba, bv = None, float("-inf")
        for acc in ACTIONS:
            sig = move(s, acc)
            r = -1.0 + (10.0 if sig == meta else 0.0)
            if modo == "SMDP":
                mu, sigma = {
                    "Norte": (2, 0.2),
                    "Sur": (2, 0.2),
                    "Este": (3, 0.3),
                    "Oeste": (3, 0.3),
                }[acc]
                desc = np.mean(
                    [gamma ** max(0.1, np.random.normal(mu, sigma)) for _ in range(20)]
                )
            else:
                desc = gamma
            val = 0.9 * (r + desc * V[sig]) + 0.1 * (-1.0 + desc * V[s])
            if val > bv:
                bv, ba = val, acc
        pi[s] = ba
    return V, pi

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Proyecto #2 — MDP / SMDP")
    reloj = pygame.time.Clock()
    modo = "MDP"
    pos_ini = get_random_start()
    robot = pos_ini
    rastro = []
    pausado = False
    pasos = 0
    tiempo = 0.0
    tick = 0
    sx = ANCHO_GRILLA + 15
    sy = MARGEN_SUP + 10
    slider_gamma = Slider(sx, sy, 230, 14, 0.5, 0.99, 0.97, "Gamma", "{:.2f}")
    sy += 45
    slider_velocidad = Slider(
        sx, sy, 230, 14, 100, 800, 350, "Velocidad (ms)", "{:.0f}"
    )
    sy += 45
    toggle_valores = Toggle(sx, sy, "Valores", True)
    toggle_flechas = Toggle(sx + 120, sy, "Flechas", True)
    sy += 35
    V_cache = {}
    pi_cache = {}
    modo_cache = None
    gamma_cache = None

    def recalcular():
        nonlocal V_cache, pi_cache, modo_cache, gamma_cache
        gamma_val = slider_gamma.valor
        if modo != modo_cache or abs(gamma_val - (gamma_cache or 0)) > 0.001:
            V_cache, pi_cache = calcular_politica(gamma_val, modo)
            modo_cache = modo
            gamma_cache = gamma_val

    def reiniciar():
        nonlocal robot, rastro, pasos, tiempo, pausado, tick, pos_ini
        pos_ini = get_random_start()
        robot = pos_ini
        rastro = []
        pasos = 0
        tiempo = 0.0
        pausado = False
        tick = 0

    def set_modo(m):
        nonlocal modo
        modo = m
        reiniciar()

    btn_mdp = Boton(sx, sy, 70, 28, "MDP", lambda: set_modo("MDP"))
    btn_smdp = Boton(sx + 80, sy, 70, 28, "SMDP", lambda: set_modo("SMDP"))
    btn_reset = Boton(sx + 160, sy, 65, 28, "Reset", reiniciar)
    sy += 40
    sy += 10
    stat_y = sy
    widgets = [
        slider_gamma,
        slider_velocidad,
        toggle_valores,
        toggle_flechas,
        btn_mdp,
        btn_smdp,
        btn_reset,
    ]
    set_modo("MDP")
    corriendo = True
    while corriendo:
        dt = reloj.tick(30)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                corriendo = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                    corriendo = False
                elif ev.key == pygame.K_1:
                    set_modo("MDP")
                elif ev.key == pygame.K_2:
                    set_modo("SMDP")
                elif ev.key == pygame.K_SPACE:
                    pausado = not pausado
                elif ev.key == pygame.K_r:
                    reiniciar()
            for w in widgets:
                w.handle_event(ev)
        recalcular()
        if not pausado and robot != get_goal():
            tick += dt
            vel = slider_velocidad.valor
            if tick >= vel:
                tick = 0
                accion = pi_cache.get(robot)
                if accion and accion != "META":
                    if random.random() < 0.9:
                        nueva = move(robot, accion)
                    else:
                        nueva = robot
                    if nueva != robot:
                        rastro.append(robot)
                        if len(rastro) > 25:
                            rastro.pop(0)
                        pasos += 1
                        if modo == "SMDP":
                            mu, sigma = {
                                "Norte": (2, 0.2),
                                "Sur": (2, 0.2),
                                "Este": (3, 0.3),
                                "Oeste": (3, 0.3),
                            }[accion]
                            tiempo += max(0.1, np.random.normal(mu, sigma))
                        else:
                            tiempo += 1.0
                    robot = nueva
        pantalla.fill(C["fondo"])
        pygame.draw.rect(
            pantalla, C["panel"], (ANCHO_GRILLA + 2, 0, PANEL_LATERAL, ALTO)
        )
        pygame.draw.line(
            pantalla, C["borde"], (ANCHO_GRILLA + 2, 0), (ANCHO_GRILLA + 2, ALTO), 1
        )
        dibujar_header(
            pantalla,
            f"Proyecto #2 — {'MDP' if modo == 'MDP' else 'SMDP'} (gamma={slider_gamma.valor:.2f})",
        )
        dibujar_grilla(
            pantalla,
            V_cache,
            pi_cache,
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
        y = stat_y
        for label, val in [
            ("Pasos", str(pasos)),
            ("Tiempo", f"{tiempo:.1f}s"),
            ("P exito", "90%"),
            ("Inicio", str(pos_ini)),
        ]:
            pantalla.blit(f.render(label, True, C["dim"]), (sx, y))
            pantalla.blit(fb.render(val, True, C["texto"]), (sx + 90, y))
            y += 20
        estado = "PAUSADO" if pausado else "CORRIENDO"
        eclr = C["warn"] if pausado else C["ok"]
        pantalla.blit(fb.render(estado, True, eclr), (sx, y + 10))
        if modo == "SMDP":
            y += 40
            for linea in [
                "Tiempos (SMDP):",
                "  N/S ~ N(2, 0.2)",
                "  E/O ~ N(3, 0.3)",
                "  descuento = gamma^tau",
            ]:
                pantalla.blit(f.render(linea, True, C["dim"]), (sx, y))
                y += 16
        dibujar_footer(
            pantalla,
            "1=MDP  2=SMDP  ESPACIO=Pausar  R=Reset  Q=Salir  |  Sliders ajustables",
        )
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
