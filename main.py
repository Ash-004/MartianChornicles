import sys
import os
import requests
import threading
from PyQt5 import QtGui,uic,QtCore,QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import smtplib, ssl
import resources

class MainWindow(QMainWindow):
    
    def __init__(self):

        super(MainWindow,self).__init__()
        uic.loadUi("martiangui.ui",self)
        self.show()
        

        self.file_list= None
        self.filecounter = 0
        
        self.filenames=[]
        
        self.rover = None
        self.cam = None
        self.calendarWidget.hide()
        self.earth_date_label.hide()
        self.current_folder = ""
        
        
        closeicon = QtGui.QIcon(":/icons/close.png")
        minicon = QtGui.QIcon(":/icons/minimize-sign.png")
        maxicon = QtGui.QIcon(":/icons/maximize.png")
        rovericon = QtGui.QIcon(":/icons/rover.png")
        webicon = QtGui.QIcon(":/icons/web.png")
        imgicon = QtGui.QIcon(":/icons/gallery.png")
        mailicon = QtGui.QIcon(":/icons/mail.png")

        self.close_button.setIcon(closeicon)
        self.maximise_button.setIcon(maxicon)
        self.minimize_button.setIcon(minicon)
        self.menu_button.setIcon(rovericon)
        self.fetch_web_button.setIcon(webicon)
        self.image_view_button.setIcon(imgicon)
        self.image_view_button.setIcon(imgicon)
        self.mail_button.setIcon(mailicon)

        self.current_file = "imgs/default.jpg"
        pixmap = QtGui.QPixmap(self.current_file)
        pixmap = pixmap.scaled(self.image_view_label.width(), self.image_view_label.height())
        self.image_view_label.setPixmap(pixmap)
        self.image_view_label.resize(self.width(), self.height())
        
        
        self.fetch_web_button.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.fetch_page))
        self.image_view_button.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.img_viewpage))
        self.image_view_button.clicked.connect(self.open_directory)
        self.mail_button.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.mail_page))
        self.add_image_button.clicked.connect(self.attach)
        self.add_image_button.clicked.connect(self.attachmentview)
        

        self.fetch_button.clicked.connect(self.fetch)
        self.next_image_button.clicked.connect(self.next_img)
        self.prev_image_button.clicked.connect(self.prev_img)
        
        def on_date_changed(date):
            self.selecteddate = self.calendarWidget.selectedDate().toPyDate()
        self.calendarWidget.clicked.connect(on_date_changed)

        self.mailbody = str(self.body_line)

        self.send_mail_button.clicked.connect(self.mail)
        
        
        def rover_handle_rb_toggled():
            if self.curiosity_radio.isChecked():
                self.rover = 'curiosity'
                self.l_date = QDate(2012, 8, 6)
                self.calendarWidget.setMinimumDate(self.l_date)

            elif self.spirit_radio.isChecked():
                self.rover = 'spirit'
                self.l_date = QDate(2004, 1, 4)
                self.m_date = QDate(2010, 3, 21)
                self.calendarWidget.setDateRange(self.l_date, self.m_date)
            elif self.opportunity_radio.isChecked():
                self.rover = 'opportunity'
                self.l_date = QDate(2004, 1, 25)
                self.m_date = QDate(2018, 6, 11)
                self.calendarWidget.setDateRange(self.l_date, self.m_date)

        
        
        def cam_handle_rb_toggled():
            if self.fhaz_radio.isChecked():
                self.cam = 'fhaz'
            elif self.rhaz_radio.isChecked():
                self.cam = 'rhaz'
            elif self.navcam_radio.isChecked():
                self.cam = 'navcam'
            elif self.pandcam_radio.isChecked():
                self.cam = 'pancam'
                
                
        def calendarshow():
            if self.no_butt.isChecked():
                self.calendarWidget.show()
                self.earth_date_label.show()
                self.notlatest = True
            if self.yes_butt.isChecked():
                self.calendarWidget.hide()
                self.earth_date_label.hide()
                self.notlatest = False
                
        self.no_butt.toggled.connect(calendarshow)
        self.yes_butt.toggled.connect(calendarshow)
        self.curiosity_radio.toggled.connect(rover_handle_rb_toggled)
        self.spirit_radio.toggled.connect(rover_handle_rb_toggled)
        self.opportunity_radio.toggled.connect(rover_handle_rb_toggled)
        
        self.fhaz_radio.toggled.connect(cam_handle_rb_toggled)
        self.rhaz_radio.toggled.connect(cam_handle_rb_toggled)
        self.pandcam_radio.toggled.connect(cam_handle_rb_toggled)
        self.navcam_radio.toggled.connect(cam_handle_rb_toggled)

    def attachmentview(self):
        self.imagenames = [f[-10:] for f in self.filenames]
        self.attachments.setText('\n'.join(self.imagenames))
    def attach(self):
        options = QFileDialog.Options()
        self.filenames, _ = QFileDialog.getOpenFileNames(self,"Open images","","Images (*.jpg)",options=options)

                                                    
    def fetch(self):
        thread = threading.Thread(target=self.fetch_images)
        thread.start()
        
    def mail(self):
        thread2 = threading.Thread(target=self.send_email)
        thread2.start()


    def fldr_mk(self):
        now = datetime.now()
        os.makedirs(f"imgs/{now}")
        self.current_folder = f"imgs/{now}"
        
    def fetch_images(self):
        if self.notlatest:
            r = requests.get(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{self.rover}/photos?camera={self.cam}&earth_date={self.selecteddate}&api_key=YDwPCOW5SoD01sO7BXAfoOfl53TkHqdnKzvpFNbU")
        else:
            r = requests.get(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{self.rover}/latest_photos?camera={self.cam}&api_key=YDwPCOW5SoD01sO7BXAfoOfl53TkHqdnKzvpFNbU")

        print(f"https://api.nasa.gov/mars-photos/api/v1/rovers/{self.rover}/photos?camera={self.cam}&api_key=YDwPCOW5SoD01sO7BXAfoOfl53TkHqdnKzvpFNbU")
        re = r.json()
        j=0
        
        
        self.fldr_mk()
        for key in ['photos', 'latest_photos']:
            if key in re:
                for i in re[key]:
                    imag = i['img_src']
                    ImgRequest = requests.get(f"{imag}")
                    img = open(f"{self.current_folder}/image{j}.jpg","wb")
                    img.write(ImgRequest.content)
                    img.close()
                    print("done")
                    j+=1
                print("DONE")


    def open_directory(self):
        if self.current_folder == "":
            self.attach()
            self.file_list = self.filenames
            self.filecounter = len(self.filenames)
            try:
                self.current_file = self.file_list[self.filecounter]
            except IndexError:
                pass
            print('opening')
            pixmap = QtGui.QPixmap(self.current_file)
            pixmap = pixmap.scaled(self.image_view_label.width(),self.image_view_label.height())
            self.image_view_label.setPixmap(pixmap)

        else:
            self.file_list = [self.current_folder + "/" + f for f in os.listdir(self.current_folder) if f.endswith(".jpg")]
            self.filecounter = 0
            self.current_file = self.file_list[self.filecounter]
            print('opening')
            pixmap = QtGui.QPixmap(self.current_file)
            pixmap = pixmap.scaled(self.image_view_label.width(),self.image_view_label.height())
            self.image_view_label.setPixmap(pixmap)
            self.image_view_label.resize(self.width(), self.height())

        
    
    def next_img(self):
        self.filecounter = (self.filecounter + 1) % len(self.file_list)
        self.current_file = self.file_list[self.filecounter]
        pixmap = QtGui.QPixmap(self.current_file)
        pixmap = pixmap.scaled(self.image_view_label.width(), self.image_view_label.height())
        self.image_view_label.setPixmap(pixmap)
        self.image_view_label.resize(self.width(), self.height())
            
            

    def prev_img(self):
        if self.filecounter != 0:
            self.filecounter -= 1
            self.filecounter = (self.filecounter + len(self.file_list)) % len(self.file_list)
            self.current_file = self.file_list[self.filecounter]
            pixmap = QtGui.QPixmap(self.current_file)
            pixmap = pixmap.scaled(self.image_view_label.width(), self.image_view_label.height())
            self.image_view_label.setPixmap(pixmap)
            self.image_view_label.resize(self.width(), self.height())
        else:
            
            self.counter = len(self.file_list)
            self.filecounter -= 1
            self.filecounter = (self.filecounter + len(self.file_list)) % len(self.file_list)
            self.current_file = self.file_list[self.filecounter]
            pixmap = QtGui.QPixmap(self.current_file)
            pixmap = pixmap.scaled(self.image_view_label.width(), self.image_view_label.height())
            self.image_view_label.setPixmap(pixmap)
            self.image_view_label.resize(self.width(), self.height())

            
    
            
            
    def resizeEvent(self,event):
        try:
            pixmap = QtGui.QPixmap(self.current_file)
        except:
            pixmap = QtGui.QPixmap("imgs/default.jpg")

        pixmap = pixmap.scaled(self.image_view_label.width(), self.image_view_label.height())
        self.image_view_label.setPixmap(pixmap)
        # self.image_view_label.resize(self.width(), self.height())


    def send_email(self):

        self.to = self.to_line.text()
        self.subject = self.subject_line.text()
        
        msg = MIMEMultipart()
        msg['From'] = "martianchroniclesmail@gmail.com"
        msg['To'] = self.to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = self.subject
 
        msg.attach(MIMEText(self.body_line.toPlainText()))

        for file in self.filenames:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(file, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=file)
            msg.attach(part)

        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "martianchroniclesmail@gmail.com"

        context = ssl.create_default_context()


        try:
            server = smtplib.SMTP(smtp_server,port)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login("martianchroniclesmail@gmail.com", "ehzqmiguuuartxvu")
            server.sendmail(msg['From'], self.to, msg.as_string())
            print(msg['From'], msg["To"], msg.as_string())
            server.close()
            QMessageBox.information(self, "Information", "Email sent Whooo!!.")
        except Exception as e:
            print(e)
        
    
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
    # window.setWindowFlag(QtCore.Qt.MaximizeButtonHint, False)
    # window.setWindowFlag(QtCore.Qt.MinimizeButtonHint, False)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()