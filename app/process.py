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
            
            message_dict['time-up'] = line_split[2]
            message_dict['time-down'] = line_split[3]
            message_dict['class'] = line_split[4]
            message_dict['emitter-type'] = line_split[5]
            continue

        if line_split[0] == 'EMLOC':
            message_dict['loc'] = line_split[3].split(":")[1]
            message_dict['orientation'] = line_split[5][:-1]
            message_dict['semi-major'] = line_split[6][:-2]
            message_dict['semi-minor'] = line_split[7][:-2]
            message_dict['units'] = line_split[6][-2:]
            continue

        if line_split[0] == 'PRM':
            message_dict['freq'] = line_split[2][:-3]
            message_dict['freq-units'] = line_split[2][-3:]
            message_dict['pri'] = line_split[4].split(":")[1]
            message_dict['pd'] = line_split[6].split(":")[1]
            processed_message_list.append(message_dict)
            continue
        elif line_split[0] !=  'PRM' and 'loc' in message_dict.keys():
            processed_message_list.append(message_dict)
            continue