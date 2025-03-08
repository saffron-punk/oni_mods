import logging; logger = logging.getLogger(__name__)
import inkex

from onispritetools.lib import ost_doc
from lib import sprite_rect, utils, scml_loader
from onispritetools.lib.ost_extension import OSTExtension


class DisplayToggles(OSTExtension):
    def add_arguments(self, pars):
        pars.add_argument(
            '--show_pivots',
            type=inkex.Boolean,
            default=False,
            dest='show_pivots')

        pars.add_argument(
            '--show_boxes',
            type=inkex.Boolean,
            default=False,
            dest='show_boxes')

        pars.add_argument(
            '--show_extra_elems',
            type=inkex.Boolean,
            default=False,
            dest='show_extra_elems')

        pars.add_argument(
            '--show_sprite_groups',
            type=inkex.Boolean,
            default=False,
            dest='show_sprite_groups')


    def effect(self):
        show_pivots = self.options.show_pivots
        show_boxes = self.options.show_boxes
        show_extras = self.options.show_extra_elems
        show_sprite_groups = self.options.show_sprite_groups

        logger.info(f"Show pivots: {show_pivots}")
        logger.info(f"Show boxes: {show_boxes}")
        logger.info(f"Show extras: {show_extras}")

        doc = self.doc

        doc.toggle_pivots(show_pivots)
        doc.toggle_extras(show_extras)

        if show_boxes:
            doc.update_all_boxes()
        else:
            doc.delete_all_boxes()


        for layer in doc.get_selected_frame_layers():
            sprite_group = doc.layer_get_sprite_group(layer)
            if show_sprite_groups:
                sprite_group.style["display"] = "inline"
            else:
                sprite_group.style["display"] = "none"





if __name__ == '__main__':
    DisplayToggles().run()
