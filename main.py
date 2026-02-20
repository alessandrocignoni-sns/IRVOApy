# import of all functions
import config as conf
import functions.api_funs as api_funs
import functions.csv_funs as csv_funs
import functions.json_funs as json_funs
import functions.normalization as norm
import functions.comparing as comp

# cofig variables questions
debug_flag = input('[config] Enable JSON file printing for debuggibng? (y/n): ')
if debug_flag.lower() == 'y':
    conf.DEBUG = True
iris_flag = input('[config] IR source is CINECA\'s IRIS? (y/n): ')
if iris_flag.lower() == 'y':
    conf.IRIS = True

# get year range of analysis
start_year = int(input("[main] Enter start year of the analysis: "))
end_year = int(input("[main] Enter end year of the analysis: "))

# get OpenAIRE id of input organization
org_ror = input("[main] Enter organization ROR: ")
org_id = api_funs.get_orgs(org_ror)
print(f'[main] Organization id: {org_id}')

# get list of publication affiliated to organization (PA)
conf.AP = api_funs.get_ap(org_id, start_year, end_year)
conf.AP_norm = norm.normalize_OpenAIRE_dataset(conf.AP)
if conf.DEBUG:
    json_funs.save_json(conf.AP, 'AP')
    json_funs.save_json(conf.AP_norm, 'AP_norm')

# get list of publication from author list (PfAL)
PfAL_flag = csv_funs.ask_for_AL()
if PfAL_flag:
    conf.PfAL = api_funs.get_PfAL(start_year, end_year)
    conf.PfAL_norm = norm.normalize_OpenAIRE_dataset(conf.PfAL)
    if conf.DEBUG:
        json_funs.save_json(conf.PfAL, 'PfAL')
        json_funs.save_json(conf.PfAL_norm, 'PfAL_norm')

# get list of publication from Istitutional Repository (PfIR)
PfIR_flag = csv_funs.ask_for_PfIR()
if PfIR_flag:
    conf.PfIR = csv_funs.import_PfIR()
    conf.PfIR_norm = norm.normalize_IR_dataset(conf.PfIR, conf.IRIS)
    if conf.DEBUG:
        json_funs.save_json(conf.PfIR, 'PfIR')
        json_funs.save_json(conf.PfIR_norm, 'PfIR_norm')

# start comparison
possible_comparisons = comp.check_for_comparison()
while True:
    selected_comparison = comp.ask_for_comparison(possible_comparisons)
    if selected_comparison == 0:
        print('[main] End of program.')
        break
    else:
        comp.launch_comparison(selected_comparison)