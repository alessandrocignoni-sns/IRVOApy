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


#### EXPORT FUNCTIONS ####
# exports dataset to CSV file, procedure
def export_pub_dataset(pub_dataset, dataset_name, normalized):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, '..', 'output')
    today_date = datetime.today().strftime('%Y-%m-%d')
    file_name = today_date + '_' + dataset_name + '.csv'
    file_path = os.path.join(output_dir, file_name)

    if not normalized:
        fields = ['id', 'type', 'title', 'authors_names', 'authors_orcids', 'lang',
                  'doi', 'year', 'publisher', 'container_name', 'issn', 'volume', 'issue']
    else:
        fields = ['id', 'title', 'authors_names', 'authors_orcids', 'lang',
                  'doi', 'year', 'publisher', 'container_name', 'issn', 'vol_iss']

    if os.path.exists(file_path):
        flag_overwrite = input(f"[csv_funs] {file_name}.csv already exists. Overwrite? (y/n):")
        if not flag_overwrite.lower() == 'y':
            print("[csv-funs] Export cancelled.")
            return

    with open(file_path, mode='w', newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        for pub in pub_dataset:
            authors_orcids = "; ".join(aut['orcid'] for aut in pub['authors'])
            if not normalized:
                authors_names = "; ".join(f"{aut['surname']}, {aut['name']}" for aut in pub['authors'])
            else:
                authors_names = "; ".join(aut['name'] for aut in pub['authors'])
            
            pub_data = {
                'id': pub['id'],
                'title': pub['title'],
                'authors_names': authors_names,
                'authors_orcids': authors_orcids,
                'lang': pub['lang'],
                'doi': pub['doi'],
                'year': pub['year'],
                'publisher': pub['publisher'],
                'container_name': pub['container_name'],
                'issn': pub['issn'],
            }
            if not normalized:
                pub_data['type'] = pub['type']
                pub_data['volume'] = pub['volume'] 
                pub_data['issue'] = pub['issue']
            else:
                pub_data['vol_iss'] = pub['vol_iss']
            writer.writerow(pub_data)

        print(f"[csv-funs] Saved {len(pub_dataset)} records to {file_name}.csv in output folder.")

# exports matches dataset resulting from comparisons to CSV file, procedure
def export_matches(dataset, dataset_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, '..', 'output')
    today_date = datetime.today().strftime('%Y-%m-%d')
    file_name = today_date + '_' + dataset_name + '.csv'
    file_path = os.path.join(output_dir, file_name)

    flag_IR = False
    if re.search(r"^PfIR", dataset_name):
        flag_IR = True

    if flag_IR:
        fields = ['IR_id', 'OA_id', 'confidence', 'matched_fields']
    else:
        fields = ['OA_id', 'IR_id', 'confidence', 'matched_fields']

    if os.path.exists(file_path):
        flag_overwrite = input(f"[csv_funs] {file_name}.csv already exists. Overwrite? (y/n):")
        if not flag_overwrite.lower() == 'y':
            print("[csv-funs] Export cancelled.")
            return

    with open(file_path, mode='w', newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()

        for matched in dataset:
            fields_string = "; ".join(matched[3])
            
            if flag_IR:
                IR_id = matched[0]
                OA_id =matched[1]
            else:
                OA_id = matched[0]
                IR_id =matched[1]

            matched_data = {
                'IR_id': IR_id,
                'OA_id': OA_id,
                'confidence': matched[2],
                'matched_fields': fields_string
            }
            writer.writerow(matched_data)
    
        print(f"[csv-funs] Saved {len(dataset)} records to {file_name}.csv in output folder.")


#### ASKING FUNCTIONS ####
# asks user if they want to export dataset to CSV file, procedure
def ask_for_csv(dataset, dataset_name, normalized=False):
    csv_flag = input(f"[csv_funs] Do you want to export {dataset_name} to a CSV file? (y/n): ")
    if csv_flag.lower() == 'y':
        if not re.search(r"matches$", dataset_name):
            export_pub_dataset(dataset, dataset_name, normalized)
        else:
            export_matches(dataset, dataset_name)

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