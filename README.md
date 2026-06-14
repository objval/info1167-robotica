# INFO1167 — Robotica (UCT)

Los 3 laboratorios del curso de Robotica, semestre 1 2026.

## Estructura

```
info1167-robotica/
├── lab1-agv-sim/          Lab 1: Simulacion AGV con grafos
├── lab2-mdp-smdp/         Lab 2: MDP y SMDP (Value Iteration)
├── lab3-qlearning-smdp/   Lab 3: Q-Learning SMDP
└── docs/                  Guia de estudio (PDF + LaTeX)
```

## Requisitos

```bash
pip install pygame numpy
```

Lab 1 tiene dependencias adicionales (ver su README).

## Lab 1 — Simulacion AGV

Simula 4 robots AGV en una bodega 2D usando algoritmos de grafos (BFS, Dijkstra, DFS). Animacion con Visual Python o Tkinter.

```bash
cd lab1-agv-sim
pip install -e .
python demo.py
```

Opciones:
```bash
python demo.py --sin-animacion    # solo reportes
python demo.py --tkinter          # animacion Tkinter (mas estable)
python demo.py --ticks 600        # simulacion corta
```

## Lab 2 — MDP y SMDP

Navegacion de robot por un mapa 2D usando Value Iteration. Compara MDP clasico (descuento fijo) con SMDP (descuento ajustado por tiempo estocastico).

```bash
cd lab2-mdp-smdp
python proyecto2.py
```

Controles:
- `1` = MDP clasico
- `2` = SMDP (con tiempo estocastico)
- `ESPACIO` = pausar/reanudar
- `R` = reiniciar
- Sliders: gamma, velocidad
- Toggles: mostrar valores, mostrar flechas

## Lab 3 — Q-Learning SMDP

El robot aprende a llegar a la meta por prueba y error. Q-Learning adaptado para SMDP con descuento temporal (gamma^tau).

```bash
cd lab3-qlearning-smdp
python proyecto3.py
```

Controles:
- `ENTER` = entrenar 500 episodios
- `T` = entrenar hasta convergencia
- `A` = animar robot con politica aprendida
- `R` = reiniciar
- Sliders: gamma, alpha, epsilon, velocidad

## Guia de estudio

En `docs/GuiaCompleta.pdf` (16 paginas). Cubre los 3 labs con explicaciones desde cero, bloques de codigo, cheat sheet para la defensa oral, y rubricas.

Para editar: `docs/GuiaCompleta.tex` (LaTeX).
