#!/usr/bin/env python3
import gi

# from OnnxRuntime_Helper.pix2pix_onnx import ONNXPix2Pix, InferConfig

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
import sys
import os
import tempfile
import json
import urllib.request

plug_in_proc = "plug-in-pix2pix-compulsory-2"
LOG_FILE = os.path.join(tempfile.gettempdir(), plug_in_proc + ".log")


def log(msg):
    try:
        Gimp.message(msg)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception as e:
        print(f"Log error: {e}")

def plug_in_link_to_XXX_run(procedure, run_mode, image, drawables, config, run_data):
    log(plug_in_proc + "_run")
    log("Create New Layer")

    canvas_size = [1920, 1080]
    if image is None:
        image = Gimp.Image.new(canvas_size[0], canvas_size[1], Gimp.ImageBaseType.RGB)
        Gimp.Display.new(image)

    # Start undo group
    image.undo_group_start()

    user_layer = Gimp.Layer.new(image,
                                name="white",
                                width=canvas_size[0] /2,
                                height=canvas_size[1] /2,
                                type=0,
                                opacity=50,
                                mode=0)

    Gimp.Layer.set_offsets(user_layer, canvas_size[0] /4, canvas_size[1] /4)

    # Add layers to image
    image.insert_layer(user_layer, None, 0)

    # Fill with transparency
    user_layer.fill(Gimp.FillType.TRANSPARENT)

    # Test request to Flask server
    try:
        test_payload = {"test": "hello"}
        req_data = json.dumps(test_payload).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:5000/infer",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            response_body = resp.read().decode("utf-8")
            log(f"Server response: {response_body}")
    except Exception as e:
        log(f"Server request error: {e}")

    # Finish
    image.undo_group_end()
    Gimp.displays_flush()


class Plug_in_link_to_XXX(Gimp.PlugIn):

    def do_set_i18n(self, *args):
        # Disable localization lookup to avoid locale warnings
        return False

    def do_query_procedures(self):
        log("do_query_procedures called")
        return [plug_in_proc]

    def do_create_procedure(self, name):
        log(f"do_create_procedure called with: {name}")

        if name != plug_in_proc:
            return None

        procedure = Gimp.ImageProcedure.new(
            self, name,
            Gimp.PDBProcType.PLUGIN,
            self.run, None
        )

        procedure.set_image_types("*")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)
        procedure.set_menu_label("Pix2Pix Test")
        procedure.add_menu_path("<Image>/Filters/Test")
        procedure.set_icon_name(GimpUi.ICON_GEGL)
        procedure.set_documentation("Pix2Pix Test", "Pix2Pix Test", name)
        procedure.set_attribution("Your Name", "Your Name", "2026")

        # proc = Gimp.ImageProcedure.new(
        #     self, name,
        #     Gimp.PDBProcType.PLUGIN,
        #     self.run,
        #     None
        # )
        #
        # proc.set_image_types("*")
        # proc.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
        #
        # proc.set_menu_label(plug_in_proc + "-menu-label")
        # proc.add_menu_path("<Image>/Filters/" + plug_in_proc + "-menu")
        #
        # proc.set_documentation(
        #     plug_in_proc,
        #     name
        # )
        # proc.set_attribution("Your Name", "Your Name", "2026")

        log(f"Procedure {name} created successfully")
        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        log(f"run_data={run_data}")
        plug_in_link_to_XXX_run(procedure, run_mode, image, drawables, config, run_data)
        log(f"run_data=====>>>>>{image}")
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())



log("=== " + plug_in_proc + " Loading ===")
Gimp.main(Plug_in_link_to_XXX.__gtype__, sys.argv)
