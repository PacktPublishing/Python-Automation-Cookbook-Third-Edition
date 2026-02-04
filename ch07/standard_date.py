'''
This file will read a log file and produce an CSV file with the data
'''
import csv
import argparse
from datetime import datetime, timezone

# Timestamp formats
AMERICAN_FORMAT = '%m-%d-%Y %H:%M:%S'
CANADIAN_FORMAT = '%Y-%m-%d %H:%M:%S+00:00'


def to_isotime(timestamp, time_format):
    parsed_tmp = datetime.strptime(timestamp, time_format)
    time_with_tz = parsed_tmp.astimezone(timezone.utc)
    isotimestamp = time_with_tz.isoformat()

    return isotimestamp


def add_std_timestamp(row):
    country = row['COUNTRY']
    if country == 'USA':
        row['STD_TIMESTAMP'] = to_isotime(row['TIMESTAMP'], AMERICAN_FORMAT)
    elif country == 'CANADA':
        row['STD_TIMESTAMP'] = to_isotime(row['TIMESTAMP'], CANADIAN_FORMAT)
    else:
        raise Exception('Country not found')

    return row


def main(input_file, output_file):
    reader = csv.DictReader(input_file)
    result = [add_std_timestamp(row) for row in reader]

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
