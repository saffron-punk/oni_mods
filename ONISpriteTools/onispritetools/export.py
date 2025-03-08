from typing import List
from types import SimpleNamespace
import logging; logger = logging.getLogger(__name__)
import functools
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
from pathlib import Path
import os
import inkex
from inkex import Layer
import inkex.command

from onispritetools.lib.ost_elements import Config, Exports, Export, Symbol, Palette
from onispritetools.lib.ost_mod import DevMod

from lib import utils
from onispritetools.lib.ost_extension import OSTExtension
from onispritetools.lib.ost_doc import GetMode



class ExportData(object):
    def __init__(
            self,
            export : Export,
            layer_dict : dict,
            sorted_frame_ids : List[str],
            dpi : int,
            palette : Palette = None):

        self.export : Export = export
        self.palette : Palette = palette
        self.layers_dict : dict = layer_dict # {export frame name : Layer}
        self.sorted_frame_ids = sorted_frame_ids
        self.dpi = dpi
        self.name = ""
        self.scml_export_dir : Path = None
        self.kanim_export_dir : Path = None
        self.scml_filepath : Path = None


# TODO: Get export scale from config
EXPORT_SCALE = 0.5
UPDATE_BOUNDING_BOXES = True
OPEN_EXPORT_DIR = True

# TODO: DEBUG
MAX_EXPORTS = 50


EXPORT_TYPE = "export_type"
ExportType = SimpleNamespace()
ExportType.SCML = "export_type_scml"
ExportType.KANIM = "export_type_kanim"
ExportType.MOD = "export_type_mod"

MOD_DIR_PATH = "mod_dir_path"
MOD_ID = "mod_id"

EXPORT_NAMES_LIST = "export_names_list"
USE_PALETTES = "use_palettes"

DEBUG_NO_EXPORT = False


class ExportSymbols(OSTExtension, inkex.base.TempDirMixin, inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument(
            f"--{EXPORT_TYPE}",
            type=str,
            default=ExportType.SCML,
            dest=EXPORT_TYPE)

        pars.add_argument(
            f"--{MOD_DIR_PATH}",
            type=str,
            default="",
            dest=MOD_DIR_PATH)

        pars.add_argument(
            f"--{MOD_ID}",
            type=str,
            default="",
            dest=MOD_ID)

        pars.add_argument(
            f"--{EXPORT_NAMES_LIST}",
            type=str,
            default="",
            dest=EXPORT_NAMES_LIST)

        pars.add_argument(
            f"--{USE_PALETTES}",
            type=inkex.Boolean,
            default=True,
            dest=USE_PALETTES)


    def effect(self):
        doc = self.doc
        config = doc.get_config()

        self.export_names_list : list[str] = []
        export_names_str = getattr(self.options, EXPORT_NAMES_LIST)
        logger.info("Export names:")
        if len(export_names_str) > 0:
            for export_name in export_names_str.split(","):
                self.export_names_list.append(export_name.strip())
                logger.info(f"\t-{export_name.strip()}")

        self.use_palettes = getattr(self.options, USE_PALETTES)
        self.export_type = getattr(self.options, EXPORT_TYPE)

        self.dev_mod = None
        if self.export_type == ExportType.MOD:
            mod_dir = getattr(self.options, MOD_DIR_PATH)
            if mod_dir == "" or not Path(mod_dir).exists():
                logger.error(f"Mod directory {mod_dir} does not exist.")
                raise inkex.AbortExtension
            mod_id = getattr(self.options, MOD_ID)
            if mod_id == "":
                logger.error(f"Invalid mod ID.")
                raise inkex.AbortExtension
            self.dev_mod = DevMod(mod_id, mod_dir, False)

        self.setup_base_paths()
        self.prepare_doc_for_export()
        self.frame_layers_dict = doc.get_frame_layers_dict()

        export_list : List[ExportData] = []
        for export in config.exports:
            if len(export_list) >= MAX_EXPORTS:
                logger.warning(f"Max export count exceeded.")
                break
            if not export.is_enabled():
                logger.warning(f"Export is disabled: {export.get_name()}")
                continue
            if len(self.export_names_list) > 0:
                if not export.get_name() in self.export_names_list:
                    logger.warning(f"Export not in export names list")
                    continue
            export_list.extend(self.collect_data_for_export(export))

        if not DEBUG_NO_EXPORT:
            self.export_scml(export_list)
            if self.export_type in [ExportType.KANIM, ExportType.MOD]:
                self.export_kanim(export_list)

        if self.export_type == ExportType.MOD:
            self.create_mod_files(export_list)

        self.discard_changes()

        if OPEN_EXPORT_DIR:
            utils.open_dir(self.base_export_dir)


    def export_scml(self, export_list):
        for export_data in export_list:
            export_data.scml_filepath = self.create_scml_file(export_data)
        self.create_scml_pngs(export_list)


    def export_kanim(self, export_list : List[ExportData]):
        for export_data in export_list:
            self.convert_scml_to_kanim(export_data.scml_filepath, export_data.kanim_export_dir)


    def collect_data_for_export(self, export : Export) -> List[ExportData]:
        export_list = []

        # Collect layers to export
        layer_dict = self.get_export_layers(export)
        logger.info(f"Found {len(layer_dict)} frame layers for export {export.get_name()}.")

        # Sort frame ids in order required for ONI
        # May be slow, so we will only do it once here to share across exports.
        sorted_frame_ids = list(layer_dict.keys())
        sorted_frame_ids.sort(key=functools.cmp_to_key(utils.compare_frame_names))

        # Get DPI
        # TODO: hires?
        dpi = int(round(96*EXPORT_SCALE))

        palettes = export.get_palettes()
        if (len(palettes) == 0) or not self.use_palettes:
            palettes = [None]

        for palette in palettes:
            export_data = ExportData(export, layer_dict, sorted_frame_ids, dpi, palette)
            self.setup_export_paths(export_data)
            export_list.append(export_data)

        return export_list


    def setup_base_paths(self):
        self.base_temp_dir = self.get_temp_dir()

        if self.dev_mod is not None:
            self.base_export_dir = self.dev_mod.kanim_dir
        else:
            self.base_export_dir = self.get_export_dir()

        match self.export_type:
            case ExportType.SCML:
                self.scml_base_dir = self.base_export_dir
                self.kanim_base_dir = None
            case ExportType.KANIM | ExportType.MOD:
                self.scml_base_dir = self.base_temp_dir
                self.kanim_base_dir = self.base_export_dir

        if self.export_type == ExportType.MOD:
            _ = utils.get_or_create_dir(self.base_export_dir, clean=True)

        logger.info(f"Base directories:\n\tSCML={self.scml_base_dir}\n\tKANIM={self.kanim_base_dir}")


    def setup_export_paths(self, export_data : ExportData):
        config = self.doc.get_config()

        name = config.exports.get_full_export_name(export_data.export, export_data.palette)
        export_data.name = name
        export_data.scml_export_dir = utils.get_or_create_dir(self.scml_base_dir.joinpath(name))
        export_data.kanim_export_dir = None
        if self.export_type in [ExportType.KANIM, ExportType.MOD]:
            export_data.kanim_export_dir = utils.get_or_create_dir(self.kanim_base_dir.joinpath(name), clean=True)


    def create_scml_file(self, export_data : ExportData) -> Path:
        doc = self.doc
        logger.info(f"Exporting {export_data.name} SCML to {export_data.scml_export_dir}...")

        # Create SCML tree
        root = ET.Element("spriter_data", scml_version="1.0", generator="ONI Sprite Tools", generator_version="0.1.0")
        folder = ET.SubElement(root, "folder", id="0")
        _entity = ET.SubElement(root, "entity", id="0", name=export_data.name)

        sorted_frame_ids = export_data.sorted_frame_ids
        export_layers_dict = export_data.layers_dict

        for i in range(len(sorted_frame_ids)):
            frame_id = sorted_frame_ids[i]
            layer = export_layers_dict[frame_id]
            rect = doc.get_frame_rect(doc.elem_get_label(layer), EXPORT_SCALE)
            if rect is None:
                logger.error(f"No contents found for frame layer: {frame_id}")
                continue
            frame_filename = f"{frame_id}.png"
            frame_filepath = export_data.scml_export_dir.joinpath(frame_filename)
            logger.debug(f"\t * id={i} name={frame_filename} width={rect.width} height={rect.height} pivot_x={rect.pivot_relative_x:0.8f} pivot_y={rect.pivot_relative_y:0.8f}")

            # Add symbol file info to SCML
            _file = ET.SubElement(
                folder,
                "file",
                id=str(i),
                name=frame_filename,
                width=str(rect.width),
                height=str(rect.height),
                pivot_x=f"{rect.pivot_relative_x:0.8f}",
                pivot_y=f"{rect.pivot_relative_y:0.8f}")

        # Write SCML file
        scml_filepath = export_data.scml_export_dir.joinpath(f"{export_data.name}.scml")
        tree = ElementTree(root)
        ET.indent(tree)
        tree.write(scml_filepath, encoding='utf-8')

        return scml_filepath


    def create_scml_pngs(self, export_list : List[ExportData]):
        actions_list = self.get_actions_list(export_list)
        action_str = ";".join(actions_list)
        logger.info(f"Executing Inkscape actions (lines={len(actions_list)} chars={len(action_str)})...")
        logger.debug("\n\t".join(actions_list))
        inkex.command.inkscape_command(self.svg, actions=action_str)


    def get_actions_list(self, export_list : List[ExportData]) -> List[str]:
        doc = self.doc
        actions = [
            "export-area-page",
            "export-type:png",
            "export-png-antialias:3",
            # "export-background:#b5835a", # Changing background color does not affect AA artifacts
            "export-background-opacity:0",
            f"select-by-id:{','.join([layer.get_id() for layer in doc.get_all_frame_layers()])}",
            "object-set-attribute:style, display:none",
            "select-clear",
        ]
        for export_data in export_list:
            actions.extend(self.get_export_actions(export_data))

        # Remove last two as it will cause last export to get overwritten with blank image
        _ = actions.pop()
        _ = actions.pop()
        return actions


    def get_export_actions(self, export_data : ExportData) -> List[str]:
        actions : List[str] = [
            f"export-dpi:{export_data.dpi}",
        ]

        actions.extend(self.get_palette_actions(export_data))

        for export_frame_name, layer in export_data.layers_dict.items():
            filename = export_data.scml_export_dir.joinpath(f"{export_frame_name}.png")
            actions.extend([
                f"select-by-id:{layer.get_id()}",
                "object-set-attribute:style, display:inline",
                "fit-canvas-to-selection",
                f"export-filename:{filename}",
                "export-do",
                "object-set-attribute:style, display:none",
                "select-clear",
            ])
        return actions


    def get_palette_actions(self, export_data : ExportData) -> List[str]:
        logger.debug(f"get_palette_actions() - export: {export_data.name}")
        if export_data.palette is None:
            logger.debug(f"palette is None")
            return []

        actions : List[str] = []
        d = export_data.palette.get_elems_dict()
        logger.debug(f"dict={len(d)}")
        for label, style in d.items():
            elems = self.svg.xpath(f".//*[@inkscape:label='{label}']")
            logger.debug(f"{len(elems)} elems found for label {label}")
            ids = [elem.get_id() for elem in elems]
            ids_str = ",".join(ids)
            logger.debug(f"ids_str={ids_str}")
            actions.append(f"select-by-id:{ids_str}")
            styles = style.split(";")
            for style in styles:
                name, value = style.split(":")
                actions.append(
                    f"object-set-property:{name},{value}"
                )
            actions.append("select-clear")
        return actions


    def convert_scml_to_kanim(self, scml_filepath : str, out_dir : str):
        logger.info(f"Exporting kanim to {out_dir}...")
        config = self.doc.get_config()
        kanimal_path = config.get(Config.KANIMAL_PATH)
        if kanimal_path is None:
            logger.error("No valid kanimal path found.")
            return

        result = inkex.command.call(kanimal_path, "kanim", scml_filepath, "-o", out_dir)
        self.log_command_result(result)
        folder_name = Path(out_dir).parts[-1]
        # logger.info(f"folder_name={folder_name}")
        png_path = Path(out_dir).joinpath(f"{folder_name}.png")
        os.rename(png_path, Path(out_dir).joinpath(f"{folder_name}_0.png"))


    # We will later swap the original document for the output document,
    # so none of these changes will be saved.
    def prepare_doc_for_export(self):
        doc = self.doc

        if UPDATE_BOUNDING_BOXES:
            doc.update_all_boxes()

        # Warning dialog about relative image paths halts shell script execution.
        # So we will temporarily change relative paths to absolute paths
        # so that no user interaction is required.
        # EDIT: Disabling convert to absolute, will live with the blocking dialog.
        # Setting the image "href" to an absolute path breaks the image paths.
        # And setting the "sodipodi:absref" still results in the blocking dialog.
        doc.rebase_image_paths_for_export()

        doc.hide_non_exported_elems()
        for layer in doc.get_all_frame_layers():
            doc.elem_show(layer)


    def get_export_layers(self, export : Export) -> dict:
        doc = self.doc
        export_layers_dict = {}
        for symbol in export:
            doc_symbol_name = symbol.get_name_with_alias()
            export_symbol_name = symbol.get_name()
            if doc_symbol_name is None:
                logger.error("Invalid symbol.")
                continue
            for frame_id in doc.get_frame_layers_dict():
                if not frame_id.startswith(f"{doc_symbol_name}_"):
                    continue
                export_frame_id = frame_id.replace(doc_symbol_name, export_symbol_name)
                export_layers_dict[export_frame_id] = self.frame_layers_dict[frame_id]
        return export_layers_dict


    def create_mod_files(self, export_list : List[ExportData]):
        outfit_types = {}
        outfit_items = {}
        for export_data in export_list:
            item_id = export_data.name
            category = None
            if item_id.endswith("atmo_helmet"):
                category = "AtmoSuitHelmet"
            elif item_id.endswith("atmo_body"):
                category = "AtmoSuitBody"
            elif item_id.endswith("atmo_gloves"):
                category = "AtmoSuitGloves"
            elif item_id.endswith("atmo_belt"):
                category = "AtmoSuitBelt"
            elif item_id.endswith("atmo_shoes"):
                category = "AtmoSuitShoes"
            elif item_id.endswith("_top"):
                category = "DupeTops"
            elif item_id.endswith("_pants"):
                category = "DupeBottoms"
            elif item_id.endswith("_gloves"):
                category = "DupeGloves"
            elif item_id.endswith("_shoes"):
                category = "DupeShoes"

            if category is None:
                logger.error(f"Unable to find category for export {item_id}")
                continue

            outfit_id = None
            outfit_type = None
            if "_atmo_" in item_id:
                outfit_type = "AtmoSuit"
                outfit_id = item_id.rsplit("_", maxsplit=2)[0] + "_atmosuit"
            else:
                outfit_type = "Clothing"
                outfit_id = item_id.rsplit("_", maxsplit=1)[0] + "_outfit"
            outfit_types[outfit_id] = outfit_type
            if not outfit_id in outfit_items:
                outfit_items[outfit_id] = []
            outfit_items[outfit_id].append(item_id)

            palette_string = ""
            if export_data.palette is not None:
                palette_string = export_data.palette.get(Palette.OI_PALETTE_STRING, "")

            name_string = export_data.export.get(Export.OI_NAME_STRING, "")
            description_string = export_data.export.get(Export.OI_DESC_STRING, "")

            if len(palette_string) > 0:
                name_string = f"{name_string} ({palette_string})"

            self.dev_mod.add_clothing_item(item_id, category, name_string, description_string)

        for outfit_id, outfit_type in outfit_types.items():
            if len(outfit_items[outfit_id]) <= 1:
                continue
            self.dev_mod.add_clothing_outfit(outfit_id, outfit_type, outfit_items[outfit_id])

        self.dev_mod.create_clothing_items_json()
        self.dev_mod.create_clothing_outfits_json()



if __name__ == '__main__':
    ExportSymbols().run()
