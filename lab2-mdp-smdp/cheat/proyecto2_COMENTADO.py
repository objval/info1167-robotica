import pygame, sys, random
import numpy as np
from mapa import GRID, ROWS, COLS, ACTIONS, get_goal, get_states, move, get_random_start
from framework import *

# =============================================================
# ESTE ARCHIVO ES TU GUIA PARA LA DEFENSA
# Leelo 1 vez antes de presentar y vas a estar listo.
# No lo entregues — es solo para ti.
# =============================================================


# =============================================================
# PARAMETROS DEL JUEGO
# =============================================================
# Imagina que el robot es un wn en un laberinto oscuro.
# Cada paso que da le cuesta 1 punto (COSTO_PASO = -1).
# Si llega a la meta, gana 10 puntos (RECOMPENSA_META = +10).
# A veces resbala y no se mueve (10% de las veces).
# Y las recompensas futuras valen menos que las de ahora (gamma = 0.97).

GAMMA = 0.97           # factor de descuento
P_EXITO = 0.9          # 90% de las veces el robot se mueve bien
COSTO_PASO = -1.0      # cada paso cuesta 1 punto
RECOMPENSA_META = 10.0 # llegar a la meta da 10 puntos

# ---- tiempos de las acciones (solo para SMDP) ----
# Norte/Sur son rapidos: en promedio 2 segundos (con un poco de variacion)
# Este/Oeste son lentos: en promedio 3 segundos (con mas variacion)
# Normal(2, 0.2) significa: promedio=2, desviacion=0.2
# El 68% de las veces el tiempo queda entre 1.8 y 2.2 segundos.

TIEMPO_ACCION = {
    'Norte': (2.0, 0.2),
    'Sur':   (2.0, 0.2),
    'Este':  (3.0, 0.3),
    'Oeste': (3.0, 0.3),
}


# =============================================================
# QUE ES MDP?
# =============================================================
# MDP = Markov Decision Process.
# Es un modelo para tomar decisiones cuando no sabes que va a pasar.
# Tiene 5 ingredientes:
#   1. S (estados) = los lugares donde puede estar el robot (18 casillas)
#   2. A (acciones) = lo que puede hacer (Norte, Sur, Este, Oeste)
#   3. P(s'|s,a) = probabilidad de llegar a s' desde s (90% exito, 10% falla)
#   4. R(s,a) = recompensa (-1 por paso, +10 en la meta)
#   5. gamma = factor de descuento (0.97)
#
# QUE ES SMDP?
# SMDP = Semi-Markov Decision Process.
# Es lo mismo que MDP, pero las acciones toman TIEMPO VARIABLE.
# Norte/Sur toman ~2 seg, Este/Oeste toman ~3 seg.
# El descuento cambia de gamma a gamma^tau (tau = tiempo de la accion).
#
# DIFERENCIA CLAVE:
#   MDP:  descuento fijo = 0.97 (siempre igual)
#   SMDP: descuento variable = 0.97^tau (depende del tiempo)
#   Si tau=3 (accion lenta): 0.97^3 = 0.91 (descuenta mas)
#   Si tau=2 (accion rapida): 0.97^2 = 0.94 (descuenta menos)
#   Por eso SMDP prefiere acciones rapidas.


# =============================================================
# FUNCION PRINCIPAL: calcular_politica
# =============================================================
# Esta funcion hace todo el trabajo:
#   1. Calcula el VALOR de cada estado (que tan bueno es estar ahi)
#   2. Calcula la POLITICA (para donde ir en cada estado)
#
# Usa VALUE ITERATION: repite la ecuacion de Bellman hasta que
# los valores dejan de cambiar. Cuando ya no cambian, converge.
#
# QUE ES VALUE ITERATION?
# Es repetir la misma formula una y otra vez hasta que los valores
# se estabilicen. Como cuando calculas una raiz cuadrada a mano:
# vas aproximando hasta que el numero no cambia mas.
#
# CUANTAS ITERACIONES NECESITA?
# Con gamma=0.97 y este mapa, converge en ~17 iteraciones.
# El limite de 500 es por si acaso, en la practica nunca llega ahi.

def calcular_politica(gamma, modo='MDP'):

    estados = get_states()  # los 18 lugares donde puede estar el robot
    meta = get_goal()       # donde esta la meta: (5, 3)

    # Partimos con V(s) = 0 para todos los estados.
    # Es como decir "no sabemos nada, todos los lugares valen 0".
    # Da lo mismo partir en 0, en 100, o en -50: converge igual.
    V = {s: 0.0 for s in estados}

    # Iteramos maximo 500 veces (en la practica converge en ~17)
    for iteracion in range(500):
        max_cambio = 0
        nuevos = {}

        for s in estados:

            # La meta siempre vale 10 puntos (es la recompensa fija)
            if s == meta:
                nuevos[meta] = RECOMPENSA_META
                continue

            mejor = float('-inf')

            # Probamos las 4 acciones (Norte, Sur, Este, Oeste)
            # y nos quedamos con la que da el mayor valor
            for acc in ACTIONS:

                # ¿Donde llegaria el robot si hace esta accion?
                sig = move(s, acc)

                # Recompensa: -1 por cada paso, +10 si llega a la meta
                recompensa = COSTO_PASO
                if sig == meta:
                    recompensa += RECOMPENSA_META

                # =========================================================
                # AQUI ESTA LA UNICA DIFERENCIA ENTRE MDP Y SMDP
                # =========================================================
                #
                # MDP: el descuento es SIEMPRE gamma (0.97)
                # SMDP: el descuento es gamma^tau, donde tau es el tiempo
                #
                # tau sale de una distribucion Normal:
                #   Norte/Sur: Normal(2, 0.2) -> en promedio 2 seg
                #   Este/Oeste: Normal(3, 0.3) -> en promedio 3 seg
                #
                # Muestreamos 20 veces y promediamos para aproximar
                # el valor esperado E[gamma^tau].
                #
                # POR QUE 20 MUESTRAS?
                # Con 20 es suficiente para una buena aproximacion.
                # Mas muestras = mas preciso pero mas lento.
                # 20 es un buen balance.

                if modo == 'SMDP':
                    mu, sigma = TIEMPO_ACCION[acc]
                    muestras = []
                    for _ in range(20):
                        tau = max(0.1, np.random.normal(mu, sigma))
                        muestras.append(gamma ** tau)
                    descuento = np.mean(muestras)
                else:
                    descuento = gamma

                # =========================================================
                # ECUACION DE BELLMAN — la formula mas importante
                # =========================================================
                #
                # V(s) = max accion [
                #     0.9 * (recompensa + descuento * V(siguiente))
                #   + 0.1 * (recompensa + descuento * V(mismo_lugar))
                # ]
                #
                # 0.9 = probabilidad de exito (el robot se mueve)
                # 0.1 = probabilidad de fallo (el robot se queda quieto)
                #
                # Si el robot tiene exito -> va a "siguiente"
                # Si el robot falla -> se queda en "s" (mismo lugar)
                #
                # POR QUE V(s) APARECE EN EL TERMINO DE FALLO?
                # Porque si el robot falla, se queda donde esta.
                # Entonces el valor futuro es el de donde esta (V(s)),
                # no el de donde iba a ir (V(siguiente)).
                #
                # QUE PASA SI CHOCA CONTRA UN MURO?
                # move() devuelve el mismo estado. Es igual que un fallo:
                # el robot no se mueve. La formula lo maneja automatico.

                valor_si_exito = recompensa + descuento * V[sig]
                valor_si_fallo = COSTO_PASO + descuento * V[s]
                valor = P_EXITO * valor_si_exito + (1 - P_EXITO) * valor_si_fallo

                # Nos quedamos con el mejor valor entre las 4 acciones
                mejor = max(mejor, valor)

            nuevos[s] = mejor
            max_cambio = max(max_cambio, abs(nuevos[s] - V[s]))

        V = nuevos

        # CONVERGENCIA: si el cambio mas grande es menor a 0.001,
        # los valores ya no cambian. Paramos.
        if max_cambio < 0.001:
            break

    # =============================================================
    # EXTRAER LA POLITICA
    # =============================================================
    # La politica es simple: para cada estado, cual es la mejor accion.
    # Probamos las 4 acciones y nos quedamos con la de mayor valor.
    # Las flechas en pantalla muestran esta politica.

    pi = {}
    for s in estados:
        if s == meta:
            pi[s] = 'META'
            continue
        mejor_acc = None
        mejor_val = float('-inf')
        for acc in ACTIONS:
            sig = move(s, acc)
            recompensa = COSTO_PASO + (RECOMPENSA_META if sig == meta else 0.0)
            if modo == 'SMDP':
                mu, sigma = TIEMPO_ACCION[acc]
                muestras = []
                for _ in range(20):
                    tau = max(0.1, np.random.normal(mu, sigma))
                    muestras.append(gamma ** tau)
                descuento = np.mean(muestras)
            else:
                descuento = gamma
            valor = P_EXITO * (recompensa + descuento * V[sig]) \
                  + (1 - P_EXITO) * (COSTO_PASO + descuento * V[s])
            if valor > mejor_val:
                mejor_val = valor
                mejor_acc = acc
        pi[s] = mejor_acc

    return V, pi


# =============================================================
# PREGUNTAS QUE TE PUEDEN HACER (y que responder)
# =============================================================
#
# "Que es un MDP?"
# -> Un modelo para tomar decisiones bajo incertidumbre.
#    5 cosas: estados, acciones, probabilidades, recompensas, descuento.
#
# "Que es un SMDP?"
# -> Lo mismo que MDP pero las acciones toman tiempo variable.
#    Norte/Sur = 2 seg, Este/Oeste = 3 seg.
#
# "Cual es la diferencia entre MDP y SMDP?"
# -> El descuento. MDP usa gamma fijo (0.97).
#    SMDP usa gamma^tau, donde tau es el tiempo de la accion.
#    Acciones mas lentas descuentan mas.
#
# "Que es gamma?"
# -> El factor de descuento. Dice cuanto valoramos el futuro.
#    gamma=0.97 significa que una recompensa en 1 paso vale 97%
#    de una recompensa ahora. En 10 pasos vale 0.97^10 = 74%.
#
# "Por que gamma=0.97 y no 1.0?"
# -> Si gamma=1.0, el robot valoraria igual una recompensa hoy
#    que en 1000 pasos. Eso no es realista. Con 0.97, prefiere
#    recompensas cercanas.
#
# "Por que gamma^tau y no gamma?"
# -> Porque si una accion toma mas tiempo, la recompensa futura
#    llega mas tarde y vale menos. gamma^tau modela eso.
#    tau grande = descuento grande = la recompensa vale menos.
#
# "Que es la ecuacion de Bellman?"
# -> V(s) = max_a [ 0.9*(R + desc*V(s')) + 0.1*(R + desc*V(s)) ]
#    El valor de un estado = la mejor accion posible, considerando
#    la recompensa inmediata + el valor del futuro descontado.
#
# "Que es Value Iteration?"
# -> Un algoritmo que repite Bellman hasta converger.
#    En cada paso recalcula V(s) para todos los estados.
#    Cuando los valores dejan de cambiar, converge.
#
# "Por que 90% exito y 10% fallo?"
# -> Modela que el mundo es imperfecto. A veces el robot resbala
#    o no se mueve bien. Esto afecta la politica porque el robot
#    prefiere caminos donde un fallo no es catastrofico.
#
# "Por que -1 por paso y +10 en la meta?"
# -> -1 penaliza caminar mucho (busca camino corto).
#    +10 incentiva llegar. Si la meta diera +1, el robot
#    preferiria quedarse quieto (ahorra el -1 del paso).
#
# "Por que los valores SMDP son menores que los MDP?"
# -> Porque las acciones lentas (E/O = 3 seg) descuentan mas.
#    gamma^3 = 0.91 descuenta mas que gamma^2 = 0.94.
#    Mas descuento = valores mas bajos.
#
# "Que es una distribucion Normal?"
# -> Una campana de Gauss. Normal(2, 0.2) significa que el
#    promedio es 2 y la desviacion es 0.2. El 68% de las veces
#    el valor queda entre 1.8 y 2.2.
#
# "Cuantas iteraciones necesita para converger?"
# -> ~17 con gamma=0.97. Con gamma mas alto (0.99) necesitaria mas.
#
# "Que es la convergencia?"
# -> Cuando los valores dejan de cambiar (delta < 0.001).
#    Significa que encontramos los valores optimos.
#
# "Que representan las flechas?"
# -> La mejor accion para cada estado. Si todas apuntan hacia
#    la meta, la politica es optima.
#
# "Por que el inicio es aleatorio?"
# -> Para que funcione desde cualquier punto del mapa.
#    La politica se calcula para TODOS los estados, no solo uno.
#
# "Los sliders que hacen?"
# -> Gamma: cambia el descuento en vivo y recalcula la politica.
#    Velocidad: cambia que tan rapido se mueve el robot.
#
# "Que pasa si muevo el slider de gamma?"
# -> La politica se recalcula al instante. Si subo gamma,
#    el robot valora mas el futuro y puede cambiar de camino.
#    Si lo bajo, solo le importa el corto plazo.
#
# "Por que usamos pygame?"
# -> Para la simulacion grafica. Muestra el mapa, el robot,
#    las flechas de politica, y los valores de cada estado.
#
# "Que es la politica optima?"
# -> La mejor accion para cada estado. Es la que maximiza
#    la recompensa total esperada considerando el descuento.
#
# "El algoritmo siempre converge?"
# -> Si, siempre. Value Iteration converge para cualquier MDP
#    finito con gamma < 1. Es un teorema matematico.
#
# "Que pasa si hay dos caminos con el mismo valor?"
# -> El algoritmo elige uno cualquiera. En la practica,
#    con las probabilidades y el descuento, rara vez hay empate.
