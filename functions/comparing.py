# import of all functions
import config as conf
import functions.json_funs as json_funs
import functions.analysis as analysis

#### COMPARING FUNCTIONS ####
# merge AP and PfAL datasets without duplicates, output: list
def merge_AP_PfAL(AP_norm, PfAL_norm):
    OA_norm_dict = {}
    for pub1 in AP_norm + PfAL_norm:
        OA_norm_dict[pub1['id']] = pub1
    OA_norm = list(OA_norm_dict.values())

    target_ids = set(OA_norm_dict.keys())
    OA_dict = {}
    for pub2 in conf.AP + conf.PfAL:
        pid = pub2['id']
        if pid in target_ids:
            OA_dict[pid] = pub2
    OA = list(OA_dict.values())

    print(f"[PfIR vs OA] Merged AP and PfAL datasets. New OA dataset of {len(OA_norm)} length.")
    return [OA_norm, OA]

# compare two datasets and print differences in publication IDs, output: list
def same_source_comparison(datasets, msg_string):
    dataset1 = datasets[0]
    dataset2 = datasets[1]

    ds1_ids = {pub["id"] for pub in dataset1} # gets ids of pubs
    ds2_ids = {pub["id"] for pub in dataset2}

    ids_in_common = ds1_ids & ds2_ids
    ids_only_ds1 = ds1_ids - ds2_ids
    ids_only_ds2 = ds2_ids - ds1_ids

    dataset1_og = []
    dataset2_og = []
    match msg_string:
        case 'AP vs PfAL':
            dataset1_og = conf.AP
            dataset2_og = conf.PfAL

    in_common = [pub for pub in dataset1_og if pub["id"] in ids_in_common] # gets all metadata for selected ids
    ds1_unique = [pub for pub in dataset1_og if pub["id"] in ids_only_ds1]
    ds2_unique = [pub for pub in dataset2_og if pub["id"] in ids_only_ds2]

    return [in_common, ds1_unique, ds2_unique, msg_string]

# compare two authors, output: boolean
def aut_comparison(aut1, aut2):
    aut_match = False
    if aut1['orcid'] != '' and aut2['orcid'] != '':
        if aut1['orcid'] == aut2['orcid']:
            aut_match = True
    elif aut1['name'] != '' and aut2['name'] != '':
        if aut1['name'] == aut2['name']:
            aut_match = True
    return aut_match

# compare two issn list, output: boolean
def issn_match(small_list, large_list):
    for iss1 in small_list:
        for iss2 in large_list:
            if iss1 == iss2:
                return True
    return False

# compare two authors lists, output: boolean
def authors_match(small_list, large_list):
    used = set() 
    for aut1 in small_list:
        matched = False
        for i, aut2 in enumerate(large_list):
            if i not in used and aut_comparison(aut1, aut2):
                used.add(i)
                matched = True
                break
        if not matched:
            return False
    return True

# compare two publication, output: list
def pub_comparison(pub1, pub2, order):
    confidence = 0
    if order == 'OA-IR': # always check IR against OA for authors and issn
        IR = pub2
        OA = pub1
    else:  # IR-OA
        IR = pub1
        OA = pub2

    matched_fields = []
    if (pub1['doi'] != '' and pub2['doi'] != ''):
        if pub1['doi'] == pub2['doi']:
            confidence = 1
            matched_fields = ['doi']
    if confidence == 0:
        if (pub1['title'] !=  '' and pub2['title'] != '' and # sufficient match 1: title, year, publisher, container_name
            pub1['year'] !=  '' and pub2['year'] != '' and
            pub1['publisher'] !=  '' and pub2['publisher'] != '' and
            pub1['container_name'] !=  '' and pub2['container_name'] != ''): 
            if (pub1['title'] == pub2['title'] and
                pub1['year'] == pub2['year'] and
                pub1['publisher'] == pub2['publisher'] and
                pub1['container_name'] == pub2['container_name']):
                confidence = 1
                matched_fields = ['title', 'year', 'publisher', 'container_name']
    if confidence == 0:
        if (pub1['title'] !=  '' and pub2['title'] != '' and # sufficient match 2: title, issn, vol_iss
            pub1['issn'] != [] and pub2['issn'] != [] and
            pub1['vol_iss'] !=  '' and pub2['vol_iss'] != ''):
            if (pub1['title'] == pub2['title'] and
                pub1['vol_iss'] == pub2['vol_iss']):
                if issn_match(IR['issn'], OA['issn']):
                    confidence = 1
                    matched_fields = ['title', 'issn', 'vol_iss']
    if confidence == 0:
        if (pub1['title'] !=  '' and pub2['title'] != '' and # sufficient match 3: title, year, authors
            pub1['year'] !=  '' and pub2['year'] != '' and
            pub1['authors'] != [] and pub2['authors'] != []):
            if (pub1['title'] == pub2['title'] and
                pub1['year'] == pub2['year']):
                if authors_match(IR['authors'], OA['authors']):
                    confidence = 1
                    matched_fields = ['title', 'year', 'authors']
            
        if confidence == 0:
            if pub1['authors'] != [] and pub2['authors'] != []:
                if authors_match(IR['authors'], OA['authors']):
                    confidence += 0.25
                    matched_fields.append('authors')
            if pub1['container_name'] !=  '' and pub2['container_name'] != '':
                if pub1['container_name'] == pub2['container_name']:
                    confidence += 0.25
                    matched_fields.append('container_name')
            if pub1['issn'] !=  [] and pub2['issn'] != []:
                if issn_match(IR['issn'], OA['issn']):
                    confidence += 0.25
                    matched_fields.append('issn')
            if pub1['lang'] !=  '' and pub2['lang'] != '':
                if pub1['lang'] == pub2['lang']:
                    confidence += 0.1
                    matched_fields.append('lang')
            if pub1['publisher'] !=  '' and pub2['publisher'] != '':
                if pub1['publisher'] == pub2['publisher']:
                    confidence += 0.25
                    matched_fields.append('publisher')
            if pub1['title'] !=  '' and pub2['title'] != '':
                if pub1['title'] == pub2['title']:
                    confidence += 0.5
                    matched_fields.append('title')
            if pub1['vol_iss'] !=  '' and pub2['vol_iss'] != '':
                if pub1['vol_iss'] == pub2['vol_iss']:
                    confidence += 0.25
                    matched_fields.append('vol_iss')
            if pub1['year'] !=  '' and pub2['year'] != '':
                if pub1['year'] == pub2['year']:
                    confidence += 0.25
                    matched_fields.append('year')

    return [pub1['id'], pub2['id'], confidence, matched_fields, len(matched_fields)]

#### FUNCTIONS TO START COMPARING DATASETS ####
# launch specific comparison for certainty of matching, output: list
def diff_source_comparison(datasets, msg_string):
    IR = datasets[0]
    OA = datasets[1]

    suff = [ # certain and sufficient matches
        ['doi'],
        ['title', 'year', 'publisher', 'container_name'], # suff1
        ['title', 'issn', 'vol_iss'], # suff2
        ['title', 'year', 'authors'] # suff3
    ]

    comparison_OA_IR = []  # deduplicate OA-IR sufficient matches
    OA_duplicates = []
    OA_with_suff_match = set()
    IR_with_suff_match = set()
    print(f"[{msg_string}] Comparing OA dataset against IR dataset")
    for pub_OA in OA:
        for pub_IR in IR:
            pub_tuple = pub_comparison(pub_OA, pub_IR, 'OA-IR')
            fields = pub_tuple[3]
            id_OA = pub_tuple[0]
            id_IR = pub_tuple[1]
            if fields in suff:
                if (id_OA in OA_with_suff_match or
                    id_IR in IR_with_suff_match): # OA pub with suff match already present: duplicate
                    OA_duplicates.append(pub_tuple)
                else: # first OA pub with suff match: not duplicate
                    comparison_OA_IR.append(pub_tuple)
                    OA_with_suff_match.add(id_OA)
                    IR_with_suff_match.add(id_IR)
            else: # not suff match: always not duplicate
                comparison_OA_IR.append(pub_tuple)

    comparison_IR_OA = [] # deduplicate IR-OA sufficient matches
    IR_duplicates = []
    IR_with_suff_match = set() # reset sets
    OA_with_suff_match = set()
    print(f"[{msg_string}] Comparing IR dataset against OA dataset")
    for pub_IR in IR:
        for pub_OA in OA:
            pub_tuple = pub_comparison(pub_IR, pub_OA, 'IR-OA')
            fields = pub_tuple[3]
            id_IR = pub_tuple[0]
            id_OA = pub_tuple[1]
            if fields in suff: 
                if (id_IR in IR_with_suff_match or
                id_OA in OA_with_suff_match): # IR pub with suff match already present: duplicate
                    IR_duplicates.append(pub_tuple)
                else: # first IR pub with suff match: not duplicate
                    comparison_IR_OA.append(pub_tuple)
                    IR_with_suff_match.add(id_IR)
                    OA_with_suff_match.add(id_OA)
            else: # not suff match: always not duplicate
                comparison_IR_OA.append(pub_tuple)

    sure_pairs = set()
    for comp1 in comparison_OA_IR:
        if comp1[3] in suff:
            sure_pairs.add((comp1[0], comp1[1]))
    for comp2 in comparison_IR_OA:
        if comp2[3] in suff:
            sure_pairs.add((comp2[1], comp2[0]))

    sure_OA_ids = {oa for oa, ir in sure_pairs}
    sure_IR_ids = {ir for oa, ir in sure_pairs}

    in_common = []
    OA_unique = []
    IR_unique = []

    OA_original = [] # retrieve not normalized dataset
    match msg_string:
        case 'PfIR vs AP': OA_original = conf.AP
        case 'PfIR vs PfAL': OA_original = conf.PfAL
        case 'PfIR vs OA': OA_original = conf.OA

    for pub_OA in OA_original:
        if pub_OA['id'] in sure_OA_ids:
            in_common.append(pub_OA)
        else:
            OA_unique.append(pub_OA)

    for pub_IR in conf.PfIR:
        if pub_IR['HANDLE'] not in sure_IR_ids:
            IR_unique.append(pub_IR)

    return [in_common, IR_unique, OA_unique, IR_duplicates, OA_duplicates, comparison_IR_OA, comparison_OA_IR,  msg_string]
    
# launch the selected comparison, procedure
def launch_comparison(selected_comparison):
    comp = []
    match selected_comparison:
        case 1: # AP vs PfAL
            datasets = [conf.AP_norm, conf.PfAL_norm]
            og_datasets = [conf.AP, conf.PfAL]
            print("[AP vs PfAL] Comparing AP vs PfAL...")
            comp = same_source_comparison(datasets, 'AP vs PfAL')
            print(f"[AP vs PfAL] In common publications: {len(comp[0])}")
            print(f"[AP vs PfAL] AP unique: {len(comp[2])}")
            print(f"[AP vs PfAL] PfAL unique: {len(comp[1])}")

        case 2: # PfIR vs AP
            print('[PfIR vs AP] Comparing PfIR vs AP...')
            datasets = [conf.PfIR_norm, conf.AP_norm]
            og_datasets = [conf.PfIR, conf.AP]
            comp = diff_source_comparison(datasets, 'PfIR vs AP')
            print(f"[PfIR vs AP] In common publications: {len(comp[0])}")
            print(f"[PfIR vs AP] AP unique: {len(comp[2])}")
            print(f"[PfIR vs AP] PfIR unique: {len(comp[1])}")
            if conf.DEBUG:
                print('[PfIR vs AP] Exporting comparison matches: PfIR against AP')
                json_funs.save_json(comp[3], 'Matches_PfIR-AP')
                print('[PfIR vs AP] Exporting comparison matches: AP against PfIR')
                json_funs.save_json(comp[4], 'Matches_AP-PfIR')

        case 3: # PfIR vs PfAL
            print('[PfIR vs PfAL] Comparing PfIR vs PfAL...')
            datasets = [conf.PfIR_norm, conf.PfAL_norm]
            og_datasets = [conf.PfIR, conf.PfAL]
            comp = diff_source_comparison(datasets, 'PfIR vs PfAL')
            print(f"[PfIR vs PfAL] In common publications: {len(comp[0])}")
            print(f"[PfIR vs PfAL] PfAL unique: {len(comp[2])}")
            print(f"[PfIR vs PfAL] PfIR unique: {len(comp[1])}")
            if conf.DEBUG:
                print('[PfIR vs PfAL] Exporting comparison matches: PfIR against PfAL')
                json_funs.save_json(comp[3], 'Matches_PfIR-PfAL')
                print('[PfIR vs PfAL] Exporting comparison matches: PfAL against PfIR')
                json_funs.save_json(comp[4], 'Matches_PfAL-PfIR')

        case 4: # PfIR vs (AP U PfAL)
            print("[PfIR vs OA] Comparing PfIR vs (AP U PfAL)...")
            OA_both = merge_AP_PfAL(conf.AP_norm, conf.PfAL_norm)
            conf.OA = OA_both[1]
            conf.OA_norm = OA_both[0]
            datasets = [conf.PfIR_norm, conf.OA_norm]
            og_datasets = [conf.PfIR, conf.OA]
            comp = diff_source_comparison(datasets, 'PfIR vs OA')
            print(f"[PfIR vs OA] In common publications: {len(comp[0])}")
            print(f"[PfIR vs OA] OA unique: {len(comp[2])}")
            print(f"[PfIR vs OA] PfIR unique: {len(comp[1])}")
            if conf.DEBUG:
                print('[PfIR vs OA] Exporting comparison matches: PfIR against (AP U PfAL)')
                json_funs.save_json(comp[3], 'Matches_PfIR-OA')
                print('[PfIR vs OA] Exporting comparison matches: (AP U PfAL) against PfIR')
                json_funs.save_json(comp[4], 'Matches_OA-PfIR')
    
    analysis.ask_for_analysis(comp, og_datasets)
    

# select which comparison to perform, output: int
def ask_for_comparison(possible_comparisons):
    if possible_comparisons:
        print("[comp] Possible comparisons:")
        for i, comparison in enumerate(possible_comparisons, 1):
            if comparison != '':
                print(f"{i}. {comparison}")
        choice = int(input("[comp] Select a comparison by entering the corresponding number or 0 to exit: "))
        if choice == 0:
            return 0
        print(f"[comp] You selected: {possible_comparisons[choice - 1]}")
        return choice
    else:
        print("[comp] No comparisons available.")
        return 0

# check which comparisons are possible based on the datasets available, output: list
def check_for_comparison():
    possible_comparisons = ['', '', '', '']
    if conf.AP_norm != [] and conf.PfAL_norm != []:
        possible_comparisons[0] = 'AP vs PfAL'
    if conf.AP_norm != [] and conf.PfIR_norm != []:
        possible_comparisons[1] = 'PfIR vs AP'
    if conf.PfAL_norm != [] and conf.PfIR_norm != []:
        possible_comparisons[2] = 'PfIR vs PfAL'
    if conf.AP_norm != [] and conf.PfAL_norm != [] and conf.PfIR_norm != []:
        possible_comparisons[3] = 'PfIR vs (AP U PfAL)'
    return possible_comparisons            