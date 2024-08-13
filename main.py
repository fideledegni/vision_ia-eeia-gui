import os
import random
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication, QAction,
    QCheckBox, QComboBox, QFileDialog, QLabel, QMainWindow, QMessageBox, QPushButton, QRadioButton,
    QStyle, QWidget,
    QHBoxLayout, QVBoxLayout
)
from PyQt5.QtGui import QCursor, QIcon, QImage, QPixmap
import cv2
from config import CAMERA_SOURCE, CONFIG_INI_PATH, DEFAULT_CAMERA, DEFAULT_FPS, ICON_PATH, STYLE_PATH

VIDEO_FILES_FILTER = "Vidéos (*.mp4 *.avi *.mkv)"

DETECT_OFF_IDX = 0
DETECT_ALL_IDX = 1
DETECT_ZEM_IDX = 2

CAMERA_TEXT = 'Flux vidéo caméra externe'
WEBCAM_TEXT = 'Flux vidéo webcam'
LOCAL_FILE_TEXT = 'Fichier vidéo du PC'

APP_TITLE = "EEIA 2024 - Projets Vision/IA"



class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(150, 50, 1000, 700)
        self.showMaximized() # full screen

        self.model_index = DETECT_OFF_IDX
        self.is_playing = True
        self.fps = DEFAULT_FPS
        self.zems_number = 0

        self.setup_menu()
        self.initialize_ui()

        self.cap: cv2.VideoCapture|None = None
        # Grab frames periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000/DEFAULT_FPS))
    
    def update_fps(self, fps: int):
        # print("Will update fps with value:", fps)
        self.timer.start(int(1000/fps))

    
    def setup_menu(self):
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        menu_bar.setVisible(True)

        camera = QAction(CAMERA_TEXT, self)
        camera.setShortcut('Ctrl+E')
        camera.triggered.connect(self.open_camera)

        webcam = QAction(WEBCAM_TEXT, self)
        webcam.setShortcut('Ctrl+W')
        webcam.triggered.connect(self.open_webcam)

        local_file = QAction(LOCAL_FILE_TEXT, self)
        local_file.setShortcut('Ctrl+O')
        local_file.triggered.connect(self.open_video_file)

        source_menu = menu_bar.addMenu('Sources')
        source_menu.addAction(camera)
        source_menu.addAction(webcam)
        source_menu.addAction(local_file)
    

    def initialize_ui(self):
        widget = QWidget()
        self.main_v_layout = QVBoxLayout()
        self.tool_bar = QHBoxLayout()
        self.bottom_bar = QHBoxLayout()
        
        self.source_label = QLabel()
        self.source_label.setStyleSheet("background-color:#beffae00;font-size:14px;font-weight:bold;")
        self.source_label.setVisible(False)

        self.zems_number_label = QLabel("Nombre de Zémidjans: ")
        self.zems_number_label.setStyleSheet("background-color:#beffae00;font-size:12px;font-weight:bold;")
        self.zems_number_label.setVisible(False)

        self.model_selector = QComboBox()
        self.model_selector.addItems(["Rien", "Tous les engins", "Les Zémidjans"])

        self.count_zems_check = QCheckBox("Compter les Zémidjans")
        self.count_zems_check.setCursor(QCursor(Qt.PointingHandCursor))

        self.play_pause_btn = QPushButton("Pause")
        self.play_pause_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.play_pause_btn.setShortcut('Ctrl+P')
        self.play_pause_btn.clicked.connect(self.play_pause)
        icon = self.style().standardIcon(getattr(QStyle, "SP_MediaPause"))
        self.play_pause_btn.setIcon(icon)

        self.video_label = QLabel(self)
        self.video_label.setStyleSheet("background-color:lightgray;")

        self.init_fps_choice()

        self.model_label = QLabel("Détecter :")
        self.model_label.setStyleSheet("background-color:#0055ff;color:white;font-size:14px;font-weight:bold;")
        self.tool_bar.addWidget(self.model_label)
        self.tool_bar.addWidget(self.model_selector)
        self.tool_bar.addWidget(self.count_zems_check)
        self.tool_bar.addWidget(self.play_pause_btn)

        self.bottom_bar.addLayout(self.choose_fps)
        self.bottom_bar.addWidget(self.zems_number_label)

        self.main_v_layout.addWidget(self.source_label)
        self.main_v_layout.addLayout(self.tool_bar)
        self.main_v_layout.addWidget(self.video_label, Qt.AlignCenter)
        self.main_v_layout.addLayout(self.bottom_bar)
        
        widget.setLayout(self.main_v_layout)
        self.setCentralWidget(widget)
        self.disable_actions()
    

    def init_fps_choice(self):
        self.choose_fps = QHBoxLayout()
        self.choose_fps.addWidget(QLabel("FPS :"))

        self.fps_btn_5 = QRadioButton("5")
        self.fps_btn_5.toggled.connect(lambda:self.fps_btn_state(self.fps_btn_5))
        self.choose_fps.addWidget(self.fps_btn_5)

        self.fps_btn_15 = QRadioButton("15")
        self.fps_btn_15.toggled.connect(lambda:self.fps_btn_state(self.fps_btn_15))
        self.choose_fps.addWidget(self.fps_btn_15)

        self.fps_btn_def = QRadioButton(f"{DEFAULT_FPS}")
        self.fps_btn_def.setChecked(True)
        self.fps_btn_def.toggled.connect(lambda:self.fps_btn_state(self.fps_btn_def))
        self.choose_fps.addWidget(self.fps_btn_def)

        self.fps_btn_33 = QRadioButton("33")
        self.fps_btn_33.toggled.connect(lambda:self.fps_btn_state(self.fps_btn_33))
        self.choose_fps.addWidget(self.fps_btn_33)

        self.fps_btn_40 = QRadioButton("40")
        self.fps_btn_40.toggled.connect(lambda:self.fps_btn_state(self.fps_btn_40))
        self.choose_fps.addWidget(self.fps_btn_40)


    def fps_btn_state(self, b: QRadioButton):
        if b.isChecked():
            self.fps = int(b.text())
            self.update_fps(self.fps)


    def play_pause(self):
        if self.is_playing:
            self.timer.stop()
            self.play_pause_btn.setText("Play")
            icon = self.style().standardIcon(getattr(QStyle, "SP_MediaPlay"))
            self.play_pause_btn.setIcon(icon)
        else:
            self.update_fps(self.fps)
            self.play_pause_btn.setText("Pause")
            icon = self.style().standardIcon(getattr(QStyle, "SP_MediaPause"))
            self.play_pause_btn.setIcon(icon)
        self.is_playing = not self.is_playing
    

    def disable_actions(self):
        self.model_selector.setEnabled(False)
        self.count_zems_check.setEnabled(False)
        self.play_pause_btn.setEnabled(False)
    
    def enable_actions(self):
        self.model_selector.setEnabled(True)
        self.count_zems_check.setEnabled(True)
        self.play_pause_btn.setEnabled(True)
    

    def update_frame(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # BGR to RGB as OpenCV uses BGR

                model_index = self.model_selector.currentIndex()
                # print("model_index:", model_index)
                if model_index == DETECT_ALL_IDX:
                    frame = self.detect_all(frame)
                elif model_index == DETECT_ZEM_IDX:
                    frame = self.detect_zems(frame)

                height, width, channels = frame.shape
                bytes_per_line = channels * width
                qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))

                if self.count_zems_check.isChecked():
                    self.zems_number = self.count_zems(frame)
                    self.zems_number_label.setText(f"Nombre de Zémidjans: {self.zems_number}")
                    self.zems_number_label.setVisible(True)
                else:
                    self.zems_number_label.setVisible(False)
            else:
                # Stop the timer when the video ends
                self.timer.stop()


    def stop_capture(self):
        if self.cap is not None: self.cap.release()


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quitter', 'Êtes-vous sûr ?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.stop_capture()
            event.accept()
        else:
            event.ignore()


    def open_camera(self):
        self.stop_capture()
        self.cap = cv2.VideoCapture(CAMERA_SOURCE)
        if self.cap is None or not self.cap.isOpened():
            QMessageBox.information(self, "Erreur", f"Impossible d'ouvrir la caméra à la source '{CAMERA_SOURCE}'", QMessageBox.StandardButton.Ok)
        else:
            self.update_frame() # update image from new source even if paused
            self.source_label.setText(CAMERA_TEXT)
            self.source_label.setVisible(True)
            self.enable_actions()
            
    

    def open_webcam(self):
        self.stop_capture()
        self.cap = cv2.VideoCapture(DEFAULT_CAMERA)
        if self.cap is None or not self.cap.isOpened():
            QMessageBox.information(self, "Erreur", f"Impossible d'ouvrir la caméra à la source '{DEFAULT_CAMERA}'", QMessageBox.StandardButton.Ok)
        else:
            self.update_frame() # update image from new source even if paused
            self.source_label.setText(WEBCAM_TEXT)
            self.source_label.setVisible(True)
            self.enable_actions()
    
    
    def open_video_file(self):
        video_path = self.get_video_file()
        if video_path:
            self.video_path = video_path
            self.stop_capture()
            self.cap = cv2.VideoCapture(video_path)
            if self.cap is None or not self.cap.isOpened():
                QMessageBox.information(self, "Erreur", f"Impossible de charger la vidéo '{video_path}'", QMessageBox.StandardButton.Ok)
            else:
                self.update_frame() # update image from new source even if paused
                self.source_label.setText(LOCAL_FILE_TEXT)
                self.source_label.setVisible(True)
                self.enable_actions()
        else:
            QMessageBox.information(self, "Erreur", "Aucune vidéo chargée !", QMessageBox.StandardButton.Ok)


    def get_video_file(self):
        video_dir = self.get_video_dir()
        video_path, _ = QFileDialog.getOpenFileName(self, "Charger une Vidéo", video_dir, VIDEO_FILES_FILTER)
        if video_path:
            new_video_dir = os.path.dirname(video_path) + '/'
            with open(CONFIG_INI_PATH, "w") as config: config.write(new_video_dir)
        return video_path
    
    def get_video_dir(self):
        video_dir = os.getenv('HOME')
        if os.path.isfile(CONFIG_INI_PATH):
            config = open(CONFIG_INI_PATH, "r")
            last_video_dir = config.readline()
            if last_video_dir:
                video_dir = last_video_dir
        return video_dir
    

    def detect_all(self, frame):
        print("Will detect all...")
        self.add_text_to_image(frame, "See all?") # TODO: Call model here
        return frame

    def detect_zems(self, frame):
        print("Will detect zémidjans")
        self.add_text_to_image(frame, "See zem?") # TODO: Call model here
        return frame
    
    def count_zems(self, frame):
        print("Will count zémidjans") # TODO: Call model here
        return random.randint(0,10)
    

    def add_text_to_image(self, frame, text):
        cv2.putText(frame, text, (50, 100), cv2.FONT_ITALIC, 1, (255, 0, 255), 2)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(APP_TITLE)

    dirTranslatorPath = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)
    translator = QtCore.QTranslator()
    translator.load("qtbase_fr.qm", dirTranslatorPath)
    app.installTranslator(translator)

    main = Main()
    main.show()

    with open(STYLE_PATH, "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    
    sys.exit(app.exec_())
