# Processing functions for various USMTF message formats

def tacelint(logger_item, message_dict, lines_list, processed_message_list):

    prev_soi = []
    prev_line = []
    for line in lines_list:
        if len(prev_line) == 0:
            prev_line.append(line)
        else:
            del prev_line[0]
            prev_line.append(line)

        line_split = line.split("/")
        
        if line_split[0] == 'SOI':
            if len(prev_soi) == 0:
                prev_soi.append(line)
            else:
                del prev_soi[0]
                prev_soi.append(line)

            message_dict['tar-sig-id'] = line_split[1]
            message_dict['time-up'] = line_split[2]
            message_dict['time-down'] = line_split[3]
            message_dict['sort-code'] = line_split[4]
            message_dict['emitter-desig'] = line_split[5]

            try: message_dict['event-loc'] = line_split[6]
            except: pass

            try: message_dict['tgt-id'] = line_split[7]
            except: pass

            try: message_dict['enemy-uid'] = line_split[8]
            except: pass

            try: message_dict['wpn-type'] = line_split[9]
            except: pass
            
            try: message_dict['emitter-func-code'] = line_split[10]
            except: pass

            continue

        if line_split[0] == 'EMLOC':
            message_dict['data-entry'] = line_split[1]
            message_dict['emitter-loc-cat'] = line_split[2]
            message_dict['loc'] = line_split[3].split(":")[1]
            message_dict['orientation'] = line_split[5][:-1]
            message_dict['semi-major'] = line_split[6][:-2]
            message_dict['semi-minor'] = line_split[7][:-2]
            message_dict['units'] = line_split[6][-2:]
            
            continue

        if line_split[0] == 'PRM':
            message_dict['data-entry'] = line_split[1]
            message_dict['freq'] = line_split[2][:-3]
            message_dict['freq-units'] = line_split[2][-3:]
            message_dict['rf-op-mode'] = line_split[3]
            message_dict['pri'] = line_split[4].split(":")[1]
            
            try: message_dict['pri-ac'] = line_split[5]
            except: pass
            
            try: message_dict['pd'] = line_split[6].split(":")[1]
            except: pass

            try: message_dict['scan-type'] = line_split[7]
            except: pass

            try: message_dict['scan-rate'] = line_split[8]
            except: pass

            try:  message_dict['ant-pol'] = line_split[9]
            except: pass
            
            processed_message_list.append(message_dict)
            
            continue

        if line_split[0] == 'REF':
            message_dict['serial-letter'] = line_split[1]
            message_dict['ref-type'] = line_split[2]
            message_dict['originiator'] = line_split[3]
            message_dict['dt-ref'] = line_split[4]
            
            continue

        if line_split[0] == 'AMPN':
            message_dict['ampn'] = line_split[1]
            processed_message_list.append(message_dict)
            
            continue

        if line_split[0] == 'NARR':
            message_dict['narr'] = line_split[1]
            processed_message_list.append(message_dict)
            
            continue

        if line_split[0] == 'COLLINFO':
            try: message_dict['collector-di'] = line_split[1]
            except: pass
            
            try: message_dict['collector-tri'] = line_split[2]
            except: pass

            try: message_dict['coll-msn-num'] = line_split[3]
            except: pass
            
            try: message_dict['coll-proj-name'] = line_split[4]
            except: pass

            continue

        if line_split[0] == 'FORCODE':
            message_dict['forcode'] = line_split[1]
            processed_message_list.append(message_dict)
            
            continue

        if line_split[0] == 'PLATID':
            message_dict['scn'] = line_split[1]
            message_dict['pt-d'] = line_split[2]
            message_dict['pt'] = line_split[3]
            message_dict['plat-name'] = line_split[4]
            message_dict['ship-name'] = line_split[5]

            try: message_dict['pen-num'] = line_split[6]
            except: pass 
            
            try: message_dict['nationality'] = line_split[7]
            except: pass

            try:  message_dict['track-num'] = line_split[8]
            except:  pass

            processed_message_list.append(message_dict)

            continue

        if line_split[0] == 'DECL':
            message_dict['source-class'] = line_split[1]
            message_dict['class-reason'] = line_split[2]
            message_dict['dg-inst'] = line_split[3]

            try: message_dict['dg-exempt-code'] = line_split[4]
            except:  pass

            processed_message_list.append(message_dict)

            continue