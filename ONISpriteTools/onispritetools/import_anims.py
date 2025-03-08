import logging; logger = logging.getLogger(__name__)
import types
from typing import List
from pathlib import Path
import random
import math
import os

import inkex
from inkex.transforms import Vector2d

from onispritetools.lib import ost_doc
from lib.anim import Anim, Bank, Keyframe, FrameElement
from onispritetools.lib.ost_elements import Config
from lib import sprite_rect, utils, scml_loader, bytes_loader
from onispritetools.lib.ost_extension import OSTExtension
from onispritetools.lib.ost_doc import GetMode
from onispritetools import NS

# TODO: turn into inputs
DELETE_OLD_KEYFRAMES = True
REFRESH_ANIMS = True
GET_FOR_ALL_FRAMES = False

# Action type
ACTION_TYPE = "action_type"
ActionType = types.SimpleNamespace()
ActionType.IMPORT_FILE = "action_type_import_file"
ActionType.IMPORT_FOLDER = "action_type_import_folder"
ActionType.REFRESH_SELECTED = "action_type_refresh_selected"

# Folder import action
ANIM_DIR_PATH = "anim_dir_path"
FOLDER_IMPORT_TYPE = "folder_import_type"
FolderImportType = types.SimpleNamespace()
FolderImportType.TYPE_RANDOM = "folder_import_type_random"
FolderImportType.TYPE_SELECTED = "folder_import_type_selected"

# General options
CLONE_VISIBLE_ONLY = "clone_visible_only"
MAX_KEYFRAMES = "max_keyframes"


class ImportAnims(OSTExtension):
    def add_arguments(self, pars):
        pars.add_argument(
            f"--{ACTION_TYPE}",
            type=str,
            default=ActionType.IMPORT_FILE,
            dest=ACTION_TYPE)

        pars.add_argument(
            f"--{FOLDER_IMPORT_TYPE}",
            type=str,
            default=FolderImportType.TYPE_RANDOM,
            dest=FOLDER_IMPORT_TYPE)

        pars.add_argument(
            f"--{ANIM_DIR_PATH}",
            type=str,
            default=None,
            dest=ANIM_DIR_PATH)

        pars.add_argument(
            f"--{CLONE_VISIBLE_ONLY}",
            type=inkex.Boolean,
            default=False,
            dest=CLONE_VISIBLE_ONLY)

        pars.add_argument(
            f"--{MAX_KEYFRAMES}",
            type=int,
            default=1,
            dest=MAX_KEYFRAMES)


    def effect(self):
        keyframes : List[Keyframe] = []

        self.anim_dir_path = getattr(self.options, ANIM_DIR_PATH)
        self.clone_visible_only = getattr(self.options, CLONE_VISIBLE_ONLY)
        self.max_keyframes = getattr(self.options, MAX_KEYFRAMES)

        action_type = getattr(self.options, ACTION_TYPE)
        logger.debug(f"action_type={action_type}")
        match action_type:
            case ActionType.IMPORT_FILE:
                logger.debug("ActionType.IMPORT_FILE")
                # TODO
                pass
            case ActionType.IMPORT_FOLDER:
                logger.debug("ActionType.IMPORT_FOLDER")
                import_type = getattr(self.options, FOLDER_IMPORT_TYPE)
                logger.debug(f"import_type={import_type}")
                match import_type:
                    case FolderImportType.TYPE_RANDOM:
                        logger.debug("FolderImportType.TYPE_RANDOM")
                        keyframes = self.get_random_keyframes()
                    case FolderImportType.TYPE_SELECTED:
                        logger.debug("FolderImportType.TYPE_SELECTED")
                        keyframes = self.get_keyframes_for_selected_frames()
            case ActionType.REFRESH_SELECTED:
                keyframes = self.get_keyframes_to_refresh()

        logger.info(f"Keyframes found: {len(keyframes)} (max: {self.max_keyframes})")
        for keyframe in keyframes:
            logger.info(f"\t- {keyframe}")
            self.add_keyframe_preview(keyframe)


    def get_keyframes_to_refresh(self) -> List[Keyframe]:
        doc = self.doc

        keyframes : List[Keyframe] = []

        root_anim_layer = doc.get_root_anim_layer()
        if root_anim_layer is None:
            return

        for layer in doc.get_all_layers(root_anim_layer):
            # Don't refresh locked layers.
            if doc.elem_is_locked_recursive(layer):
                continue

            anim_path = doc.elem_get_ns_property(layer, ost_doc.ANIM_PATH_PROP)
            if anim_path is None:
                continue

            keyframe = self.get_keyframe_from_anim_path(anim_path)
            if keyframe is None:
                continue
            keyframes.append(keyframe)
        return keyframes


    def get_keyframes_for_selected_frames(self) -> List[Keyframe]:
        logger.debug("get_keyframes_for_selected_frames()")
        doc = self.doc

        selected_frame_names = set()
        frame_layers = doc.get_selected_frame_layers()
        for layer in frame_layers:
            name = doc.elem_get_label(layer)
            selected_frame_names.add(name)
        if len(selected_frame_names) == 0:
            logger.error("No symbol frames found in selection.")
            return []
        logger.debug(f"selected_frame_names={', '.join(selected_frame_names)}")

        keyframes : List[Keyframe] = []
        max_keyframes = self.max_keyframes

        for anim in self.random_anim_from_dir():
            if anim is None:
                break

            if not anim.contains_any_symbol_frame_names(selected_frame_names):
                continue

            for bank in anim.get_shuffled_banks():
                bank_has_selected_frame = False
                for keyframe in bank.get_shuffled_keyframes():
                    keyframe_has_selected_frame = False
                    keyframe_names = keyframe.get_symbol_frame_names()
                    # TODO: Change to a union function
                    for name in keyframe_names:
                        if name in selected_frame_names:
                            # Don't break iteraction.
                            # We want to give credit for any/all selected frames
                            # contained in this keyframe.
                            keyframe_has_selected_frame = True
                            selected_frame_names.remove(name)

                    if keyframe_has_selected_frame:
                        keyframes.append(keyframe)
                        logger.info(f"Adding {anim} {keyframe}... {len(selected_frame_names)} remaining")
                        bank_has_selected_frame = True
                        break

                # Break out of bank and keyframe loops so that
                # a new anim can be chosen. This will increase variety,
                # but will make execution slower if a certain frame is only
                # contained in a single or small number of anims.
                if bank_has_selected_frame:
                    break

            if len(selected_frame_names) == 0:
                # All selected frames found.
                break
            if len(keyframes) >= max_keyframes:
                # Reached max keyframes.
                break

        logger.info(f"Missing symbol frames: {len(selected_frame_names)}")
        for frame in selected_frame_names:
            logger.info(f"\t- {frame}")
        self.log_newline()

        return keyframes


    def get_random_keyframes(self) -> List[Keyframe]:
        logger.debug("get_keyframes_for_selected_frames()")
        doc = self.doc

        keyframes : List[Keyframe] = []
        max_keyframes = self.max_keyframes

        for anim in self.random_anim_from_dir():
            if len(keyframes) >= max_keyframes:
                break

            if anim is None:
                break

            bank = anim.get_shuffled_banks()[0]
            if bank is None:
                continue

            keyframe = bank.get_shuffled_keyframes()[0]
            if keyframe is None:
                continue

            keyframes.append(keyframe)

        return keyframes




    def get_keyframe_from_anim_path(self, anim_path : str) -> Keyframe:
        [filepath, bank_idx, keyframe_idx] = anim_path.split(',')
        logger.debug(f"Found anim_path:\n\tfilepath: {filepath}\n\tbank_idx: {bank_idx}\n\tkeyframe_idx: {keyframe_idx}")
        filepath = self.doc.path_convert_to_absolute(filepath)
        anim = bytes_loader.import_anim_bytes(filepath)
        bank : Bank
        try:
            bank = anim.banks[int(bank_idx)]
        except Exception as e:
            logger.error(e)
            return None
        keyframe : Keyframe = bank.keyframes[int(keyframe_idx)]
        try:
            keyframe = bank.keyframes[int(keyframe_idx)]
        except Exception as e:
            logger.error(e)
            return None
        logger.info(f"Found: {anim} {bank} {keyframe}")
        self.log_newline()
        return keyframe



    def random_anim_from_dir(self):
        dirpath = self.anim_dir_path
        if dirpath is None:
            return []
        dirpath = Path(dirpath)
        filenames = os.listdir(dirpath)
        filepaths = [dirpath.joinpath(f) for f in filenames]

        MAX_ITERS = 3
        i = 0

        while i < MAX_ITERS:
            shuffled_filepaths = filepaths.copy()
            random.shuffle(shuffled_filepaths)
            for filepath in shuffled_filepaths:
                anim : Anim
                try:
                    anim = bytes_loader.import_anim_bytes(filepath)
                except Exception as e:
                    logger.error(e)
                else:
                    yield anim
            i += 1


    def add_keyframe_preview(self, keyframe : Keyframe):
        doc = self.doc
        anim : Anim = keyframe.bank.anim

        prev_layer_xform : inkex.Transform = None
        prev_box_style : inkex.Style = None

        root_anim_layer = doc.get_root_anim_layer(GetMode.GET_OR_CREATE)

        anim_name_stripped = anim.name.removeprefix("anim_").removesuffix("_anim")
        keyframe_layer_name = f"{anim_name_stripped}__{keyframe.name}"
        rel_anim_path = doc.path_convert_to_relative(keyframe.bank.anim.filepath)
        anim_path_prop = f"{rel_anim_path},{keyframe.bank.idx},{keyframe.idx}"

        result = root_anim_layer.xpath(f".//svg:g[@{NS}:{ost_doc.ANIM_PATH_PROP}='{anim_path_prop}']")
        if len(result) > 0:
            old_keyframe_layer = result[0]
            if not doc.elem_is_locked_recursive(old_keyframe_layer):
                prev_layer_xform = old_keyframe_layer.transform
                try:
                    prev_box_style = old_keyframe_layer.xpath("./svg:rect")[0].get("style")
                except Exception as e:
                    logger.error(e)
                old_keyframe_layer.delete()

        keyframe_layer = inkex.Layer()
        doc.elem_set_label(keyframe_layer, keyframe_layer_name)
        doc.elem_set_ns_property(
            keyframe_layer,
            ost_doc.ANIM_PATH_PROP,
            anim_path_prop)

        sorted_elems = keyframe.elems.copy()
        sorted_elems.reverse()

        for elem in sorted_elems:
            clone = self.get_elem_clone(elem)
            if clone is None:
                continue
            keyframe_layer.append(clone)

        # keyframe_layer needs to be in svg to get its bounding box.
        self.svg.append(keyframe_layer)
        pos = doc.get_next_anim_pos()
        bbox = keyframe_layer.bounding_box()
        if bbox is None:
            return
        pos.x -= bbox.width/2.0
        pos.y += bbox.height/2.0
        try:
            pos.x = min(pos.x, root_anim_layer.bounding_box().left + bbox.width/2.0)
        except:
            pass

        anim_bkg = self.create_keyframe_bkg(bbox)
        keyframe_layer.insert(0, anim_bkg)
        if prev_box_style is not None:
            anim_bkg.set("style", prev_box_style)

        if prev_layer_xform is not None:
            keyframe_layer.transform = prev_layer_xform
        else:
            keyframe_layer.transform.add_translate(pos)
        self.svg.remove(keyframe_layer)
        root_anim_layer.insert(0, keyframe_layer)


    # def get_random_anims(self) -> List[Anim]:
    #     anims : List[Anim] = []
    #     anim_filepaths = os.listdir(ANIM_FOLDER_PATH)
    #     for _ in range(3):
    #         file = random.choice(anim_filepaths)
    #         filepath = Path(ANIM_FOLDER_PATH).joinpath(file)
    #         anim = bytes_loader.import_anim_bytes(filepath)
    #         if anim is None:
    #             continue
    #         logger.info(f"Anim loaded: {anim}")
    #         anims.append(anim)
    #     return anims


    # def get_random_keyframes(self, anim : Anim) -> List[Keyframe]:
    #     keyframes : List[Bank] = []
    #     for _ in range(1):
    #         bank = random.choice(anim.banks)
    #         keyframes.append(random.choice(bank.keyframes))
    #     return keyframes


    def get_elem_clone(self, elem : FrameElement) -> inkex.Use:
        doc = self.doc

        symbol_root_layer = doc.get_symbols_layer()
        results = symbol_root_layer.xpath(f".//svg:g[@inkscape:label='{elem.symbol_frame_name}']")
        symbol_frame_layer = None
        for layer in results:
            logger.debug(f"layer {doc.elem_get_label(layer)} - is_visible()={layer.is_visible()}")
            if self.clone_visible_only and not layer.is_visible():
                continue
            symbol_frame_layer = layer

        if symbol_frame_layer is None:
            logger.warning(f"No symbol layer found for {elem.symbol_frame_name}.")
            return None
        logger.info(f"Adding {elem.symbol_frame_name} to animation...")

        sprite_group = doc.layer_get_sprite_group(symbol_frame_layer)
        if sprite_group is None:
            logger.error(f"No sprite group found in layer {doc.layer_get_name(symbol_frame_layer)}.")
            return None

        clone = inkex.Use()
        clone.href = sprite_group
        doc.elem_set_label(clone, elem.symbol_frame_name)

        pivot_pos = doc.layer_get_pivot_pos(symbol_frame_layer)

        # logger.info(f"Pivot pos: {pivot_pos}")
        # logger.info(f"Matrix: {elem.matrix[0]} {elem.matrix[1]} {elem.matrix[2]} {elem.matrix[3]}")
        # logger.info(f"Translation: {elem.translation}")
        # logger.info(f"Scale: {elem.scale}")
        # logger.info(f"Angle: {elem.angle}")
        # logger.info(f"keyframe: {keyframe.x} {keyframe.y}")
        # logger.new_line()

        # Align pivot position at (0,0)
        clone.transform.add_translate(-pivot_pos)

        # Transforms must be applied in this order.
        xform = inkex.Transform()
        xform.add_translate((elem.translation * self.image_scale) / doc.get_scale())

        # 360 - elem.angle is necessary to get correct angle.
        xform.add_rotate(360 - elem.angle, pivot_pos.x, pivot_pos.y)

        # Translate before and after to scale object around pivot.
        xform.add_translate(pivot_pos)
        xform.add_scale(elem.scale.x, elem.scale.y)
        xform.add_translate(-pivot_pos)

        clone.transform = clone.transform @ xform
        return clone


    def create_keyframe_bkg(self, bbox) -> inkex.Rectangle:
        doc = self.doc
        anim_bkg = inkex.Rectangle()
        anim_bkg.set('width', bbox.width + (ost_doc.ANIM_BKG_PADDING * 2)/doc.get_scale())
        anim_bkg.set('height', bbox.height + (ost_doc.ANIM_BKG_PADDING * 2)/doc.get_scale())
        anim_bkg.transform.add_translate(
            (bbox.left - (ost_doc.ANIM_BKG_PADDING/doc.get_scale()),
             bbox.top - (ost_doc.ANIM_BKG_PADDING/doc.get_scale())))
        anim_bkg.style['fill'] = ost_doc.ANIM_BKG_COLOR
        doc.elem_set_label(anim_bkg, ost_doc.ANIM_BKG_LABEL)
        return anim_bkg


if __name__ == '__main__':
    ImportAnims().run()
