
import os
import argparse
import csv
import docx
from bs4 import UnicodeDammit
from PyPDF2 import PdfReader


def search_txt(filename, word):
    '''
    Search the word in a text file
    '''
    try:
        try:
            # Try to read in UFT-8 first
            file = open(filename, encoding='utf-8')
            file.read(1)

        except UnicodeDecodeError:
            # Guess the encoding
            with open(filename, 'rb') as file:
                content = file.read(1024)

            if not content:
                # Empty file, skip
                return False

            suggestion = UnicodeDammit(content)
            encoding = suggestion.original_encoding

            # Open and read
            file = open(filename, encoding=encoding)

        # Be sure to go to the start of the file
        file.seek(0)

        for line in file:
            if word in line.lower():
                return True
    finally:
        file.close()
    return False


def search_csv(filename, word):
    '''
    Search the word in a text file
    '''
    with open(filename) as file:
        for row in csv.reader(file):
            for column in row:
                if word in column.lower():
                    return True

    return False


def search_pdf(filename, word):
    '''
    Search the word in a PDF file
    '''
    with open(filename, 'rb') as file:
        document = PdfReader(file)
        if document.is_encrypted:
            return False
        for page in document.pages:
            text = page.extract_text()
            if word in text.lower():
                return True

    return False


def search_docx(filename, word):
    '''
    Search for the word in a Word document
    '''
    doc = docx.Document(filename)
    for paragraph in doc.paragraphs:
        if word in paragraph.text.lower():
            return True

    return False


EXTENSIONS = {
    'txt': search_txt,
    'csv': search_csv,
    'pdf': search_pdf,
    'docx': search_docx,
}


def main(directory, word):
    '''
    Open the current directory and search in all the files
    '''
    for root, dirs, files in os.walk('.'):
        if directory not in root:
            continue
        for file in files:
            # Obtain the extension
            extension = file.split('.')[-1]
            if extension in EXTENSIONS:
                search_file = EXTENSIONS.get(extension)
                full_file_path = os.path.join(root, file)
                if search_file(full_file_path, word):
                    print(f'>>> Word found in {full_file_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='Directory to scan')
    parser.add_argument('-w', type=str, help='Word to search', default='the')
    args = parser.parse_args()

    # standarize the word to lowercase
    main(args.directory, args.w.lower())
