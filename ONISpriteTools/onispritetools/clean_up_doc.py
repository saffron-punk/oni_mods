import logging; logger = logging.getLogger(__name__)
import inkex
from onispritetools.lib.ost_extension import OSTExtension

# TODO: make options
# UPDATE_BOXES = True
CONVERT_PATHS_TO_RELATIVE = True

class CleanUpDoc(OSTExtension):
    def effect(self):
        doc = self.doc
        doc.clean_up_frame_layers()

        if CONVERT_PATHS_TO_RELATIVE:
            doc.convert_image_paths_to_relative()

        # if UPDATE_BOXES:
        #     doc.update_all_boxes()





if __name__ == '__main__':
    CleanUpDoc().run()
