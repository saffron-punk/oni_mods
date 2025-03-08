import logging; logger = logging.getLogger(__name__)
import xml.etree.ElementTree as ET
from typing import List
import functools

from . import sprite_rect, utils


class Frame:
    def __init__(self, name : str, rect : sprite_rect.SpriteRect):
        self.name = name
        self.rect = rect

    def __str__(self):
        return f"<Frame: {self.name}>"

    @property
    def symbol_name(self):
        return self.name.rsplit('_', 1)[0]

    @property
    def frame_idx(self):
        return self.name.rsplit('_', 1)[1]


def load_frames_from_file(filepath : str) -> List[Frame]:
    frames = []

    try:
        tree = ET.parse(filepath)
    except Exception as e:
        logger.error(f"Error parsing {filepath}: {e.message} ({e.args})")
        return frames

    logger.info(f"Loading frames from {filepath}")
    root = tree.getroot()
    for folder in root.findall('folder'):
        for file in folder.findall('file'):
            try:
                frame_data = Frame(
                    name=utils.get_file_stem(file.get('name')),
                    rect=sprite_rect.get_rect_from_scml_frame(file))
            except Exception as e:
                logger.error(f"Error getting frame data: {e.message} ({e.args})")
                continue
            frames.append(frame_data)

    logger.info(f"before sort: {frames[0].name}")
    frames.sort(key=functools.cmp_to_key(compare_frame_names), reverse=True)
    logger.info(f"after sort: {frames[0].name}")

    return frames


def compare_frame_names(frame1, frame2):
    [name1, suffix1] = frame1.name.rsplit('_', 1)
    [name2, suffix2] = frame2.name.rsplit('_', 1)
    if name1 != name2:
        if name1 < name2:
            return -1
        else:
            return 1
    return int(suffix1) - int(suffix2)