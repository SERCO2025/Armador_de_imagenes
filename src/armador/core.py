"""Operaciones de imagen sin servicios externos ni remuestreo automático.

Compatible con Python 3.7. Las decisiones de recorte y empalme se devuelven
como propuestas para que la interfaz pueda pedir confirmación cuando haga falta.
"""
from __future__ import division

import os
import re

from PIL import Image
import numpy as np


SUPPORTED_IMAGE_EXTENSIONS = frozenset((
    ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp",
))


def pair_images(paths):
    """Empareja capturas llamadas Nombre 1.ext y Nombre 2.ext.

    Devuelve un diccionario con cuatro listas: pairs, incomplete, ambiguous
    y unmatched. La comparación del nombre base no distingue mayúsculas.
    No elige arbitrariamente si hay más de un candidato para una misma mitad.
    Los resultados propuestos usan PNG para evitar pérdidas en texto y bordes;
    esta función no lee ni modifica archivos.
    """
    groups = {}
    unmatched = []
    for path in sorted(paths, key=lambda value: str(value).lower()):
        filename = os.path.basename(str(path))
        stem, extension = os.path.splitext(filename)
        if extension.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            continue
        match = re.match(r"^(.+?)\s+([12])$", stem)
        if not match:
            unmatched.append(str(path))
            continue

        base_name = match.group(1).strip()
        if not base_name:
            unmatched.append(str(path))
            continue
        key = base_name.casefold()
        if key not in groups:
            groups[key] = {
                "base_name": base_name,
                "top": [],
                "bottom": [],
            }
        side = "top" if match.group(2) == "1" else "bottom"
        groups[key][side].append(str(path))

    result = {
        "pairs": [],
        "incomplete": [],
        "ambiguous": [],
        "unmatched": unmatched,
    }
    for key in sorted(groups):
        group = groups[key]
        top = group["top"]
        bottom = group["bottom"]
        if len(top) > 1 or len(bottom) > 1:
            result["ambiguous"].append({
                "base_name": group["base_name"],
                "top_candidates": list(top),
                "bottom_candidates": list(bottom),
                "reason": "Hay más de un archivo candidato para una mitad.",
            })
        elif not top or not bottom:
            result["incomplete"].append({
                "base_name": group["base_name"],
                "missing_part": "top" if not top else "bottom",
                "available_files": list(top or bottom),
            })
        else:
            result["pairs"].append({
                "base_name": group["base_name"],
                "top": top[0],
                "bottom": bottom[0],
                "output_name": group["base_name"] + ".png",
            })
    return result


def detect_side_borders(image, black_threshold=18, row_fraction=0.985,
                        max_border_fraction=0.20, min_content_width=32):
    """Propone límites laterales oscuros sin modificar la imagen.

    Devuelve (left, right) como límites de recorte Pillow (right exclusivo).
    Solo considera una columna como borde si es oscura en casi todas las filas.
    El recorte queda limitado para evitar eliminar demasiado contenido.
    """
    gray = np.asarray(image.convert("L"))
    height, width = gray.shape
    if width < min_content_width or height == 0:
        return (0, width)
    dark_fraction = np.mean(gray <= black_threshold, axis=0)
    max_border = int(width * max_border_fraction)
    left = 0
    while left < min(max_border, width - min_content_width):
        if dark_fraction[left] < row_fraction:
            break
        left += 1
    right = width
    while right > max(left + min_content_width, width - max_border):
        if dark_fraction[right - 1] < row_fraction:
            break
        right -= 1
    if right - left < min_content_width:
        return (0, width)
    return (left, right)


def crop_side_borders(image, bounds):
    """Aplica explícitamente unos límites ya revisados; no escala la imagen."""
    left, right = bounds
    if left < 0 or right > image.width or right <= left:
        raise ValueError("Límites de recorte inválidos")
    return image.crop((left, 0, right, image.height))


def _gray_array(image):
    return np.asarray(image.convert("L"), dtype=np.float32)


def find_vertical_overlap(top, bottom, min_overlap=40, max_overlap=None,
                          sample_width=320, stride=2):
    """Busca el solapamiento vertical más probable entre dos capturas.

    Compara franjas inferiores de top con franjas superiores de bottom.
    Devuelve un dict con píxeles de solapamiento, error y confianza orientativa.
    El resultado es una propuesta; no se acepta automáticamente.
    """
    if top.width != bottom.width:
        raise ValueError("Las imágenes deben tener el mismo ancho para compararse")
    limit = min(top.height, bottom.height)
    if max_overlap is None:
        max_overlap = min(limit, max(min_overlap, int(limit * 0.45)))
    max_overlap = min(int(max_overlap), limit)
    min_overlap = max(1, int(min_overlap))
    if max_overlap < min_overlap:
        raise ValueError("Rango de solapamiento insuficiente")

    a = _gray_array(top)
    b = _gray_array(bottom)
    if top.width > sample_width:
        step = max(1, int(top.width / sample_width))
        a = a[:, ::step]
        b = b[:, ::step]
    scores = []
    for overlap in range(min_overlap, max_overlap + 1, max(1, int(stride))):
        aa = a[-overlap:, :]
        bb = b[:overlap, :]
        if aa.shape != bb.shape:
            continue
        # La diferencia de gradientes reduce el efecto de ligeros cambios de brillo.
        ga = np.diff(aa, axis=1)
        gb = np.diff(bb, axis=1)
        score = float(np.mean(np.abs(ga - gb))) if ga.size else float(np.mean(np.abs(aa - bb)))
        scores.append((score, overlap))
    if not scores:
        raise ValueError("No se pudo evaluar un solapamiento")
    scores.sort()
    best_score, best_overlap = scores[0]
    second_score = scores[1][0] if len(scores) > 1 else best_score
    separation = max(0.0, second_score - best_score)
    confidence = separation / max(second_score, 1.0)
    return {
        "overlap_pixels": best_overlap,
        "error": best_score,
        "confidence": confidence,
        "needs_review": confidence < 0.015,
    }


def stitch_vertical(top, bottom, overlap_pixels):
    """Une dos imágenes usando el solapamiento indicado, sin interpolación.

    Conserva la parte superior de la primera captura y añade la parte de la
    segunda situada debajo del solapamiento. Exige mismo modo y ancho.
    """
    if top.width != bottom.width:
        raise ValueError("Las imágenes deben tener el mismo ancho")
    if top.mode != bottom.mode:
        raise ValueError("Las imágenes deben tener el mismo modo de color")
    overlap_pixels = int(overlap_pixels)
    if overlap_pixels < 0 or overlap_pixels > min(top.height, bottom.height):
        raise ValueError("Solapamiento inválido")
    tail = bottom.crop((0, overlap_pixels, bottom.width, bottom.height))
    result = Image.new(top.mode, (top.width, top.height + tail.height))
    result.paste(top, (0, 0))
    result.paste(tail, (0, top.height))
    return result
