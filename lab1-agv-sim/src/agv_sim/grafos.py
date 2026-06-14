import heapq
import random

import networkx as nx


def crear_grafo_cuadricula(ancho, alto):
    g = nx.Graph()
    for x in range(ancho):
        for y in range(alto):
            g.add_node((x, y))
    for x in range(ancho):
        for y in range(alto):
            if x + 1 < ancho:
                g.add_edge((x, y), (x + 1, y), peso=1.0)
            if y + 1 < alto:
                g.add_edge((x, y), (x, y + 1), peso=1.0)
    return g


def dijkstra(grafo, origen, destino):
    if origen == destino:
        return [origen]
    cola = [(0.0, origen)]
    distancias = {origen: 0.0}
    anteriores = {}

    while cola:
        d, nodo = heapq.heappop(cola)
        if nodo == destino:
            break
        if d > distancias.get(nodo, float("inf")):
            continue
        for vecino in grafo.neighbors(nodo):
            nd = d + grafo[nodo][vecino].get("peso", 1.0)
            if nd < distancias.get(vecino, float("inf")):
                distancias[vecino] = nd
                anteriores[vecino] = nodo
                heapq.heappush(cola, (nd, vecino))

    if destino not in distancias:
        return []

    camino = [destino]
    actual = destino
    while actual != origen:
        actual = anteriores[actual]
        camino.append(actual)
    camino.reverse()
    return camino


def ruta_corta_aleatoria(grafo, origen, destino, rng):
    if origen == destino:
        return [origen]

    dist_desde_origen = nx.single_source_dijkstra_path_length(grafo, origen, weight="peso")
    if destino not in dist_desde_origen:
        return []

    costo_total = dist_desde_origen[destino]
    dist_hasta_destino = nx.single_source_dijkstra_path_length(grafo, destino, weight="peso")

    camino = [origen]
    actual = origen
    seguridad = 0
    while actual != destino:
        seguridad += 1
        if seguridad > grafo.number_of_nodes() + 5:
            return []

        candidatos = []
        for vecino in grafo.neighbors(actual):
            costo_arista = grafo[actual][vecino].get("peso", 1.0)
            desde_origen = dist_desde_origen.get(actual, float("inf")) + costo_arista
            hasta_destino = dist_hasta_destino.get(vecino, float("inf"))
            if abs((desde_origen + hasta_destino) - costo_total) < 1e-9:
                candidatos.append(vecino)

        if not candidatos:
            return []

        actual = rng.choice(candidatos)
        camino.append(actual)

    return camino


def bfs(grafo, origen, destino):
    from collections import deque

    if origen == destino:
        return [origen]
    q = deque([origen])
    anteriores = {}
    visitados = {origen}
    while q:
        nodo = q.popleft()
        if nodo == destino:
            break
        for vecino in grafo.neighbors(nodo):
            if vecino in visitados:
                continue
            visitados.add(vecino)
            anteriores[vecino] = nodo
            q.append(vecino)
    if destino not in visitados:
        return []
    camino = [destino]
    actual = destino
    while actual != origen:
        actual = anteriores[actual]
        camino.append(actual)
    camino.reverse()
    return camino


def dfs(grafo, origen, destino):
    pila = [(origen, [origen])]
    visitados = set()
    while pila:
        nodo, camino = pila.pop()
        if nodo == destino:
            return camino
        if nodo in visitados:
            continue
        visitados.add(nodo)
        for vecino in grafo.neighbors(nodo):
            if vecino not in camino:
                pila.append((vecino, camino + [vecino]))
    return []


def todas_las_rutas(grafo, origen, destino, max_caminos=20, limite=6):
    caminos = []
    for i, camino in enumerate(nx.all_simple_paths(grafo, origen, destino, cutoff=limite)):
        caminos.append(camino)
        if i + 1 >= max_caminos:
            break
    return caminos
