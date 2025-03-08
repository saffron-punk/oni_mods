from __future__ import annotations
import logging; logger = logging.getLogger(__name__)
from typing import List
import math
import random
import inkex
from inkex.transforms import Vector2d



class Anim:
    def __init__(self, name : str, filepath : str):
        self.name = name
        self.filepath = filepath
        self.banks : List[Bank] = []
        self.symbol_hashes = {} # {hash : int : symbol_name : str}

    def __str__(self):
        return f"<Anim: {self.name} ({len(self.banks)} banks)>"

    # We will call this after the symbol_hashes dictionary is populated
    # to inject symbol names into keyframe elements.
    def update_frame_elements(self):
        for bank in self.banks:
            for keyframe in bank.keyframes:
                for elem in keyframe.elems:
                    symbol_name = self.symbol_hashes.get(elem.symbol_hash, None)
                    if symbol_name is None:
                        logger.error(f"No symbol name found for hash: {elem.symbol_hash}")
                        continue
                    elem.symbol_name = symbol_name
                    elem.symbol_frame_name = f"{symbol_name}_{elem.symbol_frame_id}"


    def get_all_symbol_frame_names(self) -> set:
        elem_names = set()
        for bank in self.banks:
            for keyframe in bank.keyframes:
                for name in keyframe.get_symbol_frame_names():
                    elem_names.add(name)
        return elem_names


    def contains_any_symbol_frame_names(self, frame_names) -> bool:
        anim_symbol_frames = self.get_all_symbol_frame_names()
        for name in anim_symbol_frames:
            if name in frame_names:
                return True
        return False


    def get_shuffled_banks(self) -> List[Bank]:
        shuffled_banks = self.banks.copy()
        random.shuffle(shuffled_banks)
        return shuffled_banks



class Bank:
    def __init__(self, idx : int, name : str, anim : Anim):
        self.name = name
        self.idx = idx
        self.anim = anim
        self.keyframes = []


    def add_keyframe(self, keyframe : Keyframe):
        self.keyframes.append(keyframe)
        keyframe.idx = len(self.keyframes) - 1
        keyframe.name = f"{self.name}_{keyframe.idx:03}"


    def get_shuffled_keyframes(self) -> List[Keyframe]:
        shuffled_keyframes = self.keyframes.copy()
        random.shuffle(shuffled_keyframes)
        return shuffled_keyframes


class Keyframe:
    def __init__(self,
                 idx : int,
                 x : float,
                 y : float,
                 width : float,
                 height : float,
                 bank : Bank):
        self.idx = idx
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bank = bank
        self.elems = []
        self.name = ""

    def __str__(self):
        return f"<Keyframe {self.bank.anim.name}:{self.name}>"


    def get_symbol_frame_names(self) -> set:
        elem_names = set()
        for elem in self.elems:
            elem_names.add(elem.symbol_frame_name)
        return elem_names



class FrameElement:
    def __init__(self,
                 symbol_hash : int,
                 symbol_frame_id : int,
                 matrix : List[float],
                 translation : tuple[float, float]):
        self.symbol_hash = symbol_hash
        self.symbol_frame_id = symbol_frame_id
        self.matrix = matrix
        self._translation = translation
        self.symbol_name = ""
        self.symbol_frame_name = ""

    # Adapted from kanimal-SE by skairunner (MIT)
    # https://github.com/skairunner/kanimal-SE/blob/master/kanimal/Anim.cs
    @property
    def translation(self) -> Vector2d:
        return Vector2d(self._translation[0]/2.0, self._translation[1]/2.0)


    @property
    def scale(self) -> Vector2d:
        M1 = self.matrix[0]
        M2 = self.matrix[1]
        M3 = self.matrix[2]
        M4 = self.matrix[3]
        scale_x = math.sqrt(M1*M1 + M2*M2)
        scale_y = math.sqrt(M3*M3 + M4*M4)
        det = M1*M4 - M3*M2
        if det < 0:
            scale_y *= -1
        return Vector2d(scale_x, scale_y)


    @property
    def angle(self) -> float:
        M1 = self.matrix[0]
        M2 = self.matrix[1]
        M3 = self.matrix[2]
        M4 = self.matrix[3]

        scale_x = self.scale.x
        scale_y = self.scale.y

        sinApprox = 0.5 * (M3 / scale_y - M2 / scale_x)
        cosApprox = 0.5 * (M1 / scale_x + M4 / scale_y)

        angle = math.atan2(sinApprox, cosApprox)
        if angle < 0:
            angle += 2 * math.pi
        angle *= 180 / math.pi
        return angle
