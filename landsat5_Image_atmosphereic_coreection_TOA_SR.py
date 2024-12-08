# atmosphereic correction of landsat 5 image(TOA and SR will be calculated)
# input: input the path of folder, where all image folder will be keep.
# output: define the outpath folder

import arcpy
import os
import re
from datetime import datetime
import math


# Input and output paths
input_folder = r'I:\Data Extraction\LT05_Image'
output_folder = r"I:\Data Extraction\LT05_Image_TOA"

# Don't edit
# Function to convert to TOA_SR_reflectance
def convert_to_toa_sr(input_raster, output_folder, L_Qcal_MxMin, Qcal_min, L_min, pi_d_square):
    # Extract file name without extension
    file_name = os.path.splitext(os.path.basename(input_raster))[0]
    # Construct output file path
    output_raster = os.path.join(output_folder, file_name + "_TOA.TIF")
    # Construct expression for TOA conversion accordint to Rhatin's paper
    # expression = "((({L_Qcal_MxMin} * (Float(\"{img}\") - {Qcal_min})) + {L_min})*{pi_d_square})".format(L_Qcal_MxMin, input_raster, Qcal_min, L_min, pi_d_square)
    
    expression = "((({} * (Float(\"{}\") - {})) + {})*{})".format(L_Qcal_MxMin, input_raster, Qcal_min, L_min, pi_d_square)
    

    try:
        # Perform TOA conversion
        arcpy.gp.RasterCalculator_sa(expression, output_raster)
        print("Conversion completed for:", input_raster)
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))



# Iterate through input folders
for root, dirs, files in os.walk(input_folder):
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        #print(dir_path)
        image_list = []
        REFLECTANCE_MULT_BAND_LIST = []
        REFLECTANCE_ADD_BAND_LIST  = []
        RADIANCE_MAXIMUM_BAND_LIST = []
        RADIANCE_MINIMUM_BAND_LIST = []
        QUANTIZE_CAL_MAX_BAND_LIST = []
        QUANTIZE_CAL_MIN_BAND_LIST = []
        ESUNS = [1958,1827,1551,1036,214.9,80.65]  # FOR LANDSAT 5 acceptable
        #ESUNS = [195.7,182.9,155.7,104.7,21.93,7.452]   #N0 acceptable
        mtl_file_path = os.path.join(dir_path, dir_name + '_MTL.txt')
        # Read metadata file
        if os.path.exists(mtl_file_path):
            with open(mtl_file_path, 'r') as file:
                metadata_text = file.read()
                
            #Earth Sun Distance
            earth_sun_d = re.findall(r'EARTH_SUN_DISTANCE = (.+)', metadata_text)
            earth_sun_d = float(earth_sun_d[0])   # Remove square brackets and whitespace
            #print("earth_sun_d: ",earth_sun_d)
            
            # Define the date
            aqui_date = (re.findall(r'DATE_ACQUIRED = (.+)', metadata_text))[0]
            #print("aqui_date: ",aqui_date)            
            date_object = datetime.strptime(aqui_date, "%Y-%m-%d") # Convert the date string to a datetime object            
            julian_day = date_object.timetuple().tm_yday     # Get the Julian day
            #print("Julian day:", julian_day)
            
            #Define d_square
            jd = julian_day-4
            #print("jd: ",jd)
            cosine = math.cos(earth_sun_d*jd*math.pi/180)
            #print("cosine: ",cosine)            
            d_square = float(math.pow((1-0.01674*cosine),2))
            #print("d_square: ",d_square)
                        
            # Define Solar zenith angele
            sun_elev = re.findall(r'SUN_ELEVATION = (.+)', metadata_text)
            sun_elev = float(sun_elev[0])
            #print(sun_elev)
            s_zenith = float(math.cos((90-sun_elev)*math.pi/180))
            #print("s_zenith: ",s_zenith)
            
            bands = [1, 2, 3, 4, 5, 7]   # for landsat 5
            for band in bands:
                # Define patterns for reflectance values
                pattern_1 = r'REFLECTANCE_MULT_BAND_{} = (.+)'.format(band)
                pattern_2 = r'REFLECTANCE_ADD_BAND_{} = (.+)'.format(band)
                pattern_3 = r'RADIANCE_MAXIMUM_BAND_{} = (.+)'.format(band)
                pattern_4 = r'RADIANCE_MINIMUM_BAND_{} = (.+)'.format(band)
                pattern_5 = r'QUANTIZE_CAL_MAX_BAND_{} = (.+)'.format(band)
                pattern_6 = r'QUANTIZE_CAL_MIN_BAND_{} = (.+)'.format(band)
                
                matches_1 = (re.findall(pattern_1, metadata_text))
                matches_2 = (re.findall(pattern_2, metadata_text))
                matches_3 = (re.findall(pattern_3, metadata_text))
                matches_4 = (re.findall(pattern_4, metadata_text))
                matches_5 = (re.findall(pattern_5, metadata_text))
                matches_6 = (re.findall(pattern_6, metadata_text))
                #print(matches_1,matches_2,matches_3,matches_4,matches_5,matches_6)
                
                if matches_1 and matches_2 and matches_3 and matches_4 and matches_5 and matches_6:
                    REFLECTANCE_MULT_BAND_LIST.append(float(matches_1[-1]))
                    REFLECTANCE_ADD_BAND_LIST.append(float(matches_2[-1]))
                    RADIANCE_MAXIMUM_BAND_LIST.append(float(matches_3[-1]))
                    RADIANCE_MINIMUM_BAND_LIST.append(float(matches_4[-1]))
                    QUANTIZE_CAL_MAX_BAND_LIST.append(float(matches_5[-1]))
                    QUANTIZE_CAL_MIN_BAND_LIST.append(float(matches_6[-1]))

        # Iterate through files in directory
        for file in os.listdir(dir_path):
            if file.endswith(('B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B7.TIF')):
                image_list.append(os.path.join(dir_path, file))
        
        # print((image_list))
        # print((REFLECTANCE_MULT_BAND_LIST))
        # print((REFLECTANCE_ADD_BAND_LIST))
        # print((RADIANCE_MAXIMUM_BAND_LIST))
        # print((RADIANCE_MINIMUM_BAND_LIST))
        # print((QUANTIZE_CAL_MAX_BAND_LIST))
        # print((QUANTIZE_CAL_MIN_BAND_LIST))
        

        # Create output folder
        output_subfolder = os.path.join(output_folder, 'TOA_' + dir_name)
        #print(output_subfolder)
        #os.makedirs(output_subfolder, exist_ok=True)
        if not os.path.exists(output_subfolder):
            os.mkdir(output_subfolder)
        

        #convert_to_toa_to_sr(input_raster, output_folder, L_max, L_min, Qcal_mx, Qcal_min, esun, s_zenith, d_square, rfmb, rfad)
        for (img, L_max, L_min, Qcal_mx, Qcal_min, esun) in zip(image_list, RADIANCE_MAXIMUM_BAND_LIST, RADIANCE_MINIMUM_BAND_LIST, QUANTIZE_CAL_MAX_BAND_LIST, QUANTIZE_CAL_MIN_BAND_LIST, ESUNS):
            #print(img, L_max, L_min, Qcal_mx, Qcal_min, esun)
            # This equation is collected from Ratin da paper
            pi_d_square = (math.pi * d_square) / (esun * s_zenith)
            L_Qcal_MxMin = (L_max - L_min) / (Qcal_mx - Qcal_min)
            print("pi_d_square: ",pi_d_square)
            print("L_Qcal_MxMin: ",L_Qcal_MxMin)
            convert_to_toa_sr(img, output_subfolder, L_Qcal_MxMin, Qcal_min, L_min, pi_d_square)
            
print("All processing completed.")