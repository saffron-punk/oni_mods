import logging; logger = logging.getLogger(__name__)
import inkex
from onispritetools.lib.ost_extension import OSTExtension
from onispritetools.lib.ost_elements import Palettes, Palette, PaletteElem

PALETTE_NAME = "palette_name"

class ApplyPalette(OSTExtension):
    def add_arguments(self, pars):
        pars.add_argument(
            f"--{PALETTE_NAME}",
            type=str,
            default="",
            dest=PALETTE_NAME)

    def effect(self):
        doc = self.doc

        palette_name = getattr(self.options, PALETTE_NAME)
        # logger.info(f"Palette name: {palette_name}")
        if len(palette_name) == 0:
            logger.error("No palette name provided.")
            return

        doc.apply_palette(palette_name)



if __name__ == '__main__':
    ApplyPalette().run()