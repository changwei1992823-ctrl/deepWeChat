# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from common_init import *

# from Ui_main import Ui_MainWindow

from config import *
import utils
from webHd import webHandleObj
from dataHd import dataHandleObj
import resource


from wxHd import wxHandle
from deepHd import deepHandle
import requests

from functools import partial


import cgitb  # 软件发生错误的报错信息收集
sys.utils = utils

from PyQt5 import QtMultimedia

class MainWindow(QMainWindow, wxHandle, deepHandle):
    finish = pyqtSignal()
    # resized = pyqtSignal()
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        utils.info("---"+utils.getNowTime()+" 打开游戏---")
        self.finish.connect(self.rcvWxMsgOver)
        self.wxRoleDic = {}
        self.wxAllDic = {}

        self.jdQyq = ""
        self.fdQyq = ""
        self.inHandleWx = True
        self.canUseWx = False
        self.myWxMsg = None
        self.touchTime = -1
        self.onUpdateOneTime = 0
        self.cpOne = 0.99
        self.lastSendTime = -1

        self.openOver = False
        self.needRcd = False
        self.inQieHuan = False
        self.needFtp = True
        self.needCkTime = False
        self.hasLogin = True


        self.wxQunTab = []
        self.firstOpen = True  # 关系到统计的内容
        self.setMsg = ""
        self.setupUi(self)
        GM["mainScene"] = self
        self.initDatas()

        self.replayClean()
        self.openTimer()
        webHandleObj.startThread()

        # if GM["needLogin"] == False:
        #     self.lb_1_8.setText("")
        #     self.lb_1_9.setText("")
        #     self.hasLogin = True
        # else:
        #     self.needCkTime = True
        #     self.lb_1_8.setText("软件到期时间:")
        self.wxHdInit()

        self.openOver = True

        # self.mTest()

    def makeTipBef(self):
        if self.makeTip:
            self.makeTip()

    def makeTip(self):
        # useTime = GM["toTime"] - GM["dfTime"]
        # toTime = datetime.fromtimestamp(useTime)
        # now = utils.getNow()
        # leftTime = toTime.timestamp() - now.timestamp()
        print("makeTip.leftTime")
        # if leftTime < 90*24*3600:
        #     QMessageBox.information(self,'公告',"下个月续费只能走USDT！",QMessageBox.Yes,QMessageBox.Yes)

    
    def enterPanel(self):
        self.hasEnter = True
        self.pushDelay(2, self.delayTips)


    def makeAllRecord(self):
        if self.needRcd == False:
            return
        self.makePg1Record1()

    def delayTips(self):
        self.dailyReset()

    def dailyReset(self):
        dataHandleObj.readConfig("game_data")
        todate = utils.getNow().strftime('%Y_%m_%d')
        if todate != config["game_data"]["todate"]:
            config["game_data"]["todate"] = todate
            config["game_data"]["oneTime"] = 0
            dataHandleObj.updateConfig("game_data", config["game_data"])

    # 子线程调不出 主线程的界面 只能过一层交给你主线程
    def rcvWxMsgOver(self):
        # print("rcvWxMsgOver", self.json_dict)
        # try:
        if True:
            if self.json_dict1:
                self.handleWxMsg(self.json_dict1)
                self.json_dict1 = None
            if self.json_dict2:
                self.handleWxMsg(self.json_dict2)
                self.json_dict2 = None
            if self.json_dict3:
                self.handleWxMsg(self.json_dict3)
                self.json_dict3 = None
            if self.json_dict4:
                self.handleWxMsg(self.json_dict4)
                self.json_dict4 = None
        # except Exception as e:
        #     self.json_dict1 = None
        #     self.json_dict2 = None
        #     self.json_dict3 = None
        #     self.json_dict4 = None
        #     utils.info("---rcvWxMsgOver.err---"+str(e))
        

    def closeEvent(self, event):
        if not self.openOver:
            return

        try:
            self.save_deep_history()
        except Exception:
            pass

        GM["onClose"] = True
        
        if GM["debug"]:
            webHandleObj.closeThread()
            # self.saveContent()
            self.makeAllRecord()
            self.closeMust()
        else:
            try:
                webHandleObj.closeThread()
                self.makeAllRecord()
                # self.saveContent()
                self.closeMust()
            except Exception as e:
                print("close.err", e)

        print("close.mid")

        print("close.over")
        
    def closeMust(self):
        print("closeMust")
        webHandleObj.closeThread()
        if "openLog" in GM:
            utils.info("---关闭游戏---"+utils.getNowTime())
            GM["openLog"].close()

    def mTest(self):
        # 测试
        pass

    def readDataOver(self):
        self.initRecord()
        # print(GM["PrizeDic"])
        self.readDataOverPg1()
        self.needRcd = True

        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.centralwidget.setStyleSheet("QWidget#widget{background-image: url(./231.jpg);border-radius:30px;}")
        # self.centralwidget.setStyleSheet("QWidget#widget{background-image: url(./231.jpg);border-radius:30px;}")
        # self.setStyleSheet("background-color:rgb(249,249,249);")
        # self.setStyleSheet("background-image:url(./231.jpg)")
        # self.setWindowFlags(Qt.SubWindow)

    # 清空初始化状态
    def replayClean(self):
        self.json_dict1 = None
        self.json_dict2 = None
        self.json_dict3 = None
        self.json_dict4 = None
        # 大状态状态
        self.inStart = False
        self.updateTime = 0
        self.useMd = 1
        self.delayCallArrays = []
        self.updataCallArrays = []
        self.nowMaxPrizeNum = 0
        self.lastOpenTime = utils.getNow()
        self.lineMsgTab = []
        self.scTab = []
        self.scExtTab = []
        self.hasRecord = False
        self.handChange = False
        self.bigState = config["scStates"]["input"]
        # 根据微信id 存下来的 群和个人信息列表
        self.wxMsgDic = {}
        self.inHandleWx = True  # 正在获取微信控制中
        self.canWarn = True
        self.sendWxId = ""
        self.lastOpenTime = datetime(1980, 1, 1)
        pass

    def initDatas(self):
        # 标题
        self.initWindowName()
        # logo
        self.setWindowIcon(QIcon(':/logo.ico'))
        # GM["zhuoMian"]
        me = os.path.join(os.path.expanduser("~"), 'Desktop')
        if len(me) > 7:
            GM["zhuoMian"] = me

        self.initUi()
        self.deepInit()
        pass
    # 软件名称
    def initWindowName(self):
        # self.setWindowTitle(" "*100+"wocoa")
        name = config["softName"]+" V."+str(GM["version"])
        self.setWindowTitle(name)
        pass

    
    def initUi(self):
        dataHandleObj.readConfig("main")
        if "machine" not in config["main"]:
            config["main"]["machine"] = "mckeyCreater"+str(random.randint(1000000,9000000))
        if "rcday" in config["main"]:
            now = utils.getNow().timestamp()
            if config["main"]["rcday"] > now:
                config["main"]["rcday"] = now
        else:
            config["main"]["rcday"] = 1108483200
        # 左边栏
        # 787*730 不可改变
        width = 740
        self.setFixedWidth(width)
        self.rcdHeight = 730

        self.desktop = QApplication.desktop()
        # 获取显示器分辨率大小
        self.screenRect = self.desktop.screenGeometry()
        scHeight = self.screenRect.height()

        dataHandleObj.readConfig("more")
        self.ckbx_2_waitSd.setChecked(True) if config["more"]["waitSd"] == 1 else self.ckbx_2_waitSd.setChecked(False)
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

    def saveMore(self, mQLineEdit, nowStr):
        """与 wangCai 一致：间隔参数失焦/回车时写入 config[more]。"""
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
        if self.needRcd == False:
            return
        config["more"]["waitSd"] = 1 if self.ckbx_2_waitSd.isChecked() else 0
        config["more"]["wTime"] = int(self.ledt_2_wTime.displayText())
        config["more"]["lsTime"] = int(self.ledt_2_lsTime.displayText())
        dataHandleObj.updateConfig("more", config["more"])

    # 添加绑定点击事件
    def addEvents(self):
        # QCheckBox
        pass


    def onCurrentTextChanged(self, text):
        if len(text) > 3:
            config["vs_cfg"]["choose"] = text[-1]
            dataHandleObj.updateConfig("vs_cfg", config["vs_cfg"])
            self.refreshChooseVs8()

    # 开启定时器
    def openTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onUpdate)
        # 计时结束调用operate()方法
        self.timer.start(GM["dt"]*1000)
        self.onUpdate()

    # 定时器
    def onUpdate(self):
        dt = GM["dt"]
        self.onUpdateOneTime += dt
        GM["updateAllTime"] += dt
        self.callDelay(dt)
        # print("onUpdateOneTime", self.onUpdateOneTime)
        if self.onUpdateOneTime > self.cpOne:
            self.onUpdateOneTime -= 1
            self.callUpdate(1)
            self.pg1Update(1)

    def pg1Update(self, dt):
        pass

    def pushUpdate(self, allTime, func):
        task = {}
        task["allTime"] = allTime
        task["nowTime"] = 0
        task["func"] = func
        self.updataCallArrays.append(task)

    def callUpdate(self, dt):
        if len(self.updataCallArrays) > 0:
            length = len(self.updataCallArrays) - 1
            for x in range(length,-1,-1):
                v = self.updataCallArrays[x]
                v["nowTime"] += dt
                if "func" in v:
                    v["func"](v["nowTime"])
                if v["nowTime"] >= v["allTime"]:
                    self.updataCallArrays.pop(x)

    def pushDelay(self, dalayTime, func):
        if dalayTime:
            task = {}
            task["dalayTime"] = dalayTime
            task["nowTime"] = 0
            task["func"] = func
            self.delayCallArrays.append(task)

    def callDelay(self, dt):
        if len(self.delayCallArrays) > 0:
            length = len(self.delayCallArrays) - 1
            for x in range(length,-1,-1):
                v = self.delayCallArrays[x]
                v["nowTime"] += dt
                if v["nowTime"] >= v["dalayTime"]:
                    v["func"]()
                    self.delayCallArrays.pop(x)

def main():
    path_logs = os.path.join(CUR_DIR, "logs")
    # 可行 但是不退出
    if "deepWeChat" in CUR_DIR:
        if "dist" in CUR_DIR:
            cgitb.enable(format = 'text', logdir = path_logs)
    else:
        cgitb.enable(format = 'text', logdir = path_logs)

    # cgitb.enable(format = 'text', logdir = path_logs)

    app = QApplication(sys.argv)
    dlg = MainWindow()


    # dlg.show()
    GM["the_main"] = dlg
    dlg.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
