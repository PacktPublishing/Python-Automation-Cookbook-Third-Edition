'''
This file will read a CSV file and produce another with aggregated data
'''
import csv
import json
import argparse
from datetime import datetime
from decimal import Decimal


def parse_iso(timestamp):
    # Parse the ISO format
    total = datetime.fromisoformat(timestamp)
    # Keep only the date
    return total.date()


def line(location, date, total_usd, number):
    data = {
        'LOCATION': location,
        'DATE': date,
        'TOTAL USD': total_usd,
        'NUMBER': number,
        # Round to two decimal places
        'AVERAGE': round(total_usd / number, 2),
    }
    return data


def calculate_results(reader):
    result = []
    last_date = None
    total_usd = 0
    number = 0

    for row in reader:
        location = row['LOCATION']
        date = parse_iso(row['STD_TIMESTAMP'])
        if not last_date:
            last_date = date

        if last_date < date:
            # New day!
            result.append(line(location, last_date, total_usd, number))
            total_usd = 0
            number = 0
            last_date = date

        number += 1
        total_usd += Decimal(row['USD'])

    # Final results
    result.append(line(location, date, total_usd, number))
    return result


def main(input_file, output_file):
    reader = json.load(input_file)
    result = calculate_results(reader)

    # Save into csv format
    header = result[0].keys()
    writer = csv.DictWriter(output_file, fieldnames=header)
    writer.writeheader()
    writer.writerows(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='input', type=argparse.FileType('r'),
                        help='input file')
    parser.add_argument(dest='output', type=argparse.FileType('w'),
                        help='output file')
    args = parser.parse_args()
    main(args.input, args.output)
