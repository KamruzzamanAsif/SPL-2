import json
from Frontend.Teacher_UI import ui_add_lesson, ui_sound_recorder
from Backend.VideoPlayer.videoPlayer import VideoPlayer
from Frontend.src.Document_Formatter import *
from Backend.lesson_db import lesson_data as ld
from Backend.MediaRecorder import audioRecorder
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from moviepy.editor import VideoFileClip
import os, shutil


class Lesson_Window(QMainWindow):  # Home extends QMainWindow

    def __init__(self, ui_object):
        super(QMainWindow, self).__init__()
        
        # TODO: Video should be added flawlessly

        # window
        self.lesson_window = ui_object
        self.form = None

        # widgets
        self.media_file_name = None
        self.media_file_location = None
        self.category_id = 0
        self.lesson_id = 0
        self.lesson_topic = None
        self.audio_name = None
        self.audio_location = None
        self.folder_name = None
        self.content = None
        self.lesson_elements = ld().load_table()
        self.current_category = None 

        # dictionary
        self.categories = {
            1: 'নাম_শিখন(Noun)',
            2: 'ক্রিয়া_শিখন(Verb)',
            3: 'সম্পর্ক_শিখন(Association)',
            4: 'কর্মধারা_শিখন(Activity)'
        }

        os.path.exists('Lessons') or os.mkdir('Lessons')
        self.videoFormat = ['mp4', 'avi', 'mkv', 'flv', 'wmv', 'mov', '3gp', 'webm']
        
        
        self.load_lessons()

    def create_lesson(self):
        
        print("lesson creation")
        
        # load & set up the Add Lesson Page
        # TODO: Audio file name should be shown in the sub window
        custom_form = QWidget()
        self.form = ui_add_lesson.Ui_Form()
        self.form.setupUi(custom_form)
        # custom_form.setWindowModality(Qt.ApplicationModal)
        custom_form.show()

        # set window icon and title
        custom_form.setWindowIcon(QIcon("../Teacher/Frontend/Images/primary_logo.png"))
        custom_form.setWindowTitle("নতুন লেসন তৈরি করুন")

        # connect buttons
        self.form.btn_select_photo.clicked.connect(self.manage_media)
        self.form.btn_select_audio.clicked.connect(self.manage_audio)
        self.form.btn_record_audio.clicked.connect(self.record_audio)
        self.form.btn_submit.clicked.connect(lambda: self.save_lesson_content(custom_form))

    def manage_media(self):
           
        # open file dialog box
        self.media_file_location = QFileDialog.getOpenFileName(self, "Open File")[0]

        # check file is correctly located or not
        if self.media_file_location is None:
            # TODO: Show warning box
            print("No Image Selected")
            return
        
        # check file format
        file_format = self.media_file_location.split('.')[-1]
        
        if file_format in self.videoFormat:
            
            # navigate to video page
            self.lesson_window.mediaStackWidget.setCurrentWidget(self.lesson_window.video_page)
            self.lesson_window.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

            # get and set image name
            self.media_file_name = self.media_file_location.split('/')[-1]
            self.form.lbl_photo_name.setText(self.media_file_name)
            
            # TODO: VIDEO PLAYER
            self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)                    
            self.lesson_window.video_window = QVideoWidget()                    
            self.mediaPlayer.setVideoOutput(self.lesson_window.video_window) 
                
            self.mediaPlayer.setMedia(QMediaContent(QUrl(self.media_file_location)))
            self.lesson_window.playBtn.setEnabled(True)
                
            self.lesson_window.playBtn.clicked.connect(lambda: self.play_video(self.mediaPlayer))
            
            
        else:
            self.lesson_window.mediaStackWidget.setCurrentWidget(self.lesson_window.image_page)

            # TODO: Currently we're resizing the image to fit the frame
            # But our plane is to resize the frame so that any image fit according to it's size
            self.qtimg = QPixmap(self.media_file_location)
            self.qtimg = self.qtimg.scaledToHeight(700, Qt.SmoothTransformation)
            self.lesson_window.lsn_lbl_lesson_image.setPixmap(self.qtimg)
            
            # get and set image name
            self.media_file_name = self.media_file_location.split('/')[-1]
            self.form.lbl_photo_name.setText(self.media_file_name)

    def manage_audio(self):

        # open file dialog box
        openFile = QFileDialog()
        self.audio_location = openFile.getOpenFileName()[0]
        self.audio_name = self.audio_location.split('/')[-1]

        # check file is correctly located or not
        if self.audio_location is None:
            # TODO: Show warning box
            print("No Audio Selected")
            return

    def record_audio(self):
    
        # load & set up the Add Lesson Page
        custom_form = QWidget()
        self.audio_form = ui_sound_recorder.Ui_audioRecorderWidget()
        self.audio_form.setupUi(custom_form)

        custom_form.show()

        # set window icon and title
        custom_form.setWindowIcon(QIcon("../Teacher/Frontend/Images/primary_logo.png"))
        custom_form.setWindowTitle("অডিও রেকর্ড করুন")

        # before start recording
        self.audio_form.stopButton.setEnabled(False)
        self.audio_form.soundingButton.setEnabled(False)
        self.audio_form.recordingTime.setText("00:00:00")
        self.audio_form.recordingTime.setAlignment(Qt.AlignCenter)
        # Set the initial time to 0
        self.time = QTime(0, 0, 0)
        # Create a timer that updates every second
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)

        # now record the audio
        recorder = audioRecorder.AudioRecorder()
        self.audio_form.startButton.clicked.connect(lambda: self.start_recording(recorder))
        self.audio_form.stopButton.clicked.connect(lambda: self.stop_recording(recorder))

        # close the audio form
        self.audio_form.saveButton.clicked.connect(lambda: self.save_audio(custom_form))

    def start_recording(self, recorder):
        # start recording
        self.audio_form.stopButton.setEnabled(True)
        self.audio_form.soundingButton.setEnabled(True)
        self.audio_form.startButton.setStyleSheet("background-color:  rgb(255, 131, 139); border-radius: 50px;")
        recorder.start_recording()
        # Start the timer
        self.time = QTime(0, 0, 0)
        self.timer.start()

    def stop_recording(self, recorder):
        # stop recording
        self.audio_form.stopButton.setEnabled(False)
        self.audio_form.soundingButton.setEnabled(False)
        self.audio_form.startButton.setStyleSheet("border-radius: 50px; border: 3px solid rgb(206, 95, 95)")
        recorder.stop_recording()
        # Stop the timer
        self.timer.stop()

    def update_timer(self):
        # Increment the time by one second
        self.time = self.time.addSecs(1)

        # Update the label with the new time
        self.audio_form.recordingTime.setText(self.time.toString("hh:mm:ss"))

    def save_audio(self, form):
        audio_fileName = self.audio_form.fileName.text()
        
        print(audio_fileName)
        ## TODO: audio file backend er location a save ache
        ## eitake ekhn kothay save kore rakhbi korte paros
        ## backend er folder theke copy kore niye lesson er folder a o rakhte paros
        self.audio_location = 'Backend/MediaRecorder/audio.wav'
        self.audio_name = self.audio_location.split('/')[-1]
        
        form.close()
        
    def save_lesson_content(self, childObj):
        """
            This function saves the lesson content to the database.
        """

        # TODO: Backend need to be connected
        # get & set lesson content name
        self.lesson_topic = self.form.edit_lesson_topic.text()
        self.lesson_window.lsn_lbl_lesson_topic.setText(self.lesson_topic)

        # get & set category
        self.category_id = self.form.cmb_category.currentIndex()
        self.lesson_window.lsn_cmb_category.setCurrentIndex(self.category_id)

        # get lesson id
        self.lesson_id = self.form.edit_lesson_id.text()
        self.lesson_window.lsn_cmb_lessons.addItem(self.lesson_id)

        # make a folder
        self.folder_name = self.categories[self.category_id] + '_পাঠ_' + self.lesson_id
        self.folder_location = 'Lessons/' + self.folder_name
        if os.path.exists(self.folder_location) == False:
            os.mkdir(self.folder_location)

        # copy the files
        self.content = {
            "category_id": self.category_id,
            "lesson_id": self.lesson_id,
            "lesson_topic": self.lesson_topic
        }
        with open(self.folder_location + '/' + 'content.json', 'w+') as fp:
            json.dump(self.content, fp)

        # copy the image
        # TODO: Show warning if any box of add lesson window is empty
        shutil.copy2(self.media_file_location, self.folder_location + '/' + 'media.' + self.media_file_name.split('.')[1])
        shutil.copy2(self.audio_location, self.folder_location + '/' + 'audio.' + self.audio_name.split('.')[1])
        self.media_file_location = self.folder_location + '/' + 'media.' + self.media_file_name.split('.')[1]
        self.audio_location = self.folder_location + '/' + 'audio.' + self.audio_name.split('.')[1]

        # save the data to the database
        # TODO: Show warning while adding duplicate data
        data = [self.category_id, self.lesson_id, self.lesson_topic, self.media_file_location, self.audio_location]
        ld().add_entry(data)

        childObj.hide()        

    def load_lessons(self):
        
        tmp_lsn_id = set()
               
        # add the lessons to the lesson window
        for element in self.lesson_elements:
            
            print(element)
            
            # extract the content
            cat_id, lsn_id, lsn_topic, media_loc, aud_loc = element 
            tmp_lsn_id.add(str(lsn_id))
            
        self.lesson_window.lsn_cmb_lessons.addItems(sorted(tmp_lsn_id))
            
    def on_category_changed(self, index):
        
        self.current_category = str(index)
        print("Current Category: ", self.current_category)
        
        self.lesson_window.lsn_cmb_lessons.setCurrentIndex(0)
        
    def on_lesson_changed(self, index):
        
        current_lesson = self.lesson_window.lsn_cmb_lessons.itemText(index)
        print("Current Lesson: ", current_lesson)
        
        # add the lessons to the lesson window
        for element in self.lesson_elements:
            
            print(element)
            
            # extract the content
            cat_id, db_lesson, lsn_topic, media_loc, aud_loc = element
            
            print(db_lesson, 'Type: ', type(db_lesson))
            
            if current_lesson == str(db_lesson) and self.current_category == str(cat_id):
                
                print("inside")
                
                # add the content to the lesson window
                self.lesson_window.lsn_cmb_lessons.setCurrentText(str(db_lesson))
                self.lesson_window.lsn_cmb_category.setCurrentText(str(cat_id))
                self.lesson_window.lsn_lbl_lesson_topic.setText(lsn_topic)
                
                file_extension = media_loc.split('.')[-1]
                if file_extension in self.videoFormat:
                    
                    vp = VideoPlayer(self.lesson_window, self.media_file_name)
                    
                    self.lesson_window.mediaStackWidget.setCurrentWidget(self.lesson_window.video_page)
                    
                    self.mediaPlayer = QMediaPlayer()                    
                    self.lesson_window.video_window = QVideoWidget()                    
                    self.mediaPlayer.setVideoOutput(self.lesson_window.video_window) 
                     
                    self.mediaPlayer.setMedia(QMediaContent(QUrl(media_loc)))
                    self.lesson_window.playBtn.setEnabled(True)
                        
                    self.lesson_window.playBtn.clicked.connect(lambda: self.play_video(self.mediaPlayer))

                    # self.mediaPlayer.positionChanged.connect(vp.position_changed)
                    # self.mediaPlayer.durationChanged.connect(vp.duration_changed)
                    # self.mediaPlayer.volumeChanged.connect(vp.volume_changed)
                    # self.mediaPlayer.setVolume(50)

                    # self.lesson_window.volume_Slider.sliderMoved.connect(vp.set_volume)
                    # self.lesson_window.horizontalSlider.sliderMoved.connect(vp.set_position)
                
                else:
                    self.lesson_window.mediaStackWidget.setCurrentWidget(self.lesson_window.image_page)
                    
                    print('IMG LOC: ', media_loc	)
                    self.qtimg = QPixmap(media_loc)
                    self.qtimg = self.qtimg.scaledToHeight(700, Qt.SmoothTransformation)
                    self.lesson_window.lsn_lbl_lesson_image.setPixmap(self.qtimg)
                
    def play_video(self, media_player):
        
        print("play video")
        
        if media_player.state() == QMediaPlayer.PlayingState:
            media_player.pause()
            self.lesson_window.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.lesson_window.playBtn.setText("Pause")

        else:
            media_player.play()
            self.lesson_window.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.lesson_window.playBtn.setText("Play")
                    