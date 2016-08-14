#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import getopt
import sys

from reportlab.lib.colors import black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, pica, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
from reportlab.pdfgen import canvas


class PageSettings:
    def __init__(self):
        self.columns = 4
        self.rows = 12
        self.landscape = True
        self.title = True
        self.pagesize = A4
        self.cutGrid = True

        self.margins = [10 * mm, 10 * mm, 10 * mm, 10 * mm]
        """
        Top, Left, Bottom, Right margins in Portrait orientation
        """

        self.fontSize = 16
        self.titleFontSize = 9
        self.titleHeight = 6 * mm
        self.titleIndent = 6 * mm
        self.wordMargin = 4 * mm
        """ Minimum gap between grid and word """


class Packet:
    TITLE = "title"
    FILENAME = "filename"
    SEPARATOR = "-----"

    HEADER_LINES = [TITLE, FILENAME]

    def __init__(self):
        self.words = []
        self.pages = []
        self.meta = {Packet.FILENAME: "out.pdf",
                     Packet.TITLE: "Пакет слов"}

    def loadFrom(self, filename):
        with codecs.open(filename, 'r', "utf-8") as infile:
            header = True
            headIndex = 0
            for line in infile:
                line = line.strip()
                if line[:len(Packet.SEPARATOR)] == Packet.SEPARATOR:
                    header = False
                    continue
                if header:
                    if headIndex >= len(Packet.HEADER_LINES):
                        print("Warning: extra header line:", line)
                        continue
                    self.meta[Packet.HEADER_LINES[headIndex]] = line
                    headIndex += 1
                else:
                    if line == "":
                        continue
                    if line[:1] == "#":
                        continue
                    self.words.append(line)

    def paginate(self, pageSettings: PageSettings):
        wordsPerPage = pageSettings.rows * pageSettings.columns
        self.pages = []
        words = self.words
        while len(words) > 0:
            pageWords = words[:wordsPerPage]
            words = words[len(pageWords):]
            page = []
            while len(pageWords) > 0:
                row = pageWords[:pageSettings.columns]
                page.append(row)
                pageWords = pageWords[len(row):]
            self.pages.append(page)

    def pageTitle(self, pageIndex):
        return "%s (%d words, page %d/%d)" % (self.meta[Packet.TITLE], len(self.words), pageIndex + 1, len(self.pages))

    def packetTitle(self):
        return self.meta[Packet.TITLE]

    def getOutFile(self):
        result = self.meta[Packet.FILENAME]
        if not result.endswith(".pdf"):
            result += ".pdf"
        return result


def generatePage(words, canvas: canvas.Canvas, page: PageSettings, title):
    """
    :param words: matrix of words (rows * columns)
    :param canvas: PDF canvas
    :param meta: other information (e.g page title)
    :return:
    """

    if page.landscape:
        (marginR, marginT, marginL, marginB) = page.margins
        (height, width) = page.pagesize
        titleX = marginT
        titleY = width - marginR
    else:
        (marginT, marginL, marginB, marginR) = page.margins
        (width, height) = page.pagesize
        titleX = marginL
        titleY = height - marginT

    if page.title:
        canvas.setFont("HatWordFont", page.titleFontSize)
        canvas.drawString(titleX + page.titleIndent, titleY - page.titleHeight / 2, title)

    if page.landscape:
        canvas.rotate(90)
        canvas.translate(0, -height)

    gwidth = width - marginL - marginR
    gheight = height - marginT - marginB

    goriginx = marginL
    goriginy = marginB

    if page.title:
        if page.landscape:
            gwidth -= page.titleHeight
        else:
            gheight -= page.titleHeight

    if page.cutGrid:
        canvas.setStrokeColor(black)
        # Large bold rectangle

        canvas.setLineWidth(0.4 * mm)
        canvas.rect(goriginx, goriginy, gwidth, gheight)
        # outer cutting lines:
        canvas.setLineWidth(0.3 * mm)
        canvas.line(0, goriginy, width, goriginy)
        canvas.line(0, goriginy + gheight, width, goriginy + gheight)
        canvas.line(goriginx, 0, goriginx, height)
        canvas.line(goriginx + gwidth, 0, goriginx + gwidth, height)

    # grid
    cellWidth = gwidth / page.columns
    cellHeight = gheight / page.rows

    canvas.setLineWidth(0.2 * mm)

    canvas.grid([goriginx + i * cellWidth for i in range(page.columns + 1)],
                [goriginy + j * cellHeight for j in range(page.rows + 1)])

    # add words
    canvas.setFont("HatWordFont", page.fontSize)

    # As y starts at the end of the page, adjust for it and start from the top
    # (so that empty cells will placed be at bottom).
    yoffset = goriginy + cellHeight / 2 + cellHeight * (page.rows - 1)
    for row in words:
        xoffset = goriginx + cellWidth / 2
        for word in row:
            # scale down font size for long words
            fontSize = page.fontSize
            while fontSize > 0 and canvas.stringWidth(word, fontSize=fontSize) >= cellWidth - 2 * page.wordMargin:
                fontSize -= 1
            canvas.setFontSize(fontSize)
            # Somewhat cheap guess on string height : fontsize / 2
            canvas.drawCentredString(xoffset, yoffset - fontSize / 2, word)
            xoffset += cellWidth
        yoffset -= cellHeight


def generateCover(canvas, pageSettings:PageSettings, packet:Packet, copies):
    # Cover page is always printed in portrait mode
    (width, height) = pageSettings.pagesize
    canvas.setFont("HatWordFont", pageSettings.fontSize)
    interval = pageSettings.fontSize * 2

    lines = [
        packet.packetTitle(),
        "%d words" % len(packet.words),
        "(%d pages) " % len(packet.pages),
    ]
    if copies > 1:
        lines += [
            "%d copies" % copies,
            "%d pages total" % (qty * len(packet.pages))
        ]

    hOffset = height / 2 + (interval * len(lines)) / 2
    for index, line in enumerate(lines):
        canvas.drawCentredString(width / 2, hOffset - interval * index, line)
    canvas.showPage()


def generatePdf(packet: Packet, copies, pageSettings, hasCover):
    pdfCanvas = canvas.Canvas(packet.getOutFile(), pagesize=A4)
    pdfCanvas.setTitle(packet.packetTitle())
    if hasCover:
        generateCover(pdfCanvas, pageSettings, packet, copies)
    for copy in range(copies):
        for index, page in enumerate(packet.pages):
            generatePage(page, pdfCanvas, pageSettings, packet.pageTitle(index))
            pdfCanvas.showPage()
    pdfCanvas.save()


def usage():
    print(""" Usage: packet2pdf.py [options] packet1 .... packetN
    Options:
        --cover   : print cover sheet
        --notitle : do not print title line
        --portrait
        -p        : use portrait mode (3 columns, 16 rows)
        --rows=R
        -r R      : use R rows (default: 12)
        --columns=N
        -c C      : use C columns (default: 4)
        --font=size
        -f size   : specify font size (default: 16pt)
        --copies=N
        -n N      : generate pdf with N copies
    """)


if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "phn:r:c:f:",
                                   ["help", "portrait", "notitle", "cover",
                                    "copies=", "rows=", "columns=", "font="])
    except getopt.GetoptError as err:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    pageSettings = PageSettings()

    hasCover = False
    qty = 1

    for opt, arg in opts:
        if opt == "--cover":
            hasCover = True
        elif opt == "--notitle":
            pageSettings.title = False
        elif opt in ("-n", "--copies"):
            qty = int(arg)
        elif opt in ("-r", "--rows"):
            pageSettings.rows = int(arg)
        elif opt in ("-c", "--columns"):
            pageSettings.columns = int(arg)
        elif opt in ("-f", "--font"):
            pageSettings.fontSize = int(arg)
        elif opt in ("-p", "--portrait"):
            pageSettings.landscape = False
            pageSettings.columns = 3
            pageSettings.rows = 16
        elif opt in ("-h", "--help"):
            usage()
            sys.exit(0)

    hatWordFont = ttfonts.TTFont('HatWordFont', 'DroidSans.ttf')
    pdfmetrics.registerFont(hatWordFont)

    for file in args:
        packet = Packet()
        packet.loadFrom(filename=file)
        packet.paginate(pageSettings)
        generatePdf(packet, qty, pageSettings, hasCover)
