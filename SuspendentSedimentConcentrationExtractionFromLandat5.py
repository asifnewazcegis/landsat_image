# suspended sediment values extraction from landsat 5

import arcpy
import os
from arcpy.sa import *

# define input and output paths
input_folder = r"I:\Data Extraction\LT05_Image_TOA"
output_folder = r"I:\Data Extraction\LT05_Image_SSC"

# Iterate through input folders
for root, dirs, files in os.walk(input_folder):
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        arcpy.env.workspace = dir_path                
        for file in arcpy.ListRasters():
            if file.lower().endswith('b1_toa.tif'):
                B1 = Raster(file)
            elif file.lower().endswith('b2_toa.tif'):
                B2 = Raster(file)
            elif file.lower().endswith('b3_toa.tif'):
                B3 = Raster(file)
            elif file.lower().endswith('b4_toa.tif'):
                B4 = Raster(file)

        # Extract date from folder name
        file_name = os.path.splitext(os.path.basename(dir_name))[0]
        date = file_name.split('_')[4]

        # Construct output file path
        output_subfolder = os.path.join(output_folder, file_name)
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)
        output_file = os.path.join(output_subfolder, "{}_SSC.TIF".format(date))
        #print(output_file)
        
        expression = "98.90 + 30.18 * Exp(Float('%s' / '%s')) + 314.1 * Exp(Float('%s' / '%s')) - 324.8 * Exp(Float('%s' / '%s'))" % (B4, B1, B4, B2, B4, B3)
        out_raster = arcpy.gp.RasterCalculator_sa(expression, output_file)
        print("Conversion completed for:", file_name)
        
print("All processing completed.")
        