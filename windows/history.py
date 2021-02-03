# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'history.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget


class Ui_Dialog(object):
    NAME, PATH, TYPE, PARAM, TIME = range(5)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1666, 900)
        self.treeView = QtWidgets.QTreeView(Dialog)
        self.treeView.setGeometry(QtCore.QRect(50, 60, 1561, 191))
        self.treeView.setObjectName("treeView")


        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 280, 720, 405))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(890, 280, 720, 405))

        self.wgt_video_1 = QVideoWidget(Dialog)
        self.wgt_video_1.setGeometry(QtCore.QRect(50, 280, 720, 405))
        self.player_1 = QMediaPlayer()
        self.player_1.setVideoOutput(self.wgt_video_1)
        self.wgt_video_1.setObjectName("widget")

        self.wgt_video_2 = QVideoWidget(Dialog)
        self.wgt_video_2.setGeometry(QtCore.QRect(890, 280, 720, 405))
        self.player_2 = QMediaPlayer()
        self.player_2.setVideoOutput(self.wgt_video_2)
        self.wgt_video_2.setObjectName("widget")

        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(50, 710, 1561, 151))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(20, 30, 1521, 111))
        self.label_4.setObjectName("label_4")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(50, 20, 361, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(780, 280, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(780, 320, 51, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(830, 320, 51, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_5 = QtWidgets.QPushButton(Dialog)
        self.pushButton_5.setGeometry(QtCore.QRect(780, 320, 51, 31))
        self.pushButton_5.setObjectName("pushButton_2")
        self.pushButton_6 = QtWidgets.QPushButton(Dialog)
        self.pushButton_6.setGeometry(QtCore.QRect(830, 320, 51, 31))
        self.pushButton_6.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setGeometry(QtCore.QRect(780, 360, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "原始图像"))
        self.label_2.setText(_translate("Dialog", "检测结果"))
        self.groupBox.setTitle(_translate("Dialog", "参数信息"))
        self.label_3.setText(_translate("Dialog", "用户XXX历史检测结果"))
        self.label_4.setText(_translate("Dialog", "准确率：-；召回率：-；学习率：-；训练步数：-；损失：-；参数发行日期：-；"))
        self.pushButton.setText(_translate("Dialog", "删除记录"))
        self.pushButton_2.setText(_translate("Dialog", "放大"))
        self.pushButton_3.setText(_translate("Dialog", "放大"))
        self.pushButton_4.setText(_translate("Dialog", "播放"))
        self.pushButton_5.setText(_translate("Dialog", "放大"))
        self.pushButton_6.setText(_translate("Dialog", "放大"))

    def createHistoryModel(self, parent):
        model = QStandardItemModel(0, 5, parent)
        model.setHeaderData(self.NAME, Qt.Horizontal, "原文件名")
        model.setHeaderData(self.PATH, Qt.Horizontal, "所在路径")
        model.setHeaderData(self.TYPE, Qt.Horizontal, "文件类型")
        model.setHeaderData(self.PARAM, Qt.Horizontal, "参数文件")
        model.setHeaderData(self.TIME, Qt.Horizontal, "检测时间")
        return model

    def add_history(self, model, name, path, type, param, time):
        model.insertRow(0)
        model.setData(model.index(0, self.NAME), name)
        model.setData(model.index(0, self.PATH), path)
        model.setData(model.index(0, self.TYPE), type)
        model.setData(model.index(0, self.PARAM), param)
        model.setData(model.index(0, self.TIME), time)

    def get_param_info(self, ap, ar, lr, epoch, loss, time):
        self.label_4.setText("准确率：%s；召回率：%s；学习率：%s；训练步数：%s；损失：%s；参数发行日期：%s；"
                             % (ap, ar, lr, epoch, loss, time))

