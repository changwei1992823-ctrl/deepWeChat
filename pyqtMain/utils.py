# -*- coding:utf-8 -*-

from common_init import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import wmi
import hashlib
import requests

def exec_(command, cwd):
    """
    执行本地命令
    :param command: 命令
    :param cwd: 执行环境
    :return:
    """
    sub = subprocess.Popen(command, cwd=cwd, env=None, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=4096)
    (stdout, stderr) = sub.communicate()
    return stdout, stderr

# 这个不会让你等待 上面如果打开微信会导致主进程等着收集微信消息
def exec_2(command, cwd):
    """
    执行本地命令
    :param command: 命令
    :param cwd: 执行环境
    :return:
    """
    sub = subprocess.Popen(command, cwd=cwd, env=None, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=4096)
    # (stdout, stderr) = sub.communicate()
    # return stdout, stderr

def create_ssh(username, password, ip, port=22):
    """
    创建ssh连接
    :param username: 用户名
    :param password: 密码
    :param ip: ip地址
    :param port: 端口
    :return: ssh连接客户端
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port, username, password)
    return ssh

def remotecmd(ssh_client, code):
    """
    :param ssh_client: ssh连接客户端
    :param code: 要执行的python代码
    :return: (标准输出, 错误输出)
    """
    stdin, stdout, stderr = ssh_client.exec_command(
"""
%s
"""%(code))
    out,err = stdout.read(), stderr.read()
    if type(out) == type(b''):
        out = str(out, encoding = "utf-8")
        err = str(err, encoding = "utf-8")
    return out,err
    # print(type(out))
    # print(type(b'')) 

def getNow():
    if GM["dfTime"] == 0:
        return datetime.now()
    else:
        dt = datetime.now().timestamp() + GM["dfTime"]
        return datetime.fromtimestamp(dt)

def getNowTime():
    dt = getNow()
    mStr = dt.strftime('%Y-%m-%d %H:%M:%S')
    return mStr

def strptime(opentime):
    turnTime = None
    try:
        turnTime = datetime.strptime(opentime, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        pass
    if len(opentime) == 24:
        try:
            turnTime = datetime.strptime(opentime, '%Y-%m-%dT%H:%M:%S.%fZ')
        except Exception as e:
            pass
    if turnTime == None:
        turnTime = datetime.now()
    return turnTime

def copyObj(obj):
    # dic = {}
    # for key in obj:
    #     dic[key] = obj[key]
    return copy.deepcopy(obj)

def isNumber(pStr):
    if (pStr.isdigit()):
        try:
            result = int(pStr)
            return True, result
        except:
            pass
    else:
        if len(pStr) > 0 and "." == pStr[0]:
            if len(pStr) > 1:
                return isNumber(pStr[1:])
        else:
            try:
                result = float(pStr)
                # result = int(result)
                return True, result
            except:
                pass
    return False, pStr

# 读取lineEdit为数字 默认保留两位数字
def readNumText(text, default):
    # print("this", this, lineEdtName)
    # text = this[lineEdtName].displayText()
    isNum,turnNum = isNumber(text)
    # turnNum = int(turnNum)
    if isNum:
        # turnNum = int(turnNum*100)
        return turnNum
    else:
        return default;

def InfoInit():
    # 准备好路径 和 打开txt
    path_logs = os.path.join(CUR_DIR, "logs")
    print("path_logs", path_logs)
    if not os.path.exists(path_logs):
        os.makedirs(path_logs)
    # 打开txt 作为日志的准备
    path_mLog = os.path.join(CUR_DIR, "logs", "mLog.txt")
    content = ""
    try:
        with open(path_mLog, "r") as tmp_file:
            content = tmp_file.read()
    except Exception as e:
        pass
    contentTab = content.split("\n")
    length = len(contentTab)
    # print("content", content)
    # print("length", length)
    if length > GM["logLeft"]+10:
        start = length - GM["logLeft"]
        leftContent = ""
        for x in range(start,length):
            leftContent += contentTab[x]+"\n"
        # print(leftContent)
        try:
            with open(path_mLog, "w") as tmp_file:
                tmp_file.write(leftContent)
        except Exception as e:
            pass
    if length < 100000:
        # 说明基本不是旧版本的日志
        for x in range(0,length):
            tmpStr = contentTab[x]
            if "|" in tmpStr:
                tmpTab = tmpStr.split("|")
                if len(tmpTab) > 2:
                    mType = tmpTab[0]
                    if mType in GM["logType"]:
                        GM["logType"][mType].append(tmpTab)
    GM["openLog"] = open(path_mLog, "a+")
    pass

def info(*args):
    # print("info", args)
    if "openLog" not in GM:
        InfoInit()
    length = len(args)

    if GM["debug"]:
        print("info", args)
        
    try:
        for i in range(0,length):
            mStr = str(args[i])
            GM["openLog"].write(mStr)
            if i < length-1:
                GM["openLog"].write(", ")
        GM["openLog"].write("\n")

        if GM["updateAllTime"] - GM["lastSaveLogTime"] > GM["saveItv"]:
            GM["openLog"].flush()
    except:
        pass


# 通讯日志
def info4TongXun(msg):
    msg = msg.replace("\n", "~").replace("\n", "~").replace("\n", "~").replace("\n", "~")
    now = getNowTime()
    tmpStr = "4|"+now+"|"+msg
    info(tmpStr)
    tmpTab = tmpStr.split("|")
    GM["logType"]["4"].append(tmpTab)

def toNumber(mStr):
    mF = float(mStr)
    try:
        mI = int(mStr)
        if mF == mI:
            return mI
        else:
            return mF
    except Exception as e:
        pass
    return mF


def getStrLength(mStr):
    num = 0
    for x in mStr:
        # pass
        charCode = ord(x)
        if charCode > 32 and charCode < 127:
            num += 1
        else:
            num += 9/5
    return round(num)

class MyLineEdit2(QLineEdit):
    textModified = pyqtSignal(int, str, str) # (id, before, after)

    def __init__(self, parent):
        super(MyLineEdit2, self).__init__(parent, font=QFont("Arial", 11))
        self.returnPressed.connect(self.checkText)
        self.befStr = ""

    def focusInEvent(self, event):
        if event.reason() != Qt.PopupFocusReason:
            self.befStr = self.text()
        super(MyLineEdit2, self).focusInEvent(event)

    def focusOutEvent(self, event):
        if event.reason() != Qt.PopupFocusReason:
            self.checkText()
        super(MyLineEdit2, self).focusOutEvent(event)

    def checkText(self):
        nowStr = self.text()
        if self.befStr != nowStr:
            # self._before = self.text()
            # print("修改", self._before, self.id)
            self.textModified.emit(self.msgDic["id"], self.befStr, nowStr)
            # self.befStr = nowStr

def extendLedt(mQLineEdit, useKey):
    # QLineEdit.textModified = pyqtSignal(str, str)
    mQLineEdit.befStr = ""
    mQLineEdit.useKey = useKey

    def checkText():
        nowStr = mQLineEdit.text()
        if mQLineEdit.befStr != nowStr:
            mQLineEdit.textChaned(mQLineEdit, nowStr)
            # mQLineEdit.befStr = nowStr

    mQLineEdit.checkText = checkText
    mQLineEdit.focusInEventBef = mQLineEdit.focusInEvent
    mQLineEdit.focusOutEventBef = mQLineEdit.focusOutEvent

    def focusInEvent(event):
        if event.reason() != Qt.PopupFocusReason:
            mQLineEdit.befStr = mQLineEdit.text()
        mQLineEdit.focusInEventBef(event)

    def focusOutEvent(event):
        if event.reason() != Qt.PopupFocusReason:
            mQLineEdit.checkText()
        mQLineEdit.focusOutEventBef(event)

    mQLineEdit.returnPressed.connect(mQLineEdit.checkText)
    mQLineEdit.focusInEvent = focusInEvent
    mQLineEdit.focusOutEvent = focusOutEvent

def playSound(name):
    if GM["hasMusic"] == False:
        return
    fullPath = os.path.join(PATH_AUDIO, name)
    url = QUrl.fromLocalFile(fullPath)
    content = QtMultimedia.QMediaContent(url)
    GM["player"].setMedia(content)
    GM["player"].play()
    # print("playSound", name)

# 解析下注内容
def parseXiaZhuTabToStr(xiaZhuTab):
    tmpStr = ""
    count = 0
    for tab in xiaZhuTab:
        buy_what = tab[0]
        str2 = ""

        if buy_what == "点":
            str2 = str(tab[1]) + "T" + str(tab[2])
        else:
            str2 = str(tab[0])+str(tab[1])

        if count > 0:
            tmpStr += "/"+str2
        else:
            tmpStr += str2
        count += 1

    return tmpStr

# 获得本机的机器码
def getMachine():
    if GM["mcKey"] != "":
        return GM["mcKey"]
    # GM["mcKey"] = ""
    onlyKey = ""
    try:
        c = wmi.WMI()
        tab1 = c.Win32_DiskDrive()
        tab2 = c.Win32_Processor()
        
        if len(tab1) > 0:
            onlyKey += tab1[0].SerialNumber.strip()
        if len(tab2) > 0:
            onlyKey += tab2[0].ProcessorId.strip()
    except Exception as e:
        print("getMachine.err", e)
        pass
    # onlyKey = "wocao"+str(random.randint(10,99))
    print("onlyKey", onlyKey)
    # info("onlyKey", onlyKey)
    if onlyKey == "":
        onlyKey = GM["config"]["main"]["machine"]
    else:
        onlyKey = onlyKey.replace("-", "")
        onlyKey = onlyKey.replace("/", "")
        onlyKey = onlyKey.replace(" ", "")
        if onlyKey == "":
            onlyKey = GM["config"]["main"]["machine"]
    GM["mcKey"]  = onlyKey
    return onlyKey

def parseMsg(content):
    length = len(content)
    parseDic = {}
    state = 0 # 0-寻找起始点 1-寻找key 2-寻找value
    splitTab = content.split(" ")
    useTab = []
    for tmpStr in splitTab:
        if '="' in tmpStr:
            tab = tmpStr.split("=")
            if len(tab) == 2:
                value = tab[1].replace('"', "")
                if "<" not in value and ">" not in value:
                    key = tab[0]
                    parseDic[key] = value
    return parseDic

def myFunc2(tab):
    return tab[0];

def myFunc3(tab):
    return tab[2];

def isHeGe(mStr, role):
    # app_id = role["app_id"]
    app_id = role["app_id"]
    if app_id in GM["mainScene"].wxRoleDic:
        if mStr in GM["mainScene"].wxRoleDic[app_id]["wxcount"]:
            return True
        elif mStr in role["nick_name"]:
            return True
        else:
            return False
    else:
        if mStr in role["nick_name"]:
            return True
        elif mStr in role["app_id"]:
            return True
        else:
            return False

def md5Encrypt(mStr):
    # 生成一个MD5对象
    md5 = hashlib.md5()
    # 使用md5对象里的update方法md5转换
    md5.update(mStr.encode('utf-8'))
    # 得到加密后的字符串
    code = md5.hexdigest()
    # print(code)
    return code

def mPost(url, data, callback=None, failCallback=None):
    data_json = json.dumps(data)
    try:
        r = requests.post(url, data_json)
        print(url, r.text)
        if callback:
            json_str = json.loads(r.text)
            if json_str["code"] == 0:
                callback(json_str)
            return
    except Exception as e:
        print("mPost.err", url, e)

    if failCallback:
        failCallback()

def mGet(url, callback):
    try:
    # if True:
        response = requests.get(url)
        if response.status_code == 200:
            # print("response.text", response.text)
            huiDic = json.loads(response.text)
            callback(huiDic)
            # if huiDic["code"] == 0:
            #     callback(huiDic)

    except Exception as e:
        print("mGet.err", e)

def vsMsg(key):
    if GM["config"]["vs_cfg"]["ziDing"] == 1:
        if key in GM["config"]["vsk1"]:
            return GM["config"]["vsk1"][key]
        elif key in GM["config"]["vsk2"]:
            return GM["config"]["vsk2"][key]
        elif key in GM["config"]["vsk3"]:
            return GM["config"]["vsk3"][key]
        elif key in GM["config"]["vsk4"]:
            return GM["config"]["vsk4"][key]
        elif key in GM["config"]["vsk5"]:
            return GM["config"]["vsk5"][key]
        else:
            return "key不存在."+key
    else:
        choose = GM["config"]["vs_cfg"]["choose"]
        version = GM["config"]["version_"+choose]
        if key in version:
            msg = version[key]
            return msg
        else:
            return "key不存在."+key

# InfoInit()
# info(1,2,3,[4])
if __name__ == '__main__':
    # now = getNowTime()
    # info(now)
    pass