#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
import sys
from gi.repository import Gio  # Import Gio for GFile

plug_in_proc = "plug-in-export-webp"
def prcedure_runner(procedure, inputs):
    config = procedure.create_config()
    for key, value in inputs.items():  # Loop through the dictionary directly
        config.set_property(key, value)
    procedure.run(config)

def export_webp_run(procedure, run_mode, image, drawables, config, data):
    
    # Always append ".webp" to the file path
    file_path = config.get_property('file-path')
    if not file_path:
        raise ValueError("The 'file-path' property is empty or not set.")
    file_path += ".webp"
    # Convert the file path to a GFile object
    gfile = Gio.File.new_for_path(file_path)
    # Prepare procedures to call
    file_webp_export = Gimp.get_pdb().lookup_procedure("file-webp-export")
    
    # Export the image as WebP
    image.undo_group_start()

    try:
        # Call the file-webp-export procedure using the correct property names
        file_webp_export_inputs = {
            "image": image,
            "file": gfile,
            "quality": 75,
            "alpha-quality": 75,
            "include-thumbnail": False,  
        }
        prcedure_runner(file_webp_export, file_webp_export_inputs)
    except Exception as e:
        image.undo_group_end()
        return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR,
                                           GLib.Error(f"Failed to export image: {str(e)}"))
    image.undo_group_end()

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)

class ExportWebP(Gimp.PlugIn):
    def do_query_procedures(self):
        return [plug_in_proc]

    def do_create_procedure(self, name):
        procedure = None

        if name == plug_in_proc:
            procedure = Gimp.ImageProcedure.new(self, name,
                                                Gimp.PDBProcType.PLUGIN,
                                                export_webp_run, None)
            procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE |
                                           Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
            procedure.set_menu_label("Export as _WebP")
            procedure.set_attribution("Maktabat yafa", "www.maktabatayafa.tn", "2025")
            procedure.add_menu_path("<Image>/Yafa")
            procedure.set_documentation("Export as WebP",
                                         "Exports the image as a WebP file with 75% quality and no metadata.",
                                         None)

            procedure.add_string_argument("file-path", "File Path", None, "",
                                          GObject.ParamFlags.READWRITE)

        return procedure

Gimp.main(ExportWebP.__gtype__, sys.argv)