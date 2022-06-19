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

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QPushButton, QButtonGroup, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QFileDialog, QComboBox, QLineEdit, QDoubleSpinBox, QGroupBox, QRadioButton, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QAbstractItemView, QTextEdit
from PyQt5.QtGui import QImage, QPixmap, QTransform
import io
from PIL import Image, ImageDraw, ImageFont
import sys
import os

#%% define functions



    
#%% define classes
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.image_paths = []
        self.image_dict = {}
        self.output_directory = ''
        self.output_mode = 'Individual'
        self.rotation_mode = 'Auto'
        self.crop_mode = 'None'
        self.output_size = (8.5,11)
        self.crop_x1 = 0
        self.crop_y1 = 0
        self.crop_x2 = 500
        self.crop_y2 = 500
        self.merged_name = 'merged'
        
        
        # transforms
        self.transforms = {}
        for t in [0,90,180,270]:
            self.transforms[t] = QTransform()
            self.transforms[t].rotate(t)
        
        
        
        self.app=QApplication(sys.argv)
        self.setWindowTitle('Nova Scan Tools - Image to PDF Converter')
        self.setGeometry(10,10,1250,750)
        self.move(100,100)
        self.Label_1=QLabel('<h1>**Nova Scan Tools**</h1>',parent=self)
        self.Label_1.setFixedSize(1250,25)
        self.Label_1.move(0,10)
        self.Label_1.setAlignment(Qt.AlignCenter)
        
        # add buttons
        
        # load images
        self.load_images = QPushButton('Load Images', parent=self)
        self.load_images.setFixedSize(150,25)
        self.load_images.move(50,50)
        self.load_images.clicked.connect(self.run_load_images)
        
        # set output location
        self.output_location = QPushButton('Set Output Location', parent=self)
        self.output_location.setFixedSize(150,25)
        self.output_location.move(50,600)
        self.output_location.clicked.connect(self.run_output_location)
        
        # Make PDF
        self.make_pdf = QPushButton('Make PDF', parent=self)
        self.make_pdf.setFixedSize(150,25)
        self.make_pdf.move(50,700)
        self.make_pdf.clicked.connect(self.run_make_pdf)
        
        # output mode
        self.output_mode_select = QButtonGroup(self)
        self.output_mode_select_box = QGroupBox('Output Mode',self)
        self.output_mode_select_layout = QVBoxLayout()
        self.output_mode_individual = QRadioButton("Individual",self)
        self.output_mode_individual.toggled.connect(self.update_output_mode)
        self.output_mode_merged = QRadioButton("Merged",self)
        self.output_mode_merged.toggled.connect(self.update_output_mode)
        self.output_mode_individual.setChecked(True)
        self.output_mode_select.addButton(self.output_mode_individual)
        self.output_mode_select.addButton(self.output_mode_merged)
        self.output_mode_select_layout.addWidget(self.output_mode_individual)
        self.output_mode_select_layout.addWidget(self.output_mode_merged)
        self.output_mode_select_layout.setContentsMargins(5,5,5,5)
        self.output_mode_select_box.move(50,450)
        self.output_mode_select_box.setFixedSize(100,100)
        self.output_mode_select_box.setLayout(self.output_mode_select_layout)
        
        # rotation mode
        self.rotation_mode_select = QButtonGroup(self)
        self.rotation_mode_select_box = QGroupBox('Rotation Mode',self)
        self.rotation_mode_select_layout = QVBoxLayout()
        self.rotation_mode_auto = QRadioButton("Auto",self)
        self.rotation_mode_auto.toggled.connect(self.update_rotation_mode)
        self.rotation_mode_auto.setChecked(True)
        self.rotation_mode_norot_port = QRadioButton("No Rotation-Portrait",self)
        self.rotation_mode_norot_port.toggled.connect(self.update_rotation_mode)
        self.rotation_mode_norot_land = QRadioButton("No Rotation-Landcape",self)
        self.rotation_mode_norot_land.toggled.connect(self.update_rotation_mode)
        self.rotation_mode_custom = QRadioButton("Custom",self)
        self.rotation_mode_custom.toggled.connect(self.update_rotation_mode)
        self.rotation_mode_select.addButton(self.rotation_mode_auto)
        self.rotation_mode_select.addButton(self.rotation_mode_norot_port)
        self.rotation_mode_select.addButton(self.rotation_mode_norot_land)
        self.rotation_mode_select.addButton(self.rotation_mode_custom)
        self.rotation_mode_select_layout.addWidget(self.rotation_mode_auto)
        self.rotation_mode_select_layout.addWidget(self.rotation_mode_norot_port)
        self.rotation_mode_select_layout.addWidget(self.rotation_mode_norot_land)
        self.rotation_mode_select_layout.addWidget(self.rotation_mode_custom)
        self.rotation_mode_select_layout.setContentsMargins(5,5,5,5)
        self.rotation_mode_select_box.move(150,450)
        self.rotation_mode_select_box.setFixedSize(150,100)
        self.rotation_mode_select_box.setLayout(self.rotation_mode_select_layout)
        
        # crop mode
        self.crop_mode_select = QButtonGroup(self)
        self.crop_mode_select_box = QGroupBox('Crop Mode',self)
        self.crop_mode_select_layout = QVBoxLayout()
        self.crop_mode_none = QRadioButton("None",self)
        self.crop_mode_none.toggled.connect(self.update_crop_mode)
        self.crop_mode_none.setChecked(True)
        self.crop_mode_all = QRadioButton("All",self)
        self.crop_mode_all.toggled.connect(self.update_crop_mode)
        self.crop_mode_custom = QRadioButton("Custom",self)
        self.crop_mode_custom.toggled.connect(self.update_crop_mode)
        self.crop_mode_select.addButton(self.crop_mode_none)
        self.crop_mode_select.addButton(self.crop_mode_all)
        self.crop_mode_select.addButton(self.crop_mode_custom)
        self.crop_mode_select_layout.addWidget(self.crop_mode_none)
        self.crop_mode_select_layout.addWidget(self.crop_mode_all)
        self.crop_mode_select_layout.addWidget(self.crop_mode_custom)
        self.crop_mode_select_layout.setContentsMargins(5,5,5,5)
        self.crop_mode_select_box.move(300,450)
        self.crop_mode_select_box.setFixedSize(75,100)
        self.crop_mode_select_box.setLayout(self.crop_mode_select_layout)
        
        # list of images
        self.image_list = QListWidget(self)
        self.image_list.move(50,100)
        self.image_list.setFixedSize(300,300)
        self.image_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.image_list.itemSelectionChanged.connect(self.update_image)
        
        # image path
        self.image_path_text = QTextEdit('',self)
        self.image_path_text.setFixedSize(700,25)
        self.image_path_text.move(500,650)
        
        # image crop
        
        
        
        # pdf path
        self.pdf_path_text = QTextEdit('',self)
        self.pdf_path_text.setFixedSize(300,25)
        self.pdf_path_text.move(50,650)
        
        # pdf size
        
        
        # next image
        self.next_image = QPushButton('\\/', parent = self)
        self.next_image.setFixedSize(25,25)
        self.next_image.move(400,150)
        self.next_image.clicked.connect(self.run_next_image)
        
        # prev image
        self.prev_image = QPushButton('/\\', parent = self)
        self.prev_image.setFixedSize(25,25)
        self.prev_image.move(400,125)
        self.prev_image.clicked.connect(self.run_prev_image)
        
        # clockwise
        self.image_rot_cw = QPushButton('/-->', parent = self)
        self.image_rot_cw.setFixedSize(25,25)
        self.image_rot_cw.move(850,700)
        self.image_rot_cw.clicked.connect(self.run_cw)
        
        # counterclockwise
        self.image_rot_ccw = QPushButton('<--\\', parent = self)
        self.image_rot_ccw.setFixedSize(25,25)
        self.image_rot_ccw.move(825,700)
        self.image_rot_ccw.clicked.connect(self.run_ccw)
        
        # flip vert
        self.image_flip_vert = QPushButton('Flip-Vert', parent = self)
        self.image_flip_vert.setFixedSize(75,25)
        self.image_flip_vert.move(900,700)
        self.image_flip_vert.clicked.connect(self.run_flip_vert)
        
        # flip horiz
        self.image_flip_horiz = QPushButton('Flip-Horiz', parent = self)
        self.image_flip_horiz.setFixedSize(75,25)
        self.image_flip_horiz.move(975,700)
        self.image_flip_horiz.clicked.connect(self.run_flip_horiz)
        
        #% add image
        self.PIX=QPixmap()
        self.Label_IMG=QLabel(parent = self)
        self.Label_IMG.setFixedSize(500,500)
        self.Label_IMG.setPixmap(self.PIX.scaled(500,500,Qt.KeepAspectRatio))
        self.Label_IMG.move(500,100)
        self.Label_IMG.setAlignment(Qt.AlignLeft)
        self.Label_IMG.mousePressEvent = self.get_pos_press
        self.Label_IMG.mouseReleaseEvent = self.get_pos_release
        
        
        
    def get_pos_press(self,event):
        self.crop_x1 = event.pos().x()
        self.crop_y1 = event.pos().y()
        
        
    
    def get_pos_release(self,event):
        self.crop_x2 = event.pos().x()
        self.crop_y2 = event.pos().y()
        print(f'({self.crop_x1},{self.crop_y1}) - ({self.crop_x2},{self.crop_y2})')
        self.update_crop()
        
    
    
    def update_crop(self):
        print('update crop')
        
        
        
    @pyqtSlot()
    def run_flip_vert(self):
        print('flip vert')
        self.image_dict[
            self.image_list.currentItem().text()
            ]['flip-v'] = int(
                not(
                    self.image_dict[
                        self.image_list.currentItem().text()
                        ]['flip-v']
                    )
                )
        
        print(
            'flip vert - {}'.format(
                self.image_dict[
                    self.image_list.currentItem().text()
                    ]['flip-v']
                )
            )
        self.update_image()
        
        
    @pyqtSlot()
    def run_flip_horiz(self):
        
        self.image_dict[
            self.image_list.currentItem().text()
            ]['flip-h'] = int(
                not(
                    self.image_dict[
                        self.image_list.currentItem().text()
                        ]['flip-h']
                    )
                )
        
        print(
            'flip horiz - {}'.format(
                self.image_dict[
                    self.image_list.currentItem().text()
                    ]['flip-h']
                )
            )
        self.update_image()
                
                
        
        
    @pyqtSlot()
    def run_cw(self):
        print('cw')
        new_rot = self.image_dict[
            self.image_list.currentItem().text()
            ]['rot'] + 90
        if new_rot > 270:
            new_rot = 0
        
        self.image_dict[
            self.image_list.currentItem().text()
            ]['rot'] = new_rot
        
        self.update_image()
        
    
    
    @pyqtSlot()
    def run_ccw(self):
        print('ccw')
        
        new_rot = self.image_dict[
            self.image_list.currentItem().text()
            ]['rot'] - 90
        if new_rot < 0:
            new_rot = 270
        
        self.image_dict[
            self.image_list.currentItem().text()
            ]['rot'] = new_rot
        
        self.update_image()
    
    @pyqtSlot()
    def update_image(self):
        print(self.image_list.currentItem().text())
        # update image path text
        self.image_path_text.setText(
            self.image_dict[self.image_list.currentItem().text()]['path']
            )
        
        # update image preview
        print(self.image_dict[self.image_list.currentItem().text()]['path'])
        self.PIX=QPixmap(
            self.image_dict[self.image_list.currentItem().text()]['path']
            )
        # layers of things happening here, rescaling for size, transforming for rotation and flipping (using some math to address conversion of boolian to 1 or -1)
        self.Label_IMG.setPixmap(
            self.PIX.scaled(
                500,
                500,
                Qt.KeepAspectRatio
                ).transformed(
                    self.transforms[
                        self.image_dict[
                            self.image_list.currentItem().text()]['rot']
                        ]
                    ).transformed(
                        QTransform().scale(
                            (-1*self.image_dict[
                                self.image_list.currentItem().text()]['flip-h'])**\
                                self.image_dict[
                                    self.image_list.currentItem().text()]['flip-h'],
                            (-1*self.image_dict[
                                self.image_list.currentItem().text()]['flip-v'])**\
                                self.image_dict[
                                    self.image_list.currentItem().text()]['flip-v']
                            )
                        )
            )
        self.Label_IMG.repaint()
        self.show()
        self.update()
        self.app.processEvents()
        # update image crop preview
        
        # update output path
        self.update_output_path()
    
    
    
    @pyqtSlot()
    def run_next_image(self):
        current_row = self.image_list.currentRow()
        if self.image_list.count()-1 == current_row:
            self.image_list.setCurrentRow(0)
        else:
            self.image_list.setCurrentRow(current_row+1)
        print(f'next image - {current_row+1}')
    
        
        
    @pyqtSlot()
    def run_prev_image(self):
        current_row = self.image_list.currentRow()
        if 0 == current_row:
            self.image_list.setCurrentRow(self.image_list.count()-1)
        else:
            self.image_list.setCurrentRow(current_row-1)
        print(f'previous image - {current_row-1}')
    
    
    
    @pyqtSlot()
    def update_output_mode(self):
        selected_button = self.sender()
        if selected_button.isChecked():
            self.output_mode = selected_button.text()
        print(self.output_mode)
        self.update_output_path()
        
        
        
    def update_output_path(self):
        print(self.image_list.currentItem().text())
        print(self.image_dict[
            self.image_list.currentItem().text()
            ]['filename'])
        
        
        
        
        
        if self.output_mode == 'Individual':
            self.pdf_path_text.setText(
                os.path.join(
                    self.output_directory,
                    self.image_dict[
                        self.image_list.currentItem().text()
                        ]['filename']+'.pdf'
                    )
                )
                
        else:
            self.pdf_path_text.setText(
                os.path.join(
                    self.output_directory,
                    self.merged_name+'.pdf'
                    )
                )
        
        
    
    @pyqtSlot()
    def update_crop_mode(self):
        selected_button = self.sender()
        if selected_button.isChecked():
            self.crop_mode = selected_button.text()
        print(self.crop_mode)
        
       
        
    @pyqtSlot()
    def update_rotation_mode(self):
        selected_button = self.sender()
        if selected_button.isChecked():
            self.rotation_mode = selected_button.text()
        print(self.rotation_mode)
        
        
        
    @pyqtSlot()
    def run_load_images(self):
        self.image_paths = QFileDialog.getOpenFileNames(
            self,
            'Select Images',
            '',
            """
            (
                All Files (*.*);;
                jpeg (*.jpg *.jpeg);;
                tif (*.tif);;
                gif (*.gif);;
                bmp (*.bmp)            
                )
            """,
            "jpeg (*.jpg *.jpeg)"
            )[0]
        print(self.image_paths)
        self.update_image_list()
        
        
        
    @pyqtSlot()
    def run_output_location(self):
        self.output_directory = QFileDialog.getExistingDirectory(
            self,
            'Select Output Directory',
            ''
            )
        print(self.output_directory)
        self.update_output_path()
       
    
    
    @pyqtSlot()
    def run_make_pdf(self):
        print('making pdf(s)')
       
        
       
    def update_image_list(self):
        self.image_list.clear()
        self.image_dict = {}
        for i in self.image_paths:
            self.image_list.addItem(os.path.basename(i))
            self.image_dict[os.path.basename(i)] = {
                'path':i,
                'size_x':0,
                'size_y':0,
                'crop':(0,0,0,0),
                'rot':0,
                'flip-v':0,
                'flip-h':0,
                'orientation':'Portrait',
                'filename':os.path.splitext(os.path.basename(i))[0]
                }
        self.image_list.setCurrentRow(0)
        
        
            
        
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
    MW.show()
    sys.exit(MW.app.exec_())
if __name__ == '__main__':
    main()