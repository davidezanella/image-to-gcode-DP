#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QStatusBar, QMainWindow, QSlider, QFileDialog
from PyQt5 import QtCore, QtGui
import sys

from image_manipulation import elaborate_image


class DisplayImageWidget(QWidget):
    def __init__(self, parent=None):
        super(DisplayImageWidget, self).__init__(parent)

        self.image_frame = QLabel()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)


    def update_image(self, image_opencv):
        self.image = image_opencv
        size = self.image.shape
        step = self.image.size / size[0]
        qformat = QtGui.QImage.Format_Indexed8

        if len(size) == 3:
            if size[2] == 4:
                qformat = QtGui.QImage.Format_RGBA8888
            else:
                qformat = QtGui.QImage.Format_RGB888

        self.image = QtGui.QImage(self.image.data, size[1], size[0], step, qformat).rgbSwapped()
        pixmap = QtGui.QPixmap.fromImage(self.image)
        pixmap = pixmap.scaledToWidth(500)
        self.image_frame.setPixmap(pixmap)


class MainWIndow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWIndow, self).__init__(parent)

        self.image_name = ''

        self.black_threshold = 60
        self.white_threshold = 120
        self.canny_min = 50
        self.canny_max = 200
        self.black_steps = 2
        self.gray_steps = 6


        self.statusBar = QStatusBar()
        self.setWindowTitle('Image to Gcode - Duck Plotter')
        self.setStatusBar(self.statusBar)

        layout = QHBoxLayout()

        self.display_image_widget = DisplayImageWidget()
        layout.addWidget(self.display_image_widget)


        btn_layout = QVBoxLayout()

        btn_load = QPushButton('Load image')
        btn_load.clicked.connect(self.load_image)
        btn_layout.addWidget(btn_load)

        lbl_black = QLabel('Black threshold:')
        self.slider_black = QSlider(QtCore.Qt.Horizontal)
        self.slider_black.setMinimum(0)
        self.slider_black.setMaximum(255)
        self.slider_black.setValue(self.black_threshold)
        self.slider_black.setTickPosition(QSlider.TicksBelow)
        self.slider_black.setTickInterval(5)
        self.slider_black.valueChanged.connect(self.value_change)
        btn_layout.addWidget(lbl_black)
        btn_layout.addWidget(self.slider_black)

        lbl_white = QLabel('White threshold:')
        self.slider_white = QSlider(QtCore.Qt.Horizontal)
        self.slider_white.setMinimum(0)
        self.slider_white.setMaximum(255)
        self.slider_white.setValue(self.white_threshold)
        self.slider_white.setTickPosition(QSlider.TicksBelow)
        self.slider_white.setTickInterval(5)
        self.slider_white.valueChanged.connect(self.value_change)
        btn_layout.addWidget(lbl_white)
        btn_layout.addWidget(self.slider_white)

        lbl_canny_min = QLabel('Canny min value:')
        self.slider_canny_min = QSlider(QtCore.Qt.Horizontal)
        self.slider_canny_min.setMinimum(0)
        self.slider_canny_min.setMaximum(255)
        self.slider_canny_min.setValue(self.canny_min)
        self.slider_canny_min.setTickPosition(QSlider.TicksBelow)
        self.slider_canny_min.setTickInterval(5)
        self.slider_canny_min.valueChanged.connect(self.value_change)
        btn_layout.addWidget(lbl_canny_min)
        btn_layout.addWidget(self.slider_canny_min)

        lbl_canny_max = QLabel('Canny max value:')
        self.slider_canny_max = QSlider(QtCore.Qt.Horizontal)
        self.slider_canny_max.setMinimum(0)
        self.slider_canny_max.setMaximum(255)
        self.slider_canny_max.setValue(self.canny_max)
        self.slider_canny_max.setTickPosition(QSlider.TicksBelow)
        self.slider_canny_max.setTickInterval(5)
        self.slider_canny_max.valueChanged.connect(self.value_change)
        btn_layout.addWidget(lbl_canny_max)
        btn_layout.addWidget(self.slider_canny_max)

        lbl_black_steps = QLabel('Black filling steps:')
        self.slider_black_steps = QSlider(QtCore.Qt.Horizontal)
        self.slider_black_steps.setMinimum(1)
        self.slider_black_steps.setMaximum(50)
        self.slider_black_steps.setValue(self.black_steps)
        self.slider_black_steps.setTickPosition(QSlider.TicksBelow)
        self.slider_black_steps.setTickInterval(1)
        self.slider_black_steps.valueChanged.connect(self.value_change)
        btn_layout.addWidget(lbl_black_steps)
        btn_layout.addWidget(self.slider_black_steps)

        lbl_gray_steps = QLabel('Gray filling steps:')
        self.slider_gray_steps = QSlider(QtCore.Qt.Horizontal)
        self.slider_gray_steps.setMinimum(1)
        self.slider_gray_steps.setMaximum(50)
        self.slider_gray_steps.setValue(self.gray_steps)
        self.slider_gray_steps.setTickPosition(QSlider.TicksBelow)
        self.slider_gray_steps.setTickInterval(1)
        self.slider_gray_steps.valueChanged.connect(self.value_change)
        btn_layout.addWidget(lbl_gray_steps)
        btn_layout.addWidget(self.slider_gray_steps)

        btn_update = QPushButton('Refresh image')
        btn_update.clicked.connect(self.update)
        btn_layout.addWidget(btn_update)

        btn_gcode = QPushButton('Export Gcode')
        btn_gcode.clicked.connect(self.get_gcode)
        btn_layout.addWidget(btn_gcode)

        layout.addLayout(btn_layout)

        main_widget = QWidget()
        main_widget.setLayout(layout)

        self.setCentralWidget(main_widget)

        self.load_image()


    def update(self):
        self.statusBar.showMessage('Loading image...')
        QApplication.processEvents() # update UI

        image_opencv, self.gcode = elaborate_image(self.image_name, self.black_threshold,
            self.white_threshold, self.canny_min, self.canny_max,
            self.black_steps, self.gray_steps)
        self.display_image_widget.update_image(image_opencv)

        self.statusBar.showMessage('Ready')


    def value_change(self):
        self.black_threshold = self.slider_black.value()
        self.white_threshold = self.slider_white.value()
        self.canny_min = self.slider_canny_min.value()
        self.canny_max = self.slider_canny_max.value()
        self.black_steps = self.slider_black_steps.value()
        self.gray_steps = self.slider_gray_steps.value()


    def get_gcode(self):
        with open("path.gcode", "w+") as f:
            f.write(self.gcode)

        self.statusBar.showMessage('Gcode saved!')


    def load_image(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open image", "","All Files (*);;Image Files (*.jpg)")
        if fileName:
            self.image_name = fileName
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWIndow()
    main.show()

    sys.exit(app.exec_())
