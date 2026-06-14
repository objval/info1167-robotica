# FAQ - Preguntas Frecuentes para la Defensa

**INFO1167 Robótica - Lab #1 AGV**

Este documento contiene preguntas que el profesor podría hacer durante la defensa, con respuestas listas para entregar de forma clara y directa.

---

## 1. Conceptos Generales

### ¿Qué es un AGV?
**Respuesta:** AGV significa *Automated Guided Vehicle* (Vehículo Guiado Automáticamente). Es un robot móvil usado en bodegas y centros de distribución para transportar mercancía sin conductor humano. En nuestro proyecto simulamos AGVs que navegan por códigos QR en el piso.

### ¿Por qué usan códigos QR?
**Respuesta:** Cada celda del mapa 2D tiene un código QR único. El robot lleva una cámara en su base que lee el QR y así sabe exactamente en qué coordenada (x, y) está dentro de la bodega. Es su sistema de localización.

### ¿Cuántos robots hay y dónde empiezan?
**Respuesta:** Hay 4 robots, cada uno empieza en una esquina del mapa: (0,0), (9,0), (0,7) y (9,7) para un mapa de 10×8.

### ¿Cuántos carritos hay?
**Respuesta:** Por defecto hay 4 carritos, pero en la configuración usamos 8 para que el sistema tenga más trabajo y se vea el ciclo completo varias veces.

---

## 2. Algoritmos de Grafos

### ¿Cómo modelaste la bodega como grafo?
**Respuesta:** Usamos NetworkX. Cada celda (x, y) es un nodo. Dos nodos vecinos (arriba, abajo, izquierda, derecha) se conectan con una arista de peso 1.0. No hay diagonales porque los robots solo se mueven en horizontal o vertical.

### ¿Qué algoritmos de grafos implementaste?
**Respuesta:** Cuatro:
1. **BFS** - búsqueda en anchura, encuentra la ruta con menos pasos.
2. **DFS** - búsqueda en profundidad, explora todo un camino antes de retroceder.
3. **Dijkstra** - ruta más corta con pesos, usa una cola de prioridad (min-heap).
4. **Todas las rutas** - `nx.all_simple_paths` que enumera todos los caminos simples entre dos nodos.

### ¿Cuál es la diferencia entre BFS y Dijkstra?
**Respuesta:** En nuestro caso (todas las aristas pesan 1) BFS y Dijkstra dan la misma ruta óptima en longitud. Pero Dijkstra es más general: si un paso costara más (ej. una zona lenta), Dijkstra lo considera. BFS solo cuenta la cantidad de pasos.

### ¿Por qué usaste `random_shortest` en vez de solo Dijkstra?
**Respuesta:** Si los 4 robots usaran Dijkstra puro, siempre tomarían el mismo camino y se chocarían o se amontonarían. `random_shortest` elige aleatoriamente entre todos los vecinos que mantienen la propiedad de "ruta más corta". Así cada robot puede tomar una ruta diferente pero igual de óptima.

### ¿Cómo funciona `random_shortest` matemáticamente?
**Respuesta:** Calcula dos cosas con Dijkstra: la distancia desde el origen a todos los nodos, y desde todos los nodos al destino. Luego, para cada vecino del nodo actual, verifica si:

```
distancia(origen → actual) + peso(arista) + distancia(vecino → destino) == distancia_total
```

Si se cumple, el vecino está en alguna ruta óptima. Elegimos uno al azar entre esos.

### ¿DFS encuentra la ruta más corta?
**Respuesta:** No. DFS explora tan profundo como puede antes de retroceder. Puede encontrar una ruta muy larga. Lo usamos para demostrar el concepto de exploración en profundidad, no para la navegación real de los robots.

### ¿Cómo demuestras que hay "al menos una ruta"?
**Respuesta:** NetworkX tiene `all_simple_paths` que devuelve todos los caminos sin ciclos entre dos nodos. Limitamos a 6 pasos para no explotar combinatoriamente. Si devuelve al menos un camino, demostramos que existe al menos una ruta.

### ¿Y si no hay ruta entre dos nodos?
**Respuesta:** Todos nuestros algoritmos devuelven lista vacía `[]` en ese caso. Como el grafo es una grilla conexa completa, siempre hay ruta entre cualquier par de nodos.

---

## 3. Geometría y Rotación

### ¿Cómo calculas el ángulo hacia el siguiente nodo?
**Respuesta:** Usamos `math.atan2(dy, dx)`, donde `dx = x_siguiente - x_actual` y `dy = y_siguiente - y_actual`. `atan2` devuelve el ángulo en radianes entre el eje X positivo y el vector hacia el objetivo, considerando el cuadrante correcto.

### ¿Por qué usas atan2 y no atan?
**Respuesta:** `atan` solo recibe `dy/dx` y no distingue cuadrantes. `atan2(dy, dx)` sí distingue: por ejemplo, `atan2(1, -1)` = 135° (segundo cuadrante), mientras que `atan(1/-1)` = -45° (cuarto cuadrante). Con `atan2` el robot siempre sabe hacia qué dirección girar.

### ¿Qué significa "rotación en pasos de 10°"?
**Respuesta:** El robot no gira instantáneamente al ángulo deseado. Calcula la diferencia entre su ángulo actual y el deseado. Si la diferencia es mayor a 10°, solo gira 10° en esa dirección y NO avanza. En el siguiente tick vuelve a intentar. Solo cuando la diferencia es ≤ 10° alinea exactamente y avanza.

### ¿Cómo normalizas los ángulos?
**Respuesta:** Todos los ángulos se mantienen en el rango [-180, 180]. Si un ángulo pasa de 180, le restamos 360. Si baja de -180, le sumamos 360. Así la diferencia entre dos ángulos siempre es el giro más corto.

### ¿Se ve la rotación en la animación?
**Respuesta:** Sí. En la animación Tkinter los robots son sprites con ojos que miran hacia la dirección del movimiento. Cada vez que el robot rota 10°, la dirección de la mirada cambia visiblemente. Además los ojos se desplazan ligeramente para mostrar la dirección exacta.

---

## 4. Simulación y Estados

### ¿Cuál es el ciclo de vida de un robot?
**Respuesta:** Es un ciclo cerrado de 5 estados:

```
EN_BASE → BUSCANDO_CARRITO → LLEVANDO_CARRITO → VOLVIENDO_BASE → CARGANDO → EN_BASE
```

1. **EN_BASE**: espera que se le asigne un carrito.
2. **BUSCANDO_CARRITO**: calcula ruta hacia el carrito y se mueve.
3. **LLEVANDO_CARRITO**: recoge el carrito (cambia de color), calcula ruta al destino.
4. **VOLVIENDO_BASE**: entrega el carrito (vuelve a gris), calcula ruta a su base.
5. **CARGANDO**: en la base recupera batería 5% por tick hasta 100%.

### ¿Cómo se asigna un carrito a un robot?
**Respuesta:** Al inicio de cada tick, la simulación recopila los carritos sin asignar, los mezcla aleatoriamente (`rng.shuffle`), y luego recorre los robots que estén en base o completamente cargados. El primer robot libre recibe el primer carrito de la lista mezclada.

### ¿Cómo sabemos que el carrito "se mueve" con el robot?
**Respuesta:** En el estado `LLEVANDO_CARRITO`, cada tick hacemos `carrito.nodo = r.nodo`. Es decir, la posición del carrito se iguala a la del robot. Visualmente el sprite del carrito sigue al robot.

### ¿Qué pasa cuando el robot entrega el carrito?
**Respuesta:** Tres cosas:
1. El contador de entregas del robot y del carrito aumenta.
2. El carrito se reposiciona aleatoriamente en otra celda libre y recibe un nuevo destino aleatorio.
3. El carrito vuelve a color gris y queda sin robot asignado.

### ¿Cómo funciona el sistema de batería?
**Respuesta:** Cada vez que el robot se mueve (avanza al siguiente nodo), pierde 0.8% de batería. Cuando está en estado `CARGANDO`, gana 5.0% por tick hasta llegar al 100%. Solo entonces vuelve a `EN_BASE` y puede recibir una nueva misión.

### ¿Qué pasa si la batería llega a 0?
**Respuesta:** En la configuración actual no llega a 0 porque las rutas son cortas y el robot vuelve a base antes de quedarse sin batería. Pero el código tiene `max(0.0, ...)` para evitar valores negativos.

---

## 5. Python y Visual Python

### ¿Qué es Visual Python y cómo lo usaste?
**Respuesta:** VPython es una librería para crear gráficos 3D en Python. En nuestro proyecto abre una ventana del navegador con una escena 3D interactiva donde los robots son cilindros de colores, los carritos son cajas, los destinos son anillos, y la bodega es un plano con grilla. Se puede rotar la cámara con el mouse.

### ¿Por qué también hay animación Tkinter?
**Respuesta:** VPython 7.6 tiene un bug conocido en Windows que a veces abre una pestaña del navegador en blanco (problema de WebGL). Como alternativa robusta, creamos una interfaz Tkinter 2D con sprites propios generados con Pillow. En Windows se usa Tkinter por defecto; en Linux/Mac puede usarse VPython.

### ¿Qué son los sprites que se ven en la animación?
**Respuesta:** Son imágenes generadas programáticamente con Pillow (PIL). El robot tiene ruedas, cuerpo redondeado, cabeza con ojos que miran hacia la dirección de avance, antena con luz roja, y una sonrisa. El carrito es una caja con ruedas y etiqueta. La base es una plataforma con un rayo de carga. El destino es una bandera en un palo.

### ¿Por qué no usaste imágenes descargadas de internet?
**Respuesta:** Quisimos que el proyecto sea 100% autocontenido. Si dependiéramos de archivos PNG externos, podrían faltar al mover el proyecto a otra PC. Generando los sprites con código nos aseguramos de que todo funcione solo con el código fuente.

---

## 6. Arquitectura del Código

### ¿Por qué separaste el código en tantos archivos?
**Respuesta:** Cada módulo tiene una responsabilidad única (principio de responsabilidad única):
- `grafos.py` solo sabe de grafos.
- `simulacion.py` solo sabe de la lógica de robots.
- `animacion_tkinter.py` solo dibuja.
- `verificador.py` solo revisa requisitos.

Esto permite probar cada parte por separado y reemplazar componentes sin romper el resto.

### ¿Qué son los `dataclass`?
**Respuesta:** Son una forma de Python de crear clases que solo almacenan datos. Python genera automáticamente el constructor `__init__`, el método `__repr__` para imprimir, y otros métodos úiles. Nos ahorra escribir código repetitivo.

### ¿Qué es el `Enum` de `EstadoRobot`?
**Respuesta:** Un Enum es una lista de valores constantes con nombre descriptivo. En vez de usar números mágicos como 0, 1, 2, usamos `EstadoRobot.EN_BASE`, `EstadoRobot.BUSCANDO_CARRITO`, etc. El código es mucho más legible y menos propenso a errores.

### ¿Para qué sirve la `semilla`?
**Respuesta:** La semilla (`semilla=42` por defecto) hace que los números aleatorios sean deterministas. Si corres dos veces con la misma semilla, obtienes exactamente el mismo resultado. Esto es fundamental para depurar y para la defensa, porque puedes repetir la demo con confianza.

### ¿Cómo sabes que todo funciona correctamente?
**Respuesta:** Tenemos dos mecanismos:
1. **Tests automáticos** (pytest, 11 tests) que verifican algoritmos, simulación, estados, baterías y colores.
2. **Verificador de requisitos** (`verificador.py`) que revisa los 8 requisitos R1-R8 del laboratorio y calcula un porcentaje de aprobación. Siempre da 100%.

---

## 7. Preguntas Difíciles (para ir preparado)

### ¿Cómo mejorarías la eficiencia del algoritmo de rutas?
**Respuesta:** Actualmente calculamos Dijkstra dos veces por ruta (desde origen y desde destino) para `random_shortest`. Se podría cachear las distancias precomputadas ya que el grafo no cambia. También se podría usar A* con heurística Manhattan para grafos en grillas, que es más rápido que Dijkstra.

### ¿Qué pasa si dos robots llegan al mismo nodo al mismo tiempo?
**Respuesta:** En la simulación actual no hay detección de colisiones. Los robots pueden ocupar el mismo nodo sin problema. Una mejora sería agregar un sistema de reserva de nodos: antes de moverse, el robot "reserva" el siguiente nodo, y si está ocupado, espera un tick.

### ¿Y si un carrito queda en una posición sin ruta posible?
**Respuesta:** Como nuestro grafo es una grilla completa y conexa, siempre existe al menos una ruta entre cualquier par de nodos. En una versión real con obstáculos, habría que verificar conectividad antes de asignar posiciones.

### ¿Cómo escalarías esto a 100 robots?
**Respuesta:** A mayor escala necesitaríamos:
1. Cachear rutas precomputadas entre pares de nodos frecuentes.
2. Sistema de colisiones / reserva de nodos.
3. Asignación inteligente de carritos (el carrito más cercano, no aleatorio).
4. Posiblemente paralelizar la simulación de ticks si son independientes.

### ¿Por qué usaste NetworkX en vez de implementar los grafos desde cero?
**Respuesta:** NetworkX es robusta, probada y optimizada. Implementar grafos desde cero sería posible pero tomaría mucho más tiempo y sería más propenso a bugs. El foco del laboratorio es demostrar comprensión de los algoritmos, no reinventar estructuras de datos básicas.

### ¿Podrías implementar BFS sin `deque`?
**Respuesta:** Sí. `deque` es una lista doblemente terminada optimizada para `popleft()` en O(1). Si usáramos una lista normal, `pop(0)` sería O(n) y el algoritmo sería mucho más lento. Pero conceptualmente funciona igual: una lista FIFO.

### ¿Qué es un min-heap y por qué lo usa Dijkstra?
**Respuesta:** Un min-heap es una estructura de datos en forma de árbol donde el elemento más pequeño siempre está en la raíz. Las operaciones de insertar y extraer el mínimo son O(log n). Dijkstra lo usa para siempre expandir el camino con menor costo acumulado primero, garantizando optimalidad.

### ¿Cómo demuestras que `random_shortest` siempre produce una ruta óptima?
**Respuesta:** Por construcción. Solo elegimos vecinos que satisfacen `dist(origen→actual) + peso + dist(vecino→destino) == dist_total`. Esta condición es necesaria y suficiente para que el vecino pertenezca a algún camino de longitud mínima. Como siempre avanzamos por vecinos válidos y el grafo es finito, eventualmente llegamos al destino.

---

## 8. Comandos Rápidos para la Defensa

Si el profe te pide mostrar algo en vivo, estos comandos te sacan de apuros:

```bash
# Demo completa (Windows -> Tkinter por defecto)
python demo.py

# Solo reportes, sin ventana grafica
python demo.py --sin-animacion

# Simulacion corta para no hacer esperar al profe
python demo.py --ticks 300

# Ver tests
python -m pytest tests/ -v

# Ver un algoritmo de grafos aislado
python -c "from agv_sim.grafos import *; g=crear_grafo_cuadricula(5,5); print(dijkstra(g,(0,0),(4,4)))"

# Verificar requisitos manualmente
python -c "from agv_sim.simulacion import SimulacionAGV; from agv_sim.verificador import verificar_requisitos; s=SimulacionAGV(); r=s.correr(500); print(verificar_requisitos(s,r))"
```

---

*Documento preparado para la defensa del Lab #1 - INFO1167 Robótica.*
*Profesor: Alberto Caro (LCARO@UCT.CL)*
