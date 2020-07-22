#!/usr/bin/python3

from PyQt5.QtCore import QObject, QEventLoop, QPointF, pyqtSlot
from PyQt5.QtGui import QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWebEngineWidgets import QWebEnginePage

# Code inspired by a StackOverflow answer: https://stackoverflow.com/a/59438692


class PrintHandler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_page = None
        self.m_inPrintPreview = False

    @property
    def page(self):
        return self.m_page

    @page.setter
    def page(self, page):
        if isinstance(page, QWebEnginePage):
            self.m_page = page
            self.page.printRequested.connect(self.print_preview)
        else:
            raise TypeError("page must be a QWebEnginePage")

    @pyqtSlot()
    def print(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self.page.view())
        if dialog.exec_() != QDialog.Accepted:
            return
        self.print_document(printer)

    @pyqtSlot()
    def print_preview(self):
        if self.page is None:
            return
        if self.m_inPrintPreview:
            return
        self.m_inPrintPreview = True
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self.page.view())
        preview.paintRequested.connect(self.print_document)
        preview.exec_()
        self.m_inPrintPreview = False

    @pyqtSlot(QPrinter)
    def print_document(self, printer):
        result = False
        loop = QEventLoop()

        def print_preview(success):
            nonlocal result
            result = success
            loop.quit()

        self.page.print(printer, print_preview)
        loop.exec_()
        if not result:
            painter = QPainter()
            if painter.begin(printer):
                font = painter.font()
                font.setPixelSize(20)
                painter.setFont(font)
                painter.drawText(QPointF(10, 25), "Could not generate print preview.")
                painter.end()