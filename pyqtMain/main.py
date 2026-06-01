# -*- coding: utf-8 -*-

import os
import sys
import random
import cgitb

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

from common_init import *
from config import config
import utils
from webHd import webHandleObj
from dataHd import dataHandleObj
import resource
from wxHd import wxHandle
from deepHd import deepHandle
from ui_style import apply_app_style

sys.utils = utils


class MainWindow(QMainWindow, wxHandle, deepHandle):
    finish = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        utils.info("---" + utils.getNowTime() + " 打开应用---")
        self.finish.connect(self.rcvWxMsgOver)

        self.wxRoleDic = {}
        self.wxAllDic = {}
        self.wxMsgDic = {}
        self.inHandleWx = True
        self.canUseWx = False
        self.myWxMsg = None
        self.onUpdateOneTime = 0
        self.cpOne = 0.99
        self.lastSendTime = -1
        self.openOver = False
        self.needRcd = False
        self.inQieHuan = False
        self.hasLogin = True
        self.delayCallArrays = []
        self.sendWxId = ""

        self.setupUi(self)
        GM["mainScene"] = self
        self.initDatas()
        self.replayClean()
        self.openTimer()
        webHandleObj.startThread()
        self.wxHdInit()
        self.openOver = True

    def initDatas(self):
        self.initWindowName()
        self.setWindowIcon(QIcon(":/logo.ico"))
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if len(desktop) > 7:
            GM["zhuoMian"] = desktop
        self.initUi()
        self.deepInit()

    def initWindowName(self):
        self.setWindowTitle(config["softName"] + " V." + str(GM["version"]))

    def initUi(self):
        apply_app_style(self)
        self.setFixedWidth(750)
        self.rcdHeight = 700

        dataHandleObj.readConfig("main")
        if "machine" not in config["main"]:
            config["main"]["machine"] = "mckeyCreater" + str(random.randint(1000000, 9000000))
        if "rcday" in config["main"]:
            now = utils.getNow().timestamp()
            if config["main"]["rcday"] > now:
                config["main"]["rcday"] = now
        else:
            config["main"]["rcday"] = 1108483200

        dataHandleObj.readConfig("more")
        self.ckbx_2_waitSd.setChecked(config["more"]["waitSd"] == 1)
        self.ledt_2_wTime.setText(str(config["more"]["wTime"]))
        utils.extendLedt(self.ledt_2_wTime, "wTime")
        self.ledt_2_wTime.textChaned = self.saveMore
        self.ledt_2_lsTime.setText(str(config["more"]["lsTime"]))
        utils.extendLedt(self.ledt_2_lsTime, "lsTime")
        self.ledt_2_lsTime.textChaned = self.saveMore
        self.ckbx_2_waitSd.stateChanged.connect(self.makePg1Record1)

        dataHandleObj.readConfig("set_1")
        self.initHookModeUi()
        self.needRcd = True

        self.tabWidget.setCurrentIndex(0)
        for w in (getattr(self, "lb_1_8", None), getattr(self, "lb_1_9", None)):
            if w is not None:
                w.hide()

    def saveMore(self, mQLineEdit, nowStr):
        isNum, turnNum = utils.isNumber(nowStr)
        if isNum:
            intNum = int(turnNum)
            nowStr = str(intNum)
            mQLineEdit.setText(nowStr)
            config["more"][mQLineEdit.useKey] = intNum
            mQLineEdit.befStr = nowStr
            dataHandleObj.updateConfig("more", config["more"])
        else:
            mQLineEdit.setText(mQLineEdit.befStr)

    def makePg1Record1(self):
        if not self.needRcd:
            return
        config["more"]["waitSd"] = 1 if self.ckbx_2_waitSd.isChecked() else 0
        config["more"]["wTime"] = int(self.ledt_2_wTime.displayText())
        config["more"]["lsTime"] = int(self.ledt_2_lsTime.displayText())
        dataHandleObj.updateConfig("more", config["more"])

    def makeAllRecord(self):
        if self.needRcd:
            self.makePg1Record1()

    def replayClean(self):
        self.json_dict1 = None
        self.json_dict2 = None
        self.json_dict3 = None
        self.json_dict4 = None
        self.wxMsgDic = {}
        self.inHandleWx = True
        self.sendWxId = ""

    def rcvWxMsgOver(self):
        try:
            for attr in ("json_dict1", "json_dict2", "json_dict3", "json_dict4"):
                msg = getattr(self, attr, None)
                if msg:
                    self.handleWxMsg(msg)
                    setattr(self, attr, None)
        except Exception as e:
            pass
        

    def closeEvent(self, event):
        if not self.openOver:
            return
        try:
            self.save_deep_history()
        except Exception:
            pass
        GM["onClose"] = True
        try:
            webHandleObj.closeThread()
            self.makeAllRecord()
            self.closeMust()
        except Exception as e:
            print("close.err", e)
        event.accept()

    def closeMust(self):
        webHandleObj.closeThread()
        if "openLog" in GM:
            utils.info("---关闭应用---" + utils.getNowTime())
            GM["openLog"].close()

    def openTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onUpdate)
        self.timer.start(GM["dt"] * 1000)
        self.onUpdate()

    def onUpdate(self):
        dt = GM["dt"]
        self.onUpdateOneTime += dt
        GM["updateAllTime"] += dt
        self.callDelay(dt)

    def pushDelay(self, dalayTime, func):
        if dalayTime:
            self.delayCallArrays.append({
                "dalayTime": dalayTime,
                "nowTime": 0,
                "func": func,
            })

    def callDelay(self, dt):
        if not self.delayCallArrays:
            return
        for x in range(len(self.delayCallArrays) - 1, -1, -1):
            task = self.delayCallArrays[x]
            task["nowTime"] += dt
            if task["nowTime"] >= task["dalayTime"]:
                task["func"]()
                self.delayCallArrays.pop(x)


def main():
    path_logs = os.path.join(CUR_DIR, "logs")
    if "deepWeChat" in CUR_DIR:
        cgitb.enable(format="text", logdir=path_logs)

    app = QApplication(sys.argv)
    dlg = MainWindow()
    GM["the_main"] = dlg
    dlg.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
