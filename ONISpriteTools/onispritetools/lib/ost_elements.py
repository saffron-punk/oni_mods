from typing import List
from pathlib import Path
import logging; logger = logging.getLogger(__name__)

import inkex
from inkex import BaseElement

from onispritetools import __version__, NS, NSURI


"""
CUSTOM NAMESPACES
Some time between exporting the svg from the extension back to Inkscape, and Inkscape loading it, Inkscape changes the custom namespace prefix to NS0 (or NS1, NS2, etc if there are multiple custom namespaces).

Reparsing and replacing it with the correct namespace prefix (as per https://alpha.inkscape.org/vectors/www.inkscapeforum.com/viewtopicff38.html?t=1055#p63807) allows the custom prefix to remain in the svg's nsmap throughout these scripts, but still gets replaced immediately upon Inkscape reopening the svg. This seems to localize the replacement to the core Inkscape program.

Despite that, if the prefix/URI is added to the inkex NSS dict, xpath will still work with the custom namespace prefix (likely due to converting prefix references to the URI). This works both with and without reparsing the document to correct the prefix.

So, in effect, the change to NS0 appears to be purely cosmetic, and only noticeable when reading the saved svg file manually or in the xml editor.
"""

# The extension's extra_nss is not loaded in time to prevent errors
# from class definitions that use the custom namesapce.
# Therefore, we need to register the NS here.
inkex.elements._utils.registerNS(NS, NSURI)

NONE_STR = "NONE"
ALL_STR = "ALL"
TRUE_STR = "True"
FALSE_STR = "False"

class OSTElementMixin(object):
    attr_defaults = {}

    def set_attr_defaults(self):
        for tag, default in self.attr_defaults.items():
            if self.get(tag) is None:
                self.set(tag, default)


    def validate_defaults_recursive(self):
        self.set_attr_defaults()
        for child in self:
            child.validate_defaults_recursive()


    def is_unset(self, value) -> bool:
        return (value is None) or (len(value) == 0) or (value == NONE_STR)


    def is_true(self, value) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if str(value).lower() == TRUE_STR.lower():
            return True
        try:
            value_int = int(value)
        except:
            pass
        else:
            return value_int == 1

        return False


    def is_all(self, value) -> bool:
        if value is None:
            return False
        return str(value).lower() == ALL_STR.lower()


    def set_next_id(self, id_string : str):
        id_string_count = len(self.root.xpath(f"//*[@id='{id_string}']"))
        if id_string_count == 0:
            self.set_id(id_string)
            return

        i = 0
        id_count = 1

        while id_count > 0:
            # Starting with 1, rather than 0, appears to be Inkscape's convention.
            i += 1
            next_id = f"{id_string}{i}"
            id_count = len(self.root.xpath(f"//*[@id='{next_id}']"))

        self.set_id(next_id)




class PaletteElem(OSTElementMixin, BaseElement):
    tag_name = f"{NS}:palette_elem"

    ELEM_LABEL = "elem_label"
    ELEM_STYLE = "elem_style"

    attr_defaults = {
        ELEM_LABEL : NONE_STR,
        ELEM_STYLE : NONE_STR,
    }



class Palette(OSTElementMixin, BaseElement):
    tag_name = f"{NS}:palette"

    NAME = 'palette_name'
    EXPORT = 'export'
    OI_PALETTE_STRING = "oi_palette_string"

    attr_defaults = {
        OI_PALETTE_STRING : NONE_STR,
        NAME : NONE_STR,
        EXPORT : TRUE_STR,
    }

    def set_name(self, name : str = ""):
        if self.is_unset(name):
            name = NONE_STR
        self.set(self.NAME, name)


    def get_name(self) -> str:
        name = self.get(self.NAME)
        if self.is_unset(name):
            name = self.get_id()
        return name


    def set_export(self, export_value):
        if self.is_true(export_value):
            export_value = TRUE_STR
        else:
            export_value = FALSE_STR
        self.set(self.EXPORT, export_value)


    def get_export(self) -> bool:
        return self.is_true(self.get(self.EXPORT))


    def add_elems_from_dict(self, elems_dict : dict):
        for label, style in elems_dict.items():
            elem = PaletteElem()
            elem.set(PaletteElem.ELEM_STYLE, style)
            elem.set(PaletteElem.ELEM_LABEL, label)
            self.append(elem)
            elem.set_next_id(label)

    def get_elems_dict(self) -> dict:
        d = {}
        for elem in self:
            label = elem.get(PaletteElem.ELEM_LABEL)
            style = elem.get(PaletteElem.ELEM_STYLE)
            if label is None or label == "":
                continue
            if style is None or style == "":
                continue
            d[label] = style
        return d




class Palettes(OSTElementMixin, BaseElement):
    tag_name = f"{NS}:palettes"

    # Uses re.search() to find the pattern at any location in the string.
    # Use '^' to anchor matches to start of string.
    # Use '$' to anchor matches to end of string.
    # For example, to exclude "outline" but include "outline-inner"
    # or "inner-outline", use "^outline$".
    EXCLUDE_LABELS = "exclude_labels"
    EXCLUDE_STYLES = "exclude_styles"
    attr_defaults = {
        EXCLUDE_LABELS : NONE_STR,
        EXCLUDE_STYLES : NONE_STR,
    }

    def create_palette(
            self,
            name : str = "",
            items = {},
            export : bool = True,
            replace : bool = True):

        if len(name) > 0:
            # Delete any palettes with the same name
            for palette in self.xpath(f"./{Palette.tag_name}[@{Palette.NAME}='{name}']"):
                if replace:
                    logger.info("Deleting palette...")
                    palette.delete()
                else:
                    # Update styles only if elems already exist.
                    for elem in palette:
                        style = items.get(elem.get(PaletteElem.ELEM_LABEL, None), None)
                        if style is None:
                            continue
                        elem.set(PaletteElem.ELEM_STYLE, style)
                    return

        palette = Palette()
        palette.set_attr_defaults()
        palette.set_name(name)
        palette.set_export(export)
        self.append(palette)
        if len(name) > 0:
            palette.set_next_id(name)
        else:
            palette.set_next_id()
        palette.add_elems_from_dict(items)


    def get_palette(self, name : str) -> Palette:
        result = self.xpath(f"./{Palette.tag_name}[@{Palette.NAME}='{name}']")
        if result is None or len(result) == 0:
            return None
        return result[0]




    @property
    def exclude_labels(self) -> List[str]:
        exclude_labels_str = self.get(self.EXCLUDE_LABELS)
        if self.is_unset(exclude_labels_str):
            return []
        return exclude_labels_str.split(",")


    @property
    def exclude_styles(self) -> List[str]:
        exclude_styles_str = self.get(self.EXCLUDE_STYLES)
        if self.is_unset(exclude_styles_str):
            return []
        return exclude_styles_str.split(",")




class Symbol(OSTElementMixin, BaseElement):
    tag_name = f"{NS}:symbol"

    NAME = 'symbol_name'
    ALIAS = 'symbol_alias'

    attr_defaults = {
        ALIAS : NONE_STR,
        NAME : NONE_STR,
    }


    def set_name(self, name):
        if self.is_unset(name):
            name = NONE_STR
        self.set(self.NAME, name)


    def get_name(self) -> str:
        name = self.get(self.NAME)
        if self.is_unset(name):
            return None
        return name


    def set_alias(self, alias):
        if self.is_unset(alias):
            alias = NONE_STR
        self.set(self.ALIAS, alias)


    def get_name_with_alias(self) -> str:
        alias = self.get(self.ALIAS)
        if self.is_unset(alias):
            alias = self.get_name()
        return alias



class Export(OSTElementMixin, BaseElement):
    tag_name = f"{NS}:export"

    NAME = "export_name"
    ENABLED = "enabled"
    PALETTES = "palettes"
    OI_NAME_STRING = "oi_name_string"
    OI_DESC_STRING = "oi_description_string"

    attr_defaults = {
        OI_DESC_STRING : NONE_STR,
        OI_NAME_STRING : NONE_STR,
        PALETTES : NONE_STR,
        ENABLED : TRUE_STR,
        NAME : NONE_STR,
    }

    def get_name(self) -> str:
        name = self.get(self.NAME)
        if self.is_unset(name):
            name = self.get_id()
        return name


    def set_name(self, name):
        if self.is_unset(name):
            name = NONE_STR
        self.set(self.NAME, name)


    def add_symbol(self, symbol_name : str, symbol_alias : str = ""):
        symbol = Symbol()
        symbol.set_attr_defaults()
        symbol.set_name(symbol_name)
        symbol.set_alias(symbol_alias)
        self.append(symbol)
        symbol.set_next_id(symbol_name)


    def is_enabled(self) -> bool:
        return self.is_true(self.get(self.ENABLED, self.attr_defaults[self.ENABLED]))


    def get_palettes(self) -> List[Palette]:
        palette_str = self.get(self.PALETTES)
        if self.is_unset(palette_str):
            return []

        palettes = []
        # TODO: change to xpath for config elem
        for palette in self.ancestors()[1].palettes:
            if palette.get_export():
                palettes.append(palette)

        if self.is_all(palette_str):
            return palettes

        named_palettes = []
        for palette_name in palette_str.split(","):
            palette_name = palette_name.strip()
            for palette in palettes:
                if palette.get_name().lower() == palette_name.lower():
                    named_palettes.append(palette)

        return named_palettes


class Exports(OSTElementMixin, BaseElement):
    tag_name = f"{NS}:exports"

    EXPORT_TARGET_KANIM = "KANIM"
    EXPORT_TARGET_SCML = "SCML"

    BASE_EXPORT_DIR = "base_export_dir"
    EXPORT_PREFIX = "export_prefix"

    attr_defaults = {
        EXPORT_PREFIX : NONE_STR,
        BASE_EXPORT_DIR : "./exports",
    }

    def create_export(self, name : str, symbols : List):
        if len(name) > 0:
            for export in self.xpath(f"./{Export.tag_name}[@{Export.NAME}='{name}']"):
                logger.info("Deleting export...")
                export.delete()

        export = Export()
        export.set_attr_defaults()
        export.set_name(name)
        self.append(export)
        if len(name) > 0:
            export.set_next_id(name)
        else:
            export.set_next_id()

        for symbol in symbols:
            if isinstance(symbol, tuple):
                export.add_symbol(symbol[0], symbol[1])
            elif isinstance(symbol, str):
                export.add_symbol(symbol)
            else:
                logger.error(f"Unrecognized symbol data: {symbol}")
                continue


    def get_export_dir(self, export : Export) -> Path:
        base_export_dir = self.get(self.BASE_EXPORT_DIR)
        if self.is_unset(base_export_dir):
            logger.error("No base export dir found.")
            return None
        # TODO: add try/except for getting path
        return Path(base_export_dir).joinpath(self.get_full_export_name(export))


    def get_full_export_name(self, export : Export, palette : Palette = None) -> str:
        # TODO: remove invalid path characters
        export_name = export.get_name().lower()

        if palette is not None:
            palette_name = palette.get_name().lower()
            export_name = f"{palette_name}_{export_name}"

        export_prefix = self.get(self.EXPORT_PREFIX)
        if not self.is_unset(export_prefix):
            export_name = f"{export_prefix}_{export_name}"
        return export_name




class Config(OSTElementMixin, BaseElement):
    tag_name = f"{NS}:onispritetools"

    SVG_DOC_IDX = 0

    FRAME_MARGIN = "frame_margin"
    KANIMAL_PATH = "kanimal_path"
    TEMP_DIR = "temp_dir"
    IMAGE_SCALE = "doc_scale"
    VERSION = "ost_version"

    attr_defaults = {
        FRAME_MARGIN : 5,
        KANIMAL_PATH : NONE_STR,
        TEMP_DIR : "./temp",
        IMAGE_SCALE : 1.0,
    }


    def update_version(self):
        self.set(self.VERSION, __version__)


    @property
    def exports(self) -> Exports:
        result = self.xpath(f"./{Exports.tag_name}")
        if result is None or len(result) == 0:
            exports = Exports()
            exports.set_attr_defaults()
            self.append(exports)
            exports.set_next_id(exports.TAG)
            return exports
        elif len(result) == 1:
            return result[0]
        else:
            logger.error(f"Multiple <{Exports.tag_name}> tags found.")
            return result[0]


    @property
    def palettes(self) -> Palettes:
        result = self.xpath(f"./{Palettes.tag_name}")
        if result is None or len(result) == 0:
            palettes = Palettes()
            palettes.set_attr_defaults()
            self.append(palettes)
            palettes.set_next_id(palettes.TAG)
            return palettes
        elif len(result) == 1:
            return result[0]
        else:
            logger.error(f"Multiple <{Palettes.tag_name}> tags found.")
            return result[0]

