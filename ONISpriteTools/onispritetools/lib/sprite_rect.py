# allows using class type as return type
from __future__ import annotations
import xml.etree.ElementTree as ET
import inkex
from . import utils



DEFAULT_PIVOT_POS : tuple[float, float] = (0.0, 1.0)

class SpriteRect:
    def __init__(
            self,
            origin : tuple[float, float] = (0.0, 0.0),
            size : tuple[float, float] = (1.0, 1.0),
            pivot_relative : tuple[float, float] = DEFAULT_PIVOT_POS,
            svg_scale : float = 1.0):

        self.origin = origin
        self.size = size
        self.pivot_relative = pivot_relative
        self.svg_scale = svg_scale

    def __str__(self):
        return f"""<SpriteRect origin=({self.x},{self.y}) size=({self.width}, {self.height})>"""

    @property
    def x(self):
        return self.origin[0]

    @property
    def y(self):
        return self.origin[1]

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def pivot_relative_x(self):
        return self.pivot_relative[0]

    @property
    def pivot_relative_y(self):
        return self.pivot_relative[1]

    @property
    def pivot_absolute_x(self):
        return self.x + (self.width * self.pivot_relative_x)

    @property
    def pivot_absolute_y(self):
        return (self.y + self.height) - (self.height * self.pivot_relative_y)

    @property
    def pivot_absolute(self):
        return (self.pivot_absolute_x, self.pivot_absolute_y)


    def set_pivot_absolute(self, pivot_absolute : tuple[float, float]):
        abs_x = pivot_absolute[0]
        abs_y = pivot_absolute[1]
        rel_x = (abs_x - self.x)/(self.width)
        rel_y = -(abs_y - (self.y + self.height))/(self.height)
        self.pivot_relative = (rel_x, rel_y)


    def get_scaled_rect(
            self,
            scale : float = 1.0,
            origin : tuple[float, float] = (0.0,0.0)) -> SpriteRect:
        width = round(self.width * self.svg_scale * scale)
        height = round(self.height * self.svg_scale * scale)
        return SpriteRect(
            origin=origin,
            size=(width, height),
            pivot_relative=self.pivot_relative,
            svg_scale=1.0,
        )


def get_rect_from_scml_frame(elem : ET.Element) -> SpriteRect:
    return SpriteRect(
        size=(float(elem.get('width')), float(elem.get('height'))),
        pivot_relative=(float(elem.get('pivot_x')), float(elem.get('pivot_y'))),
    )


def get_rect_from_svg_rect(
        rect : inkex.Rectangle,
        svg : inkex.ISVGDocumentElement) -> SpriteRect:
    return SpriteRect(
        origin=(rect.left, rect.top),
        size=(rect.width, rect.height),
        svg_scale=svg.scale,
    )
