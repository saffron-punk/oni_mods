import logging; logger = logging.getLogger(__name__)
from types import SimpleNamespace
import inkex
import re
from onispritetools.lib.ost_extension import OSTExtension
from onispritetools.lib.ost_elements import Config, Palettes, Palette, PaletteElem


PALETTE_NAME = "palette_name"

CREATE_TYPE = "create_type"
CreateType = SimpleNamespace()
CreateType.NEW = "create_type_new"
CreateType.TEMPLATE = "create_type_template"

UPDATE_ONLY = "update_only"
TEMPLATE_PALETTE_NAME = "template_palette_name"

SELECTED_ONLY = "selected_only"


INCLUDE_CLONES = False
INCLUDE_GROUPS = False


class SavePalette(OSTExtension):
    def add_arguments(self, pars):
        pars.add_argument(
            f"--{PALETTE_NAME}",
            type=str,
            default="",
            dest=PALETTE_NAME)

        pars.add_argument(
            f"--{CREATE_TYPE}",
            type=str,
            default=CreateType.NEW,
            dest=CREATE_TYPE)

        pars.add_argument(
            f"--{UPDATE_ONLY}",
            type=inkex.Boolean,
            default=False,
            dest=UPDATE_ONLY)

        pars.add_argument(
            f"--{TEMPLATE_PALETTE_NAME}",
            type=str,
            default="",
            dest=TEMPLATE_PALETTE_NAME)

        pars.add_argument(
            f"--{SELECTED_ONLY}",
            type=inkex.Boolean,
            default=False,
            dest=SELECTED_ONLY)


    def effect(self):
        doc = self.doc
        config = doc.get_config()
        palettes = config.palettes


        palette_name = getattr(self.options, PALETTE_NAME)
        if len(palette_name) == 0:
            logger.error("Palette must have a name.")
            return

        create_type = getattr(self.options, CREATE_TYPE)
        from_template = False
        template_palette_name = ""

        if create_type == CreateType.NEW:
            update_only = getattr(self.options, UPDATE_ONLY)
        elif create_type == CreateType.TEMPLATE:
            update_only = True
            from_template = True
            template_palette_name = getattr(self.options, TEMPLATE_PALETTE_NAME)

        selected_only = getattr(self.options, SELECTED_ONLY)

        elem_styles = {}
        sprite_elems = self.get_sprite_elems(selected_only)

        sorted_labels = list(sprite_elems.keys())
        sorted_labels.sort()

        for label in sorted_labels:
            elem = sprite_elems[label]
            style_list = self.get_styles_list(elem)
            if style_list is None or len(style_list) == 0:
                continue
            style_str = ";".join(style_list)
            elem_styles[label] = style_str

        logger.debug("Styles")
        for label, style in elem_styles.items():
            logger.debug(f"\t{label} = {style}")

        if from_template:
            template_palette = palettes.get_palette(template_palette_name)
            if template_palette is None:
                logger.error(f"No template palette found with name: {template_palette_name}")
                raise inkex.AbortExtension("Template palette not found.")

            new_palette = template_palette.duplicate()
            new_palette.set_name(palette_name)
            new_palette.set_next_id(palette_name)
            for elem in new_palette:
                elem.set_next_id(elem.get(PaletteElem.ELEM_LABEL))

        if update_only:
            palette_count = len(palettes.xpath(f"./{Palette.tag_name}[@{Palette.NAME}='{palette_name}']"))
            if palette_count == 0:
                logger.error(f"No palette found with name {palette_name}")
                raise inkex.AbortExtension("Palette name not found.")

        # Create palette
        palettes.create_palette(palette_name, elem_styles, replace=(not update_only))



    def get_sprite_elems(self, selected_only : bool) -> dict:
        doc = self.doc
        config = doc.get_config()
        palettes = config.palettes
        exclude_labels = palettes.exclude_labels

        elems = {}

        frame_layers : list[inkex.Layer] = []
        if selected_only == True:
            frame_layers = doc.get_selected_frame_layers()
        else:
            frame_layers = doc.get_all_frame_layers()

        for layer in frame_layers:
            sprite_group = doc.layer_get_sprite_group(layer)
            if sprite_group is None:
                continue
            for elem in sprite_group.xpath(".//*"):
                if not INCLUDE_CLONES and isinstance(elem, inkex.Use):
                    continue
                if not INCLUDE_GROUPS and isinstance(elem, inkex.Group):
                    continue

                label = doc.elem_get_label(elem)
                if label is None:
                    continue
                if label in elems:
                    # Only parse each label once.
                    continue

                excluded = False
                for exclude_pattern in exclude_labels:
                    if re.search(exclude_pattern, label) is not None:
                        excluded = True
                        break
                if excluded:
                    continue

                elems[label] = elem
        return elems



    def get_styles_list(self, elem : inkex.BaseElement) -> list[str]:
        NONE_STYLE = "none"
        EPSILON = 0.0001

        doc = self.doc
        config = doc.get_config()
        exclude_styles = config.palettes.exclude_styles

        styles_list = []

        if elem._is_visible(False):
            styles_list.append("display:inline")
        else:
            # Don't save extraneous styles if element is hidden
            styles_list.append("display:none")
            return styles_list

        exclude_styles.append("display")

        style = elem.specified_style()

        # Don't save unnecessary stroke/fill data if stroke or fill is not displayed.
        stroke_style = style.get("stroke", NONE_STYLE)
        stroke_width = style.get("stroke-width", 0.0)
        stroke_opacity = style.get_color("stroke").alpha
        if stroke_style == NONE_STYLE or float(stroke_width) < EPSILON or stroke_opacity < EPSILON:
            exclude_styles.append("stroke")
            if not isinstance(elem, inkex.Group):
                styles_list.append("stroke:none")

        fill_style = style.get("fill", NONE_STYLE)
        fill_opacity = 1.0
        try:
            fill_opacity = style.get_color("fill").alpha
        except Exception as e:
            logger.error("Retrieving fill opacity failed.")

        if fill_style == NONE_STYLE or fill_opacity < EPSILON:
            exclude_styles.append("fill")
            if not isinstance(elem, inkex.Group):
                styles_list.append("fill:none")

        for key, value in style.items():
            excluded = False
            for exclude_pattern in exclude_styles:
                if re.search(exclude_pattern, key) is not None:
                    excluded = True
                    break
            if excluded:
                continue

            styles_list.append(f"{key}:{value}")

        return styles_list




if __name__ == '__main__':
    SavePalette().run()