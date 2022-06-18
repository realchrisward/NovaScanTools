# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 10:52:12 2022

@author: wardc

utility tool for image to pdf conversion

expected inpute/outputs
input: list of filepaths to jpg images
output_mode: merge-fast, merge-newname, individual-fast, individual-newname
ouput_path: path to location to store outputs
resize_rotate_crop: 
    user specify size (default 8.5 x 11), 
    no rotate / user spec rotate / auto rotate, 
    no crop / user spec crop
output_name: name to use for output file (used for newname output modes)

"""

#%% import libraries

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QComboBox, QLineEdit, QDoubleSpinBox
from PyQt5.QtGui import QImage, QPixmap
import io
from PIL import Image, ImageDraw, ImageFont
import sys

#%% define functions


#%% define classes
class MainWindow:
    def __init__(self):
        
        #%% create instance of application
        app=QApplication([])
        window = QWidget()
        window.setWindowTitle('Image to PDF Converter')
        window.setGeometry(10,10,1600,900)
        window.move(100,100)
        Label_1=QLabel('<h1>**Trace Viewer**</h1>',parent=window)
        Label_1.move(1280,720)
        #% add image
        bytes_img=io.BytesIO()
        
        QIM=QImage()
        QIM.loadFromData(bytes_img.getvalue())
        PIX=QPixmap.fromImage(QIM)
        Label_IMG=QLabel(parent=window)
        Label_IMG.setPixmap(PIX)
        Label_IMG.move(0,0)
        
        window.show()
        sys.exit(app.exec_())
#%% create GUI





#%% button callbacks

# initialize gui

#[left column - settings]
#[right column - preview window for user spec crop - also buttons to navigate images]


# collect input list

# specify output_mode

# specify output_path

# specify output_size

def main():
    MW = MainWindow()

if __name__ == '__main__':
    main()