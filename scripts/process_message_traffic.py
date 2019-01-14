import os
import arcpy
import json
import time

text_file = r"C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\source_data"
tacelint_out_dir = r'C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\tacelint'
recceexrep_out_dir = r'C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\RECCEXREP'
tacrep_long_out_dir = r'C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\tacrep_long'
marop_out_dir = r'C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\tacrep\marop'
airop_out_dir =r'C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\tacrep\airop'
gndop_out_dir = r'C:\Users\jame9353\Box Sync\Projects\DCGS-A Message Traffic\data\tacrep\gndop'

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
                tacrep_message = {}

                tacelint = file.read()
                lines = tacelint.split("\n")
                if lines[1].startswith("MSGID/"):
                    msg_type = lines[1].split("/")[1]
                    if msg_type == 'TACELINT'or msg_type == 'RECCEXREP' or msg_type == 'TACREP':
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
                        if msg_type == 'TACREP':
                            oper_type = ''
                            oper_name = ''
                            doc_class = ''
                            country_orig = ''
                            ampn = ''
                            di = ''
                            net = ''
                            tskr = ''
                            rfreq = ''
                            marop_list = []
                            elp_list = []
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
                            
                            if line.startswith("EMLOC/"):
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
                            if line.startswith('EXER/') or line.startswith('OPER/'):
                                op_type = split_line[0]
                                op_name = split_line[1]
                                ####
                                oper_type = op_type
                                oper_name = op_name
                            
                            if line.startswith('/'):
                                if len(split_line) == 8:
                                    if msg_type == 'TACELINT' or msg_type == 'RECCEXREP':
                                        classification = split_line[5]
                                        orig_country = split_line[4]
                                        msg_dt = split_line[1]
                                        ####
                                        doc_class = classification
                                        country_orig = orig_country
                                        dt_msg = msg_dt
                                        
                            if line.startswith('MISSNID/'):
                                unit = split_line[2]
                                unit_code = split_line[5]
                                ####
                                unit_name = unit
                                u_code = unit_code
                            if line.startswith('ITEM/'):
                                item_num = split_line[1]
                                item_desc = split_line[2]
                                ben = split_line[3].split(":")[1]
                                sfx = split_line[4].split(":")[1]
                                cat = split_line[5].split(":")[1]
                                ####
                                item_list.append([item_num, item_desc, ben, sfx, cat])
                            if line.startswith("TOT/"):
                                time_target = split_line[1]
                                ####
                                tot = time_target
                            if line.startswith("LOC/"):
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
                            
                            if line.startswith("AMPN/"):
                                ampn = split_line[1]
                            
                            if line.startswith('MAROP/'):
                                marop_time = split_line[1]
                                marop_callsign = split_line[6].split(":")[1]
                                marop_loc = split_line[7].split(":")[1]
                                marop_point = extract_tacelint(marop_loc, int_file)
                                marop_list.append([marop_point[0], marop_point[1], marop_callsign, marop_time])
                                
                            if line.startswith('/ELP'):
                                ellipse = split_line[1].split(":")[1].split("-")
                                semimajor = ellipse[0]
                                semiminor = ellipse[1]
                                orientation = ellipse[2]
                                if len(split_line) == 5:
                                    snqal = split_line[2].split(":")[1]
                                    snsrcd = split_line[3].split(":")[1]
                                    snnr = split_line[4].split(':')[1]
                                    elp_list.append([semimajor, semiminor, orientation, snqal, snsrcd, snnr])
                                else:
                                    snqal = 'None'
                                    snsrcd = split_line[2].split(":")[1]
                                    snnr = split_line[3].split(':')[1]
                                    elp_list.append([semimajor, semiminor, orientation, snqal, snsrcd, snnr])
                            
                            if line.startswith('OPSUP/'):
                                di = split_line[1].split(":")[1]
                                net = split_line[2].split(":")[1]
                                tskr = split_line[3].split(":")[1]
                                rfreq = split_line[4].split(":")[1]
                        
                            if arcpy.Exists(int_file) == True:
                                arcpy.Delete_management(int_file)
                        
                        
                        if msg_type == 'TACELINT':
                            emloc_length = len(emloc_list)
                            if emloc_length > 0:
                                for x in range(emloc_length):
                                    out_file = os.path.splitext(filename)[0]
                                    soi_message = {
                                                "message_type": msg_type,
                                                "operation_type": oper_type,
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
                        
                        if msg_type == 'TACREP':
                            marop_length = len(marop_list)
                            if marop_length > 0:
                                for x in range(marop_length):
                                    print(filename)
                                    tacrep_long_message = {
                                                    "message_type": msg_type,
                                                    "operation_type": oper_type,
                                                    "operation_name": oper_name, 
                                                    "classification": doc_class,
                                                    "origin_country": country_orig,
                                                    "ampn": ampn,
                                                    "long":marop_list[x-1][0],
                                                    "lat":marop_list[x-1][1],
                                                    "callsign":marop_list[x-1][2],
                                                    "time":marop_list[x-1][3],
                                                    "semimajor":elp_list[x-1][0], 
                                                    "semiminor":elp_list[x-1][1], 
                                                    "orientation":elp_list[x-1][2], 
                                                    "snqal":elp_list[x-1][3], 
                                                    "snsrcd":elp_list[x-1][4], 
                                                    "snnr":elp_list[x-1][5],
                                                    "di":di,
                                                    "net":net,
                                                    "tskr":tskr,
                                                    "rfreq":rfreq
                                                    }
                                    
                                    tacrep_long_file = os.path.join(tacrep_long_out_dir, filename + '_' + str(time.time())+ ".json")
                                    
                                    with open(tacrep_long_file, 'w') as outfile:
                                        json.dump(tacrep_long_message, outfile)
                                    
                                    print(tacrep_long_message)
                                
                        if msg_type == 'RECCEXREP':
                            item_length = len(item_list)
                            if item_length > 0:
                                for x in range(item_length):
                                    print(filename)
                                    item_message = {
                                                "message_type": msg_type,
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
                
                elif lines[0].startswith("MSGID/") or lines[1].startswith("MSGID/"):
                    if lines[0].startswith("MSGID/") and lines[0].split("/")[1] == 'TACREP':
                        msg_type = "TACREP"
                    elif lines[1].startswith("MSGID/") and lines[1].split("/")[1] == 'TACREP':
                        msg_type = "TACREP"
                    
                    marop_list = []
                    gndop_list = []
                    airop_list = []
                    alt_list = []
                    
                    if msg_type == 'TACREP':
                        print(filename)
                        for line in lines:
                            split_line = line.split("/")
                            int_file = "in_memory/tacrep_file"
                            
                            if line.startswith('/'):
                                if len(split_line) == 8:
                                    if msg_type == 'TACREP':
                                        tacrep_message['classification'] = split_line[5]
                                        tacrep_message['orig_country'] = split_line[4]
                                        tacrep_message['msg_dt'] = split_line[1]
                                        
                            if line.startswith("AMPN/"):
                                tacrep_message['ampn'] = split_line[1]
                            
                            if line.startswith('MAROP/'):
                                marop_time = split_line[1]
                                marop_callsign = split_line[6].split(":")[1]
                                marop_flag = split_line[3]
                                marop_class = split_line[5].split(":")[1]
                                marop_type = split_line[4]
                                marop_loc = split_line[7].split(":")[1]
                                marop_point = extract_tacelint(marop_loc, int_file)
                                marop_list.append([marop_point[0], marop_point[1], marop_callsign, marop_time, marop_class, marop_flag, marop_type])
                            
                            if line.startswith('GNDOP/'):
                                gndop_time = split_line[1]
                                gndop_cntry = split_line[3]
                                equipment_type = split_line[4]
                                eqn = split_line[5].split(":")[1]
                                callsign = split_line[6].split(":")[1]
                                gndop_loc = split_line[7].split(":")[1]
                                gndop_point = extract_tacelint(gndop_loc, int_file)
                                gndop_list.append([gndop_point[0], gndop_point[1], gndop_time, gndop_cntry, equipment_type, eqn, callsign])
                            
                            if line.startswith('AIROP/'):
                                ao_time = split_line[1]
                                cntry = split_line[3]
                                equipment_type = split_line[5]
                                tn = split_line[6].split(":")[1]
                                loc = split_line[7].split(":")[1]
                                crs = split_line[8].split(":")[1]
                                spd = split_line[9].split(":")[1]
                                airop_point = extract_tacelint(loc, int_file)
                                airop_list.append([airop_point[0], airop_point[1], ao_time, cntry, equipment_type, tn, crs, spd])
                            
                            if line.startswith("/ALT"):
                                alt_list.append([split_line[1].split(":")[1]])
                            
                            if line.startswith('OPSUP/'):
                                 tacrep_message['opsup_msg'] = split_line[1].split(":")[1]
                        
                            if arcpy.Exists(int_file) == True:
                                arcpy.Delete_management(int_file)
                                
                        marop_length = len(marop_list)
                        if marop_length > 0:
                            for x in range(marop_length):
                                marop_message = dict(tacrep_message)
                                print(filename)
                                    
                                marop_message["long"]=marop_list[x-1][0]
                                marop_message["lat"]=marop_list[x-1][1]
                                marop_message["callsign"]=marop_list[x-1][2]
                                marop_message["time"]=marop_list[x-1][3]
                                marop_message['class']=marop_list[x-1][4]
                                marop_message['flag']=marop_list[x-1][5]
                                marop_message['type']=marop_list[x-1][6]

                                    
                                marop_file = os.path.join(marop_out_dir, filename + '_' + str(time.time())+ ".json")
                                    
                                with open(marop_file, 'w') as outfile:
                                    json.dump(marop_message, outfile)
                                    
                                print(marop_message)
                                    
                        gndop_length = len(gndop_list)
                        if gndop_length > 0:
                            for x in range(gndop_length):
                                gndop_message = dict(tacrep_message)
                                print(filename)
                                                                        
                                gndop_message["long"]=gndop_list[x-1][0]
                                gndop_message["lat"]=gndop_list[x-1][1]
                                gndop_message["callsign"]=gndop_list[x-1][6]
                                gndop_message["time"]=gndop_list[x-1][2]
                                gndop_message['country']=gndop_list[x-1][3]
                                gndop_message['equipment_type']=gndop_list[x-1][4]
                                gndop_message['eqn']=gndop_list[x-1][5]

                                    
                                gndop_file = os.path.join(gndop_out_dir, filename + '_' + str(time.time())+ ".json")
                                    
                                with open(gndop_file, 'w') as outfile:
                                    json.dump(gndop_message, outfile)
                                    
                                print(gndop_message)
                                    
                        airop_length = len(airop_list)
                        alt_length = len(alt_list)
                        if airop_length > 0 and alt_length > 0:
                            for x in range(airop_length):
                                airop_message = dict(tacrep_message)
                                print(filename)
                                                                        
                                airop_message["long"]=airop_list[x-1][0]
                                airop_message["lat"]=airop_list[x-1][1]
                                airop_message["tn"]=airop_list[x-1][5]
                                airop_message["time"]=airop_list[x-1][2]
                                airop_message['country']=airop_list[x-1][3]
                                airop_message['equipment_type']=airop_list[x-1][4]
                                airop_message['crs']=airop_list[x-1][6]
                                airop_message['spd']=airop_list[x-1][7]
                                airop_message['alt']=alt_list[x-1][0]

                                    
                                airop_file = os.path.join(airop_out_dir, filename + '_' + str(time.time())+ ".json")
                                    
                                with open(airop_file, 'w') as outfile:
                                    json.dump(airop_message, outfile)
                                    
                                print(airop_message)
                            
                                
    if count == 10:
        print("Exiting")
        break