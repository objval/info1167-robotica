"""
Generador de sprites amigables para la simulacion AGV.
Todas las posiciones son proporcionales al tamano para evitar recortes.
"""

import math
from io import BytesIO

from PIL import Image, ImageDraw

PALETA = {
    "rojo": "#e85d5d",
    "azul": "#4a90d9",
    "verde": "#5cb85c",
    "naranja": "#f0ad4e",
    "gris": "#95a5a6",
    "gris_claro": "#bdc3c7",
    "fondo": "#faf9f7",
    "grid": "#e8e6e1",
    "sombra": "#00000033",
    "blanco": "#ffffff",
    "negro": "#2c3e50",
    "destino": "#e74c3c",
    "base": "#8e44ad",
}


def _circulo(draw, cx, cy, r, fill, outline=None, width=1):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)


def _rect_redondeado(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def _oscurecer(hex_color, factor):
    h = hex_color.lstrip("#")
    r = max(0, int(int(h[0:2], 16) * factor))
    g = max(0, int(int(h[2:4], 16) * factor))
    b = max(0, int(int(h[4:6], 16) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def _aclarar(hex_color, factor):
    h = hex_color.lstrip("#")
    r = min(255, int(int(h[0:2], 16) * factor))
    g = min(255, int(int(h[2:4], 16) * factor))
    b = min(255, int(int(h[4:6], 16) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def generar_robot(tam=64, color="rojo", angulo=0):
    """
    Robot con ojos, antena y ruedas.
    Todo proporcional al tamano, sin recortes.
    """
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = tam * 0.5
    # Centro mas abajo para dar espacio a la antena arriba
    cy = tam * 0.58

    c = PALETA.get(color, PALETA["rojo"])
    c_oscuro = _oscurecer(c, 0.72)
    c_claro = _aclarar(c, 1.35)

    # Proporciones (todo basado en tam)
    r_rueda = tam * 0.09
    r_cabeza = tam * 0.16
    r_ojo = tam * 0.07
    r_pupila = tam * 0.038
    r_antena = tam * 0.055

    y_ruedas = cy + tam * 0.22
    y_cuerpo_top = cy - tam * 0.12
    y_cuerpo_bot = cy + tam * 0.18
    y_cabeza = cy - tam * 0.18
    y_antena_base = cy - tam * 0.32
    y_antena_punta = cy - tam * 0.42
    y_ojos = cy - tam * 0.20
    y_boca = cy - tam * 0.16

    # Sombra (ovalo plano debajo)
    sombra_y = cy + tam * 0.20
    draw.ellipse(
        [cx - tam * 0.30, sombra_y, cx + tam * 0.30, sombra_y + tam * 0.08],
        fill=PALETA["sombra"]
    )

    # Ruedas
    _circulo(draw, cx - tam * 0.22, y_ruedas, r_rueda, PALETA["negro"])
    _circulo(draw, cx + tam * 0.22, y_ruedas, r_rueda, PALETA["negro"])

    # Cuerpo (rectangulo redondeado)
    _rect_redondeado(
        draw,
        [cx - tam * 0.22, y_cuerpo_top, cx + tam * 0.22, y_cuerpo_bot],
        radius=int(tam * 0.08),
        fill=c, outline=c_oscuro, width=max(1, int(tam * 0.03))
    )

    # Brillo en cuerpo
    _rect_redondeado(
        draw,
        [cx - tam * 0.16, y_cuerpo_top + tam * 0.04, cx + tam * 0.10, y_cuerpo_top + tam * 0.10],
        radius=int(tam * 0.04),
        fill=c_claro
    )

    # Cabeza
    _circulo(draw, cx, y_cabeza, r_cabeza, c, outline=c_oscuro, width=max(1, int(tam * 0.03)))

    # Antena (linea + punto)
    draw.line(
        [(cx, y_antena_base), (cx, y_antena_punta)],
        fill=PALETA["negro"], width=max(1, int(tam * 0.025))
    )
    _circulo(draw, cx, y_antena_punta, r_antena, PALETA["destino"])

    # Ojos: rotan segun angulo para mostrar direccion
    rad = math.radians(-angulo)
    ojo_offset = tam * 0.07
    ojo_dx = math.cos(rad) * ojo_offset
    ojo_dy = math.sin(rad) * ojo_offset

    # Ojo izquierdo
    _circulo(draw, cx - tam * 0.08 + ojo_dx * 0.3, y_ojos + ojo_dy * 0.3, r_ojo, PALETA["blanco"])
    _circulo(draw, cx - tam * 0.08 + ojo_dx, y_ojos + ojo_dy, r_pupila, PALETA["negro"])

    # Ojo derecho
    _circulo(draw, cx + tam * 0.08 + ojo_dx * 0.3, y_ojos + ojo_dy * 0.3, r_ojo, PALETA["blanco"])
    _circulo(draw, cx + tam * 0.08 + ojo_dx, y_ojos + ojo_dy, r_pupila, PALETA["negro"])

    # Boca (sonrisa)
    draw.arc(
        [cx - tam * 0.06, y_boca - tam * 0.03, cx + tam * 0.06, y_boca + tam * 0.03],
        start=0, end=180, fill=c_oscuro, width=max(1, int(tam * 0.025))
    )

    return img


def generar_carrito(tam=48, color="gris"):
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = tam * 0.5
    cy = tam * 0.52

    c = PALETA.get(color, PALETA["gris"])
    c_oscuro = _oscurecer(c, 0.70)

    # Sombra
    sombra_y = cy + tam * 0.16
    draw.ellipse(
        [cx - tam * 0.22, sombra_y, cx + tam * 0.22, sombra_y + tam * 0.06],
        fill=PALETA["sombra"]
    )

    # Ruedas
    r_rueda = tam * 0.07
    _circulo(draw, cx - tam * 0.16, cy + tam * 0.16, r_rueda, PALETA["negro"])
    _circulo(draw, cx + tam * 0.16, cy + tam * 0.16, r_rueda, PALETA["negro"])

    # Caja
    _rect_redondeado(
        draw,
        [cx - tam * 0.22, cy - tam * 0.14, cx + tam * 0.22, cy + tam * 0.14],
        radius=int(tam * 0.06),
        fill=c, outline=c_oscuro, width=max(1, int(tam * 0.03))
    )

    # Etiqueta blanca
    _rect_redondeado(
        draw,
        [cx - tam * 0.14, cy - tam * 0.06, cx + tam * 0.14, cy + tam * 0.04],
        radius=int(tam * 0.03),
        fill=PALETA["blanco"]
    )

    # Lineas de etiqueta
    lw = max(1, int(tam * 0.03))
    draw.line([(cx - tam * 0.08, cy - tam * 0.01), (cx + tam * 0.08, cy - tam * 0.01)], fill=c_oscuro, width=lw)
    draw.line([(cx - tam * 0.05, cy + tam * 0.03), (cx + tam * 0.05, cy + tam * 0.03)], fill=c_oscuro, width=lw)

    return img


def generar_base(tam=56, color="base"):
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = tam * 0.5
    cy = tam * 0.55

    c = PALETA.get(color, PALETA["base"])
    c_oscuro = _oscurecer(c, 0.70)

    # Sombra
    sombra_y = cy + tam * 0.14
    draw.ellipse(
        [cx - tam * 0.26, sombra_y, cx + tam * 0.26, sombra_y + tam * 0.06],
        fill=PALETA["sombra"]
    )

    # Plataforma exterior
    draw.ellipse(
        [cx - tam * 0.28, cy - tam * 0.08, cx + tam * 0.28, cy + tam * 0.18],
        fill=c, outline=c_oscuro, width=max(1, int(tam * 0.03))
    )

    # Plataforma interior
    draw.ellipse(
        [cx - tam * 0.18, cy - tam * 0.02, cx + tam * 0.18, cy + tam * 0.12],
        fill=_aclarar(c, 1.4), outline=c_oscuro, width=max(1, int(tam * 0.02))
    )

    # Rayo
    rayo = [
        (cx - tam * 0.02, cy - tam * 0.02),
        (cx + tam * 0.06, cy - tam * 0.02),
        (cx + tam * 0.01, cy + tam * 0.06),
        (cx + tam * 0.09, cy + tam * 0.06),
        (cx + tam * 0.02, cy + tam * 0.16),
        (cx - tam * 0.02, cy + tam * 0.08),
        (cx - tam * 0.09, cy + tam * 0.08),
    ]
    draw.polygon(rayo, fill=PALETA["blanco"], outline=c_oscuro)

    return img


def generar_destino(tam=40):
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = tam * 0.5
    cy = tam * 0.55

    c = PALETA["destino"]
    c_oscuro = _oscurecer(c, 0.70)

    # Sombra base
    draw.ellipse(
        [cx - tam * 0.08, cy + tam * 0.18, cx + tam * 0.08, cy + tam * 0.24],
        fill=PALETA["sombra"]
    )

    # Palo
    draw.line(
        [(cx, cy - tam * 0.30), (cx, cy + tam * 0.18)],
        fill=PALETA["negro"], width=max(1, int(tam * 0.05))
    )

    # Bandera (triangulo)
    bandera = [
        (cx + tam * 0.02, cy - tam * 0.30),
        (cx + tam * 0.22, cy - tam * 0.20),
        (cx + tam * 0.02, cy - tam * 0.10),
    ]
    draw.polygon(bandera, fill=c, outline=c_oscuro)

    # Base del palo
    _circulo(draw, cx, cy + tam * 0.18, tam * 0.06, PALETA["negro"])

    return img


def generar_suelo_tile(tam=64):
    img = Image.new("RGBA", (tam, tam), PALETA["fondo"])
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, tam - 1, tam - 1], outline=PALETA["grid"], width=1)
    return img


def _img_to_tk(img):
    from tkinter import PhotoImage
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return PhotoImage(data=buffer.read())


def crear_sprite_sheet(robots_colores=None, tam_robot=56, tam_carrito=40, tam_base=48, tam_destino=36):
    from tkinter import PhotoImage

    if robots_colores is None:
        robots_colores = ["rojo", "azul", "verde", "naranja"]

    sheet = {"robot": {}, "carrito": {}, "base": {}, "destino": None, "suelo": None}

    for color in robots_colores:
        sheet["robot"][color] = {}
        for ang in range(0, 360, 30):
            img = generar_robot(tam=tam_robot, color=color, angulo=ang)
            sheet["robot"][color][ang] = _img_to_tk(img)

    for color in list(robots_colores) + ["gris"]:
        img = generar_carrito(tam=tam_carrito, color=color)
        sheet["carrito"][color] = _img_to_tk(img)

    for color in robots_colores:
        img = generar_base(tam=tam_base, color=color)
        sheet["base"][color] = _img_to_tk(img)

    sheet["destino"] = _img_to_tk(generar_destino(tam_destino))
    sheet["suelo"] = _img_to_tk(generar_suelo_tile(64))

    return sheet


def obtener_robot_mas_cercano(sheet, color, angulo):
    angulos = sorted(sheet["robot"][color].keys())
    angulo = angulo % 360
    return sheet["robot"][color][min(angulos, key=lambda a: abs(a - angulo))]
