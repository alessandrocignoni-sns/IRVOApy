# collect publication authors existing data, output: list of dictionaries
def get_authors(authors_list):
    if authors_list is None:
        return []
    else:
        authors = []

        for author in authors_list:
            name = author['name']
            surname = author['surname']

            orcid = None
            pid = author['pid']
            if pid and pid['id']:
                if pid['id']['scheme'] in ('orcid', 'orcid_pending'):
                    orcid = pid['id']['value']

            if (name and surname) or orcid: # add author only if name/surname or orcid exist
                authors.append({ # None values converted to empty string
                    'name': name or '',
                    'surname': surname or '',
                    'orcid': orcid or ''
                })

        return authors


# collect publication language data, output: string    
def get_lang(lang_field):
    if lang_field['code'] == 'und':
        return ''
    else:
        return lang_field['code']
    
# collect publication DOI from pids field, output: string
def get_doi(pids_list):
    doi = ''
    if pids_list != None:
        for pid in pids_list:
            if pid['scheme'] == 'doi':
                doi = pid['value']
                break
    return doi

# merge publication title and subtitle, output: string
def get_title(main_title, sub_title):
    if sub_title != None:
        return f"{main_title} : {sub_title}"
    else:
        return main_title
    
# exctract publication year from publication date, output: string
def get_year(publication_date):
    if publication_date != None:
        return publication_date[:4]
    else:
        return ""

# unpack publication container data, output: string
def unpack_container(container, key):
    requested_value = ""
    if container != None:
        if container[key] != None:
            requested_value = container[key]
    return requested_value