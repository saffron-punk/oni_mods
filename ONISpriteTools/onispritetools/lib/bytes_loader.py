import logging; logger = logging.getLogger(__name__)
from typing import List
import struct
from pathlib import Path

from .anim import Anim, Bank, Keyframe, FrameElement

# Adapted from kanimal-SE by skairunner (MIT)
# (https://github.com/skairunner/kanimal-SE/blob/master/kanimal/Reader/KanimReader.cs)
def import_anim_bytes(filepath) -> Anim:
    anim = Anim(Path(filepath).stem, filepath)

    with open(filepath, mode='rb') as file:
        expected_header = "ANIM"
        header = file.read(len(expected_header)).decode('ascii')
        if header != expected_header:
            logger.error(f"{filepath} is not a kanim animation.", True)
            return None

        logger.info(f"Loading animation from {filepath}...")

        [_version, _elem_count, _frame_count, bank_count] = struct.unpack('iiii', file.read(16))

        for bank_idx in range(bank_count):
            name = read_p_str(file)
            [_hash, _rate, keyframe_count] = struct.unpack('ifi', file.read(12))

            bank = Bank(bank_idx, name, anim)
            anim.banks.append(bank)

            for keyframe_idx in range(keyframe_count):
                [x, y, width, height, elem_count] = struct.unpack('ffffi', file.read(20))
                keyframe = Keyframe(keyframe_idx, x, y, width, height, bank)
                bank.add_keyframe(keyframe)

                for _ in range(elem_count):
                    [symbol_hash, symbol_frame_id, _layer, _flags] = struct.unpack('iiii', file.read(16))
                    [_A, _B, _G, _R, M1, M2, M3, M4, M5, M6, _order] = struct.unpack('f' * 11, file.read(11 * 4))
                    elem = FrameElement(symbol_hash, symbol_frame_id, [M1, M2, M3, M4], (M5, M6))
                    keyframe.elems.append(elem)

        [_max_visible_symbol_frames] = struct.unpack('i', file.read(4))
        [symbol_hash_count] = struct.unpack('i', file.read(4))

        for _ in range(symbol_hash_count):
            [hash] = struct.unpack('i', file.read(4))
            text = read_p_str(file)
            anim.symbol_hashes[hash] = text

    anim.update_frame_elements()
    return anim


def read_p_str(file) -> str:
    size = read_int32(file)
    if size <= 0:
        return ""
    return file.read(size).decode('ascii')


def read_int32(file) -> int:
    return struct.unpack('i', file.read(4))[0]