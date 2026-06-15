import pygame, sys, random
import numpy as np
from mapa import GRID, ROWS, COLS, ACTIONS, get_goal, get_states, move, get_random_start
from framework import *

# ============================================================
# PARAMETROS DEL PROBLEMA
# ============================================================
#
# PREGUNTA: "Por que gamma=0.97 y no 1.0?"
# Si gamma=1.0, el robot valdria igual una recompensa hoy que en 1000 pasos.
# Con gamma=0.97, las recompensas futuran valen menos:
#   ahora = 1.0, en 1 paso = 0.97, en 10 pasos = 0.97^10 = 0.74
# Esto hace que el robot PREFIERA caminos cortos.
#
# PREGUNTA: "Por que probabilidad de exito 90% y no 100%?"
# En el mundo real los robots fallan. 90% modela que a veces el robot
# resbala o no se mueve bien. Esto afecta la politica porque el robot
# prefiere caminos donde un fallo no lo deja en peligro.
#
# PREGUNTA: "Por que costo -1 y recompensa +10?"
# -1 por paso penaliza caminar mucho (el robot busca el camino corto).
# +10 en la meta incentiva llegar. La proporcion importa: si la meta
# diera +1, el robot preferiria quedarse quieto (ahorra el costo de -1).

GAMMA = 0.97
P_EXITO = 0.9
COSTO_PASO = -1.0
RECOMPENSA_META = 10.0

# PREGUNTA: "Por que Norte/Sur toman 2 seg y Este/Oeste 3 seg?"
# Esto es para el SMDP. En el mundo real, no todas las acciones toman
# el mismo tiempo. Norte/Sur son mas rapidos (2s), Este/Oeste mas lentos (3s).
# La distribucion Normal(media, sigma) modela variabilidad natural:
# a veces toma 1.8s, a veces 2.2s, pero en promedio 2s.
#
# PREGUNTA: "Que es una distribucion Normal?"
# Es una campana de Gauss. El 68% de las veces el valor cae entre
# media-sigma y media+sigma. Normal(2, 0.2) -> 68% entre 1.8 y 2.2.

TIEMPO_ACCION = {
    'Norte': (2.0, 0.2),   # rapido, baja variabilidad
    'Sur':   (2.0, 0.2),   # rapido, baja variabilidad
    'Este':  (3.0, 0.3),   # lento, alta variabilidad
    'Oeste': (3.0, 0.3),   # lento, alta variabilidad
}


# ============================================================
# FUNCION: calcular_politica
# ============================================================
# Esta es la funcion principal. Calcula:
#   V(s) = el valor de estar en cada estado
#   pi(s) = la mejor accion para cada estado
#
# Usa VALUE ITERATION: itera la ecuacion de Bellman hasta converger.
#
# PREGUNTA: "Que es Value Iteration?"
# Es un algoritmo que calcula el valor de cada estado repitiendo
# la ecuacion de Bellman. En cada iteracion, los valores se actualizan
# basandose en los valores de la iteracion anterior. Cuando los valores
# dejan de cambiar (delta < 0.001), converge.
#
# PREGUNTA: "Cuantas iteraciones necesita?"
# Depende del mapa y gamma. Con gamma=0.97 y este mapa, converge
# en ~17 iteraciones. Con gamma mas alto (0.99) necesitaria mas.
#
# PREGUNTA: "Por que 500 iteraciones maximo?"
# Es un limite de seguridad. En la practica converge mucho antes (~17).
# Pero si gamma fuera muy cercano a 1, podria necesitar mas.

def calcular_politica(gamma, modo='MDP'):
    estados = get_states()   # 18 estados transitables
    meta = get_goal()        # (5, 3)

    # Inicializar V(s) = 0 para todos los estados
    # PREGUNTA: "Por que empieza en 0?"
    # Es la inicializacion estandar. No sabemos nada al inicio,
    # asi que asumimos que todos los estados valen 0.
    # Con otras inicializaciones convergeria al mismo resultado.
    V = {s: 0.0 for s in estados}

    for iteracion in range(500):
        max_cambio = 0
        nuevos = {}

        for s in estados:
            # La meta siempre vale 10 (recompensa fija)
            if s == meta:
                nuevos[meta] = RECOMPENSA_META
                continue

            mejor = float('-inf')

            # Probar las 4 acciones y quedarnos con la mejor
            for acc in ACTIONS:
                sig = move(s, acc)  # donde llegaria el robot

                # Recompensa: -1 por paso, +10 si llega a la meta
                recompensa = COSTO_PASO + (RECOMPENSA_META if sig == meta else 0.0)

                # ============================================================
                # AQUI ESTA LA DIFERENCIA ENTRE MDP Y SMDP
                # ============================================================
                #
                # MDP: descuento FIJO = gamma (0.97)
                #   Cada paso toma exactamente 1 unidad de tiempo.
                #   El descuento siempre es el mismo.
                #
                # SMDP: descuento VARIABLE = gamma^tau
                #   Cada accion toma un tiempo distinto (distribucion normal).
                #   tau se muestrea de la distribucion correspondiente.
                #   gamma^tau ajusta el descuento: mas tiempo = mas descuento.
                #
                # Ejemplo numerico:
                #   MDP:  descuento = 0.97^1 = 0.97
                #   SMDP: descuento = 0.97^3.1 = 0.91 (accion lenta)
                #         descuento = 0.97^1.9 = 0.94 (accion rapida)
                #
                # PREGUNTA: "Por que SMDP produce valores menores?"
                # Porque las acciones lentas (E/O, 3s) descuentan mas,
                # lo que reduce el valor total de los estados lejanos.
                #
                # PREGUNTA: "Como se calcula E[gamma^tau]?"
                # Muestreamos tau 20 veces de la distribucion normal
                # y promediamos gamma^tau. Con mas muestras seria mas
                # preciso, pero 20 es suficiente para converger.

                if modo == 'SMDP':
                    mu, sigma = TIEMPO_ACCION[acc]
                    muestras = [gamma ** max(0.1, np.random.normal(mu, sigma)) for _ in range(20)]
                    descuento = np.mean(muestras)
                else:
                    descuento = gamma

                # ============================================================
                # ECUACION DE BELLMAN
                # ============================================================
                #
                # V(s) = max_a [ P_exito * (R + desc * V(s')) + P_fallo * (R + desc * V(s)) ]
                #
                # P_exito = 0.9: el robot se mueve a s' (el estado destino)
                # P_fallo = 0.1: el robot se queda en s (no se mueve)
                #
                # PREGUNTA: "Por que V(s) aparece en el termino de fallo?"
                # Porque si el robot falla, se queda en el mismo estado s.
                # Entonces el valor futuro es V(s), no V(s').
                #
                # PREGUNTA: "Que pasa si el robot choca contra un muro?"
                # move() devuelve el mismo estado s. Entonces es como
                # un fallo: el robot se queda donde esta.

                valor_exito = recompensa + descuento * V[sig]
                valor_fallo = COSTO_PASO + descuento * V[s]
                valor = P_EXITO * valor_exito + (1 - P_EXITO) * valor_fallo

                mejor = max(mejor, valor)

            nuevos[s] = mejor
            max_cambio = max(max_cambio, abs(nuevos[s] - V[s]))

        V = nuevos

        # PREGUNTA: "Que es la convergencia?"
        # Cuando max_cambio < 0.001, los valores ya no cambian
        # significativamente. Esto significa que encontramos los
        # valores optimos y podemos parar.
        if max_cambio < 0.001:
            break

    # ============================================================
    # EXTRAER POLITICA
    # ============================================================
    # La politica es: para cada estado, cual es la mejor accion.
    # Se calcula probando las 4 acciones y quedandose con la de mayor valor.
    #
    # PREGUNTA: "Que representan las flechas en pantalla?"
    # Cada flecha muestra la mejor accion para ese estado.
    # Si todas las flechas apuntan hacia la meta, la politica es optima.

    pi = {}
    for s in estados:
        if s == meta:
            pi[s] = 'META'
            continue
        mejor_acc, mejor_val = None, float('-inf')
        for acc in ACTIONS:
            sig = move(s, acc)
            recompensa = COSTO_PASO + (RECOMPENSA_META if sig == meta else 0.0)
            if modo == 'SMDP':
                mu, sigma = TIEMPO_ACCION[acc]
                muestras = [gamma ** max(0.1, np.random.normal(mu, sigma)) for _ in range(20)]
                descuento = np.mean(muestras)
            else:
                descuento = gamma
            valor = P_EXITO * (recompensa + descuento * V[sig]) \
                  + (1 - P_EXITO) * (COSTO_PASO + descuento * V[s])
            if valor > mejor_val:
                mejor_val, mejor_acc = valor, acc
        pi[s] = mejor_acc

    return V, pi


# ============================================================
# RESUMEN RAPIDO PARA DEFENSA
# ============================================================
#
# MDP vs SMDP:
#   MDP:  descuento fijo gamma=0.97, cada paso = 1 unidad de tiempo
#   SMDP: descuento variable gamma^tau, tau ~ N(2,0.2) o N(3,0.3)
#
# Ecuacion de Bellman:
#   V(s) = max_a [ 0.9*(R + desc*V(s')) + 0.1*(R + desc*V(s)) ]
#
# Factor de descuento:
#   gamma=0.97 -> recompensa en 10 pasos vale 0.97^10 = 0.74
#
# Probabilidad:
#   90% exito -> se mueve a donde quiere
#   10% fallo -> se queda quieto
#
# Convergencia:
#   ~17 iteraciones con gamma=0.97
#
# Politica:
#   Para cada estado, la accion con mayor valor
#   Se muestra como flechas en pantalla
#
# Sliders:
#   Gamma: ajusta el descuento en vivo (recalcula la politica)
#   Velocidad: ajusta que tan rapido se mueve el robot
