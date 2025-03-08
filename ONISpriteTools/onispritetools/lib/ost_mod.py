from typing import List
import logging; logger = logging.getLogger(__name__)
import sys
import os
import subprocess
import functools
from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
from pathlib import Path
import json

import inkex
from inkex import Layer
import inkex.command

from onispritetools.lib.ost_elements import Config, Exports, Export, Symbol, Palette

from lib import utils
from onispritetools.lib.ost_extension import OSTExtension
from onispritetools.lib.ost_doc import GetMode


KANIM_SUBDIR = "anim/assets"
OUTFITPACK_SUBDIR = "outfits_included"
MOD_YAML_FILENAME = "mod.yaml"
MOD_INFO_YAML_FILENAME = "mod_info.yaml"
OI_CLOTHING_ITEMS_FILENAME = "clothing_items.json"
OI_CLOTHING_OUTFITS_FILENAME = "clothing_outfits.json"
MIN_BUILD = "652372"


class DevMod(object):
    def __init__(self, mod_id : str, root_dir : str | Path, replace : bool):
        self.mod_id = mod_id

        self.mod_dir_name = mod_id
        if "." in mod_id:
            self.mod_dir_name = mod_id.split(".")[-1]

        self.base_dir = utils.get_or_create_dir(Path(root_dir).joinpath(self.mod_dir_name), clean=replace)
        self.kanim_dir = utils.get_or_create_dir(self.base_dir.joinpath(KANIM_SUBDIR))
        self.outfitpack_dir = utils.get_or_create_dir(self.base_dir.joinpath(OUTFITPACK_SUBDIR))

        self._create_mod_yaml()
        self._create_mod_info_yaml()

        self._clothing_items_categories = {}
        self._clothing_items_name_strings = {}
        self._clothing_items_description_strings = {}
        self._clothing_outfit_items = {}
        self._clothing_outfit_types = {}


    def _create_mod_yaml(self):
        filepath = self.base_dir.joinpath(MOD_YAML_FILENAME)
        with open(filepath, "w") as file:
            file.write(f"title: {self.mod_dir_name}\n")
            file.write("description: A testing mod.\n")
            file.write(f"staticID: {self.mod_id}")


    def _create_mod_info_yaml(self):
        filepath = self.base_dir.joinpath(MOD_INFO_YAML_FILENAME)
        with open(filepath, "w") as file:
            file.write("supportedContent: ALL\n")
            file.write(f"minimumSupportedBuild: {MIN_BUILD} \n")
            file.write("version: 0.0.0\n")
            file.write("APIVersion: 2")


    def add_clothing_item(self, id : str, category : str, name_string = "", description_string = ""):
        self._clothing_items_categories[id] = category
        if len(name_string) != 0:
            self._clothing_items_name_strings[id] = name_string
        if len(description_string) != 0:
            self._clothing_items_description_strings[id] = description_string


    def add_clothing_outfit(self, id : str, type : str, item_ids : list[str]):
        self._clothing_outfit_items[id] = item_ids
        self._clothing_outfit_types[id] = type


    def create_clothing_items_json(self):
        data = {"items": []}
        for id, category in self._clothing_items_categories.items():
            item_dict = {
                "id": id,
                "category": category,
            }
            name_string = self._clothing_items_name_strings.get(id, "")
            description_string = self._clothing_items_description_strings.get(id, "")
            if len(name_string) > 0:
                item_dict["name"] = name_string
            if len(description_string) > 0:
                item_dict["description"] = description_string
            data["items"].append(item_dict)
        filepath = self.outfitpack_dir.joinpath(OI_CLOTHING_ITEMS_FILENAME)
        with open(filepath, "w") as file:
            json.dump(data, file, indent=True, sort_keys=True)


    def create_clothing_outfits_json(self):
        data = {"outfits": []}
        for id, type in self._clothing_outfit_types.items():
            clothing_items = self._clothing_outfit_items.get(id, None)
            if clothing_items is None:
                logger.error(f"No clothing items for outfit {id}")
                continue
            data["outfits"].append({
                "id": id,
                "type": type,
                "name": id,
                "items": clothing_items,
            })
        filepath = self.outfitpack_dir.joinpath(OI_CLOTHING_OUTFITS_FILENAME)
        with open(filepath, "w") as file:
            json.dump(data, file, indent=True, sort_keys=True)
