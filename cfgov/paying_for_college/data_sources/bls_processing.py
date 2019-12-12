from __future__ import unicode_literals

import datetime
import json
import logging
import os
import subprocess

from paying_for_college.models import PFC_ROOT, cdr

"""
# Data processing steps

This script was used to process a few xlsx files to look at expediture data
based on income and region
- source: https://www.bls.gov/cex/tables.htm#crosstab
- 4 regional xlsx files under "Region of residence by income before taxes":
  - xregnmw.xlsx
  - xregnne.xlsx
  - xregns.xlsx
  - xregnw.xlsx

The xlsx files were converted manually using the following steps:
- Use csvkit to convert to a UTF-8 CSV with the BOM and fake heading removed.
  Example command:
  ```bash
  in2csv xregnmw.xlsx | tail -n +3 | csvcut -e utf8-sig > xregnmw.csv
- Remove newline characters from the column names so we have a 1-line header.
- Lower down, remove everything from the line "Addenda:" to the end.
- Copy the four CSVs to /cfgov/paying_for_college/data_sources

This results in a CSV file with 11 columns.
The column names are common across the four CSVs, except for the second column,
which is unique to each region.

  1: Item
  2: Total south
  3: Less than $15,000
  4: $15,000 to $29,999
  5: $30,000 to $39,999
  6: $40,000 to $49,999
  7: $50,000 to $69,999
  8: $70,000 to $99,999
  9: $100,000 to $149,999
 10: $150,000 to $199,999
 11: $200,000 and more

The script can now be run from the Django shell:

```
./cfgov/manage.py shell
from paying_for_college.data_sources.bls_processing import create_bls_json_file
create_bls_json_file()
```

This will create a new file `current_bls_data.json`
at `paying_for_college/fixtures/bls_data.json`
and rename the former current fixture with its year prefix as a backup.

"""
# BLS releases new annual tables around Sept. 10, for the previous year
YEAR = datetime.date.today().year - 1
DATA_DIR = '{}/data_sources'.format(PFC_ROOT)
OUT_FILE = '{}/fixtures/current_bls_data.json'.format(PFC_ROOT)

REGION_MAP = {
    'NE': {'region': 'northeast', 'file': '{}/xregnne.csv'.format(DATA_DIR)},
    'SO': {'region': 'south', 'file': '{}/xregns.csv'.format(DATA_DIR)},
    'MW': {'region': 'midwest', 'file': '{}/xregnmw.csv'.format(DATA_DIR)},
    'WE': {'region': 'west', 'file': '{}/xregnw.csv'.format(DATA_DIR)}
}
CATEGORIES_KEY_MAP = {
    "Food": "Food",
    "Housing": "Housing",
    "Transportation": "Transportation",
    "Healthcare": "Healthcare",
    "Entertainment": "Entertainment",
    "Personal insurance and pensions": "Retirement",
    "Apparel and services": "Clothing",
    "Personal taxes (contains some imputed values)": "Taxes",
    # Other
    "Alcoholic beverages": "Other",
    "Personal care products and services": "Other",
    "Reading": "Other",
    "Education": "Other",
    "Tobacco products and smoking supplies": "Other",
    "Miscellaneous": "Other",
    "Cash contributions": "Other"
}
# INCOME_KEY_MAP_2014 = {
#     "Less than $5,000": "less_than_5000",
#     "$5,000 to $9,999": "5000_to_9999",
#     "$10,000 to $14,999": "10000_to_14999",
#     "$15,000 to $19,999": "15000_to_19999",
#     "$20,000 to $29,999": "20000_to_29999",
#     "$30,000 to $39,999": "30000_to_39999",
#     "$40,000 to $49,999": "40000_to_49999",
#     "$50,000 to $69,999": "50000_to_69999",
#     "$70,000 and more": "70000_or_more"
# }
INCOME_KEY_MAP = {
    "Less than $15,000": "less_than_15000",
    "$15,000 to $29,999": "15000_to_29999",
    "$30,000 to $39,999": "30000_to_39999",
    "$40,000 to $49,999": "40000_to_49999",
    "$50,000 to $69,999": "50000_to_69999",
    "$70,000 to $99,999": "70000_to_99999",
    "$100,000 to $149,999": "100000_to_149999",
    "$150,000 to $199,999": "150000_to_199999",
    "$200,000 and more": "200000_or_more"
}
PAYLOAD = {
    'Year': YEAR,
    "Food": {"note": "Dining out and in; all food costs"},
    "Housing": {"note": "Mortgage, rent, utilities, insurance"},
    "Transportation": {"note": "Cars, public transit, insurance"},
    "Healthcare": {"note": "Including insurance"},
    "Entertainment": {"note": "Events, pets, hobbies, equipment"},
    "Retirement": {"note": "Pensions and personal insurance"},
    "Clothing": {"note": "Apparel and services"},
    "Taxes": {"note": ("Personal federal, state, and local taxes; "
                       "contains some imputed values")},
    "Other": {"note": "Other expeditures"}
}

logger = logging.getLogger(__name__)


def load_bls_data(csvfile):
    with open(csvfile, 'rU') as f:
        reader = cdr(f)
        return [row for row in reader]


def add_bls_region(region):
    global PAYLOAD
    region_name = REGION_MAP[region]['region']
    csv_file = REGION_MAP[region]['file']
    data = load_bls_data(csv_file)  # load CSV rows as dicts
    logger.info("\nProcessing the {} region data".format(region_name))
    for row in data:
        item = row['Item']
        if item in CATEGORIES_KEY_MAP.keys():
            logger.info("Adding {}".format(item))
            PAYLOAD[CATEGORIES_KEY_MAP[item]].setdefault(region, {})
            income_item_dict = PAYLOAD[CATEGORIES_KEY_MAP[item]][region]
            average_column = 'Total {}'.format(region_name)
            overall_average = row.get(average_column).replace(',', '')
            income_item_dict.setdefault('overall_average', 0)
            income_item_dict['overall_average'] += int(overall_average)
            for income_key, income_json_key in INCOME_KEY_MAP.items():
                amount = row[income_key].replace(',', '')
                income_item_dict.setdefault(income_json_key, 0)
                income_item_dict[income_json_key] += int(amount)


def create_bls_json_file():
    if os.path.isfile(OUT_FILE):
        with open(OUT_FILE, 'r') as f:
            data = json.loads(f.read())
            existing_year = data.get('Year')
        backup = '{}/fixtures/{}_bls_data.json'.format(PFC_ROOT, existing_year)
        if not os.path.isfile(backup):
            subprocess.call(['cp', OUT_FILE, backup])
    for region in REGION_MAP:
        add_bls_region(region)
    with open(OUT_FILE, 'w') as outfile:
        outfile.write(json.dumps(PAYLOAD, indent=4))
