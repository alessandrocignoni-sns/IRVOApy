# library imports
import re

# roman to arabic conversion table
roman_map = { 'm': 1000, 'cm': 900, 'd': 500, 'cd': 400, 'c': 100, 'xc': 90, 'l': 50, 'xl': 40, 'x': 10, 'ix': 9, 'v': 5, 'iv': 4, 'i': 1 }

# convert roman numeral to integer, output: int
def roman_to_int(s):
    i = 0
    result = 0

    while i < len(s):
        if i + 1 < len(s) and s[i : i + 2] in roman_map: # check for two-character match
            result += roman_map[s[i : i + 2]]
            i += 2
        else:
            result += roman_map[s[i]]
            i += 1

    return result


#### SINGLE FIELD NORMALIZATION FUNCTIONS ####
# normalize string by lowering case and removing whitespace and punctuation, output: string
def normalize_string(input_string):
    if input_string is None or input_string == 'none':
        return ''
    else:
        input_string = str(input_string)
        normalized_string = input_string.lower()
        normalized_string = re.sub(r"\s+", "", normalized_string)     # removes spaces, tab, newline
        normalized_string = re.sub(r"[^\w]", "", normalized_string)    # removes punctuation
        return normalized_string

# normalize number by converting roman numerals to arabic and removing non-digit characters, output: string
def normalize_number(input_string):
    normalized_string = normalize_string(input_string)

    digits = re.sub(r"\D", "", normalized_string)
    if digits != '':
        return str(int(digits))
    elif re.fullmatch(r"[ivxlcdm]+", normalized_string):
        return str(roman_to_int(normalized_string))
    else:
        return ''

# normalize author name by combining normalized surname and name, output: string
def normalize_name(name, surname):
    normalized_name = f"{normalize_string(surname)}{normalize_string(name)}"
    return normalized_name

# normalize volume and issue by combining with hyphen, output: string
def normalize_vol_iss(volume, issue):
    if (volume is None or volume == 'none' or 
    issue is None or issue == 'none'):
        return ''
    else:
        normalized_vol_iss = f"{normalize_number(volume)}-{normalize_number(issue)}"
        return normalized_vol_iss


# normalize IRIS first name by removing common storing error, output: string
def normalize_IRIS_name(name):
    normalized_name = re.sub(r" Codice Fiscale Calcolato", "", name)
    return normalized_name

#### DATASET NORMALIZATION FUNCTIONS ####
# normalization functions for OpenAIRE dataset, output: list
def normalize_OpenAIRE_dataset(dataset):
    normalized_dataset = []

    for publication in dataset:
        normalized_authors = []

        for author in publication['authors']:
            normalized_author = {
                'name': normalize_name(author['name'], author['surname']),
                'orcid': author['orcid']
            }
            normalized_authors.append(normalized_author)

        normalized_pub = {
            'id': publication['id'],
            'title': normalize_string(publication['title']),
            'authors': normalized_authors,
            'year': publication['year'],
            'doi': publication['doi'],
            'lang': publication['lang'],
            'publisher': normalize_string(publication['publisher']),
            'container_name': normalize_string(publication['container_name']),
            'issn': publication['issn'],
            'vol_iss': normalize_vol_iss(publication['volume'], publication['issue'])
        }
        normalized_dataset.append(normalized_pub)

    return normalized_dataset

# normalization functions for IR dataset, output: list
def normalize_IR_dataset(dataset, iris_flag=False):
    normalized_dataset = []

    for publication in dataset:
        normalized_authors = []

        for author in publication['authors']:
            if iris_flag:
                normalized_author = { # not IR keys because of deduplication
                    'name': normalize_name(normalize_IRIS_name(author['name']), author['surname']),
                    'orcid': author['orcid']
                }
            else:
                normalized_author = { # not IR keys because of deduplication
                    'name': normalize_name(author['name'], author['surname']),
                    'orcid': author['orcid']
                }
            normalized_authors.append(normalized_author)

        container_name = normalize_string(publication['REL_ISPARTOFBOOK'] or publication['REL_ISPARTOFJOURNAL'] or '')

        normalized_pub = {
            'id': publication['HANDLE'],
            'title': normalize_string(publication['TITLE']),
            'authors': normalized_authors,
            'year': publication['DATE_ISSUED_YEAR'],
            'doi': publication['IDE_DOI'],
            'lang': publication['LAN_ISO_1'],
            'publisher': normalize_string(publication['PUB_NAME']),
            'container_name': container_name,
            'issn': publication['issn'], # not IR keys because of deduplication
            'vol_iss': normalize_vol_iss(publication['REL_VOLUME'], publication['REL_ISSUE'])
        }
        normalized_dataset.append(normalized_pub)

    return normalized_dataset