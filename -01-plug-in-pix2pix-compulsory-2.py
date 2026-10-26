#!/usr/bin/env python3

import gi
import sys

gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
from gi.repository import Gimp, GimpUi, GLib

from config import PLUGIN_PROC
from logger import log
from plugin_implementation import run_pix2pix


class Pix2PixCompulsory2Plugin(Gimp.PlugIn):
    def do_set_i18n(self, procname):
        return False

    def do_query_procedures(self):
        log("do_query_procedures called")
        return [PLUGIN_PROC]
    
    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(
            self,
            name,
            Gimp.PDBProcType.PLUGIN,
            self.run,
            None
        )

        procedure.set_image_types("*")
        procedure.set_menu_label("Pix2Pix Compulsory 2")
        procedure.add_menu_path("<Image>/Filters/Compulsory/")

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        log("run called")
        try:
            run_pix2pix(image, drawables)
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
        except Exception as error:
            log(f"run failed: {error}")
            return procedure.new_return_values(
                Gimp.PDBStatusType.EXECUTION_ERROR,
                GLib.Error(str(error)),
            )

log("plugin is loading")
log(f"STARTUP current proc = {PLUGIN_PROC}")
Gimp.main(Pix2PixCompulsory2Plugin.__gtype__, sys.argv)