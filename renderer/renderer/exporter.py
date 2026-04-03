import pygame
import cairo
import io

def export_to_png(surface, filename):
    pygame.image.save(surface, filename)

def export_to_svg(surface, filename):
    width, height = surface.get_size()
    data = pygame.image.tostring(surface, "RGBA")

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
