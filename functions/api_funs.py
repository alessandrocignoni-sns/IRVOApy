# library imports
import requests

# import of necessary functions
import functions.csv_funs as csv_funs
from . import pub_funs as pub_funs

# for duplicate publications create single instance with authors dictionary, output: list
def deduplicate_OA(publication_list):
    deduplicated_OA = []

    publication_list = sorted(publication_list, key=lambda x: x['id']) # sort publications by HANDLE
    
    deduplicated_OA.append(publication_list[0]) # add first publication to deduplicated list
    checked_pubs = [publication_list[0]['id']]

    for pub in publication_list[1:]: # start from second publication
        if pub['id'] not in checked_pubs: # new publication, add to deduplicated list
            checked_pubs.append(pub['id'])
            deduplicated_OA.append(pub)

    return deduplicated_OA


#### ACTUAL API FUNCTIONS ####
# from ror, gets OpenAIRE id of organization, output: string
def get_orgs(org_ror):
    print('[api_org] Retriving organization OpenAIRE id...')

    org_endpoint = 'https://api.openaire.eu/graph/v1/organizations'
    org_params = {'pid': org_ror}
    headers = {'accept': 'application/json'}

    org_response = requests.get(org_endpoint, params=org_params, headers=headers)
    if org_response.status_code == 200:
        org_data = org_response.json()
    else:
        print(f"[api_org] Error: {org_response.status_code}")
    return org_data["results"][0]["id"]

# from OpenAIRE organization id, gets list of publications (AP), output: list
def get_ap(org_id, start_year, end_year):
    print('[api_ap] Retriving publications affiliated to organization...')

    endpoint = 'https://api.openaire.eu/graph/v2/researchProducts'
    headers = {'accept': 'application/json'}

    publications = []

    params = {
        'pageSize': 100,
        'relOrganizationId': org_id
    }

    for year in range(start_year, end_year + 1):
        page = 1
        params['fromPublicationDate'] = f"{year}-01-01"
        params['toPublicationDate'] = f"{year}-12-31"
        while True:
            params['page'] = page
            response = requests.get(endpoint, headers=headers, params=params)
            if response.status_code == 200:
                results = response.json()
            else:
                print(f"[api_ap] Error: {response.status_code}")
                break

            for i, publication in enumerate(results['results']):
                pub_id = publication['id']
                pub_type = publication['type']
                pub_title = pub_funs.get_title(publication['mainTitle'], publication['subTitle'])
                pub_authors = pub_funs.get_authors(publication['authors'])
                pub_lang = pub_funs.get_lang(publication['language'])
                pub_doi = pub_funs.get_doi(publication['pids'])
                pub_year = pub_funs.get_year(publication['publicationDate'])
                pub_publisher = publication['publisher']
                pub_container_name = pub_funs.unpack_container(publication['container'], 'name')

                pub_issn = []
                pub_issnPrinted = pub_funs.unpack_container(publication['container'], 'issnPrinted')
                pub_issnOnline = pub_funs.unpack_container(publication['container'], 'issnOnline')
                if pub_issnPrinted != '':
                    pub_issn.append(pub_issnPrinted)
                if pub_issnOnline != '':
                    pub_issn.append(pub_issnOnline)

                pub_volume = pub_funs.unpack_container(publication['container'], 'vol')
                pub_issue = pub_funs.unpack_container(publication['container'], 'iss')

                pub_data = {
                    'id': pub_id,
                    'type': pub_type,
                    'title': pub_title,
                    'authors': pub_authors,
                    'lang': pub_lang,
                    'doi': pub_doi,
                    'year': pub_year,
                    'publisher': pub_publisher,
                    'container_name': pub_container_name,
                    'issn': pub_issn,
                    'volume': pub_volume,
                    'issue': pub_issue
                }
                publications.append(pub_data)

            if len(results["results"]) < 100:
                break

            page += 1
        
        print(f"[api_ap] Completed {year}. So far: {len(publications)} publications.")

    return deduplicate_OA(publications)

# from author list, gets list of publications (PfAL), output: list
def get_PfAL(start_year, end_year):
    AL_file_name = input("[api_pfal] Enter author list file name: ")
    AL = csv_funs.import_AL(AL_file_name)

    no_pubs_aut = 0

    if AL == []:
        return []
    else:
        print('[api_pfal] Retriving publications for author list...')
        endpoint = 'https://api.openaire.eu/graph/v2/researchProducts'
        headers = {'accept': 'application/json'}

        publications = []

        params = {
            'pageSize': 100,
            'fromPublicationDate': f"{start_year}-01-01",
            'toPublicationDate' : f"{end_year}-12-31"
        }

        for author in AL:
            if author['ORCID']:
                found_any = False
                page = 1
                while True:
                    if author['ORCID']:
                        params['authorOrcid'] = author['ORCID']
                        params['page'] = page
                        response = requests.get(endpoint, headers=headers, params=params)
                        if response.status_code == 200:
                            results = response.json()
                        else:
                            print(f"[api_pfal] Error: {response.status_code}")
                            break

                        if len(results['results']) == 0:
                            no_pubs_aut += 1
                            print(f"[api_pfal] No results for {author['PERSON_LAST_NAME']}, {author['PERSON_FIRST_NAME']}")
                            break
                        else:
                            found_any = True
                            for i, publication in enumerate(results['results']):
                                pub_id = publication['id']
                                pub_type = publication['type']
                                pub_title = pub_funs.get_title(publication['mainTitle'], publication['subTitle'])
                                pub_authors = pub_funs.get_authors(publication['authors'])
                                pub_lang = pub_funs.get_lang(publication['language'])
                                pub_doi = pub_funs.get_doi(publication['pids'])
                                pub_year = pub_funs.get_year(publication['publicationDate'])
                                pub_publisher = publication['publisher']
                                pub_container_name = pub_funs.unpack_container(publication['container'], 'name')

                                pub_issn = []
                                pub_issnPrinted = pub_funs.unpack_container(publication['container'], 'issnPrinted')
                                pub_issnOnline = pub_funs.unpack_container(publication['container'], 'issnOnline')
                                if pub_issnPrinted != '':
                                    pub_issn.append(pub_issnPrinted)
                                if pub_issnOnline != '':
                                    pub_issn.append(pub_issnOnline)

                                pub_volume = pub_funs.unpack_container(publication['container'], 'vol')
                                pub_issue = pub_funs.unpack_container(publication['container'], 'iss')

                                pub_data = {
                                    'id': pub_id,
                                    'type': pub_type,
                                    'title': pub_title,
                                    'authors': pub_authors,
                                    'lang': pub_lang,
                                    'doi': pub_doi,
                                    'year': pub_year,
                                    'publisher': pub_publisher,
                                    'container_name': pub_container_name,
                                    'issn': pub_issn,
                                    'volume': pub_volume,
                                    'issue': pub_issue
                                }

                                publications.append(pub_data)

                            if len(results["results"]) < 100:
                                break

                            page += 1
                if found_any:
                    print(f"[api_pfal] Completed {author['PERSON_LAST_NAME']}, {author['PERSON_FIRST_NAME']}. So far: {len(publications)} publications.")
            else:
                print(f"[api_pfal] No ORCID for {author['PERSON_LAST_NAME']}, {author['PERSON_FIRST_NAME']}.")
        print(f"[api_pfal] {no_pubs_aut} authors without publication on OpenAIRE")
        return deduplicate_OA(publications)