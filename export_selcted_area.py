#!/usr/bin/env python

from gimpfu import *
import os

def get_unique_file_path(file_path):
    """Generates a unique file path by adding a suffix (n) if the file already exists."""
    base, extension = os.path.splitext(file_path)
    counter = 1
    new_file_path = file_path
    while os.path.exists(new_file_path):
        # Use Python 2.7 compatible string formatting
        new_file_path = "{}({}){}".format(base, counter, extension)
        counter += 1
    return new_file_path

def export_selected_area(image, drawable):
    """Crops the image to the current selection and exports it as a WebP file with 75% quality."""
    # File path workflow
    original_file_path = pdb.gimp_image_get_filename(image)
    file_name, file_extension = os.path.splitext(original_file_path)
    new_file_path = file_name + "_q75.webp"
    new_file_path = get_unique_file_path(new_file_path)
    
    # Check if there's an active selection
    if not pdb.gimp_selection_bounds(image)[0]:
        # Export the image as WebP with 75% quality
        pdb.file_webp_save(
            image, drawable, new_file_path, new_file_path,
            0, 0, 75.0, 75.0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        )
        return
    
    # Get selection bounds
    non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
    
    # Calculate new width and height
    new_width = x2 - x1
    new_height = y2 - y1
    
    # Crop the image to the selection
    pdb.gimp_image_crop(image, new_width, new_height, x1, y1)
    
    # Export the image as WebP with 75% quality
    pdb.file_webp_save(
        image, drawable, new_file_path, new_file_path,
        0, 0, 75.0, 75.0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    )

register(
    "python-fu-export-selected-area",  # Use hyphens, not underscores
    "Export selected area into WebP file",
    "Export the image or the selected area as a WebP file with 75% quality.",
    "Bacem",
    "Me",
    "2020",
    "Export Selected Area",  # Direct menu path
    "*",
    [
        (PF_IMAGE, "image", "takes current image", None),
        (PF_DRAWABLE, "drawable", "input layer", None),
    ],
    [],
    export_selected_area,
    menu="<Image>/Image"
)

main()