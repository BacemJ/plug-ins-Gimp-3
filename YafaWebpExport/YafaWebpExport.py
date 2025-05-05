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

plug_in_proc = "plug-in-export-webp"

def export_webp_run(procedure, run_mode, image, drawables, config, data):
    
    # Get the file path for saving
    file_path = config.get_property('file-path')
    
    file_path += ".webp"

    # Export the image as WebP
    image.undo_group_start()
    try:
        Gimp.file_save(image, drawables[0], file_path, file_path, {
            "quality": 75,
            "save-metadata": False
        })
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
            procedure.set_attribution("Maktabat yafa", "Bacem Jarraya", "2025")
            procedure.add_menu_path("<Image>/Yafa/Export As WebP")
            procedure.set_documentation("Export as WebP",
                                         "Exports the image as a WebP file with 75% quality and no metadata.",
                                         None)

            procedure.add_string_argument("file-path", "File Path", None, "",
                                          GObject.ParamFlags.READWRITE)

        return procedure

Gimp.main(ExportWebP.__gtype__, sys.argv)