import logging; logger = logging.getLogger(__name__)
from typing import List
from types import SimpleNamespace

import inkex

from onispritetools.lib import ost_doc
from lib import sprite_rect, utils, scml_loader
from onispritetools.lib.ost_extension import OSTExtension



ALIGN_OPTION = "align_option"
AlignOption = SimpleNamespace()
AlignOption.XY = "align_xy"
AlignOption.X = "align_x"
AlignOption.Y = "align_y"
AlignOption.Matching = "align_matching"

DUPLICATE_TYPE = "duplicate_type"
DuplicateType = SimpleNamespace()
DuplicateType.CLONE = "clone"
DuplicateType.DUPLICATE = "duplicate"

DUPLICATE_POS = "duplicate_pos"
DuplicatePos = SimpleNamespace()
DuplicatePos.INSIDE_SPRITE_FRONT = "inside_sprite_front"
DuplicatePos.INSIDE_SPRITE_BACK = "inside_sprite_back"
DuplicatePos.OVER_SPRITE = "over_sprite"
DuplicatePos.UNDER_SPRITE = "under_sprite"

TARGET_SYMBOL = "target_symbol"


class AlignPivots(OSTExtension):

    def add_arguments(self, pars):
        pars.add_argument(
            f"--tab",
            type=self.arg_method("do"),
            default="align_pivots",
        )

        pars.add_argument(
            f"--{ALIGN_OPTION}",
            type=str,
            default=AlignOption.XY,
            dest=ALIGN_OPTION)

        pars.add_argument(
            f"--{DUPLICATE_TYPE}",
            type=str,
            default=DuplicateType.CLONE,
            dest=DUPLICATE_TYPE,
        )

        pars.add_argument(
            f"--{DUPLICATE_POS}",
            type=str,
            default=DuplicatePos.INSIDE_SPRITE_FRONT,
            dest=DUPLICATE_POS,
        )

        pars.add_argument(
            f"--{TARGET_SYMBOL}",
            type=str,
            default="",
            dest=TARGET_SYMBOL,
        )


    def effect(self):
        logger.info("Effect")
        self.options.tab()


    def do_align_pivots(self):
        logger.info("Align pivots")
        align_option = getattr(self.options, ALIGN_OPTION)
        match align_option:
            case AlignOption.XY:
                self.align_selected_pivots(True, True)
            case AlignOption.X:
                self.align_selected_pivots(True, False)
            case AlignOption.Y:
                self.align_selected_pivots(False, True)
            case AlignOption.Matching:
                self.align_matching_pivots()


    def do_duplicate(self):
        logger.info("Duplicate")
        duplicate_type = getattr(self.options, DUPLICATE_TYPE)
        duplicate_pos = getattr(self.options, DUPLICATE_POS)
        logger.debug(f"duplicate_type: {duplicate_type}")
        logger.debug(f"duplicate_pos: {duplicate_pos}")

        for elem in self.svg.selection:
            self.duplicate_elem(elem, duplicate_type, duplicate_pos)


    def do_move(self):
        logger.info("Move")
        doc = self.doc
        target_symbol_name = getattr(self.options, TARGET_SYMBOL)
        elem_labels : List[str] = []
        frame_layer : inkex.Layer = None
        for elem in self.svg.selection:
            elem_frame_layer = doc.elem_get_frame_layer_parent(elem)
            if frame_layer is None:
                frame_layer = elem_frame_layer
            elif frame_layer != elem_frame_layer:
                logger.error("Elements in multiple frames selected, aborting...")
                raise inkex.AbortExtension
            elem_labels.append(doc.elem_get_label(elem))

        source_symbol_layer = doc.elem_get_parent(frame_layer)
        source_symbol_name = doc.elem_get_label(source_symbol_layer)
        for source_layer in source_symbol_layer:
            source_sprite_group = doc.layer_get_sprite_group(source_layer)
            target_layer_label = doc.elem_get_label(source_layer).replace(source_symbol_name, target_symbol_name)
            target_layer = doc.get_layer(target_layer_label)
            if target_layer is None:
                logger.warning(f"Unable to find target layer: {target_layer_label}")
                continue
            target_sprite_group = doc.layer_get_sprite_group(target_layer)
            for elem_label in elem_labels:
                elems = source_sprite_group.xpath(f".//*[@inkscape:label='{elem_label}']")
                if len(elems) == 0:
                    logger.warning(f"No matching element <{elem_label}> found for layer {doc.elem_get_label(source_layer)}")
                    continue
                if len(elems) > 1:
                    logger.warning(f"Multiple matching elements <{elem_label}> found in {doc.elem_get_label(source_layer)}")
                for elem in elems:
                    source_idx = doc.elem_get_index(elem)
                    elem_parent = doc.elem_get_parent(elem)
                    if elem_parent != source_sprite_group:
                        logger.error(f"Elem is not a child of a sprite group.")
                        raise inkex.AbortExtension
                    elem_parent.remove(elem)
                    if source_idx == 0:
                        target_sprite_group.insert(0, elem)
                    else:
                        target_sprite_group.append(elem)
















    # -------------------------------------------------------

    def align_selected_pivots(self, align_x : bool, align_y : bool):
        doc = self.doc

        frame_layers = doc.get_selected_frame_layers()

        logger.info(f"Found {len(frame_layers)} frame layers in selection ({len(self.svg.selection)} elems)")
        if len(frame_layers) == 0:
            logger.warning("No frame layers found in selection.")
            return
        if len(frame_layers) == 1:
            logger.warning("Only one frame layer selected.")
            return

        doc.align_frame_layers(
            frame_layers,
            align_x=align_x,
            align_y=align_y)


    def align_matching_pivots(self):
        doc = self.doc
        matching_pivots = [
            ["torso", "pelvis", "belt"],
            ["foot", "leg", "leg_skin"],
            # ["snapto_hair", "snapto_hair_always"],
            # ["cuff", "arm_lower_sleeve"],
        ]

        MAX_IDX = 70
        frame_layers = doc.get_all_frame_layers()
        layer_dict = {}
        for layer in frame_layers:
            layer_dict[doc.elem_get_label(layer)] = layer

        for symbol_list in matching_pivots:
            for i in range(MAX_IDX):
                layers : List[inkex.Layer] = []

                for symbol in symbol_list:
                    frame_name = f"{symbol}_{i}"
                    # logger.info(frame_name)
                    layer = layer_dict.get(frame_name)
                    if layer is None:
                        continue
                    layers.append(layer)

                if len(layers) > 1:
                    logger.info(f"Aligning layers: {', '.join([doc.layer_get_name(layer) for layer in layers])}")
                    doc.align_frame_layers(layers)

    # -------------------------------------------------------

    def duplicate_elem(
            self,
            elem : inkex.BaseElement,
            duplicate_type : str,
            duplicate_pos : str):

        doc = self.doc

        frame_layer = doc.elem_get_frame_layer_parent(elem)
        symbol_layer = doc.elem_get_parent(frame_layer)
        target_frame_layers : List[inkex.Layer] = [layer for layer in symbol_layer if doc.is_frame_layer(layer)]

        for target_layer in target_frame_layers:
            if target_layer == frame_layer:
                continue
            logger.debug(f"target_layer={target_layer}")
            target_parent : inkex.BaseElement = None

            if duplicate_pos in [DuplicatePos.INSIDE_SPRITE_FRONT, DuplicatePos.INSIDE_SPRITE_BACK]:
                target_parent = doc.layer_get_sprite_group(target_layer)
            if duplicate_pos in [DuplicatePos.OVER_SPRITE, DuplicatePos.UNDER_SPRITE]:
                target_parent = target_layer

            logger.debug(f"target_parent={target_parent}")

            new_elem : inkex.BaseElement
            if duplicate_type == DuplicateType.DUPLICATE:
                new_elem = elem.copy()
            else:
                new_elem = inkex.Use()
                new_elem.set("xlink:href", f"#{elem.get_id()}")
                doc.elem_set_label(new_elem, doc.elem_get_label(elem))

            logger.debug(f"new_elem: {new_elem}")

            # TODO: position elem relative to pivot

            if duplicate_pos in [DuplicatePos.INSIDE_SPRITE_FRONT, DuplicatePos.OVER_SPRITE]:
                target_parent.append(new_elem)
            elif duplicate_pos in [DuplicatePos.INSIDE_SPRITE_BACK, DuplicatePos.UNDER_SPRITE]:
                target_parent.insert(0, new_elem)











if __name__ == '__main__':
    AlignPivots().run()
