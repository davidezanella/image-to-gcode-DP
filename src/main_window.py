#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QVBoxLayout, QSplitter, QLabel, \
    QStatusBar, QMainWindow, QSlider, QFileDialog
from PyQt5 import QtCore, QtGui
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

from src.image_manipulation import elaborate_image
from src.print_handler import PrintHandler


class DisplayImageWidget(QWidget):
    def __init__(self, parent=None):
        super(DisplayImageWidget, self).__init__(parent)

        self.image_frame = QSvgWidget()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)

    def update_image(self, svg_img):
        svg_bytes = bytearray(svg_img, encoding='utf-8')
        self.image_frame.renderer().load(svg_bytes)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.image_name = ''

        self.black_threshold = 60
        self.white_threshold = 120
        self.canny_min = 50
        self.canny_max = 200
        self.black_steps = 2
        self.gray_steps = 6
        self.margin = 10
        self.draw_width = 150

        self.statusBar = QStatusBar()
        self.setWindowTitle('Image to Gcode - Duck Plotter')
        self.setStatusBar(self.statusBar)

        layout = QSplitter()

        self.display_image_widget = DisplayImageWidget()
        layout.addWidget(self.display_image_widget)

        btn_layout = QVBoxLayout()

        btn_load = QPushButton('Load image')
        btn_load.clicked.connect(self.load_image)
        btn_load.setIcon(QtGui.QIcon.fromTheme("document-open"))
        btn_layout.addWidget(btn_load)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        btn_layout.addWidget(line)

        self.lbl_black = QLabel()
        self.slider_black = QSlider(QtCore.Qt.Horizontal)
        self.slider_black.setMinimum(0)
        self.slider_black.setMaximum(255)
        self.slider_black.setValue(self.black_threshold)
        self.slider_black.setTickPosition(QSlider.TicksBelow)
        self.slider_black.setTickInterval(5)
        self.slider_black.valueChanged.connect(self.value_change)
        btn_layout.addWidget(self.lbl_black)
        btn_layout.addWidget(self.slider_black)

        self.lbl_white = QLabel()
        self.slider_white = QSlider(QtCore.Qt.Horizontal)
        self.slider_white.setMinimum(0)
        self.slider_white.setMaximum(255)
        self.slider_white.setValue(self.white_threshold)
        self.slider_white.setTickPosition(QSlider.TicksBelow)
        self.slider_white.setTickInterval(5)
        self.slider_white.valueChanged.connect(self.value_change)
        btn_layout.addWidget(self.lbl_white)
        btn_layout.addWidget(self.slider_white)

        self.lbl_canny_min = QLabel()
        self.slider_canny_min = QSlider(QtCore.Qt.Horizontal)
        self.slider_canny_min.setMinimum(0)
        self.slider_canny_min.setMaximum(255)
        self.slider_canny_min.setValue(self.canny_min)
        self.slider_canny_min.setTickPosition(QSlider.TicksBelow)
        self.slider_canny_min.setTickInterval(5)
        self.slider_canny_min.valueChanged.connect(self.value_change)
        btn_layout.addWidget(self.lbl_canny_min)
        btn_layout.addWidget(self.slider_canny_min)

        self.lbl_canny_max = QLabel()
        self.slider_canny_max = QSlider(QtCore.Qt.Horizontal)
        self.slider_canny_max.setMinimum(0)
        self.slider_canny_max.setMaximum(255)
        self.slider_canny_max.setValue(self.canny_max)
        self.slider_canny_max.setTickPosition(QSlider.TicksBelow)
        self.slider_canny_max.setTickInterval(5)
        self.slider_canny_max.valueChanged.connect(self.value_change)
        btn_layout.addWidget(self.lbl_canny_max)
        btn_layout.addWidget(self.slider_canny_max)

        self.lbl_black_steps = QLabel()
        self.slider_black_steps = QSlider(QtCore.Qt.Horizontal)
        self.slider_black_steps.setMinimum(1)
        self.slider_black_steps.setMaximum(50)
        self.slider_black_steps.setValue(self.black_steps)
        self.slider_black_steps.setTickPosition(QSlider.TicksBelow)
        self.slider_black_steps.setTickInterval(1)
        self.slider_black_steps.valueChanged.connect(self.value_change)
        btn_layout.addWidget(self.lbl_black_steps)
        btn_layout.addWidget(self.slider_black_steps)

        self.lbl_gray_steps = QLabel()
        self.slider_gray_steps = QSlider(QtCore.Qt.Horizontal)
        self.slider_gray_steps.setMinimum(1)
        self.slider_gray_steps.setMaximum(50)
        self.slider_gray_steps.setValue(self.gray_steps)
        self.slider_gray_steps.setTickPosition(QSlider.TicksBelow)
        self.slider_gray_steps.setTickInterval(1)
        self.slider_gray_steps.valueChanged.connect(self.value_change)
        btn_layout.addWidget(self.lbl_gray_steps)
        btn_layout.addWidget(self.slider_gray_steps)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        btn_layout.addWidget(line)

        self.lbl_margin = QLabel()
        self.slider_margin = QSlider(QtCore.Qt.Horizontal)
        self.slider_margin.setMinimum(1)
        self.slider_margin.setMaximum(50)
        self.slider_margin.setValue(self.margin)
        self.slider_margin.setTickPosition(QSlider.TicksBelow)
        self.slider_margin.setTickInterval(1)
        self.slider_margin.valueChanged.connect(self.value_change)
        btn_layout.addWidget(self.lbl_margin)
        btn_layout.addWidget(self.slider_margin)

        self.lbl_draw_width = QLabel()
        self.slider_draw_width = QSlider(QtCore.Qt.Horizontal)
        self.slider_draw_width.setMinimum(1)
        self.slider_draw_width.setMaximum(210)
        self.slider_draw_width.setValue(self.draw_width)
        self.slider_draw_width.setTickPosition(QSlider.TicksBelow)
        self.slider_draw_width.setTickInterval(1)
        self.slider_draw_width.valueChanged.connect(self.value_change)
        btn_layout.addWidget(self.lbl_draw_width)
        btn_layout.addWidget(self.slider_draw_width)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        btn_layout.addWidget(line)

        btn_update = QPushButton('Refresh image')
        btn_update.clicked.connect(self.update)
        btn_update.setIcon(QtGui.QIcon.fromTheme("view-refresh"))
        btn_layout.addWidget(btn_update)

        btn_gcode = QPushButton('Export Gcode')
        btn_gcode.clicked.connect(self.get_gcode)
        btn_gcode.setIcon(QtGui.QIcon.fromTheme("document-save"))
        btn_layout.addWidget(btn_gcode)

        btn_preview = QPushButton('Image preview')
        btn_preview.clicked.connect(self.print_preview)
        btn_preview.setIcon(QtGui.QIcon.fromTheme("document-print"))
        btn_layout.addWidget(btn_preview)

        btn_layout_widget = QWidget()
        btn_layout_widget.setLayout(btn_layout)
        layout.addWidget(btn_layout_widget)
        layout.setStretchFactor(0, 3)
        layout.setStretchFactor(1, 1)

        self.setCentralWidget(layout)

        self.value_change()
        self.load_image()

    def update(self):
        self.statusBar.showMessage('Loading image...')
        QApplication.processEvents()  # update UI

        self.svg_img, self.gcode, self.img_dims = elaborate_image(self.image_name, self.black_threshold,
                                                                  self.white_threshold, self.canny_min, self.canny_max,
                                                                  self.black_steps, self.gray_steps, self.margin,
                                                                  self.draw_width)
        self.display_image_widget.update_image(self.svg_img)

        self.statusBar.showMessage('Ready')

    def value_change(self):
        self.black_threshold = self.slider_black.value()
        self.white_threshold = self.slider_white.value()
        self.canny_min = self.slider_canny_min.value()
        self.canny_max = self.slider_canny_max.value()
        self.black_steps = self.slider_black_steps.value()
        self.gray_steps = self.slider_gray_steps.value()
        self.margin = self.slider_margin.value()
        self.draw_width = self.slider_draw_width.value()

        self.lbl_black.setText('Black threshold: ' + str(self.black_threshold))
        self.lbl_white.setText('White threshold: ' + str(self.white_threshold))
        self.lbl_canny_min.setText('Canny min value: ' + str(self.canny_min))
        self.lbl_canny_max.setText('Canny max value: ' + str(self.canny_max))
        self.lbl_black_steps.setText('Black filling steps: ' + str(self.black_steps))
        self.lbl_gray_steps.setText('Gray filling steps: ' + str(self.gray_steps))
        self.lbl_margin.setText('Margin on the paper: ' + str(self.margin) + ' mm')
        self.lbl_draw_width.setText('Width of the draw: ' + str(self.draw_width) + ' mm')

    def get_gcode(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save GCode", "path.gcode", "Gcode Files (*.gcode)")
        if file_name:
            self.update()
            with open(file_name, "w+") as f:
                f.write(self.gcode)

            self.statusBar.showMessage('Gcode saved!')

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open image", "", "All Files (*);;Image Files (*.jpg)")
        if file_name:
            self.image_name = file_name
            self.update()

    def print_preview(self):
        self.view = QWebEngineView()
        code = """
            <html>
                <head>
                    <style>
                        svg { 
                            width: """ + str(self.img_dims[0]) + """mm;
                            height: """ + str(self.img_dims[1]) + """mm;
                        }
                    </style>
                </head>
            <body>
                """ + self.svg_img + """
            </body>
            </html> 
        """
        self.view.loadFinished.connect(self.preview_load_finished)
        self.view.setHtml(code)

    def preview_load_finished(self):
        handler = PrintHandler(self)
        handler.page = self.view.page()
        handler.print_preview()