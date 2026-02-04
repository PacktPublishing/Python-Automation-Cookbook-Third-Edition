'''
This file will read a log file in CSV and transform it into JSON data. Each log will be validated in JSON
'''
import csv
import json
import argparse
from pydantic import BaseModel, ValidationError, model_validator
from typing import Literal
from datetime import datetime

US_STATES = {'OH', 'NJ'}
CA_PROVINCES = {'ON', 'QC'}


class Log(BaseModel):
    LOCATION: Literal['ON', 'OH']
    TIMESTAMP: str
    PRODUCT: int
    PRICE: float
    COUNTRY: Literal['USA', 'CANADA']
    CURRENCY: Literal['USD', 'CAD']
    USD: float
    STD_TIMESTAMP: datetime

    @model_validator(mode='after')
    def check_location_and_currency(self):
        # Check location and country match
        if self.COUNTRY == 'USA' and self.LOCATION not in US_STATES:
            raise ValueError('For COUNTRY=USA, LOCATION should be a valid state')
        elif self.COUNTRY == 'CANADA' and self.LOCATION not in CA_PROVINCES:
            raise ValueError('For COUNTRY=CANADA, LOCATION should be a valid province')

        # Check currency match
        if self.COUNTRY == 'CANADA' and self.CURRENCY != 'CAD':
            raise ValueError('For COUNTRY=CANADA, CURRENCY should be CAD')
        elif self.COUNTRY == 'USA' and self.CURRENCY != 'USD':
            raise ValueError('For COUNTRY=USA, CURRENCY should be USD')

        return self


def verify_log(log):
    try:
        Log.model_validate(log)
        return True
    except ValidationError as err:
        print(f'Error validating log: {log}, {err}. \n--- Skippingn---')
        return False


def main(input_file, output_file):
    reader = csv.DictReader(input_file)

    # Go for each of the rows and verify that is correct
    # Only correct rows will be added to the saved data
    data = [row for row in reader if verify_log(row)]
    json.dump(data, output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='input', type=argparse.FileType('r'),
                        help='input file')
    parser.add_argument(dest='output', type=argparse.FileType('w'),
                        help='output file')
    args = parser.parse_args()
    main(args.input, args.output)
