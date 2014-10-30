# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# btm-model.py
# Usage: btm-model <Workspace> <Input_Bathymetric_Raster>
#    <Broad-scale_BPI_inner_radius> <Broad-scale_BPI_outer_radius>
#    <Fine-scale_BPI_inner_radius_value> <Fine-scale_BPI_outer_radius>
#    <Classification_dictionary> <Output_Zone_Classification_raster>
#
# Description:
# Run all steps of the BTM model.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
import os
import sys

# local imports
import utils
import config

import bpi
import classify
import slope

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def main(out_workspace, input_bathymetry, broad_bpi_inner_radius,
         broad_bpi_outer_radius, fine_bpi_inner_radius,
         fine_bpi_outer_radius, classification_dict, output_zones):
    """
    Compute complete model. The crux of this computation maps ranges
    of values provided in the classification dictionary (a CSV or Excel
    spreadsheet) to bathymetry derivatives: standardized
    fine- and broad- scale BPI and slope.
    """
    # Load required toolboxes
    local_path = os.path.dirname(__file__)
    btm_toolbox = os.path.abspath(os.path.join(local_path, '..', 'btm.pyt'))
    arcpy.ImportToolbox(btm_toolbox)

    # local variables:
    broad_bpi = os.path.join(out_workspace, "broad_bpi")
    fine_bpi = os.path.join(out_workspace, "fine_bpi")
    slope_rast = os.path.join(out_workspace, "slope")
    broad_std = os.path.join(out_workspace, "broad_std")
    fine_std = os.path.join(out_workspace, "fine_std")

    utils.workspace_exists(out_workspace)
    # set geoprocessing environments
    arcpy.env.scratchWorkspace = out_workspace
    arcpy.env.workspace = out_workspace

    # TODO: currently set to automatically overwrite, expose this as option
    arcpy.env.overwriteOutput = True

    try:
        # Process: Build Broad Scale BPI
        utils.msg("Calculating broad-scale BPI...")
        bpi.main(input_bathymetry, broad_bpi_inner_radius,
                 broad_bpi_outer_radius, broad_bpi, bpi_type='broad')

        # Process: Build Fine Scale BPI
        utils.msg("Calculating fine-scale BPI...")
        bpi.main(input_bathymetry, fine_bpi_inner_radius,
                 fine_bpi_outer_radius, fine_bpi, bpi_type='fine')

        # Process: Standardize BPIs
        utils.msg("Standardizing BPI rasters...")
        arcpy.standardizebpi_btm(
            broad_bpi, "0", "0", broad_std, fine_bpi, "0", "0", fine_std)

        # Process: Calculate Slope
        slope.main(input_bathymetry, slope_rast)

        # Process: Zone Classification Builder
        outputs_base = arcpy.env.addOutputsToMap
        arcpy.env.addOutputsToMap = True
        utils.msg("Classifying Zones...")
        classify.main(classification_dict, broad_std, fine_std,
                      slope_rast, input_bathymetry, output_zones)
        arcpy.env.addOutputsToMap = outputs_base

    except Exception as e:
        # Print error message if an error occurs
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(
        out_workspace=sys.argv[1],
        input_bathymetry=sys.argv[2],
        broad_bpi_inner_radius=sys.argv[3],
        broad_bpi_outer_radius=sys.argv[4],
        fine_bpi_inner_radius=sys.argv[5],
        fine_bpi_outer_radius=sys.argv[6],
        classification_dict=sys.argv[7],
        output_zones=sys.argv[8])
