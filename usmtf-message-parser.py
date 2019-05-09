import os
import json
import time

from app.GPLogger import GPLogger
from app import process

with open('config.json') as config_file:
    config_data = json.load(config_file)

    file_directory = config_data['input-directory']

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
                messages = []

                message = file.read()
                lines = message.split("\n")
                msg_id = [i for i in lines if 'MSGID' in i][0].split("/")
                msg_type = msg_id[1]
                base_message['msg_type'] = msg_type
                base_message['msg_unit'] = msg_id[2]

                if msg_type == 'TACELINT':

                    try:
                        process.tacelint(logger, base_message, lines, messages)
                        logger.info("{0} events created from {1}".format(str(len(messages)), doc))
                    except Exception as e:
                        logger.error('Error on message: {}'.format(doc), e)
                
            

if __name__ == "__main__":
    main()