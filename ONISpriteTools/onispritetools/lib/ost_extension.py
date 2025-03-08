import logging; logger = logging.getLogger(__name__)
import os
from datetime import datetime
from pathlib import Path
from platform import python_version
import sys

from lxml import etree
from io import StringIO

import inkex
from inkex import EffectExtension

from onispritetools import __version__, NS, NSURI
from onispritetools.lib import ost_doc, utils
from onispritetools.lib.ost_elements import Config, Exports


class OSTExtension(EffectExtension):
    extra_nss = {NS: NSURI}
    log_filename = 'onispritetools.log'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log_setup()


    def _log_setup(self):
        document_dir = Path(self.document_path()).parent
        filepath = Path(document_dir).joinpath(self.log_filename)
        logging.basicConfig(
            filename=filepath,
            filemode='w',
            format='%(levelname)s: %(message)s',
            level=logging.DEBUG)

        pythondir = Path(sys.executable).parent
        scriptname = Path(sys.modules[self.__module__].__file__).name
        docfilepathparts = Path(self.document_path()).parts
        if len(docfilepathparts) >= 2:
            docfileloc = docfilepathparts[-2] + "\\" + docfilepathparts[-1]
        else:
            docfileloc = "Unsaved document"

        logger.info(datetime.now())
        logger.info(f"Interpreter: Python {python_version()} ({pythondir})")
        logger.info(f"Extension: ONI Sprite Tools {__version__}: {self.name} ({scriptname})")
        logger.info(f"Document: {docfileloc}")
        self.log_divider()


    def log_newline(self):
        logger.info("")


    def log_divider(self):
        logger.info("-" * 74)


    def log_command_result(self, result : str):
        self.log_newline()
        s = "Result:\n\t"
        s += "\n\t".join(result.splitlines())
        logger.debug(s)



    # The svg is not loaded at the time of init() so we cannot create it above.
    # But, by the time we reference it from the extension's methods, the svg will be loaded,
    # so we can lazy load it like this.
    # The alternative would be overriding the SvgInputMixin's load()
    # to load it right after the svg is loaded. But, in testing, that caused
    # inheritance problems and resulted in an empty document property.
    _doc : ost_doc.OSTDoc = None
    @property
    def doc(self) -> ost_doc.OSTDoc:
        if self._doc is None:
            # self.validate_ns()
            self._doc = ost_doc.OSTDoc(self)
        return self._doc

    @property
    def image_scale(self) -> float:
        return float(self._doc.get_config().get(Config.IMAGE_SCALE))

    # Discards any changes made to the input document in this script,
    # and passes the original document back to Inkscape.
    def discard_changes(self):
        self.document = self.original_document


    def get_document_dir(self) -> Path:
        return Path(self.document_path()).parent


    def get_temp_dir(self) -> Path:
        config = self.doc.get_config()
        if config is None:
            return None
        temp_dir = config.get(Config.TEMP_DIR)
        if not os.path.isabs(temp_dir):
            temp_dir = self.get_document_dir().joinpath(temp_dir)
        return utils.get_or_create_dir(temp_dir, clean=True)


    def get_export_dir(self) -> Path:
        config = self.doc.get_config()
        if config is None:
            return None
        export_dir = config.exports.get(Exports.BASE_EXPORT_DIR)
        if not os.path.isabs(export_dir):
            export_dir = self.get_document_dir().joinpath(export_dir)
        return utils.get_or_create_dir(export_dir, clean=False)



