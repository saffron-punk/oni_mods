import logging; logger = logging.getLogger(__name__)
from pathlib import Path
import os
import shutil
import subprocess

def get_file_stem(filepath : str) -> str:
    return Path(filepath).stem


# Sorts names alphabetically, then numerically by number after underscore,
# so that _10 is listed after _1.
# (Comparison functions return negative if the first item should come first,
# positive if it should be second, and 0 if they are equivalent.)
# layers.sort(key=functools.cmp_to_key(compare_frame_names))
def compare_frame_names(item1, item2):
    [name1, suffix1] = item1.rsplit('_', 1)
    [name2, suffix2] = item2.rsplit('_', 1)
    if name1 != name2:
        if name1 < name2:
            return -1
        else:
            return 1
    return int(suffix1) - int(suffix2)




def is_equal_approx(a : float, b : float, e : float) -> bool:
    return abs(a - b) <= e


def get_or_create_dir(path, clean=False) -> Path:
    if not path:
        return None
    path = Path(path)
    if path.exists():
        if clean:
            logger.debug(f"Deleting {path}...")
            shutil.rmtree(path)
            path.mkdir(parents=True)
    else:
        path.mkdir(parents=True)
    return path


# def dir_remove_contents(path, remove_dir=False):
#     dir = Path(path)
#     if not dir.exists():
#         return
#     for item in dir.iterdir():
#         if item.is_dir():
#             dir_remove_contents(item, True)
#         else:
#             item.unlink()
#     if remove_dir:
#         dir.rmdir()


# https://stackoverflow.com/questions/2878712/make-os-open-directory-in-python
def open_dir(path):
    try:
        # Windows only
        os.startfile(path)
    except:
        # May work on unix-based systems
        subprocess.Popen(['xdg-open', path])




