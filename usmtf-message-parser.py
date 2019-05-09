import os
import json
import time

from GPLogger import GPLogger

with open('config.json') as config_file:
    config_data = json.load(config_file)

    file_directory = config_data['input-directory']

def process_tacelint(logger_item, message_dict, lines_list, processed_message_list):

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

def main():
    # Logging functionality
    logger = GPLogger("USMTF DataPump")
    logger.info('Beginning monitor for USMTF Messages...')
    
    # Function to watch a folder and detect new images on a 1 second refresh interval
    #before = dict ([(f, None) for f in os.listdir (text_file)])
    before = {}
    count = 0
    errors = 0

    while True:
        
        # Compares the folder contents after the sleep to what existed beforehand, and makes a list of adds and removes
        after = dict ([(f, None) for f in os.listdir(file_directory)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]

        if added: logger.info(("Added: ", ", ".join (added)))
        if removed: logger.info(("Removed: ", ", ".join (removed)))
        before = after

        if count == 10:
            print("Exiting")
            exit()

        for doc in added:
            count +=1
            doc_path = os.path.join(file_directory, doc)

            with open(doc_path, mode='r') as file:
                base_message = {}

                message = file.read()
                lines = message.split("\n")
                msg_id = [i for i in lines if 'MSGID' in i][0].split("/")
                msg_type = msg_id[1]
                base_message['msg_type'] = msg_type
                base_message['msg_unit'] = msg_id[2]

                if msg_type == 'TACELINT':
                    messages = []
                    process_tacelint(logger, base_message, lines, messages)
                    logger.info(len(messages))
                
            

if __name__ == "__main__":
    main()