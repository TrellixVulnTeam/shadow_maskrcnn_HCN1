# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'predict_main.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import datetime
import multiprocessing
import requests
import os, sys
import cv2
import torch
import torchvision
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from mxnet import image
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import dialog
import media_choose_dialog
import get_net
import loadARP
from predict_terminal import ARP_predict, rcnn_predict

ARP_MODEL_NAME = 'res34_cbam_parallel'
ARP_PATH = '../param/res34_bcam_parallel_625_0.2043_0.945_9.74.params'
SHADOW_PERCENT = 0.5

NUM_CLASS = 10
DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
RCNN_MODEL = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=False, num_classes=NUM_CLASS)
RCNN_PATH = '../param/model_new_1.pth'
PARAMS = {}
PARAMS['all_file_path'] = []


class msg_dialog(QDialog):
    def __init__(self, msg="正在预测，请勿关闭应用程序！"):
        QDialog.__init__(self)
        self.msg_dialog = dialog.Ui_Dialog()
        self.msg_dialog.setupUi(self, msg)


class media_dialog(QDialog):
    _signal = QtCore.pyqtSignal(str)

    def __init__(self, media_type):
        QDialog.__init__(self)
        self.media_type = media_type
        self.media_dialog = media_choose_dialog.Ui_Dialog()
        self.media_dialog.setupUi(self, media_type)

        self.media_dialog.pushButton_2.clicked.connect(self.locale)
        self.media_dialog.pushButton.clicked.connect(self.online)

    def locale(self):
        if self.media_type == '图片':
            imgName, imgType = QFileDialog.getOpenFileName(QWidget(), "打开图片", "../images",
                                                           "*.png;;*.jpg;;All Files(*)")
            if imgName != '':
                self._signal.emit(imgName)

        elif self.media_type == '视频':
            videoName, videoType = QFileDialog.getOpenFileName(QWidget(), "打开视频", "../videos",
                                                               "*.mp4;;*.avi;;All Files(*)")
            if videoName != '':
                self._signal.emit(videoName)

    def online(self):
        url = self.media_dialog.lineEdit.text()
        if (self.media_type == '图片' and url.endswith(('jpg', 'png'))) \
                or (self.media_type == '视频' and url.endswith(('mp4', 'avi'))) \
                and url.startswith(('http', 'www', 'ftp')):
            self.media_dialog.pushButton_2.setEnabled(False)
            self.media_dialog.pushButton.setText('下载中请稍后...')
            self.media_dialog.pushButton.setEnabled(False)
            self.media_dialog.lineEdit.setEnabled(False)
            self.timer = QTimer()
            self.timer.timeout.connect(lambda: self.download(url))
            self.timer.start(100)
        else:
            self.media_dialog.lineEdit.clear()
            if self.media_type == '图片':
                self.media_dialog.lineEdit.setPlaceholderText('请输入正确的url，确保http//或https//开头，且结尾为.jpg或.png！')
            elif self.media_type == '视频':
                self.media_dialog.lineEdit.setPlaceholderText('请输入正确的url，确保http//或https//开头，且结尾为.mp4或.avi！')

    def download(self, url):
        self.timer.stop()
        file = requests.get(url)
        if self.media_type == '图片':
            media_Name = '../images/' + url.split('/')[-1]
        elif self.media_type == '视频':
            media_Name = '../videos/' + url.split('/')[-1]
        open(media_Name, 'wb').write(file.content)
        self._signal.emit(media_Name)


class Ui_ShadowRCNN(QWidget):
    def setupUi(self, ShadowRCNN):
        ShadowRCNN.setObjectName("ShadowRCNN")
        ShadowRCNN.resize(1600, 900)
        self.centralwidget = QtWidgets.QWidget(ShadowRCNN)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(160, 40, 1280, 720))
        self.label.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label.setStyleSheet("QLabel{background:white;}"
                                 "QLabel{color:rgb(300,300,300,120);font-size:20px;font-weight:bold;}"
                                 )

        self.wgt_video = QVideoWidget(self.centralwidget)
        self.wgt_video.setGeometry(QtCore.QRect(160, 40, 1280, 720))
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.wgt_video)
        self.wgt_video.hide()
        self.wgt_video.setObjectName("widget")

        self.pushButton_play = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_play.setVisible(False)
        self.pushButton_play.setGeometry(QtCore.QRect(1480, 40, 80, 41))
        self.pushButton_play.setObjectName("pushButton")
        self.video_is_play = False
        self.pushButton_play.clicked.connect(self.video_play_change)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(100, 790, 161, 41))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.open_image)

        self.pushButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton1.setGeometry(QtCore.QRect(883, 790, 161, 41))
        self.pushButton1.setObjectName("pushButton")
        self.pushButton1.clicked.connect(self.predict)

        self.pushButton_camera = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_camera.setGeometry(QtCore.QRect(622, 790, 161, 41))
        self.pushButton_camera.setObjectName("pushButton")
        self.pushButton_camera.clicked.connect(self.camera)

        self.check_continue = QtWidgets.QCheckBox(self.centralwidget)
        self.check_continue.setGeometry(QtCore.QRect(622, 825, 100, 41))
        self.check_continue.setObjectName("checkButton")
        self.check_continue.stateChanged.connect(self.continue_camera)

        self.label1 = QtWidgets.QLabel(self.centralwidget)
        self.label1.setGeometry(QtCore.QRect(720, 825, 30, 41))
        self.label1.setObjectName("label")

        self.line_second = QtWidgets.QLineEdit(self.centralwidget)
        self.line_second.setGeometry(QtCore.QRect(752, 834, 20, 20))
        self.line_second.setObjectName("lineEdit")
        self.line_second.setEnabled(False)

        self.label2 = QtWidgets.QLabel(self.centralwidget)
        self.label2.setGeometry(QtCore.QRect(774, 825, 30, 41))
        self.label2.setObjectName("label")

        self.pushButton_video = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_video.setGeometry(QtCore.QRect(361, 790, 161, 41))
        self.pushButton_video.setObjectName("pushButton")
        self.pushButton_video.clicked.connect(self.open_video)

        self.pushButton_delete = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_delete.setGeometry(QtCore.QRect(1144, 790, 161, 41))
        self.pushButton_delete.setObjectName("pushButton")
        self.pushButton_delete.clicked.connect(self.delete)

        self.pushButton_history = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_history.setGeometry(QtCore.QRect(1405, 790, 161, 41))
        self.pushButton_history.setObjectName("pushButton")
        self.pushButton_history.clicked.connect(self.history)

        ShadowRCNN.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ShadowRCNN)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1600, 26))
        self.menubar.setAutoFillBackground(False)
        self.menubar.setObjectName("menubar")
        ShadowRCNN.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ShadowRCNN)
        self.statusbar.setObjectName("statusbar")
        ShadowRCNN.setStatusBar(self.statusbar)

        self.timer = QTimer()
        self.retranslateUi(ShadowRCNN)
        QtCore.QMetaObject.connectSlotsByName(ShadowRCNN)

    def retranslateUi(self, ShadowRCNN):
        _translate = QtCore.QCoreApplication.translate
        ShadowRCNN.setWindowTitle(_translate("ShadowRCNN", "ShadowRCNN"))
        self.label.setText(_translate("ShadowRCNN", "请选择图片"))
        self.pushButton.setText(_translate("ShadowRCNN", "选择图片"))
        self.pushButton1.setText(_translate("ShadowRCNN", "开始预测"))
        self.pushButton_play.setText(_translate("ShadowRCNN", "暂停"))
        self.pushButton_camera.setText(_translate("ShadowRCNN", "拍摄照片"))
        self.pushButton_video.setText(_translate("ShadowRCNN", "选择视频"))
        self.pushButton_delete.setText(_translate("ShadowRCNN", "删除缓存"))
        self.pushButton_history.setText(_translate("ShadowRCNN", "历史信息"))
        self.check_continue.setText(_translate("ShadowRCNN", "连拍模式"))
        self.label1.setText(_translate("ShadowRCNN", "每秒"))
        self.line_second.setText(_translate("ShadowRCNN", "1"))
        self.label2.setText(_translate("ShadowRCNN", "张"))

    def open_image(self):
        self.image_choose_dialog = media_dialog(media_type='图片')
        self.image_choose_dialog.show()
        self.image_choose_dialog._signal.connect(self.get_image)

    def get_image(self, imgName):
        self.label.clear()
        self.player.setMedia(QMediaContent())
        self.wgt_video.hide()
        self.label.show()
        self.pushButton_play.setVisible(False)
        jpg = QtGui.QPixmap(imgName).scaled(self.label.width(), self.label.height())
        if imgName != '':
            self.label.setPixmap(jpg)
            self.statusbar.showMessage('当前图片：' + imgName)
        PARAMS['imgPath'] = imgName
        self.image_choose_dialog.close()

    def ARP_predict(self, mode='image'):
        shadow_write_path, shadow_write_name = os.path.split(PARAMS['imgPath'])
        shadow_write_name = shadow_write_name.split('.')[0] + '_shadow' + '.' + shadow_write_name.split('.')[1]
        self.shadow_write_path = os.path.join(shadow_write_path, shadow_write_name)
        print(self.shadow_write_path)
        if mode == 'image':
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            p = multiprocessing.Process(target=ARP_predict,
                                        args=(return_dict, PARAMS['imgPath'], ARP_MODEL_NAME, ARP_PATH, SHADOW_PERCENT))
            p.start()
            p.join()

            PARAMS['ARP_result'] = return_dict.values()[0]
            cv2.imwrite(self.shadow_write_path, PARAMS['ARP_result'])
            if 'shadow_write_path' not in PARAMS.keys():
                PARAMS['shadow_write_path'] = []
            PARAMS['shadow_write_path'].append(self.shadow_write_path)
            PARAMS['all_file_path'].append(self.shadow_write_path)
        elif mode == 'video':
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            p = multiprocessing.Process(target=ARP_predict,
                                        args=(
                                            return_dict, PARAMS['imgPath'], ARP_MODEL_NAME, ARP_PATH,
                                            SHADOW_PERCENT, 'video', self.shadow_write_path))
            p.start()
            p.join()

            PARAMS['all_file_path'].append(self.shadow_write_path)

    def rcnn_predict(self, mode='image'):
        rcnn_write_path, rcnn_write_name = os.path.split(PARAMS['imgPath'])
        rcnn_write_name = rcnn_write_name.split('.')[0] + '_rcnn' + '.' + rcnn_write_name.split('.')[1]
        self.rcnn_write_path = os.path.join(rcnn_write_path, rcnn_write_name)
        print(self.rcnn_write_path)
        if mode == 'image':
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            p = multiprocessing.Process(target=rcnn_predict,
                                        args=(return_dict, PARAMS['ARP_result'], False, RCNN_PATH))
            p.start()
            p.join()
            PARAMS['RCNN_result'] = return_dict.values()[0]
            if PARAMS['RCNN_result'] is not None:
                cv2.imwrite(self.rcnn_write_path, PARAMS['RCNN_result'])
                if 'rcnn_write_path' not in PARAMS.keys():
                    PARAMS['rcnn_write_path'] = []
                PARAMS['rcnn_write_path'].append(self.rcnn_write_path)
                PARAMS['all_file_path'].append(self.rcnn_write_path)
                jpg = QtGui.QPixmap(self.rcnn_write_path).scaled(self.label.width(), self.label.height())
                self.label.setPixmap(jpg)
        elif mode == 'video':
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            p = multiprocessing.Process(target=rcnn_predict,
                                        args=(return_dict, self.shadow_write_path, False, RCNN_PATH,
                                              'video', self.rcnn_write_path))
            p.start()
            p.join()

            PARAMS['all_file_path'].append(self.rcnn_write_path)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.rcnn_write_path)))
            self.player.play()
            self.video_is_play = True
            self.pushButton_play.setText('暂停')

    def predict(self):
        if 'imgPath' in PARAMS.keys():
            self.msgDialog = msg_dialog()
            self.msgDialog.show()
            self.timer = QTimer()
            self.timer.timeout.connect(self.start_connect)
            self.timer.start(500)
            self.statusbar.showMessage('预测完成')
        else:
            msg = QMessageBox.information(self, '提示', '请先选择图片或视频', QMessageBox.Yes, QMessageBox.Yes)

    def continue_camera(self, state):
        # state 0 没选中 1 选中
        if state == 0:
            self.pushButton_camera.setText('拍摄照片')
            self.line_second.setEnabled(False)
        elif state == 2:
            self.pushButton_camera.setText('开始连拍')
            self.line_second.setEnabled(True)

    def camera(self):
        self.label.clear()
        self.player.setMedia(QMediaContent())
        self.wgt_video.hide()
        self.label.show()
        self.pushButton_play.setVisible(False)
        if self.check_continue.checkState() != QtCore.Qt.Checked:
            self.pushButton_camera.setText('按Q拍照')
            cap = cv2.VideoCapture(0)
            while True:
                ret, frame = cap.read()
                # show a frame
                cv2.imshow("Capture", frame)

                if cv2.waitKey(1) == ord('q'):
                    cap_name = '../images/capimg_' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')) + '.jpg'
                    cv2.imwrite(cap_name, frame)
                    jpg = QtGui.QPixmap(cap_name).scaled(self.label.width(), self.label.height())
                    self.label.setPixmap(jpg)
                    cap.release()  # 释放摄像头
                    cv2.destroyAllWindows()  # 删除建立的全部窗口
                    PARAMS['imgPath'] = cap_name
                    PARAMS['all_file_path'].append(cap_name)
                    self.pushButton_camera.setText('拍摄照片')
                    break

                if cv2.getWindowProperty("Capture", cv2.WND_PROP_AUTOSIZE) < 1:
                    cv2.destroyAllWindows()
                    self.pushButton_camera.setText('拍摄照片')
                    break
        else:
            self.now_continue_num = 0
            self.pushButton_camera.setEnabled(False)
            self.pushButton_camera.setText('正在连拍')
            per_second_photo_num = self.line_second.text()
            self.msgDialog = msg_dialog(msg='准备开始连拍')
            self.cap = cv2.VideoCapture(0)
            self.msgDialog.show()
            self.msgDialog.move(1200, 500)
            self.timer = QTimer()
            self.continue_list = []
            self.timer.timeout.connect(self.start_continue_photo)
            self.timer.start(int(1000 / int(per_second_photo_num)))

    def start_continue_photo(self):
        self.now_continue_num += 1
        self.msgDialog.setWindowTitle('正在连拍')
        self.msgDialog.msg_dialog.label.setText('正在拍摄第 {}/9 张...'.format(self.now_continue_num))
        # 拍照
        ret, frame = self.cap.read()
        # show a frame
        cv2.imshow("Capture", frame)
        image_name = '../images/capimg_' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')) + '.jpg'
        cv2.imwrite(image_name, frame)
        PARAMS['all_file_path'].append(image_name)
        self.continue_list.append(image_name)

        # 结束拍照
        if self.now_continue_num == 9:
            self.timer.stop()
            self.msgDialog.msg_dialog.label.setText('正在处理结果')
            self.pushButton_camera.setText('开始连拍')
            self.pushButton_camera.setEnabled(True)
            self.msgDialog.close()
            cv2.destroyAllWindows()
            self.cap.release()
            # 横向拼接结果
            continue_list_middle = [np.hstack(
                [cv2.imread(self.continue_list[0], 1), cv2.imread(self.continue_list[1], 1),
                 cv2.imread(self.continue_list[2], 1)]), np.hstack(
                [cv2.imread(self.continue_list[3], 1), cv2.imread(self.continue_list[4], 1),
                 cv2.imread(self.continue_list[5], 1)]), np.hstack(
                [cv2.imread(self.continue_list[6], 1), cv2.imread(self.continue_list[7], 1),
                 cv2.imread(self.continue_list[8], 1)])]
            # 纵向拼接
            continue_photo = np.vstack([continue_list_middle[0], continue_list_middle[1], continue_list_middle[2]])
            # 展示结果
            continue_photo_name = '../images/' + self.continue_list[0][:-10] + '_9in1.jpg'
            PARAMS['imgPath'] = continue_photo_name
            PARAMS['all_file_path'].append(continue_photo_name)
            cv2.imwrite(continue_photo_name, continue_photo)
            jpg = QtGui.QPixmap(continue_photo_name).scaled(self.label.width(), self.label.height())
            self.label.setPixmap(jpg)

    def open_video(self):
        self.video_choose_dialog = media_dialog(media_type='视频')
        self.video_choose_dialog.show()
        self.video_choose_dialog._signal.connect(self.get_video)

    def get_video(self, videoName):
        if videoName != '':
            self.label.clear()
            self.player.setMedia(QMediaContent())
            self.wgt_video.show()
            self.label.hide()
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(videoName)))
            self.player.play()
            self.video_is_play = True
            self.pushButton_play.setVisible(True)
            self.statusbar.showMessage('当前视频：' + videoName)
        PARAMS['imgPath'] = videoName
        self.video_choose_dialog.close()

    def video_play_change(self):
        self.video_is_play = bool(1 - self.video_is_play)
        if self.video_is_play:
            self.player.play()
            self.pushButton_play.setText('暂停')
        else:
            self.player.pause()
            self.pushButton_play.setText('播放')

    def delete(self):
        self.label.clear()
        self.player.setMedia(QMediaContent())
        file_num = 0
        for file_name in PARAMS['all_file_path']:
            if os.path.exists(file_name):
                os.remove(file_name)
                file_num += 1
        self.statusbar.showMessage('缓存清除成功，共' + str(file_num) + '个文件')

    def history(self):
        print('history')

    def start_connect(self):
        if str(PARAMS['imgPath']).endswith(('png', 'jpg')):
            self.ARP_predict()
            self.rcnn_predict()
        else:
            self.ARP_predict(mode='video')
            self.rcnn_predict(mode='video')

        self.timer.stop()
        self.msgDialog.close()
