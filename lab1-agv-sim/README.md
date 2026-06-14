# robotica-lab1-agv-sim

Implementacion completa del **Lab #1 INFO1167 Robotica** (UCT).
Simula 4 robots AGV en una bodega 2D usando algoritmos de grafos.

## Que incluye

- Motor de simulacion AGV con semillas deterministas
- 4 robots, asignacion aleatoria de carritos, recogida/entrega, retorno a base, carga al 100%, reinicio de ciclo
- Cambio de color del carrito al color del robot asignado
- Rotacion en pasos de 10 grados
- Algoritmos de grafos:
  - BFS (busqueda en anchura)
  - Dijkstra (ruta mas corta)
  - DFS (profundidad)
  - Enumeracion de rutas simples
- Animacion 3D con **Visual Python**
- Pipeline por etapas y reporte automatico de requisitos

## Demo completa en un archivo

Corre un solo archivo para todo:

```bash
python demo.py
```

Opciones:
```bash
python demo.py --sin-animacion      # solo reportes, sin animacion
python demo.py --tkinter            # usar animacion Tkinter (mas estable que VPython)
python demo.py --ticks 600          # simulacion mas corta
python demo.py --velocidad 15       # animacion mas rapida
```

**Nota:** Visual Python (VPython) a veces abre una pestana del navegador en blanco en Windows. Si pasa eso, `demo.py` cambia automaticamente a la animacion Tkinter. O usa `--tkinter` directamente.

## Pipeline por etapas (alternativa)

```bash
cd robotica-lab1-agv-sim
python3 -m venv .venv
source .venv/bin/activate

# Etapa 1: dependencias
python scripts/pipeline.py setup

# Etapa 2: tests
python scripts/pipeline.py test

# Etapa 3: simulacion
python scripts/pipeline.py simular --ticks 1000 --semilla 42 --modo-ruta random_shortest --salida outputs

# Etapa 4: verificar requisitos
python scripts/pipeline.py verificar --salida outputs

# Todo de una
python scripts/pipeline.py todo --ticks 1000 --semilla 42 --modo-ruta random_shortest --salida outputs
```

### Animacion Visual Python

```bash
python scripts/ejecutar_vpython.py --ticks 600 --velocidad 10
```

Requiere pantalla/navegador (VPython abre un servidor local).

### Modos de ruta

- `random_shortest` (default): ruta mas corta con desempate aleatorio
- `dijkstra`: ruta corta determinista
- `bfs`: busqueda en anchura

## Salidas

Despues de simular:

- `outputs/resumen.json` -> entregas, entidades, config, evidencia de grafos
- `outputs/reporte_requisitos.json` -> checklist de requisitos del lab (R1..R8)
- `outputs/captura.png` -> imagen para la defensa

## Estructura

- `demo.py` - demo completa en un archivo
- `scripts/pipeline.py` - pipeline por etapas
- `scripts/ejecutar_simulacion.py` - simulacion + archivos
- `scripts/ejecutar_vpython.py` - animacion Visual Python
- `src/agv_sim/modelos.py` - entidades y configuracion
- `src/agv_sim/grafos.py` - grafos + BFS/DFS/Dijkstra + rutas
- `src/agv_sim/simulacion.py` - maquina de estados AGV
- `src/agv_sim/verificador.py` - verificador de requisitos
- `src/agv_sim/visualizador.py` - exportador de imagen matplotlib
- `src/agv_sim/animacion_vpython.py` - animador 3D Visual Python
- `tests/` - verificacion automatica
- `docs/assets/` - PDF original del lab + texto extraido

## Puntos para la defensa

1. Bodega modelada como grafo 2D de nodos QR.
2. Cuatro AGV inician en las esquinas y reciben asignacion aleatoria.
3. El carrito cambia al color del robot; vuelve a gris despues de entregar.
4. Rotacion de 10 grados antes de moverse por la ruta del grafo.
5. Ciclo completo: asignar -> recoger -> entregar -> volver -> cargar -> reiniciar.
6. Evidencia de temas de grafos: DFS, Dijkstra, rutas multiples.
7. Visual Python para la animacion 3D.
8. Geometria con atan2 y rotacion paso a paso.

## Licencia

MIT
