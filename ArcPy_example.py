""" This code loops through each mosaic raster. It calculates zonal statistics (based  on multi-zone buffer layer),
joins the statistics to the multi-zone buffer's table, exports joined table, and deletes table for memory efficiency.
"""

import arcpy, os
arcpy.env.workspace = r"C:\Users\Name\MosaicFolder"
arcpy.env.overwriteOutput = True

zonalBufFile = r"C:\Users\Name\MultiZoneBuffer_layer"
tablefolder = tablefolder = r"C:\Users\Name\TablesFolder" #folder path to save tables (not in .gdb)
outfolder = r"C:\Users\Name\project.gdb"


# List all the subfolders (each corresponding to a year) in the external folder
yfolders = arcpy.ListWorkspaces("y*", "Folder")

# Iterate through each year folder
for yf in yfolders:
    arcpy.env.workspace = yf
    name = os.path.basename(yf)
    
    # List all the mosaic raster files in the current year folder
    rasters = arcpy.ListRasters("resamp*", "TIF")
    
    # iterate through each mosaic raster and create paths that will be used in zonal stats tool
    for raster in rasters:
        rasterpath = arcpy.env.workspace + "\\" + raster
        bandNum = range(1,22) # corresponds to band number 1 - 21
        for num in bandNum: # create paths for the 21 bands
            rasterbandpath = rasterpath + f"\\Band_{num}" # path name for the current Band#
            #print(rasterbandpath)
            table = "zonalStats_resamp_" + f"{name}" + f"_b{num}" # output name of zonal stats table
            outpath =  os.path.join(outfolder,table) # path for zonal stats table
            #print(outpath)
            tjoined = "joined_resamp_" + f"{name}" + f"_b{num}"
            outfeat = os.path.join(outfolder,tjoined)
            tableext = table + ".xlsx" #same name as table saved to .gdb but add extension to table file
            exporttable = os.path.join(tablefolder,tableext) 

            # use zonal stats to table tool for current Band#
            arcpy.ia.ZonalStatisticsAsTable(
                in_zone_data=zonalBufFile,
                zone_field="OBJECTID",
                in_value_raster=rasterbandpath,
                out_table=outpath,
                ignore_nodata="DATA",
                statistics_type="ALL",
                process_as_multidimensional="CURRENT_SLICE",
                percentile_values=[25,75],
                percentile_interpolation_type="LINEAR",
                circular_calculation="ARITHMETIC",
                circular_wrap_value=360
            )
            print(f"Completed table {outpath}")

            joinedtable = arcpy.management.AddJoin(
                in_layer_or_view=zonalBufFile, #table to have join added to (the one with all the multizone buffers)
                in_field="OBJECTID",
                join_table=outpath, #table with the stats (may not have stats for each multizone buffer)
                join_field="OBJECTID_1",
                join_type="KEEP_ALL",
                index_join_fields="NO_INDEX_JOIN_FIELDS"
            )

            result = arcpy.management.CopyFeatures(joinedtable, outfeat)

            arcpy.conversion.TableToExcel(
                Input_Table = outfeat, #this table now has the joined data
                Output_Excel_File=exporttable,#export table
                Use_field_alias_as_column_header="NAME",
                Use_domain_and_subtype_description="CODE"
            )
            
            arcpy.management.Delete(outfeat)#delete table in .gdb because now saved as external table (excel file)
            arcpy.management.Delete(outpath)
            arcpy.management.Delete("zonalBuf_R210m_Layer")
            print(f"Completed export {exporttable}")



