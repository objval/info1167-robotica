# Trazabilidad de Requisitos (Lab #1 INFO1167 Robotica)

Fuente:
- `docs/assets/Lab_1_INFO1167_Robotica_original.pdf`
- `docs/assets/Lab_1_INFO1167_Robotica_original.txt`

## Regla del lab -> Implementacion (1:1)

1. **Simular 4 robots AGV en mapa 2D (nodos QR)**
   - `ConfigSimulacion(cantidad_robots=4)` en `src/agv_sim/modelos.py`.
   - Grafo cuadricula en `crear_grafo_cuadricula(ancho, alto)` (`src/agv_sim/grafos.py`).

2. **Inicio en bases y busqueda de carrito asignado aleatoriamente**
   - Bases en las esquinas en `_iniciar_entidades()` (`src/agv_sim/simulacion.py`).
   - Asignacion aleatoria en `_asignar_robots_libres()` con semilla.

3. **Carrito cambia al color del robot asociado (robots con color unico)**
   - Acoplamiento de color al asignar (`carrito.color_original = robot.color`).
   - Reset a gris despues de entregar.

4. **Rutas con algoritmos de grafos**
   - Modos operativos: `random_shortest`, `dijkstra`, `bfs`.
   - Implementado en `_obtener_ruta()` y `grafos.py`.

5. **Movimiento aleatorio hacia nodo final**
   - `ruta_corta_aleatoria(...)` desempata aleatoriamente entre rutas cortas equivalentes.
   - Mantiene inteligencia de ruta corta pero introduce aleatoriedad.

6. **Al alcanzar carrito: llevar a destino, liberar, volver a base, cargar**
   - Maquina de estados:
     - `BUSCANDO_CARRITO -> LLEVANDO_CARRITO -> VOLVIENDO_BASE -> CARGANDO -> EN_BASE`
   - Eventos de transicion logueados como evidencia del ciclo.

7. **Rotaciones en pasos de 10 grados**
   - `paso_rotacion=10.0` en la configuracion.
   - Aplicado en `_rotar_y_mover()` antes de mover el nodo.

8. **Temas de grafos exigidos (profundidad, ruta mas corta, todas y al menos una ruta)**
   - Evidencia DFS: `dfs(...)`.
   - Evidencia ruta corta: `dijkstra(...)`.
   - Evidencia al menos una ruta: chequeos de camino no vacio.
   - Evidencia multiples rutas: `todas_las_rutas(...)` con muestra limitada.

9. **Visual Python (tema relacionado obligatorio)**
   - Animador 3D en `src/agv_sim/animacion_vpython.py`.
   - Entrypoint: `scripts/ejecutar_vpython.py`.
   - Muestra grilla, robots, carritos, bases, destinos y anima rotaciones.

10. **Geometria (tema relacionado obligatorio)**
    - Calculo de angulo con `atan2` (`_angulo_deseado()`).
    - Normalizacion de angulo y pasos de 10 grados (`_rotar_y_mover()`).
    - Vector de direccion actualizado con cos/sen en `animacion_vpython.py`.

## Artefactos de validacion

Generados por el pipeline (`scripts/pipeline.py`):
- `outputs/reporte_requisitos.json` (R1..R8 pass/fail + evidencia)
- `outputs/resumen.json` (config, seniales, ejemplos de grafos, eventos)
- `outputs/captura.png` (evidencia visual)
