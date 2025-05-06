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

def increment_file_name(file_path):
    """
    Increment the file name by appending (n) if a file with the same name exists.
    """
    gfile = Gio.File.new_for_path(file_path)
    if not gfile.query_exists(None):
        return file_path  # Return the original file path if it doesn't exist

    base_name, ext = file_path.rsplit('.', 1)  # Split the file name and extension
    counter = 1

    while True:
        new_file_path = f"{base_name}({counter}).{ext}"
        gfile = Gio.File.new_for_path(new_file_path)
        if not gfile.query_exists(None):
            return new_file_path  # Return the new file path if it doesn't exist
        counter += 1

def export_webp_run(procedure, run_mode, image, drawables, config, data):
    # Try to get the file path from the active image
    gfile = image.get_file()
    if gfile:
        file_path = gfile.get_path()
    else:
        # If the image does not have an associated file, provide a default path
        file_path = "/tmp/untitled_image"

    # Always append ".webp" to the file path
    file_path += ".webp"

    # Increment the file name if a file with the same name exists
    file_path = increment_file_name(file_path)

    # Debug: Print the final file path to GIMP's error console
    Gimp.message(f"Final file path: {file_path}")

    # Convert the file path to a GFile object
    gfile = Gio.File.new_for_path(file_path)

    # Prepare procedures to call
    file_webp_export = Gimp.get_pdb().lookup_procedure("file-webp-export")

    # Export the image as WebP
    image.undo_group_start()

    try:
        # Check if there is a selection in the image
        selection = Gimp.Selection.is_empty(image)

        if selection:
            Gimp.message("No selection object found. Exporting the entire image.")
            file_webp_export_inputs = {
                "image": image,
                "file": gfile,
                "quality": 75,
                "alpha-quality": 75,
                "include-thumbnail": False,
            }
            prcedure_runner(file_webp_export, file_webp_export_inputs)
        else:
            Gimp.message("There is a selected area")
            #area = Gimp.Image.get_selection(image)
            area = Gimp.Selection.save(image)
            file_webp_export_inputs = {
                "image": area,
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