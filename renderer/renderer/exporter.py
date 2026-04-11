"""
exporter.py – Legacy Renderer Exporter (FÁZA 4)

Poskytuje:
- bezpečný export pygame Surface do PNG
- bezpečný export pygame Surface do SVG cez Cairo
- fallback pri chýbajúcich knižniciach
- ochranu pred None surface
- ochranu pred nevalidnými rozmermi
"""

import io

# ---------------------------------------------------------
# OPTIONAL DEPENDENCIES
# ---------------------------------------------------------
try:
    import pygame
except Exception:
    pygame = None

try:
    import cairo
except Exception:
    cairo = None


# ---------------------------------------------------------
# PNG EXPORT
# ---------------------------------------------------------
def export_to_png(surface, filename):
    """
    Export pygame Surface do PNG.
    Bezpečné: ak pygame alebo surface chýba → nič nespraví.
    """
    if pygame is None:
        print("[Exporter] PNG export skipped – pygame nie je dostupný.")
        return

    if surface is None:
        print("[Exporter] PNG export skipped – surface je None.")
        return

    try:
        pygame.image.save(surface, filename)
        print(f"[Exporter] PNG uložené: {filename}")
    except Exception as e:
        print(f"[Exporter] PNG export error: {e}")


# ---------------------------------------------------------
# SVG EXPORT
# ---------------------------------------------------------
def export_to_svg(surface, filename):
    """
    Export pygame Surface do SVG cez Cairo.
    Bezpečné: ak Cairo alebo pygame chýba → nič nespraví.
    """
    if pygame is None:
        print("[Exporter] SVG export skipped – pygame nie je dostupný.")
        return

    if cairo is None:
        print("[Exporter] SVG export skipped – Cairo nie je dostupné.")
        return

    if surface is None:
        print("[Exporter] SVG export skipped – surface je None.")
        return

    # Získanie rozmerov
    try:
        width, height = surface.get_size()
    except Exception:
        print("[Exporter] SVG export skipped – neviem získať rozmery surface.")
        return

    # Získanie pixelových dát
    try:
        data = pygame.image.tostring(surface, "RGBA")
    except Exception as e:
        print(f"[Exporter] SVG export error (tostring): {e}")
        return

    # Cairo export
    try:
        with cairo.SVGSurface(filename, width, height) as svg_surface:
            ctx = cairo.Context(svg_surface)

            img_surface = cairo.ImageSurface.create_for_data(
                bytearray(data),
                cairo.FORMAT_ARGB32,
                width,
                height,
                width * 4
            )

            ctx.set_source_surface(img_surface, 0, 0)
            ctx.paint()

        print(f"[Exporter] SVG uložené: {filename}")

    except Exception as e:
        print(f"[Exporter] SVG export error: {e}")
