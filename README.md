# IRVOApy

## Description
Institutional Repository Vs OpenAIRE py (IRVOApy) is a Python3 script to collect research project metadata from OpenAIRE and compare it to an Institutional Repository dataset to find out common and uniques records.
...

## Features
- Common and unique records of Institutional Repository dataset and OpenAIRE
- Different comparison to analyse indexing of institution production by OpenAIRE
- output XLSX file with summary tables and graphs

## Project Structure
    IRVOApy/
    │
    ├── functions/                  # Python libraries
    │   ├── \__init__.py            # Builds package
    │   ├── analysis.py             # Builds XLSX file
    │   ├── api_funs.py             # Connects to OpenAIRE APIs using requests
    │   ├── comparing.py            # Dataset comparison
    │   ├── csv_funs.py             # Extract datasets from input CSV files
    │   ├── json_funs.py            # Read/write JSON files in output folder (debugging)
    │   ├── normalization.py        # Dataset normalization functions
    │   └── pub_funs.py             # Dataset extraction functions
    │
    ├── input/                      # Input CSV files
    │   ├── AL_placeholder.csv      # Author List CSV file structure
    │   └── PfIR_placeholder.csv    # Products from Institutional Repository CSV file structure
    │
    ├── output/                     # Output XLSX files
    ├── AUTHORS.md                  # Contributors and roles
    ├── config.py                   # Global variables
    ├── LICENCE.md                  # License information
    ├── main.py                     # Executable Python script
    └── README.md                   # Project overview

## Installation
Instructions to install required libraries.

    $ python -m pip install requests
    $ python -m pip install openpyxl

## Usage
Import in input folder the CSV files for Author Lists and Products from Institutional Repository.
Structure of CSV files is show in two mock up files in input folders.

How to run project:

    $ cd <installation_folder>
    $ python main.py

## License
GNU LESSER GENERAL PUBLIC LICENSE

## Acknowledgments
...

