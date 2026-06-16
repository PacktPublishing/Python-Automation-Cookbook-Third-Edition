#!/usr/bin/env python3

import fpdf
from random import randint
from lorem_text import lorem


class StructuredPDF(fpdf.FPDF):

    LINE_HEIGHT = 5

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        # Page number. Notice the {nb} which will be replaced
        # The double curly brackes will be replaced by a single one
        page_number = 'Page {number}/{{nb}}'.format(number=self.page_no())
        self.cell(0, self.LINE_HEIGHT, page_number, 0, align='R')

    def chapter(self, title, paragraphs):
        self.add_page()
        link = self.title_text(title)
        page = self.page_no()

        for paragraph in paragraphs:
            self.multi_cell(0, self.LINE_HEIGHT, paragraph)
            self.ln()

        return link, page

    def title_text(self, title):
        self.set_font('Times', 'B', 15)
        self.cell(0, self.LINE_HEIGHT, title)
        self.set_font('Times', '', 12)
        self.line(10, 17, 110, 17)
        link = self.add_link()
        self.set_link(link)
        self.ln()
        self.ln()

        return link

    def get_full_line(self, head, tail, fill):
        '''
        It returns the line up to the width with the proper number
        of fill elements.
        '''
        WIDTH = 120
        width = 0
        number = 1
        while width < WIDTH:
            number += 1
            line = '{} '.format(head) + '.' * number + '  {}'.format(tail)
            width = self.get_string_width(line)

        return line

    def toc(self, links):
        self.add_page()
        self.title_text('Table of contents')
        self.set_font('Times', 'I', 12)

        for title, page, link in links:
            line = self.get_full_line(title, page, '.')
            self.cell(0, self.LINE_HEIGHT, line, link=link)
            self.ln()


def main():
    document = StructuredPDF()
    document.alias_nb_pages()
    links = []
    num_chapters = randint(5, 40)
    for index in range(1, num_chapters):
        chapter_title = 'Chapter {}'.format(index)
        num_paragraphs = randint(10, 15)
        paragraphs = [lorem.paragraph() for _ in range(num_paragraphs)]
        link, page = document.chapter(chapter_title, paragraphs)
        links.append((chapter_title, page, link))

    document.toc(links)

    document.output('structure-pdf-report.pdf')


if __name__ == '__main__':
    main()
