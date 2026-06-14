#!/usr/bin/env python3
"""Genera PDF completo de defensa: FAQ, codigo, archivos, problemas Mac."""

from pathlib import Path
from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("DejaVu", "", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "INFO1167 Robotica Lab #1 - Guia de Defensa", new_x="LMARGIN", new_y="NEXT", align="L")
            self.cell(0, 8, f"Pagina {self.page_no()}", new_x="LMARGIN", new_y="NEXT", align="R")
            self.set_draw_color(200, 200, 200)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(3)

    def chapter_title(self, title, level=1):
        if level == 1:
            self.set_font("DejaVu", "B", 16)
            self.set_text_color(30, 58, 138)
            self.ln(8)
            self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(30, 58, 138)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(4)
        else:
            self.set_font("DejaVu", "B", 12)
            self.set_text_color(50, 50, 50)
            self.ln(6)
            self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def body_text(self, text):
        self.set_font("DejaVu", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(self.w - self.l_margin - self.r_margin, 5.5, text)
        self.ln(2)

    def code_block(self, code):
        self.set_font("DejaVu", "", 8)
        self.set_text_color(60, 60, 60)
        self.set_fill_color(245, 245, 245)
        self.multi_cell(self.w - self.l_margin - self.r_margin, 4.5, code, fill=True)
        self.ln(2)

    def bullet(self, text):
        self.set_font("DejaVu", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(5, 5.5, "\u2022", new_x="RIGHT", new_y="TOP")
        self.multi_cell(self.w - self.l_margin - self.r_margin - 5, 5.5, text)
        self.ln(1)

    def highlight_box(self, text):
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(30, 58, 138)
        self.set_fill_color(235, 245, 255)
        self.multi_cell(self.w - self.l_margin - self.r_margin, 6, text, fill=True)
        self.ln(2)


pdf = PDF()
pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
pdf.set_auto_page_break(auto=True, margin=20)

# ============================================================
# PORTADA
# ============================================================
pdf.add_page()
pdf.set_font("DejaVu", "B", 28)
pdf.set_text_color(30, 58, 138)
pdf.ln(60)
pdf.cell(0, 15, "INFO1167 Robotica", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 15, "Laboratorio #1", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("DejaVu", "", 16)
pdf.set_text_color(80, 80, 80)
pdf.ln(10)
pdf.cell(0, 10, "Guia Completa de Defensa", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(20)
pdf.set_font("DejaVu", "", 11)
pdf.cell(0, 8, "Nico Perez", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 8, "Ingenieria Civil Informatica - UCT", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 8, "Profesor: Alberto Caro (LCARO@UCT.CL)", new_x="LMARGIN", new_y="NEXT", align="C")

# ============================================================
# CAP 1: ARCHIVOS A TENER ABIERTOS
# ============================================================
pdf.add_page()
pdf.chapter_title("1. Archivos que Debes Tener Abiertos")
pdf.body_text("Durante la defensa, el profesor puede pedirte que muestres el codigo. Ten estos archivos abiertos en tu editor (VS Code / PyCharm) para acceder rapido:")

archivos = [
    ("demo.py", "Punto de entrada. Pipeline: tests -> simulacion -> reporte -> animacion."),
    ("src/agv_sim/modelos.py", "Dataclasses: Robot, Carrito, ConfigSimulacion. Modelado del mundo."),
    ("src/agv_sim/grafos.py", "ALGORITMOS ESTRELLA. BFS, DFS, Dijkstra, random_shortest."),
    ("src/agv_sim/simulacion.py", "Maquina de estados FSM. Ciclo completo del robot."),
    ("src/agv_sim/animacion_tkinter.py", "Visualizacion profesional. Rutas, controles, metricas. Dark theme."),
    ("src/agv_sim/sprites.py", "Sprites propios con Pillow. No imagenes descargadas."),
    ("tests/test_grafos.py", "Tests de algoritmos. BFS, Dijkstra, random_shortest."),
    ("tests/test_simulacion.py", "Tests de simulacion. Entregas, estados, baterias, colores."),
    ("src/agv_sim/verificador.py", "Verificacion automatica R1-R8. Cumplimiento total."),
]

for nombre, desc in archivos:
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, nombre, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 5.5, desc)
    pdf.ln(2)

pdf.highlight_box("TIP: Abre VS Code con el proyecto y deja pinned los archivos grafos.py, simulacion.py y animacion_pygame.py.")

# ============================================================
# CAP 2: POR QUE NO FUNCIONA VPYTHON EN MAC
# ============================================================
pdf.add_page()
pdf.chapter_title("2. Por Que VPython No Funciona en macOS")

pdf.body_text("El laboratorio pide Visual Python. Intentamos VPython 7.6 en macOS 15.7.3 y fallo. Diagnostico:")

pdf.chapter_title("2.1 El Error", level=2)
pdf.code_block("""*** Terminating app due to uncaught exception 'NSInvalidArgumentException',
reason: '-[NSApplication macOSVersion]: unrecognized selector sent to instance ...'
libc++abi: terminating due to uncaught exception of type NSException""")

pdf.body_text("VPython 7.6 incluye Tcl/Tk 8.6 que intenta llamar al selector macOSVersion de NSApplication. En macOS 15.7.3, este selector no existe. Es un bug de compatibilidad conocido entre VPython y macOS Sequoia.")

pdf.chapter_title("2.2 Soluciones Intentadas", level=2)
pdf.bullet("Python 3.12/3.13 desde python.org -> mismo error (Tk bundled tiene el bug).")
pdf.bullet("Tcl/Tk 8.6.17 via Homebrew -> pyenv Python no es Framework build, Tkinter no crea ventanas.")
pdf.bullet("Homebrew Python + python-tk@3.12 -> bottle precompilado enlaza contra Tcl/Tk 9.")

pdf.chapter_title("2.3 La Solucion", level=2)
pdf.bullet("TKINTER como motor principal. Funciona perfectamente en macOS 15 con Tcl/Tk 8.6 via Homebrew.")
pdf.bullet("En Windows, VPython abre pestanas en blanco por bug WebGL, asi que Tkinter es la solucion multiplataforma.")
pdf.bullet("En demo.py, Tkinter es el default.")

pdf.highlight_box("Para la defensa: Intentamos VPython como pide el laboratorio, pero tiene un bug de compatibilidad con macOS 15.7.3 documentado en la comunidad. Como alternativa profesional, implementamos visualizacion con Tkinter que cumple la misma funcion y funciona perfectamente en macOS 15 tras instalar Tcl/Tk 8.6 via Homebrew.")

# ============================================================
# CAP 3: FAQ - PREGUNTAS DEL PROFESOR
# ============================================================
pdf.add_page()
pdf.chapter_title("3. Preguntas Frecuentes de la Defensa")

faq = [
    ("Que es un AGV?", "AGV = Automated Guided Vehicle. Robot autonomo que se mueve por un almacen siguiendo rutas calculadas por algoritmos de grafos. Amazon, Alibaba y DHL usan miles de AGVs."),
    ("Por que usan un grafo para modelar la bodega?", "La bodega es una cuadricula 10x8. Cada celda es un nodo y los robots se mueven entre nodos adyacentes (aristas). Esto es un grafo no dirigido. Los algoritmos de grafos permiten encontrar rutas, la mas corta, o explorar todas las opciones."),
    ("Cual es la diferencia entre BFS y Dijkstra?", "BFS encuentra el camino con menos aristas sin considerar pesos. Dijkstra encuentra el camino con menor costo total. En nuestra grilla sin pesos, ambos dan el mismo resultado, pero Dijkstra es mas general: si anadieramos pesos (zonas lentas), solo Dijkstra seguiria siendo optimo."),
    ("Por que no usan solo Dijkstra?", "El laboratorio pide demostrar BFS, DFS, Dijkstra y al menos una ruta. Ademas, random_shortest usa Dijkstra internamente pero anade variacion aleatoria: cuando hay varios caminos optimos de igual longitud, elige uno al azar."),
    ("Que hace random_shortest?", "1. Calcula distancias mas cortas desde el robot con Dijkstra. 2. Retrocede desde el destino eligiendo aleatoriamente entre vecinos que mantienen la propiedad de ruta optima. Resultado: ruta optima pero con variacion en cada ejecucion."),
    ("Por que rotan de a 10 grados por tick?", "El laboratorio lo pide explicitamente. Implementamos _rotar_y_mover que calcula el angulo con atan2(dy, dx) y gira 10 grados por tick hasta alinear. Simula un robot real que no gira instantaneamente."),
    ("Que es atan2 y por que no atan?", "atan2(y, x) devuelve el angulo correcto en todos los cuadrantes (0 a 360). atan(y/x) falla en el segundo y tercer cuadrante porque pierde el signo. Ej: atan2(1, -1) = 135 grados, atan(1/-1) = -45 grados (incorrecto)."),
    ("Como sabe el carrito que sigue al robot?", "En estado LLEVANDO_CARRITO, cada tick actualizamos carrito.nodo = robot.nodo. El carrito teletransporta a la posicion del robot, simulando que lo lleva consigo."),
    ("Como funciona la maquina de estados?", "5 estados en ciclo cerrado: EN_BASE (espera) -> BUSCANDO_CARRITO (se mueve hacia carrito) -> LLEVANDO_CARRITO (se mueve hacia destino) -> VOLVIENDO_BASE (vuelve a base) -> CARGANDO (bateria sube 5% por tick) -> EN_BASE."),
    ("Por que cada robot tiene color unico?", "Requisito R3: Carrito adopta color unico del robot asignado. Usamos 4 colores: rojo, azul, verde, naranja. Al recoger un carrito, cambia al color del robot. Al entregar, vuelve a gris."),
    ("Cuantos tests tienen?", "11 tests con pytest: 5 de grafos (Dijkstra, BFS, DFS, random_shortest, todas_las_rutas) y 6 de simulacion (entregas, estados, baterias, cambio de color, resumen JSON, reporte R1-R8)."),
    ("Que pasa con 100 robots?", "La arquitectura soporta escalado. El cuello de botella es la asignacion de carritos (O(n*m)). Para 100 robots, usariamos un algoritmo de matching tipo Hungaro o dividiriamos la bodega en zonas."),
    ("Como evitan colisiones?", "En la version actual los robots pueden ocupar el mismo nodo. La deteccion de colisiones es facil de anadir: verificar si dos robots comparten nodo en el mismo tick, y si es asi, uno espera. La arquitectura modular lo permite."),
    ("Que es una dataclass?", "@dataclass de Python genera automaticamente __init__, __repr__, __eq__, etc. Nos ahorra codigo repetitivo. Es codigo limpio y Pythonico."),
    ("Por que usan seed?", "Para que la simulacion sea REPRODUCIBLE. Con semilla=123, siempre obtienes los mismos carritos, bases y destinos. Es crucial para debugging y la defensa."),
]

for pregunta, respuesta in faq:
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(30, 58, 138)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 6, f"P: {pregunta}")
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 5.5, f"R: {respuesta}")
    pdf.ln(3)

# ============================================================
# CAP 4: CODIGO CLAVE EXPLICADO
# ============================================================
pdf.add_page()
pdf.chapter_title("4. Codigo Clave con Explicaciones")

pdf.chapter_title("4.1 Dijkstra - Ruta mas corta", level=2)
pdf.body_text("Calcula distancia minima desde un nodo a todos los demas. Usa min-heap para eficiencia O((V+E) log V).")
pdf.code_block("""def dijkstra(grafo, inicio):
    dist = {n: float('inf') for n in grafo.nodes}
    dist[inicio] = 0
    visitados = set()
    heap = [(0, inicio)]
    while heap:
        d_actual, actual = heapq.heappop(heap)
        if actual in visitados:
            continue
        visitados.add(actual)
        for vecino in grafo.neighbors(actual):
            peso = grafo[actual][vecino].get('peso', 1)
            nueva = d_actual + peso
            if nueva < dist[vecino]:
                dist[vecino] = nueva
                heapq.heappush(heap, (nueva, vecino))
    return dist""")
pdf.body_text("El heap extrae siempre el nodo con menor distancia. Cuando un nodo sale del heap, su distancia es definitiva y optima.")

pdf.chapter_title("4.2 Random Shortest", level=2)
pdf.body_text("Usa Dijkstra para calcular distancias, luego retrocede desde el destino eligiendo aleatoriamente entre vecinos optimos.")
pdf.code_block("""def ruta_corta_aleatoria(grafo, inicio, fin, semilla=None):
    rng = random.Random(semilla)
    dist = dijkstra(grafo, inicio)
    if fin not in dist or dist[fin] == float('inf'):
        return None
    ruta = [fin]
    while ruta[-1] != inicio:
        actual = ruta[-1]
        vecinos = list(grafo.neighbors(actual))
        optimos = [v for v in vecinos if dist[v] == dist[actual] - 1]
        if not optimos:
            return None
        ruta.append(rng.choice(optimos))
    return list(reversed(ruta))""")
pdf.body_text("La condicion dist[v] == dist[actual] - 1 elige solo vecinos que mantienen la propiedad de estar un paso mas cerca del inicio.")

pdf.chapter_title("4.3 Maquina de Estados", level=2)
pdf.body_text("Robot opera como FSM con 5 estados en ciclo cerrado.")
pdf.code_block("""if robot.estado == EstadoRobot.EN_BASE:
    self._asignar_carrito(robot)
elif robot.estado == EstadoRobot.BUSCANDO_CARRITO:
    if robot.nodo == carrito.nodo:
        robot.estado = EstadoRobot.LLEVANDO_CARRITO
    else:
        self._mover_robot_hacia(robot, carrito.nodo)
elif robot.estado == EstadoRobot.LLEVANDO_CARRITO:
    if robot.nodo == carrito.destino:
        self._entregar_carrito(robot, carrito)
    else:
        self._mover_robot_hacia(robot, carrito.destino)
        carrito.nodo = robot.nodo  # Sigue al robot""")

pdf.chapter_title("4.4 Rotacion con atan2", level=2)
pdf.code_block("""def _angulo_deseado(self, robot, destino):
    dx = destino[0] - robot.nodo[0]
    dy = destino[1] - robot.nodo[1]
    return math.atan2(dy, dx)

def _rotar_y_mover(self, robot, destino):
    deseado = self._angulo_deseado(robot, destino)
    diff = deseado - robot.angulo
    while diff > math.pi:  diff -= 2*math.pi
    while diff < -math.pi: diff += 2*math.pi
    if abs(diff) > math.radians(10):
        robot.angulo += math.copysign(math.radians(10), diff)
    else:
        robot.angulo = deseado
        robot.nodo = destino""")
pdf.body_text("La normalizacion del angulo diff es crucial. Sin ella, un robot podria dar una vuelta completa en vez de girar 10 grados correctamente.")

pdf.chapter_title("4.5 Verificador R1-R8", level=2)
pdf.code_block("""def verificar_requisitos(sim, resumen):
    checks = [
        {"id": "R1", "ok": len(sim.robots) == 4, ...},
        {"id": "R2", "ok": resumen['entregas_totales'] > 0, ...},
        {"id": "R3", "ok": resumen['colores_unicos'] == 4, ...},
        {"id": "R4", "ok": resumen['modo_ruta'] in [...], ...},
        {"id": "R5", "ok": ..., "requisito": "Variacion aleatoria"},
        {"id": "R6", "ok": resumen['paso_rotacion'] == 10.0, ...},
        {"id": "R7", "ok": ..., "requisito": "Entrega y retorno"},
        {"id": "R8", "ok": ..., "requisito": "Temas de grafos"},
    ]
    return {"aprobados": sum(1 for c in checks if c['ok']),
            "porcentaje": round(aprobados/8*100, 1)}""")

# ============================================================
# CAP 5: COMANDOS RAPIDOS
# ============================================================
pdf.add_page()
pdf.chapter_title("5. Comandos Rapidos para la Defensa")

comandos = [
    ("Ver todos los tests", "pytest tests/ -v"),
    ("Demo completa (Tkinter)", "python demo.py"),
    ("Demo con Tkinter (explicito)", "python demo.py --tkinter"),
    ("Demo rapida", "python demo.py --ticks 300"),
    ("Demo lenta para explicar", "python demo.py --velocidad 5"),
    ("Solo reportes sin GUI", "python demo.py --no-gui"),
    ("Ver resumen JSON", "cat outputs/resumen.json | python -m json.tool"),
    ("Ver reporte R1-R8", "cat outputs/reporte_requisitos.json | python -m json.tool"),
]

for desc, cmd in comandos:
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, desc, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.set_fill_color(245, 245, 245)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 5, cmd, fill=True)
    pdf.ln(2)

pdf.highlight_box("TIP: Practica estos comandos antes de la defensa. Escribe los mas importantes en un post-it.")

# ============================================================
# CAP 6: CONSEJOS PARA LA DEFENSA
# ============================================================
pdf.add_page()
pdf.chapter_title("6. Consejos para la Defensa")

tips = [
    "Empieza corriendo 'python demo.py'. Mientras carga, explica el concepto de AGV.",
    "Cuando la animacion corra, senala las rutas punteadas: 'Ahi ven como Dijkstra calculo el camino optimo'.",
    "Pausa la animacion (ESPACIO) cuando un robot gire: 'Miren, atan2 calculo ese angulo y gira de a 10 grados'.",
    "Muestra el panel de requisitos: 'Ahi ven que cumplimos los 8 requisitos al 100%'.",
    "Si te preguntan por VPython en Mac, muestra este PDF o explica el bug NSInvalidArgumentException.",
    "Si te preguntan por escalabilidad, responde honestamente: 'Con 4 robots funciona perfecto. Para 100, dividiriamos la bodega en zonas'.",
    "Muestra los tests: 'Tenemos 11 tests que verifican todo'.",
    "Muestra los sprites: 'Los iconos son codigo propio con Pillow, no imagenes descargadas'.",
    "Si te atascas en una pregunta, di: 'Buena pregunta. En la version actual no lo implementamos, pero la arquitectura modular lo permite.'",
    "Lleva el proyecto en GitHub y localmente. Si hay problemas de red, usa la version local.",
]

for i, tip in enumerate(tips, 1):
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, f"{i}.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 5.5, tip)
    pdf.ln(2)

# Guardar
Path("docs").mkdir(exist_ok=True)
pdf.output("docs/INFO1167_Lab1_Guia_Defensa.pdf")
print("PDF generado: docs/INFO1167_Lab1_Guia_Defensa.pdf")
