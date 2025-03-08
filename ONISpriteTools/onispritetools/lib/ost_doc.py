import re
from enum import Enum
from pathlib import Path, PurePath
import os
import shutil
import logging; logger = logging.getLogger(__name__)
import inkex
from inkex import BaseElement, Vector2d, Layer, Use, Rectangle, PathElement
from inkex.interfaces.IElement import ISVGDocumentElement
from typing import List
from . import sprite_rect, utils
from .ost_elements import Config, Exports, Export, Symbol, Palettes, Palette, PaletteElem
from onispritetools import __version__, NS, NSURI





class GetMode(Enum):
    GET_ONLY = 1
    GET_OR_CREATE = 2
    REPLACE = 3

NSPREFIX = "ost"

FRAME_LAYER_PATTERN = r'[a-z_]+?_\d+'

META_LAYER_LABEL = "__oniSVG"
META_PROP_KANIM_DIR = "kanim_export_dir"
META_PROP_KANIM_DIR_DEFAULT = ".\\export"
META_PROP_TEMP_DIR = "temp_dir"
META_PROP_TEMP_DIR_DEFAULT = ".\\temp"
META_PROP_EXPORT_PREFIX = "prefix"
META_PROP_EXPORT_PREFIX_DEFAULT = ""


SYMBOLS_LAYER_LABEL = "Symbols"
ROOT_ANIM_LAYER_LABEL = "Previews"

SPRITE_GROUP_LABEL = "Sprite"
BOX_LABEL = "box"
PIVOT_LABEL = "pivot"
PIVOT_MARKER_ID = "pivot_marker"
PIVOT_SYMBOL_ID = "pivot_symbol"
ANIM_BKG_LABEL = "anim_bkg"

ANIM_PATH_PROP = "anim_path"

BOX_COLOR = "#ACACAC"
ANIM_BKG_COLOR = "#D9D9D9"

PIVOT_SCALE = 0.3
PIVOT_FILL = "#000000"
PIVOT_STROKE = "#00ffdf"
PIVOT_STROKE_WIDTH = 2.5

XPATH_ALL_LAYERS = f'.//svg:g[@inkscape:groupmode="layer"]'
XPATH_SPRITE_GROUPS = f'./svg:g[@inkscape:label="{SPRITE_GROUP_LABEL}"]'
XPATH_BOXES = f'./svg:rect[@inkscape:label="{BOX_LABEL}"]'
XPATH_PIVOTS = f'./svg:path[@inkscape:label="{PIVOT_LABEL}"]'

ANIM_MARGIN_RIGHT = 100
ANIM_MARGIN_TOP = 200
ANIM_BKG_PADDING = 25


class OSTDoc:
    def __init__(
            self,
            extension : inkex.base.InkscapeExtension):

        self.extension = extension
        self.svg : ISVGDocumentElement = extension.svg
        self.validate_config()
        self.update_pivot_symbol_def()
        self.update_pivots_to_symbols()
        self.clean_up_image_paths()


    def validate_config(self):
        configs = self.svg.xpath(f"./{Config.tag_name}")
        config : Config = None
        if len(configs) > 1:
            logger.error("Multiple config elems found.")
            return
        elif len(configs) == 1:
            config = configs[0]
            logger.info(f"Found existing OST config, version={config.get(Config.VERSION)}")
        else:
            logger.info(f"No OST config found, initializing with new config...")
            config = Config()
            self.svg.insert(Config.SVG_DOC_IDX, config)
            config.set_next_id(config.TAG)

        config.update_version()
        config.validate_defaults_recursive()


    def get_config(self) -> Config:
        path = self.svg.xpath(f"./{Config.tag_name}[1]")
        if len(path) == 0:
            return None
        return path[0]


    def get_scale(self) -> float:
        return self.svg.scale


    def get_all_layers(
            self,
            parent : Layer = None) -> List[Layer]:
        if parent is None:
            elems = self.svg.xpath(XPATH_ALL_LAYERS)
        else:
            elems = parent.xpath(XPATH_ALL_LAYERS)
        layers : List[Layer] = []
        for layer in elems:
            # logger.info(f"found layer: {self.layer_get_name(layer)}")
            if not isinstance(layer, Layer):
                continue
            layers.append(layer)
        return layers


    # https://inkscapetutorial.org/lxml-basics.html
    # If parent is provided, only direct children of the parent are searched.
    # If no parent is provided, the whole document is searched.
    def get_layer(
            self,
            label : str,
            get_mode = GetMode.GET_ONLY,
            parent : Layer = None,
            recursive = True) -> Layer:

        if not label:
            return None

        if parent is None:
            parent = self.svg

        if recursive == True:
            path = f'//svg:g[@inkscape:label="{label}"]'
        else:
            path = f'./svg:g[@inkscape:label="{label}"]'

        elems = parent.xpath(path)

        if elems:
            layer = elems[0]
            if isinstance(layer, Layer):
                if get_mode == GetMode.REPLACE:
                    layer.delete()
                else:
                    return layer

        if get_mode == GetMode.GET_ONLY:
            return None

        # Create layer.
        layer = Layer()
        self.elem_set_label(layer, label)
        if parent is None:
            self.svg.append(layer)
        else:
            parent.append(layer)
        return layer


    def get_symbols_layer(
            self,
            get_mode = GetMode.GET_ONLY) -> Layer:

        return self.get_layer(
            SYMBOLS_LAYER_LABEL,
            get_mode,
            self.svg,
            recursive=False)


    def get_root_anim_layer(
            self,
            get_mode = GetMode.GET_ONLY) -> Layer:

        return self.get_layer(
            ROOT_ANIM_LAYER_LABEL,
            get_mode,
            self.svg,
            recursive=False)


    def get_all_frame_layers(self, parent : Layer = None) -> List[Layer]:
        if parent is None:
            parent = self.get_symbols_layer(GetMode.GET_ONLY)
            if parent is None:
                # Don't search outside of top-level symbols layer.
                return []

        layers = self.get_all_layers(parent)
        frame_layers = []
        for layer in layers:
            # logger.debug(f"Layer: {self.elem_get_label(layer)}")
            if self.is_frame_layer(layer):
                frame_layers.append(layer)
        return frame_layers


    def get_frame_layers_dict(self, parent : Layer = None) -> dict:
        layers = self.get_all_frame_layers(parent)
        dict = {}
        for layer in layers:
            key = self.elem_get_label(layer)
            dict[key] = layer
        return dict


    def get_selected_frame_layers(self) -> List[Layer]:
        frame_layers = []
        for elem in self.svg.selection:
            if self.is_frame_layer(elem):
                frame_layers.append(elem)
            else:
                child_frame_layers = self.get_all_frame_layers(elem)
                if child_frame_layers:
                    frame_layers.extend(child_frame_layers)
        return frame_layers


    # Rect with origin (0,0) and scaled to pixel values
    # for export to scml.
    def get_frame_rect(self, name : str, scale = 1.0) -> sprite_rect.SpriteRect:
        layer = self.get_layer(name)
        if layer is None:
            logger.error(f"Unable to find layer for {name}.")
            return None
        box_rect = self.layer_get_box_rect(layer)
        if box_rect is None:
            logger.error(f"Unable to find box for {name}.")
            return None
        return box_rect.get_scaled_rect(scale)


    def is_frame_layer(self, obj) -> bool:
        # logger.debug(f"Is frame layer: {self.elem_get_label(obj)}")
        if not isinstance(obj, Layer):
            # logger.debug("\tFalse")
            return False

        if not re.match(FRAME_LAYER_PATTERN, self.elem_get_label(obj)):
            # logger.debug("\tFalse")
            return False

        # logger.debug("\tTrue")
        return True



    def align_frame_layers(
            self,
            layers : List[Layer],
            align_x : bool = True,
            align_y : bool = True):

        target_layer = layers.pop()
        target_pos = self.layer_get_pivot_pos_absolute(target_layer)
        if target_pos is None:
            logger.error(f"Unable to get the target pivot position for {self.elem_get_label(target_layer)}", True)
            return

        for layer in layers:
            self.layer_move_frame_to_pos(
                layer,
                target_pos,
                align_x=align_x,
                align_y=align_y,
            )


    def create_image(
            self,
            parent,
            path : str,
            doc_path : str,
            rect : sprite_rect.SpriteRect,
            label : str) -> inkex.Image:

        if not Path(path).is_file():
            logger.error(f"Image not found at path: {path}")
            return None

        logger.info(f"Adding image at {path}...")
        doc_dir = Path(doc_path).parent
        rel_path = self.path_convert_to_relative(path)
        image = inkex.Image()
        image.set('xlink:href', rel_path)
        image.set('width', rect.width)
        image.set('height', rect.height)
        image.style['display'] = 'inline'
        self.elem_set_label(image, label)
        parent.append(image)
        return image


    # TODO: Will currently only work if files on C drive
    def rebase_image_paths_for_export(self):
        for item in self.svg.xpath(".//svg:image"):
            image : inkex.Image = item
            href = image.get('xlink:href')
            href = href.replace("%5C", "/")
            if href.startswith("file:"):
                continue
            logger.debug(f"href: {href}")

            absolute_path = self.path_convert_to_absolute(href)
            logger.debug(f"absolute_path: {absolute_path}")
            file_abs_path = "file:///" + absolute_path.removeprefix("C:\\").replace("\\", "/")
            logger.debug(f"file_abs_path: {file_abs_path}")

            image.set('xlink:href', file_abs_path)


    def convert_image_paths_to_relative(self):
        for item in self.svg.xpath(".//svg:image"):
            image : inkex.Image = item
            href = image.get('xlink:href')
            relative_href = self.path_convert_to_relative(href)
            image.set('xlink:href', relative_href)


    def clean_up_image_paths(self):
        for item in self.svg.xpath(".//svg:image"):
            image : inkex.Image = item
            href = image.get('xlink:href')
            href = href.replace("%5C", "/")
            image.set('xlink:href', href)



    def path_convert_to_absolute(self, path) -> str:
        if os.path.isabs(path):
            return path
        return self.extension.absolute_href(path)


    def path_convert_to_relative(self, path) -> str:
        if not os.path.isabs(path):
            return path
        doc_path = self.extension.document_path()
        doc_folder_path = Path(doc_path).parent
        return PurePath(path).relative_to(doc_folder_path)


    def apply_palette(self, palette):
        config = self.get_config()
        palettes = config.palettes

        if isinstance(palette, str):
            palette_name = palette
            palette = palettes.get_palette(palette_name)
            if palette is None:
                logger.error(f"Unable to find palette with name {palette_name}")
                return

        logger.info(f"Applying palette '{palette.get_name()}'...")

        for item in palette:
            palette_elem : PaletteElem = item
            label = palette_elem.get(PaletteElem.ELEM_LABEL)
            style = palette_elem.get(PaletteElem.ELEM_STYLE)

            elems_to_update : list[inkex.BaseElement] = []

            for layer in self.get_all_frame_layers():
                sprite_group = self.layer_get_sprite_group(layer)
                if sprite_group is None:
                    continue

                elems = sprite_group.xpath(f".//*[@inkscape:label='{label}']")
                elems_to_update.extend(elems)

            palette_layer = self.get_layer("Palette")
            if palette_layer is not None:
                elems_to_update.extend(palette_layer.xpath(f".//*[@inkscape:label='{label}']"))

            for item in elems_to_update:
                elem : inkex.BaseElement = item
                elem.set("style", style)



    # ----------------------------------------------------------
    # DISPLAY
    # ----------------------------------------------------------

    def clean_up_frame_layers(self):
        for layer in self.get_all_frame_layers():
            self.layer_clean_up_frame_layer(layer)


    def hide_non_exported_elems(self):
        self.toggle_boxes(False)
        self.toggle_pivots(False)
        self.toggle_extras(False)


    def update_all_boxes(self):
        for layer in self.get_all_frame_layers():
            self.layer_update_box(layer)


    def delete_all_boxes(self):
        for layer in self.get_all_frame_layers():
            # logger.info(f"Layer: {self.elem_get_label(layer)}")
            if self.layer_get_sprite_bbox(layer) is not None:
                # logger.info(f"Deleting box for layer {self.elem_get_label(layer)}")
                self.layer_delete_box(layer)
            else:
                # If there is no sprite group, the box may be a placeholder for the size.
                # Don't remove it, just hide it.
                logger.debug(f"Hiding box for layer {self.elem_get_label(layer)}")
                box = self.layer_get_box(layer)
                if box is not None:
                    self.box_hide(box)


    def toggle_boxes(self, visible : bool):
        for layer in self.get_all_frame_layers():
            box = self.layer_get_box(layer)
            if box is None:
                continue
            if visible:
                self.box_show(box)
            else:
                self.box_hide(box)


    def toggle_pivots(self, visible : bool):
        for layer in self.get_all_frame_layers():
            pivot = self.layer_get_pivot(layer)
            if pivot is None:
                continue
            if visible:
                self.pivot_show(pivot)
            else:
                self.pivot_hide(pivot)

    # TODO: delete before release
    # For documents saved in an earlier version
    # with pivot markers.
    def update_pivots_to_symbols(self):
        for layer in self.get_all_frame_layers():
            pivot_list = layer.xpath(f"./svg:path[@inkscape:label='{PIVOT_LABEL}']")
            if pivot_list is None or len(pivot_list) == 0:
                # logger.info(f"No pivots to replace in layer {self.elem_get_label(layer)}")
                continue
            for pivot_marker in pivot_list:
                pivot_pos = pivot_marker.bounding_box().center
                self.layer_create_pivot_at_pos(layer, pivot_pos)
                pivot_marker.delete()



    def toggle_extras(self, visible : bool):
        for layer in self.get_all_frame_layers():
            box = self.layer_get_box(layer)
            pivot = self.layer_get_pivot(layer)
            sprite_group = self.layer_get_sprite_group(layer)

            for elem in layer:
                if elem in [box, pivot, sprite_group]:
                    continue
                if visible:
                    self.elem_show(elem)
                else:
                    self.elem_hide(elem)

    # ----------------------------------------------------------
    # POSITIONS
    # ----------------------------------------------------------

    # Place the next animation to the left of the symbols,
    # and below any existing animation frames.
    def get_next_anim_pos(self) -> Vector2d:
        anim_layer = self.get_root_anim_layer()
        anim_box = anim_layer.bounding_box() if anim_layer is not None else None
        symbols_layer = self.get_symbols_layer()
        symbols_box = symbols_layer.bounding_box() if symbols_layer is not None else None

        max_x = 0
        if symbols_box is not None:
            max_x = symbols_box.left

        x = max_x - (ANIM_MARGIN_RIGHT / self.get_scale())

        min_y = 0
        if anim_box is not None:
            min_y = anim_box.bottom + (ANIM_MARGIN_TOP / self.get_scale())
        elif symbols_box is not None:
            min_y = min(symbols_box.top, 0.0)

        y = min_y
        return Vector2d(x,y)


    # ----------------------------------------------------------
    # ELEM
    # ----------------------------------------------------------

    def elem_get_label(self, elem : inkex.BaseElement) -> str:
        if elem is None:
            return '<None>'
        name = elem.get('inkscape:label')
        if name is None:
            name = elem.get('id')
        return name

    def elem_set_label(self, elem : inkex.BaseElement, label : str):
        if elem is None:
            return
        elem.set('inkscape:label', label)


    def elem_hide(self, elem : inkex.ShapeElement):
        if elem is None:
            return
        elem.style['display'] = 'none'


    def elem_show(self, elem : inkex.ShapeElement):
        if elem is None:
            return
        elem.style['display'] = 'inline'


    def elem_move_first(self, elem : BaseElement):
        if elem is None:
            return
        elem_idx = self.elem_get_index(elem)
        if elem_idx == 0:
            return
        parent = self.elem_get_parent(elem)
        if parent is None:
            return
        parent.remove(elem)
        parent.insert(0, elem)


    def elem_move_last(self, elem : BaseElement):
        if elem is None:
            return
        elem_idx = self.elem_get_index(elem)
        parent = self.elem_get_parent(elem)
        if parent is None:
            return
        child_count = self.elem_get_child_count(parent)
        last_idx = child_count - 1
        if elem_idx == last_idx:
            return
        parent.remove(elem)
        parent.append(elem)



    def elem_get_index(self, elem : BaseElement) -> int:
        parent = self.elem_get_parent(elem)
        if parent is None:
            return None
        return self.elem_get_children(parent).index(elem)


    def elem_get_child_count(self, elem : BaseElement) -> int:
        if elem is None:
            return 0
        return len(self.elem_get_children(elem))


    def elem_get_children(self, elem : BaseElement) -> List[BaseElement]:
        if elem is None:
            return []
        children = []
        for child in elem:
            children.append(child)
        return children


    def elem_get_parent(self, elem : BaseElement) -> BaseElement:
        if elem is None:
            return None
        ancestors = elem.ancestors()
        if ancestors is None:
            return None
        return ancestors[0]


    def elem_get_frame_layer_parent(self, elem : BaseElement) -> Layer:
        if elem is None:
            return None
        for ancestor in elem.ancestors():
            if self.is_frame_layer(ancestor):
                return ancestor
        return None


    # inkex namespace functions appear to be broken broken,
    # and attempting to add a custom namespace manually results in
    # unreliable behavior when Inkscape saves the document.
    # So we will avoid using a true custom namespace.
    def elem_set_ns_property(self, elem : inkex.BaseElement, prop : str, value : str):
        set_ns_property(elem, prop, value)


    def elem_get_ns_property(self, elem :inkex.BaseElement, prop : str):
        return get_ns_property(elem, prop)


    def elem_get_child_count(self, elem : BaseElement) -> int:
        return len(elem.xpath("./*"))


    def elem_is_locked_recursive(self, elem : BaseElement) -> bool:
        if not elem.is_sensitive():
            return True
        for parent in elem.ancestors():
            if not parent.is_sensitive():
                return True
        return False



    # ----------------------------------------------------------
    # LAYER
    # ----------------------------------------------------------

    # Delete all qualifying boxes just in case.
    def layer_delete_box(self, layer : Layer):
        elems = layer.xpath(XPATH_BOXES)
        for elem in elems:
            if isinstance(elem, Rectangle):
                elem.delete()


    def layer_create_box(
            self,
            layer : Layer,
            rect : sprite_rect.SpriteRect):

        if rect is None:
            logger.error("No rect provided.")
            return

        # logger.debug(f"Creating box for {self.layer_get_name(layer)}...")

        box = Rectangle.new(rect.x, rect.y, rect.width, rect.height)
        # box.set("width", rect.width)
        # box.set("height", rect.height)
        self.elem_set_label(box, BOX_LABEL)
        self.box_set_default_style(box)
        layer.insert(0, box)
        # layer.append(box)


    # https://inkscape.org/th/forums/extensions/extension-access-children-of-layer/
    def layer_get_box(self, layer : Layer) -> Rectangle:
        elems = layer.xpath(XPATH_BOXES)
        if elems:
            box = elems[0]
            if isinstance(box, Rectangle):
                return box
        return None


    def layer_get_box_rect(self, layer : Layer) -> sprite_rect.SpriteRect:
        box = self.layer_get_box(layer)
        if box is None:
            return None
        box_rect = sprite_rect.get_rect_from_svg_rect(box, self.svg)
        pivot_pos = self.layer_get_pivot_pos(layer)
        box_rect.set_pivot_absolute((pivot_pos.x, pivot_pos.y))
        return box_rect


    def layer_get_sprite_bbox(self, layer : Layer) -> inkex.BoundingBox:
        sprite_group = self.layer_get_sprite_group(layer)
        if sprite_group is None:
            logger.warning(f"Sprite group not found in layer '{self.layer_get_name(layer)}'")
            return None
        bbox = sprite_group.bounding_box()
        if bbox is None:
            logger.warning(f"Sprite group has no bbox in layer '{self.layer_get_name(layer)}'")
            return None
        return bbox


    def layer_update_box(self, layer : Layer):
        bbox = self.layer_get_sprite_bbox(layer)
        if bbox is None:
            return

        box = self.layer_get_box(layer)
        if not box is None:
            box.delete()

        config = self.get_config()
        margin = float(config.get(Config.FRAME_MARGIN))
        margin_to_add = (margin * 2.0)/self.get_scale()

        bbox = bbox.resize(margin_to_add)

        box_rect = sprite_rect.SpriteRect(
            origin=(bbox.left, bbox.top),
            size=(bbox.width, bbox.height),
            svg_scale=self.get_scale(),
        )

        self.layer_create_box(layer, box_rect)


    def layer_get_name(self, layer : Layer) -> str:
        return self.elem_get_label(layer)


    def layer_get_sprite_group(
            self,
            layer : Layer,
            get_mode = GetMode.GET_ONLY) -> inkex.Group:

        groups = layer.xpath(XPATH_SPRITE_GROUPS)
        # logger.info(f"Sprite groups found: {len(groups)}")
        if len(groups) > 1:
            logger.error(f"More than 1 sprite group in layer {self.layer_get_name(layer)}")
            return None

        if groups:
            sprite_group = groups[0]
            if isinstance(sprite_group, inkex.Group):
                if get_mode == GetMode.REPLACE:
                    sprite_group.delete()
                else:
                    return sprite_group

        logger.info(f"Creating Sprite group for {self.layer_get_name(layer)}...")
        sprite_group = inkex.Group()
        self.elem_set_label(sprite_group, SPRITE_GROUP_LABEL)
        layer.append(sprite_group)

        return sprite_group


    # Removes and re-orders all the layer elements.
    def layer_clean_up_frame_layer(self, layer : Layer):
        logger.info(f"Cleaning up frame layer {self.layer_get_name(layer)}...")

        box = self.layer_get_box(layer)
        if box is not None:
            self.elem_move_first(box)

        pivot = self.layer_get_pivot(layer)
        if pivot is not None:
            self.elem_move_last(pivot)


    # Applies translation to the layer's transform so that
    # the pivot is located at the given position.
    def layer_move_frame_to_pos(
            self,
            layer : Layer,
            pos : Vector2d,
            align_x : bool = True,
            align_y : bool = True):

        current_pos = self.layer_get_pivot_pos_absolute(layer)
        x_translation = pos.x - current_pos.x
        y_translation = pos.y - current_pos.y
        translation = (0.0, 0.0)
        if align_x and align_y:
            translation = (x_translation, y_translation)
        elif align_x:
            translation = (x_translation, 0.0)
        elif align_y:
            translation = (0.0, y_translation)

        layer.transform.add_translate(translation)


    # ----------------------------------------------------------
    # PIVOTS
    # ----------------------------------------------------------
    # SYMBOL DEF

    def update_pivot_symbol_def(self):
        symbol_def = self.get_pivot_symbol_def()
        if symbol_def is not None:
            symbol_def.delete()

        self.create_pivot_symbol_def()


    def create_pivot_symbol_def(self):
        symbol = inkex.Symbol()
        self.svg.defs.append(symbol)
        symbol.set_id(PIVOT_SYMBOL_ID)
        symbol.title = "pivot symbol"
        path = inkex.PathElement()
        path.set("d", "M 144 324 L 136.80078 324.80078 C 131.53411 326.03411 126.85 328.68333 122.75 332.75 C 118.68333 336.85 116.03411 341.53411 114.80078 346.80078 C 114.26745 349.10078 114 351.5 114 354 C 114 356.5 114.26745 358.89922 114.80078 361.19922 C 116.03411 366.46589 118.68333 371.13255 122.75 375.19922 C 126.85 379.29922 131.53411 381.96589 136.80078 383.19922 L 144 384 L 151.19922 383.19922 C 156.46589 381.96589 161.13255 379.29922 165.19922 375.19922 C 169.29922 371.13255 171.96589 366.46589 173.19922 361.19922 C 173.73255 358.89922 174 356.5 174 354 C 174 351.5 173.73255 349.10078 173.19922 346.80078 C 171.96589 341.53411 169.29922 336.85 165.19922 332.75 C 161.13255 328.68333 156.46589 326.03411 151.19922 324.80078 L 144 324 z M 140.25 328.25 L 142 330 L 142 344 L 146 344 L 146 330 L 147.75 328.25 C 153.35 328.98333 158.23372 331.43294 162.40039 335.59961 C 166.56706 339.76628 169.01667 344.65 169.75 350.25 L 168 352 L 154 352 L 154 356 L 168 356 L 169.75 357.75 C 169.01667 363.35 166.56706 368.23372 162.40039 372.40039 C 158.23372 376.56706 153.35 379.01667 147.75 379.75 L 146 378 L 146 364 L 142 364 L 142 378 L 140.25 379.75 C 134.65 379.01667 129.76628 376.56706 125.59961 372.40039 C 121.43294 368.23372 118.98333 363.35 118.25 357.75 L 120 356 L 134 356 L 134 352 L 120 352 L 118.25 350.25 C 118.98333 344.65 121.43294 339.76628 125.59961 335.59961 C 129.76628 331.43294 134.65 328.98333 140.25 328.25 z M 144 352 C 143.43333 352 142.95078 352.18411 142.55078 352.55078 C 142.18411 352.95078 142 353.43333 142 354 C 142 354.56667 142.18411 355.03372 142.55078 355.40039 C 142.95078 355.80039 143.43333 356 144 356 C 144.56667 356 145.03372 355.80039 145.40039 355.40039 C 145.80039 355.03372 146 354.56667 146 354 C 146 353.43333 145.80039 352.95078 145.40039 352.55078 C 145.03372 352.18411 144.56667 352 144 352 z ")
        symbol.append(path)


    def get_pivot_symbol_def(self) -> inkex.Symbol:
        result = self.svg.defs.xpath(f"./svg:symbol[@id='{PIVOT_SYMBOL_ID}']")
        if result is None or len(result) == 0:
            return None
        return result[0]


    # ----------------------------------------------------------
    # PIVOT METHODS

    def pivot_get_pos(self, pivot : inkex.ShapeElement) -> Vector2d:
        return pivot.bounding_box().center


    def pivot_set_default_style(self, pivot : Use):
        pivot.style['display'] = 'inline'
        pivot.style['fill'] = PIVOT_FILL
        pivot.style['stroke'] = PIVOT_STROKE
        pivot.style['stroke-width'] = PIVOT_STROKE_WIDTH / (self.get_scale())


    # Setting display to none ensures it does not contribute
    # to layer bounding box for export.
    def pivot_hide(self, pivot : Use):
        self.pivot_set_default_style(pivot)
        pivot.style['display'] = 'none'


    def pivot_show(self, pivot : Use):
        self.pivot_set_default_style(pivot)


    # ----------------------------------------------------------
    # LAYER PIVOT METHODS

    def layer_get_pivot(self, layer : Layer) -> Use:
        result = layer.xpath(f"./svg:use[@inkscape:label='{PIVOT_LABEL}']")
        if result is None or len(result) == 0:
            return None
        return result[0]


    def layer_get_pivot_pos(self, layer : Layer) -> Vector2d:
        pivot = self.layer_get_pivot(layer)
        if pivot is None:
            # logger.error(f"No pivot found for layer {self.layer_get_name(layer)}")
            return Vector2d(0.0, 0.0)
        return self.pivot_get_pos(pivot)


    def layer_get_pivot_pos_absolute(self, layer : Layer) -> Vector2d:
        pivot = self.layer_get_pivot(layer)
        if pivot is None:
            # logger.error(f"No pivot found for layer {self.layer_get_name(layer)}")
            return None
        rel_pos = self.pivot_get_pos(pivot)
        return layer.transform.apply_to_point(rel_pos)


    def layer_create_pivot(
            self,
            layer : Layer,
            relative_pos : tuple[float, float]):

        logger.info(f"Creating pivot for {self.layer_get_name(layer)}...")
        box_rect = self.layer_get_box_rect(layer)
        if box_rect is None:
            logger.error(f"Error getting box rect for layer {self.layer_get_name(layer)}")
            return

        box_rect.pivot_relative = relative_pos
        (pos_x, pos_y) = box_rect.pivot_absolute
        self.layer_create_pivot_at_pos(layer, inkex.Vector2d(pos_x, pos_y))


    def layer_create_pivot_at_pos(
            self,
            layer : Layer,
            absolute_pos : inkex.Vector2d):

        logger.info(f"Creating pivot for layer {self.elem_get_label(layer)}...")
        pivot = Use()
        pivot.set('xlink:href', f'#{PIVOT_SYMBOL_ID}')
        layer.append(pivot)
        self.pivot_set_default_style(pivot)
        self.elem_set_label(pivot, PIVOT_LABEL)

        bbox = pivot.bounding_box()
        center = bbox.center
        scale = PIVOT_SCALE/self.get_scale()

        # Before adding transform,
        # move pivot so center is at 0,0.
        pivot.transform.add_translate(-center)

        xform = inkex.Transform()

        # Translate it to the target position.
        xform.add_translate(absolute_pos)

        # Translate by center and then back,
        # so that it scales around its center.
        xform.add_translate(center)
        xform.add_scale(scale)
        xform.add_translate(-center)
        pivot.transform = pivot.transform @ xform


    # ----------------------------------------------------------
    # BOX
    # ----------------------------------------------------------

    def box_set_default_style(self, box : Rectangle):
        box.style['display'] = 'inline'
        box.style['fill'] = BOX_COLOR
        box.style['stroke'] = 'none'
        box.style['stroke-width'] = 0


    # Setting fill to none hides it but still
    # allows it to contribute to layer bounding box for export.
    def box_hide(self, box : Rectangle):
        self.box_set_default_style(box)
        box.style['fill'] = 'none'


    def box_show(self, box : Rectangle):
        self.box_set_default_style(box)



def get_ns_property(elem : BaseElement, prop : str):
    if not isinstance(elem, BaseElement):
        return None
    return elem.get(f'{NS}:{prop}', None)


def set_ns_property(elem : BaseElement, prop : str, value : str):
        if not isinstance(elem, BaseElement):
            return
        elem.set(f'{NS}:{prop}', value)