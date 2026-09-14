import arcpy

input_DEM = arcpy.GetParameterAsText(0) #input for Elevation Data
input_road = arcpy.GetParameterAsText(1) #input for road data
input_fuels = arcpy.GetParameterAsText(2) #input for fuel model data
input_boundary = arcpy.GetParameterAsText(3) #input for the boundary
output_model = arcpy.GetParameterAsText(4) #output for the model

#DEM data needs to be projected before you can use it
#This projects the DEM to the given boundary's projection
srs = arcpy.Describe(input_boundary).spatialReference

project_DEM = arcpy.management.ProjectRaster(in_raster = input_DEM,
                                             out_raster = 'project_DEM',
                                             out_coor_system = srs,
                                             resampling_type = 'BILINEAR',
                                             cell_size = 10)

#This turns the DEM layer into a slope layer
slope_DEM = arcpy.sa.Slope(in_raster = project_DEM,
                  output_measurement = "PERCENT_RISE",
                  method = "PLANAR",
                  analysis_target_device = "GPU_THEN_CPU")

#This reclassifies the slope layer to be binary
#the target risk critera of 25% grade is set to 1
#Everything else is set to 0
reclassify_slope = arcpy.sa.GreaterThan(in_raster_or_constant1 = slope_DEM, 
                                        in_raster_or_constant2 = 25)

#This turns the DEM layer into an aspect layer
aspect_DEM = arcpy.sa.Aspect(in_raster = project_DEM,
                             method = "PLANAR",
                             analysis_target_device = "GPU_THEN_CPU")

#This reclassifies the aspect layer to be binary
#Our risk criteria is for South facing slopes which fall from 112.5 to 247.5.  These are set as 1
#All other aspects are set to 0
values = [[-1, 112.5, 0], 
          [112.5, 247.5, 1], 
          [247.5, 360, 0]]

remap = arcpy.sa.RemapRange(remapTable=values)
remap.remapTable

reclassify_aspect = arcpy.sa.Reclassify(in_raster = aspect_DEM, 
                    reclass_field='VALUE', 
                    remap=remap)

#The fuel data is for the entire USA, this clips the data to only be within our boundary
fuels_clip = arcpy.management.Clip(in_raster = input_fuels,
                      out_raster = "fuels_clip",
                      in_template_dataset = input_boundary,
                      clipping_geometry = "false")

#This reprojects the fuel data to align with our boundary data
project_fuels = arcpy.management.ProjectRaster(in_raster = fuels_clip,
                                               out_raster = 'project_fuels',
                                               out_coor_system = srs,
                                               resampling_type = 'NEAREST',
                                               cell_size = 30)

#This reclassifies the fuel layer to be binary
#The risk criteria is for fuel models that have medium or higher flame length and medium or higher rate of spread.
#All the models with 1 fit this criteria and everything else is 0
catagories = [["Fill-NoData", 0],
              ["NB1", 0],
              ["NB2", 0],
              ["NB3", 0],
              ["NB8", 0],
              ["NB9", 0],
              ["GR1", 0],
              ["GR2", 1],
              ["GR3", 1],
              ["GR4", 1],
              ["GR5", 1],
              ["GR6", 1],
              ["GR7", 1],
              ["GR8", 1],
              ["GR9", 1],
              ["GS1", 0],
              ["GS2", 1],
              ["GS3", 1],
              ["GS4", 1],
              ["SH1", 0],
              ["SH2", 0],
              ["SH3", 0],
              ["SH4", 1],
              ["SH5", 1],
              ["SH6", 1],
              ["SH7", 1],
              ["SH8", 1],
              ["SH9", 1],
              ["TU1", 0],
              ["TU2", 0],
              ["TU3", 1],
              ["TU4", 1],
              ["TU5", 1],
              ["TL1", 0],
              ["TL2", 0],
              ["TL3", 0],
              ["TL4", 0],
              ["TL5", 0],
              ["TL6", 0],
              ["TL7", 0],
              ["TL8", 0],
              ["TL9", 1],
              ["SB1", 0],
              ["SB2", 1],
              ["SB3", 1],
              ["SB4", 1]]

remap2 = arcpy.sa.RemapRange(remapTable=catagories)
remap2.remapTable

reclassify_fuels = arcpy.sa.Reclassify(in_raster = project_fuels, 
                    reclass_field='FBFM40', 
                    remap=remap2)

#Our road criteria is for anything within 1 km of a road
#This buffer is created to account for roads that are just outside the target boundary
boundary_buffer = arcpy.analysis.PairwiseBuffer(in_features = input_boundary, 
                                        out_feature_class = "boundary_buffer.shp", 
                                        buffer_distance_or_field = "1 kilometers", 
                                        dissolve_option = "ALL")

#This clips the road data to the previous buffer to work with just the target data and not all the road data
road_clip = arcpy.analysis.Clip(in_features = input_road,
                    clip_features = boundary_buffer,
                    out_feature_class = "road_clip.shp")

#This creates the 1 km buffer around all the roads for the risk criteria
road_buffer = arcpy.analysis.PairwiseBuffer(in_features = road_clip, 
                                            out_feature_class = "road_buffer.shp", 
                                            buffer_distance_or_field = "1 kilometers", 
                                            dissolve_option = "ALL")

#This converts the buffer polygon into a raster layer with the same cell size as the DEM
road_raster = arcpy.conversion.PolygonToRaster(in_features = road_buffer, 
                                 value_field = 'id', 
                                 out_rasterdataset = "road_raster",
                                 cellsize = input_DEM)

#This reclassifies the 1km buffer layer to be binary
#Anything within 1 km is set to 1
#Anything outside of 1 km is set to 0
values2 = [['NODATA', 0], 
          [0, 1]]

remap2 = arcpy.sa.RemapRange(remapTable=values2)
remap2.remapTable

reclassify_road = arcpy.sa.Reclassify(in_raster = road_raster, 
                    reclass_field='VALUE', 
                    remap=remap2)

#Since the smallest cell size is the DEM this converts the raster layer to match that size
fuels_resample = arcpy.management.Resample(in_raster = reclassify_fuels,
                                           out_raster = 'fuels_resample',
                                           cell_size = 10,
                                           resampling_type = "NEAREST")

#This adds up the 4 binary layers together to create a range of values 0-4 for risk
risk_calc = fuels_resample + reclassify_road + reclassify_aspect + reclassify_slope

#This cleans up the resulting layer 
risk_resample = arcpy.management.Resample(in_raster = risk_calc,
                                           out_raster = 'risk_resample',
                                           cell_size = 10,
                                           resampling_type = "NEAREST")

#This clips the layer to the target boundary and returns the output for the model
fire_risk_model = arcpy.management.Clip(in_raster = risk_resample,
                                  out_raster = output_model,
                                  in_template_dataset = input_boundary,
                                  clipping_geometry = "true")
