import logging; logger = logging.getLogger(__name__)
import types
from typing import List
from pathlib import Path
import os
import shutil

import inkex
from inkex import Layer, Group, Vector2d
from onispritetools.lib import ost_doc
from onispritetools.lib.ost_doc import GetMode
from onispritetools.lib.ost_extension import OSTExtension
from onispritetools.lib.ost_elements import Config
from lib import sprite_rect, utils, scml_loader


# TODO: add options
CREATE_EXPORTS = True
CREATE_NEW_FRAME_LAYERS = True
CREATE_DUPLICATES = True
COPY_IMAGES = True
IMAGE_DIR = "./img"

LINK_IMAGES = True
ARRANGE_FRAMES = True
X_PADDING = 25
Y_PADDING = 50

# ARGS
IMPORT_FORMAT = "import_format"
ImportFormat = types.SimpleNamespace()
ImportFormat.SCML = "import_format_scml"
ImportFormat.KANIM = "import_format_kanim"
SCML_FILES = "scml_files"
IMAGE_FILE = "image_file"
BUILD_FILE = "build_file"

SYMBOL_SELECTION = "symbol_selection"
SymbolSelection = types.SimpleNamespace()
SymbolSelection.ALL = "all"
SymbolSelection.SPECIFIED = "specified"
SPECIFIED_SYMBOLS_LIST = "specified_symbols_list"

RENAME_SYMBOLS_LIST = "rename_symbols_list"

EXISTING_FRAME_MODE = "existing_frame_mode"
ExistingFrameMode = types.SimpleNamespace()
ExistingFrameMode.SKIP = "existing_frame_mode_skip"
ExistingFrameMode.APPEND = "existing_frame_mode_append"

IMPORT_NAME_OVERRIDE = "import_name_override"
CREATE_EXPORTS = "create_exports"
IMPORT_SCALE = "import_scale"

# class FrameData(object):
#     def __init__(self, symbol_frame_id : str):
#         self.symbol_frame_id = symbol_frame_id

#         self.symbol_name = ""
#         self.frame_id = ""



class SymbolData(object):
    def __init__(self, name : str, alias : str):
        self.name = name
        self.alias = alias
        self.frames = {} # {frame_name : layer}
        self.layer : Layer = None
        self.already_exists = False

    # We hard-code the UI symbol alias layer handling.
    # Since there is only one each, we will group them
    # in the same symbol name layer.
    # For aliases from user input, we will use the alias
    # as the layer name.
    def get_symbol_layer_label(self) -> str:
        symbol_layer_name = self.name
        if self.alias is not None:
            if not self.name.startswith("ui"):
                symbol_layer_name = self.alias
        return symbol_layer_name




class ImportData(object):
    def __init__(self, name : str):
        self.name = name
        self.symbols = {} # {symbol_name : SymbolData}



class ImportSymbolFrames(OSTExtension):
    def add_arguments(self, pars):
        pars.add_argument(
            f"--{IMPORT_FORMAT}",
            type=str,
            default=ImportFormat.SCML,
            dest=IMPORT_FORMAT)

        pars.add_argument(
            f"--{SCML_FILES}",
            type=str,
            default="",
            dest=SCML_FILES)

        pars.add_argument(
            f"--{IMAGE_FILE}",
            type=str,
            default="",
            dest=IMAGE_FILE)

        pars.add_argument(
            f"--{BUILD_FILE}",
            type=str,
            default="",
            dest=BUILD_FILE)

        pars.add_argument(
            f"--{IMPORT_NAME_OVERRIDE}",
            type=str,
            default="",
            dest=IMPORT_NAME_OVERRIDE)

        pars.add_argument(
            f"--{SYMBOL_SELECTION}",
            type=str,
            default=SymbolSelection.ALL,
            dest=SYMBOL_SELECTION)

        pars.add_argument(
            f"--{SPECIFIED_SYMBOLS_LIST}",
            type=str,
            default="",
            dest=SPECIFIED_SYMBOLS_LIST)

        pars.add_argument(
            f"--{RENAME_SYMBOLS_LIST}",
            type=str,
            default="",
            dest=RENAME_SYMBOLS_LIST)

        pars.add_argument(
            f"--{EXISTING_FRAME_MODE}",
            type=str,
            default="",
            dest=EXISTING_FRAME_MODE)

        pars.add_argument(
            f"--{CREATE_EXPORTS}",
            type=inkex.Boolean,
            default=False,
            dest=CREATE_EXPORTS)

        pars.add_argument(
            f"--{IMPORT_SCALE}",
            type=float,
            default=1.0,
            dest=IMPORT_SCALE)


    def effect(self):
        self.imports : List[ImportData] = []
        doc = self.doc
        self.last_scml_pos = (0.0, 0.0)

        import_name_override = getattr(self.options, IMPORT_NAME_OVERRIDE)
        self.import_name_override = import_name_override if import_name_override != "" else None

        self.existing_frame_mode = getattr(self.options, EXISTING_FRAME_MODE)
        self.create_exports = getattr(self.options, CREATE_EXPORTS)
        import_scale = getattr(self.options, IMPORT_SCALE)
        self.image_import_scale = import_scale * self.image_scale/doc.get_scale()

        self.symbols_to_import = None
        if getattr(self.options, SYMBOL_SELECTION) == SymbolSelection.SPECIFIED:
            symbols_str : str = getattr(self.options, SPECIFIED_SYMBOLS_LIST)
            self.symbols_to_import = symbols_str.split(r"\n")

        rename_symbols_str = getattr(self.options, RENAME_SYMBOLS_LIST)
        self.symbol_aliases = {}
        for s in rename_symbols_str.split(r"\n"):
            if len(s) <= 2:
                continue
            symbol, alias = s.split("=")
            self.symbol_aliases[symbol] = alias

        import_format = getattr(self.options, IMPORT_FORMAT)
        match import_format:
            case ImportFormat.KANIM:
                build_filepath = getattr(self.options, BUILD_FILE)
                image_filepath = getattr(self.options, IMAGE_FILE)
                scml_filepath = self.convert_kanim_to_scml(build_filepath, image_filepath)
                self.import_symbols_from_scml(scml_filepath)
            case ImportFormat.SCML:
                filepaths : List[str] = getattr(self.options, SCML_FILES).split("|")
                for path in filepaths:
                    self.import_symbols_from_scml(path)

        self.arrange_frame_layers()
        if self.create_exports:
            self.add_exports_to_config()
        self.clean_up_doc()


    def convert_kanim_to_scml(self, build_filepath : str, image_filepath : str) -> str:
        temp_dir = self.get_temp_dir()
        kanim_dir = utils.get_or_create_dir(temp_dir.joinpath("kanim"))
        scml_dir = utils.get_or_create_dir(temp_dir.joinpath("scml"))

        import_name = Path(build_filepath).stem.removesuffix("_build")
        import_image_filepath = kanim_dir.joinpath(f"{import_name}_0.png")
        import_build_filepath = kanim_dir.joinpath(f"{import_name}_build.bytes")
        import_anim_filepath = kanim_dir.joinpath(f"{import_name}_anim.bytes")

        scml_filepath = scml_dir.joinpath(f"{import_name}.scml")

        shutil.copyfile(build_filepath, import_build_filepath)
        shutil.copyfile(image_filepath, import_image_filepath)

        try:
            anim_filepath = self.get_resource("resources/empty_anim.bytes")
        except Exception as e:
            logger.error(e)
            return None
        else:
            shutil.copyfile(anim_filepath, import_anim_filepath)

        logger.info(f"Exporting scml to {scml_dir}...")
        config = self.doc.get_config()
        kanimal_path = config.get(Config.KANIMAL_PATH)
        if kanimal_path is None:
            logger.error("No valid kanimal path found.")
            return None

        result = inkex.command.call(
            kanimal_path,
            "scml",
            import_image_filepath,
            import_anim_filepath,
            import_build_filepath,
            "-o",
            scml_dir)
        self.log_command_result(result)

        return scml_filepath


    def import_symbols_from_scml(self, filepath):
        doc = self.doc

        logger.info(f"Importing symbols from {filepath}...")
        import_name = self.import_name_override if self.import_name_override is not None else Path(filepath).stem
        import_data = ImportData(name=import_name)
        self.imports.append(import_data)

        frames = scml_loader.load_frames_from_file(filepath)

        for frame in frames:
            symbol_name = frame.symbol_name

            # Get or create symbol data and layer.
            # Create even if we won't add a frame to it,
            # so we can use it to export.
            # Empty layers will get cleaned up later.
            symbol : SymbolData = import_data.symbols.get(symbol_name, None)
            if symbol is None:
                symbol = self.create_symbol(symbol_name, import_data.name)
                import_data.symbols[symbol.name] = symbol

            # If none, assume import all.
            # If there is a list, assume import specified only.
            if self.symbols_to_import is not None:
                if symbol_name not in self.symbols_to_import:
                    logger.debug(f"Skipping frame: {frame}, symbol {symbol_name} not in symbols to import.")
                    continue

            frame_label = frame.name
            if symbol.alias is not None:
                frame_label = f"{symbol.alias}_{frame.frame_idx}"

            # logger.debug(f"symbol.name: {symbol.name}")
            # logger.debug(f"symbol.alias: {symbol.alias}")
            # logger.debug(f"frame_label: {frame_label}")

            # We will first try to get and use the frame layer
            # from anywhere under the symbols root layer.
            frame_layer = doc.get_layer(
                frame_label,
                parent=doc.get_symbols_layer(),
                recursive=True)

            if frame_layer is not None:
                # If any frame for the symbol is already in the document,
                # mark this as true to skip arranging any of the frames.
                symbol.already_exists = True

                if self.existing_frame_mode == ExistingFrameMode.SKIP:
                    logger.debug(f"Skipping frame {frame.name}, already exists...")
                    continue
            else:
                # If the frame layer doesn't already exist,
                # we will create it in our (new) symbol layer.
                frame_layer = doc.get_layer(
                    frame_label,
                    GetMode.GET_OR_CREATE,
                    symbol.layer,
                    recursive=False)

            symbol.frames[frame_label] = frame_layer

            # Create layer elements
            rect = frame.rect.get_scaled_rect(self.image_import_scale)
            sprite_group = doc.layer_get_sprite_group(frame_layer, GetMode.GET_OR_CREATE)

            image_path = Path(filepath).parent.joinpath(frame.name + ".png")
            self.import_frame_image(image_path, import_data.name, rect, sprite_group)

            # If no image was added and there are no existing elems,
            # add a box as a placeholder.
            if doc.elem_get_child_count(sprite_group) == 0:
                doc.layer_create_box(frame_layer, rect)
                box = doc.layer_get_box(frame_layer)
                frame_layer.remove(box)
                sprite_group.append(box)
                doc.elem_set_label(box, "placeholder_rect")

            pivot = doc.layer_get_pivot(frame_layer)
            if pivot is None:
                doc.layer_create_pivot_at_pos(frame_layer, Vector2d(rect.pivot_absolute))
            else:
                # Test if pivot positions are equal
                import_pivot_pos = Vector2d(rect.pivot_absolute_x, rect.pivot_absolute_y)
                existing_pivot = doc.layer_get_pivot_pos(frame_layer)
                if (utils.is_equal_approx(import_pivot_pos.x, existing_pivot.x, 0.9)) and (utils.is_equal_approx(import_pivot_pos.y, existing_pivot.y, 0.9)):
                    logger.info("Pivots are equal")
                else:
                    logger.warning(f"Pivots are not equal: new pivot: {import_pivot_pos} existing pivot: {existing_pivot}")

            logger.debug(f"Added frame layer: {frame_label}")
            doc.layer_clean_up_frame_layer(frame_layer)
            self.log_newline()



    def arrange_frame_layers(self):
        doc = self.doc
        logger.info("Arranging frame layers...")

        max_height = 0.0
        last_pos = Vector2d(0.0,0.0)
        last_width = 0.0

        for import_data in self.imports:
            # logger.debug(f"Arranging import {import_data.name}")
            for symbol_name, symbol in import_data.symbols.items():
                # logger.debug(f"Arranging symbol {symbol.name}")
                if symbol.already_exists:
                    logger.debug(f"Symbol {symbol.name} already has layers in document, skipping arrange frame layers...")
                    continue
                pos = Vector2d(0.0, last_pos.y)
                pos.y += max_height + Y_PADDING if (max_height > 0.001) else 0.0
                first_frame = True
                max_height = 0.0

                # logger.debug(f"Frames count: {len(symbol.frames)}")

                for frame_name, layer in symbol.frames.items():
                    # logger.debug(f"Arranging frame {frame_name}")
                    bbox = layer.bounding_box()
                    if bbox is None:
                        logger.warning(f"No bbox found for {frame_name}")
                        continue

                    if not first_frame:
                        pos = Vector2d(last_pos.x + last_width + X_PADDING, last_pos.y)

                    # logger.debug(f"\tpos={pos}")

                    layer.transform.add_translate(pos)
                    last_pos = pos
                    last_width = bbox.width
                    max_height = max(max_height, bbox.height)

                    first_frame = False


    def clean_up_doc(self):
        doc = self.doc

        logger.info("Cleaning up...")

        for import_data in self.imports:
            for symbol_name, symbol in import_data.symbols.items():
                layer = symbol.layer
                # Delete unused symbol layers
                if doc.elem_get_child_count(layer) == 0:
                    layer.delete()



    def create_symbol(self, symbol_name : str, import_name : str) -> SymbolData:
        doc = self.doc
        symbols_root_layer = doc.get_symbols_layer(ost_doc.GetMode.GET_OR_CREATE)
        if symbols_root_layer is None:
            return

        # Get symbol alias
        # By default, we will handle ui aliases.
        # But allow user alias to overwrite it.
        symbol_alias = self.symbol_aliases.get(symbol_name, None)
        if symbol_alias is None and symbol_name.startswith("ui"):
            symbol_alias = f"{import_name}_{symbol_name}"

        symbol = SymbolData(symbol_name, symbol_alias)

        # Get or create symbol layer
        symbol.layer = doc.get_layer(
            symbol.get_symbol_layer_label(),
            GetMode.GET_OR_CREATE,
            symbols_root_layer,
            recursive=False)
        return symbol


    def import_frame_image(
            self,
            image_path : str,
            import_name : str,
            rect : sprite_rect.SpriteRect,
            sprite_group : Group):

        doc = self.doc
        if COPY_IMAGES:
            image_path = doc.path_convert_to_absolute(image_path)
            image_root_dir = utils.get_or_create_dir(Path(self.get_document_dir()).joinpath(IMAGE_DIR))
            image_dir = utils.get_or_create_dir(image_root_dir.joinpath(import_name))
            dst_image_path = image_dir.joinpath(Path(image_path.name))
            shutil.copyfile(image_path, dst_image_path)
            image_path = dst_image_path
        _image = doc.create_image(
            sprite_group,
            image_path,
            self.document_path(),
            rect,
            import_name,
        )


    def add_exports_to_config(self):
        logger.info("Creating export(s)...")
        doc = self.doc
        config = doc.get_config()
        exports = config.exports

        for import_data in self.imports:
            symbols_list = []
            for symbol_name, symbol in import_data.symbols.items():
                if symbol.alias is not None:
                    symbols_list.append((symbol.name, symbol.alias))
                else:
                    symbols_list.append(symbol.name)
            exports.create_export(import_data.name, symbols_list)
            logger.info(f"Created export {import_data.name}")




if __name__ == '__main__':
    ImportSymbolFrames().run()
