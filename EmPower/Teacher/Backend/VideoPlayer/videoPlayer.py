import sys
import time
from datetime import datetime

from moviepy.editor import VideoFileClip
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *


def get_duration(fileName):
    clip = VideoFileClip(fileName)
    duration = clip.duration
    t = time.strftime("%H:%M:%S", time.gmtime(duration))
    print(t)
    return t


class VideoPlayer(QWidget):
    
    def __init__(self, ui_obj, filename):
        super(QWidget, self).__init__()

        # # load ui
        self.ui = ui_obj
        self.fileName = filename
        self.ui.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        
        # # video player settings
        self.mediaPlayer = QMediaPlayer()
        self.ui.video_window = QVideoWidget()
        self.mediaPlayer.setVideoOutput(self.ui.video_window)   
        
        print(self.fileName)

        if self.fileName != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl(self.fileName)))
            self.ui.playBtn.setEnabled(True)    

        # # function call
        self.ui.openfile.clicked.connect(self.openfile)
        self.ui.playBtn.clicked.connect(self.play_video)

        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.volumeChanged.connect(self.volume_changed)
        self.mediaPlayer.setVolume(50)

        self.ui.volume_Slider.sliderMoved.connect(self.set_volume)
        self.ui.horizontalSlider.sliderMoved.connect(self.set_position)

    def openfile(self):

        fileName = QFileDialog.getOpenFileName(self, "Open Video")[0]
        print(fileName)

        if fileName != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl(fileName)))
            self.ui.playBtn.setEnabled(True)

        print(self.mediaPlayer.duration())
        print(self.mediaPlayer.volume())

    def play_video(self):
        
        print("play video")
        
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.ui.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            # self.ui.playBtn.setText("Pause")

        else:
            self.mediaPlayer.play()
            self.ui.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            # self.ui.playBtn.setText("Play")

    def position_changed(self, position):
        self.ui.horizontalSlider.setValue(position)

    def duration_changed(self, duration):
        self.ui.horizontalSlider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def volume_changed(self, volume):
        self.ui.volume_Slider.setValue(volume)

    def set_volume(self, volume):
        self.mediaPlayer.setVolume(volume)


if __name__ == '__main__':
    app = QApplication([])
    window = VideoPlayer()
    window.show()
    sys.exit(app.exec_())
