import os
import arcpy
import json
import time

text_file = r"C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\source_data"
tacelint_out_dir = r'C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\tacelint'
recceexrep_out_dir = r'C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\RECCEXREP'

def extract_tacelint(text, intermediate_file):

    
    arcpy.conversion.ExtractLocationsText(coords, 
                                      intermediate_file, 
                                      None, "FIND_DD_LATLON", "FIND_DD_XYDEG", "FIND_DD_XYPLAIN", "FIND_DM_LATLON", 
                                      "FIND_DM_XYMIN", "FIND_DMS_LATLON", "FIND_DMS_XYSEC", "FIND_DMS_XYSEP", 
                                      "FIND_UTM_MAINWORLD", "DONT_FIND_UTM_NORTHPOLAR", "DONT_FIND_UTM_SOUTHPOLAR", 
                                      "FIND_MGRS_MAINWORLD", "DONT_FIND_MGRS_NORTHPOLAR", "DONT_FIND_MGRS_SOUTHPOLAR", 
                                      "USE_DOT_DECIMAL_MARK", "PREFER_LATLON", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 11258999068426.2;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision", 
                                      None, "DONT_USE_FUZZY", None, None, "FIND_DATE_MONTHNAME", "FIND_DATE_M_D_Y", "FIND_DATE_YYYYMMDD", 
                                      "FIND_DATE_YYMMDD", "FIND_DATE_YYJJJ", None, None, None, None, 
                                      None, None, None, 254, 254, "STD_COORD_FMT_DD")
    
    if arcpy.Exists(intermediate_file) == True:
        result = arcpy.GetCount_management(intermediate_file)
        if int(result[0]) >0:
            fields = [f.name for f in arcpy.ListFields(intermediate_file)]
            with arcpy.da.SearchCursor(intermediate_file, fields) as cursor:
                for row in cursor:
                    shape = row[0]
                
                    return shape
        else:
            return "No valid coordinates extracted", 0, 0
    else:
        return "No valid coordinates extracted", 0, 0
    
    del intermediate_file

# Function to watch a folder and detect new images on a 1 second refresh interval
#before = dict ([(f, None) for f in os.listdir (text_file)])
before = {}
count = 0
errors = 0

while True:
    
    
    # Compares the folder contents after the sleep to what existed beforehand, and makes a list of adds and removes
    after = dict ([(f, None) for f in os.listdir (text_file)])
    added = [f for f in after if not f in before]
    removed = [f for f in before if not f in after]

    if added: print("Added: ", ", ".join (added))
    if removed: print("Removed: ", ", ".join (removed))
    before = after

    for filename in added:
        if filename.endswith(".txt"):
            #print("Processing " + file)
            count +=1
            with open(os.path.join(text_file, filename), mode='r') as file:
                tacelint = file.read()
                lines = tacelint.split("\n")
                if lines[1].startswith("MSGID/"):
                    msg_type = lines[1].split("/")[1]
                    if msg_type == 'TACELINT'or msg_type == 'RECCEXREP':
                        if msg_type == 'TACELINT':
                            oper_type = ''
                            oper_name = ''
                            doc_class = ''
                            country_orig = ''
                            dt_msg = ''
                            soi_list = []
                            emloc_list = []
                        if msg_type == 'RECCEXREP':
                            oper_type = ''
                            oper_name = ''
                            doc_class = ''
                            country_orig = ''
                            dt_msg = ''
                            unit_name = ''
                            u_code = ''
                            long = ''
                            lat = ''
                            tot = ''
                            item_list = []
                        for line in lines:
                            int_file = "in_memory/tacelint_file"
                            split_line = line.split("/")
                            if line.startswith("SOI/"):
                                date_obs = split_line[2]
                                date_rep = split_line[3]
                                asset = split_line[5]
                                reference = split_line[7]
                                ####
                                soi_list.append([date_obs, date_rep, asset, reference])
                            
                            elif line.startswith("EMLOC/"):
                                coords = split_line[3].split(":")[1]
    
                                if len(split_line) == 7:
                                    semiminor = split_line[4]
                                    semimajor = split_line[4]
                                    orientation = "0"
                                if len(split_line) == 10:
                                    semiminor = split_line[7]
                                    semimajor = split_line[6]
                                    orientation = split_line[5]
                                point = extract_tacelint(coords, int_file)
                                if type(point) == tuple:
                                    ####
                                    emloc_list.append([point[0], point[1], semiminor, semimajor, orientation])
                                else:
                                    print(point)
                                #except:
                                    #print("Error processing data, passing...")
                            elif line.startswith('EXER/') or line.startswith('OPER/'):
                                op_type = split_line[0]
                                op_name = split_line[1]
                                ####
                                oper_type = op_type
                                oper_name = op_name
                            
                            elif line.startswith('/'):
                                if len(split_line) == 8:
                                    if msg_type == 'TACELINT' or msg_type == 'RECCEXREP':
                                        classification = split_line[5]
                                        orig_country = split_line[4]
                                        msg_dt = split_line[1]
                                        ####
                                        doc_class = classification
                                        country_orig = orig_country
                                        dt_msg = msg_dt
                                        
                            elif line.startswith('MISSNID/'):
                                unit = split_line[2]
                                unit_code = split_line[5]
                                ####
                                unit_name = unit
                                u_code = unit_code
                            elif line.startswith('ITEM/'):
                                item_num = split_line[1]
                                item_desc = split_line[2]
                                ben = split_line[3].split(":")[1]
                                sfx = split_line[4].split(":")[1]
                                cat = split_line[5].split(":")[1]
                                ####
                                item_list.append([item_num, item_desc, ben, sfx, cat])
                            elif line.startswith("TOT/"):
                                time_target = split_line[1]
                                ####
                                tot = time_target
                            elif line.startswith("LOC/"):
                                coords = split_line[2].split(":")[1]
                                
                                point = extract_tacelint(coords, int_file)
                                if type(point) == tuple:
                                    lon = point[0]
                                    latt = point[1]
                                    ####
                                    long = lon
                                    lat = latt
                                else:
                                    print(point)
                        
                            if arcpy.Exists(int_file) == True:
                                arcpy.Delete_management(int_file)
                        
                        
                        if msg_type == 'TACELINT':
                            emloc_length = len(emloc_list)
                            if emloc_length > 0:
                                for x in range(emloc_length):
                                    out_file = os.path.splitext(filename)[0]
                                    soi_message = {"operation_type": oper_type,
                                                "operation_name": oper_name,
                                                "classification": doc_class,
                                                "country_orig": country_orig,
                                                "msg_datetime": dt_msg,
                                                "date_observed":soi_list[x-1][0],
                                                "date_received":soi_list[x-1][1],
                                                "asset":soi_list[x-1][2],
                                                "reference_num":soi_list[x-1][3],
                                                "long": emloc_list[x-1][0],
                                                "lat":emloc_list[x-1][1],
                                                "semiminor":emloc_list[x-1][2],
                                                "semimajor":emloc_list[x-1][3],
                                                "orientation":emloc_list[x-1][4] }
                                    soi_file = os.path.join(tacelint_out_dir, filename + '_' + str(time.time())+ ".json")
                                    
                                    with open(soi_file, 'w') as outfile:
                                        json.dump(soi_message, outfile)
                                    
                                    print(soi_message)
                                
                        if msg_type == 'RECCEXREP':
                            item_length = len(item_list)
                            if item_length > 0:
                                for x in range(item_length):
                                    print(filename)
                                    item_message = {
                                                "operation_type":oper_type,
                                                "operation_name":oper_name,
                                                "classification":doc_class,
                                                "origin_country":country_orig,
                                                "msg_datetime":dt_msg,
                                                "unit_name":unit_name,
                                                "unit_code":u_code, 
                                                "long":long,
                                                "lat":lat,
                                                "tot":tot,
                                                "item_num": item_list[x-1][0],
                                                "subject": item_list[x-1][1],
                                                "time":item_list[x-1][2],
                                                "reference": item_list[x-1][3],
                                                "category": item_list[x-1][4]}
                                    
                                    item_file = os.path.join(recceexrep_out_dir, filename + '_' + str(time.time())+ ".json")
                                    
                                    with open(item_file, 'w') as outfile:
                                        json.dump(item_message, outfile)
                                    
                                    print(item_message)
                                
        #print("Processed " + str(count) + " files...")
                                
    if count == 5:
        print("Exiting")
        break