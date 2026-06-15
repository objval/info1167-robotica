import pygame, sys, random
import numpy as np
from collections import defaultdict
from mapa import GRID, ROWS, COLS, ACTIONS, get_goal, get_states, move, get_random_start
from framework import *

# ============================================================
# PARAMETROS
# ============================================================
#
# PREGUNTA: "Que es alpha?"
# La tasa de aprendizaje. alpha=0.10 significa que cada actualizacion
# solo cambia el valor en un 10%. Si alpha fuera 1.0, borraria todo
# lo que el robot aprendio antes. Con 0.10, el aprendizaje es gradual.
#
# PREGUNTA: "Por que alpha=0.10 y no 0.5 o 0.01?"
# 0.10 es un balance: aprende rapido pero no olvida lo anterior.
# 0.5 seria muy agresivo (cambia mucho por una experiencia).
# 0.01 seria muy lento (necesitaria miles de episodios mas).

GAMMA = 0.97
ALPHA = 0.10
P_EXITO = 0.9
COSTO_PASO = -1.0
RECOMPENSA_META = 10.0

TIEMPO_ACCION = {
    'Norte': (2.0, 0.2),
    'Sur':   (2.0, 0.2),
    'Este':  (3.0, 0.3),
    'Oeste': (3.0, 0.3),
}


# ============================================================
# CLASE: AgenteQLearning
# ============================================================
#
# PREGUNTA: "Que es Q-Learning?"
# Algoritmo de aprendizaje por refuerzo LIBRE DE MODELO.
# El robot no conoce las reglas del juego. Aprende por prueba y error.
#
# PREGUNTA: "Que es libre de modelo?"
# Significa que no necesita conocer las probabilidades de transicion
# P(s|s,a) ni las recompensas R(s,a). Solo necesita interactuar
# con el entorno y observar que pasa.
#
# PREGUNTA: "Cual es la diferencia con el Lab 2?"
# Lab 2 (MDP/SMDP): CONOCE las reglas, calcula con Bellman directamente.
# Lab 3 (Q-Learning): NO CONOCE las reglas, aprende jugando.
# Ambos llegan a la misma politica, pero por caminos distintos.
#
# PREGUNTA: "Que es la tabla Q?"
# Una tabla donde el robot apunta notas: Q[(estado, accion)] = valor.
# Al principio todo es 0 (no sabe nada). Despues de muchos episodios,
# los valores se llenan y el robot sabe que hacer.

class AgenteQLearning:
    def __init__(self):
        self.q = defaultdict(float)  # todo empieza en 0
        self.estados = get_states()
        self.meta = get_goal()
        self.episodios = 0
        self.recompensas = []

    def mejor_accion(self, s):
        # Devuelve la accion con mayor Q para este estado
        mejor, mejor_q = None, float('-inf')
        for a in ACTIONS:
            if self.q[(s, a)] > mejor_q:
                mejor_q, mejor = self.q[(s, a)], a
        return mejor

    def max_q(self, s):
        # Devuelve el maximo Q entre todas las acciones
        return max((self.q[(s, a)] for a in ACTIONS), default=0.0)

    def elegir(self, s, epsilon):
        # ============================================================
        # EPSILON-GREEDY
        # ============================================================
        # PREGUNTA: "Que es epsilon-greedy?"
        # Estrategia de explorar vs explotar.
        # Con probabilidad epsilon: accion random (EXPLORAR)
        # Con probabilidad 1-epsilon: mejor accion conocida (EXPLOTAR)
        #
        # PREGUNTA: "Por que epsilon empieza alto y baja?"
        # Al inicio el robot no sabe nada, necesita explorar mucho.
        # Con el tiempo ya aprendio y puede explotar lo que sabe.
        # Siempre explora: nunca converge. Siempre explota: puede
        # quedar atrapado en un camino suboptimo.
        if random.random() < epsilon:
            return random.choice(ACTIONS)
        return self.mejor_accion(s)

    def mover(self, s, a):
        # 90% exito, 10% se queda quieto
        if random.random() < P_EXITO:
            return move(s, a)
        return s

    def tiempo_accion(self, a):
        # Muestrea el tiempo de la distribucion normal
        mu, sigma = TIEMPO_ACCION[a]
        return max(0.1, np.random.normal(mu, sigma))

    def entrenar_episodio(self, gamma, alpha, epsilon):
        # ============================================================
        # UN EPISODIO DE ENTRENAMIENTO
        # ============================================================
        # PREGUNTA: "Que es un episodio?"
        # Un intento completo del robot de llegar a la meta.
        # Empieza en una posicion random y termina cuando llega
        # a la meta o hace 200 pasos.
        #
        # PREGUNTA: "Por que inicio aleatorio?"
        # Para que el robot explore todo el mapa, no solo un camino.
        # Si siempre empieza en el mismo lugar, solo aprende un camino.

        s = get_random_start()
        total = 0

        for _ in range(200):
            # 1. Elegir accion (epsilon-greedy)
            a = self.elegir(s, epsilon)

            # 2. Ejecutar accion (90% exito)
            sig = self.mover(s, a)

            # 3. Calcular recompensa
            r = COSTO_PASO + (RECOMPENSA_META if sig == self.meta else 0.0)

            # 4. Muestrear tiempo y calcular descuento SMDP
            tau = self.tiempo_accion(a)
            desc = gamma ** tau  # <-- CLAVE DEL SMDP

            # ============================================================
            # ACTUALIZACION DE Q (la ecuacion mas importante)
            # ============================================================
            #
            # Q(s,a) += alpha * [ R + gamma^tau * max Q(s') - Q(s,a) ]
            #
            # PREGUNTA: "Explica la ecuacion de actualizacion"
            # - Q(s,a): mi nota actual para esta accion en este estado
            # - alpha (0.10): cuanto ajusto (10%)
            # - R: lo que acaba de pasar (-1 o +10)
            # - gamma^tau: descuento por tiempo (SMDP)
            # - max Q(s'): lo mejor que espero del siguiente estado
            # - Q(s,a) viejo: mi nota antes
            # - El error temporal = R + gamma^tau * max Q(s') - Q(s,a)
            #
            # PREGUNTA: "Que es el error temporal?"
            # La diferencia entre lo que esperaba y lo que paso.
            # Si esperaba 5 y paso 7, el error es +2, ajusto hacia arriba.
            # Si esperaba 5 y paso 3, el error es -2, ajusto hacia abajo.
            #
            # PREGUNTA: "Por que gamma^tau y no gamma?"
            # Porque es SMDP. La accion tomo tau segundos, asi que
            # la recompensa futura llega mas tarde y vale menos.

            viejo = self.q[(s, a)]
            self.q[(s, a)] = viejo + alpha * (r + desc * self.max_q(sig) - viejo)

            total += r
            s = sig
            if s == self.meta:
                break

        self.episodios += 1
        self.recompensas.append(total)

    def politica(self):
        # Extraer la politica aprendida
        return {s: ('META' if s == self.meta else self.mejor_accion(s)) for s in self.estados}

    def valores(self):
        # V(s) = max_a Q(s,a)
        return {s: self.max_q(s) for s in self.estados}

    def promedio(self, n=30):
        # Promedio de las ultimas N recompensas (para ver convergencia)
        return np.mean(self.recompensas[-n:]) if self.recompensas else 0


# ============================================================
# PREGUNTAS EXTRA QUE TE PUEDEN HACER
# ============================================================
#
# "Cuantos episodios necesita para converger?"
# ~1500-2000. La recompensa sube de -17 (al inicio) a +1 (convergido).
#
# "Por que la recompensa empieza en -17?"
# Al inicio el robot no sabe nada, camina mucho y no llega a la meta.
# Cada paso cuesta -1, asi que 17 pasos sin exito = -17.
#
# "Como sabes que convergio?"
# El grafico en la sidebar muestra la curva de recompensa.
# Cuando se estabiliza, convergio.
#
# "Que pasa si cambias alpha a 0.5?"
# Aprende mas rapido pero es inestable. Una experiencia rara puede
# borrar todo lo que aprendio antes.
#
# "Que pasa si cambias epsilon a 0.01?"
# Casi siempre explota. Puede converger mas rapido pero corre el
# riesgo de quedar atrapado en un camino suboptimo.
#
# "Los sliders afectan el entrenamiento?"
# Si. Si cambias gamma, alpha o epsilon durante el entrenamiento,
# la tabla Q se actualiza con los nuevos valores.
#
# "Por que Q-Learning es mejor que MDP?"
# No es "mejor", es diferente. MDP es mas eficiente cuando CONOCES
# las reglas. Q-Learning es util cuando NO las conoces o el entorno
# es muy complejo para modelar.
