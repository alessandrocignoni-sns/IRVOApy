# library imports
import os
import csv
import re
from datetime import datetime

# for duplicate publications create single instance with authors dictionary, output: list
def deduplicate_PfIR(publication_list):
    deduplicated_PfIR = []

    publication_list = sorted(publication_list, key=lambda x: x['HANDLE']) # sort publications by HANDLE
    
    for pub_1 in publication_list: # convert authors info and issn into list, for all publications
        pub_1['authors'] = [{
            'name': pub_1['FIRST_NAME'],
            'surname': pub_1['LAST_NAME'],
            'orcid': pub_1['ORCID'],
            }]

        pub_1['issn'] = [pub_1['REL_ISSN']]

    deduplicated_PfIR.append(publication_list[0]) # add first publication to deduplicated list
    checked_pubs = [publication_list[0]['HANDLE']]

    for pub_2 in publication_list[1:]: # start from second publication
        if pub_2['HANDLE'] in checked_pubs: # duplicate found, append author ORCID
            deduplicated_PfIR[len(deduplicated_PfIR)-1]['authors'].append({
                'name': pub_2['FIRST_NAME'],
                'surname': pub_2['LAST_NAME'],
                'orcid': pub_2['ORCID']
                })
        else: # new publication, add to deduplicated list
            checked_pubs.append(pub_2['HANDLE'])
            deduplicated_PfIR.append(pub_2)

    for pub_3 in deduplicated_PfIR: # remove redundant author fields from all publications
        pub_3.pop('FIRST_NAME', None)
        pub_3.pop('LAST_NAME', None)
        pub_3.pop('ORCID', None)
        pub_3.pop('REL_ISSN', None)

    return deduplicated_PfIR


#### ASKING FUNCTIONS ####
# ask user if author list has been uploaded, output: boolean
def ask_for_AL():
    AL_flag = input("[csv_funs] Have you uploaded author list? (y/n): ")
    if AL_flag.lower() == 'y':
        return True
    else:
        return False

# ask user if institutional repository list has been uploaded, output: boolean
def ask_for_PfIR():
    IR_flag = input("[csv_funs] Have you uploaded institutional repository list? (y/n): ")
    if IR_flag.lower() == 'y':
        return True
    else:
        return False


#### IMPORT FUNCTIONS ####
# import AL from CSV file, output: list
def import_AL(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "..", "input")
    file_path = os.path.join(input_dir, f"{file_name}.csv")

    if not os.path.exists(file_path):
        print(f"[csv_funs] Error: {file_name}.csv not found in input folder.")
        return []
    else:
        print(f"[csv_funs] Importing author list from {file_name}.csv ...")
        author_list = []
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                author_list.append(row)
        print(f"[csv_funs] Imported {len(author_list)} authors.")
        return author_list
    
# import PfIR from CSV file, output: list
def import_PfIR():
    file_name = input("[api_pfir] Enter publication from institutional repository list file name: ")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, '..', 'input')
    file_path = os.path.join(input_dir, f"{file_name}.csv")

    if not os.path.exists(file_path):
        print(f"[csv_funs] Error: {file_name}.csv not found in input folder.")
        return []
    else:
        print(f"[csv_funs] Importing publication list from {file_name}.csv ...")
        publication_list = []
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                publication_list.append(row)

        publication_list = deduplicate_PfIR(publication_list)

        print(f"[csv_funs] Imported {len(publication_list)} publications.")
        return publication_list
