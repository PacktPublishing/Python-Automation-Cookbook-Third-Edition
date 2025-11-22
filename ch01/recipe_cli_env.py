import argparse
import os

default_character = os.environ.get('DEFAULT_CHAR', '#')


def main(character, number):
    print(character * number)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int, help='A number')
    help_msg = f'Character to print (default "{default_character}"). Set with env DEFAULT_CHAR'
    parser.add_argument('-c', type=str, help=help_msg,
                        default=default_character)
    args = parser.parse_args()
    main(args.c, args.number)
