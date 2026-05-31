# -*- coding:utf-8 -*-
import sys
sys.setrecursionlimit(200)
# reload(sys)
# sys.setdefaultencoding("utf-8")
import os
import json
import shutil
# import urllib
import traceback
from datetime import datetime
import time
import paramiko
import threading
import copy
import pyperclip
import random

from pprint import pprint
import subprocess
# 获取当前脚本执行目录
CUR_DIR = os.getcwd()
PATH_MEDIA = os.path.join(CUR_DIR, "media")
if not os.path.exists(PATH_MEDIA):
    os.makedirs(PATH_MEDIA)
PATH_TEMP = os.path.join(PATH_MEDIA, "temp")
PATH_TOOL = os.path.join(PATH_MEDIA, "tool")
PATH_AUDIO = os.path.join(PATH_MEDIA, "audio")
try:
	if os.path.exists(PATH_TEMP):
		shutil.rmtree(PATH_TEMP)
	os.makedirs(PATH_TEMP)
except Exception as e:
	pass

from PyQt5 import QtMultimedia

GM = {}
# 用户的内存缓存
GM["AppDic"] = {}    # 人物信息
GM["RoleDic"] = {}   # 人物详细信息
GM["BackDic"] = {}
GM["LimitDic"] = {}


GM["dayGains"] = {}   # 一天的盈利
# GM["AppDicCopy"] = {} # 用于判断的时候可能需要迭代
GM["dt"] = 0.05   # 定时器 多久执行一次
GM["wxVersion"] = "3.9.12.55"

GM["allDelete"] = False # 全部删除标识符号
GM["waitMsgTab"] = []
GM["waitImgTab"] = []

GM["updateAllTime"] = 0
GM["lastSaveLogTime"] = -4
GM["saveItv"] = 0       # 间隔多久存储一次 3

GM["zhuoMian"] = r"C:\Users\Administrator\Desktop"
GM["tryLogin"] = False
GM["dfTime"] = 0   # 本地时间 + 这个 = 服务器时间
GM["sendWxId"] = ""
GM["onClose"] = False
GM["inFtp"] = False


sys.GM = GM

# 数字表
GM["numTab"] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
# letter 字母表
GM["letTab"] = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
# 单个关键字 不能识别 给你过
GM["alwTab"] = ["", ":", ",", "，", "：", "。", " "]

# GM["numTab"]
# GM["debug"] = True
GM["debug"] = False
if "deepWeChat" in CUR_DIR:
	if "dist" in CUR_DIR:
		pass
	else:
		GM["debug"] = True

GM["formal"] = False # 正式版本
GM["iptBill"] = False # 正在导入账单状态

GM["typeDic"] = type({})
GM["typeTab"] = type([])
GM["typeInt"] = type(1)
GM["typeFlo"] = type(1.1)

# 确保鬼手服务有开的端口
GM["sureUrl1"] = "http://127.0.0.1:9999/status"
GM["baseApi1"] = "http://127.0.0.1:9999/"

GM["sureUrl"] = GM["sureUrl1"]
GM["baseApi"] = GM["baseApi1"]

# GM["hookModel"] = 0 # 0-鬼手 1-
GM["sureUrl2"] = "http://127.0.0.1:30001/"
GM["baseApi2"] = "http://127.0.0.1:30001/"

GM["sureUrl3"] = "http://127.0.0.1:1234/"
GM["baseApi3"] = "http://127.0.0.1:1234/"

GM["sureUrl4"] = "http://127.0.0.1:19088/"
GM["baseApi4"] = "http://127.0.0.1:19088/api/"

GM["version"] = 1001

GM["goldMgType"] = 0  # 0-不做处理 1-上分 2-下分 3-手动修改即管控

GM["mcKey"] = ""  # 机器码

GM["logLeft"] = 10000
GM["logType"] = {
	"1": [],
	"2": [],
	"3": [],
	"4": [],
}
GM["rizhiTab"] = []

# mCmd = os.path.join(PATH_TOOL, "CInjectTool.exe")+" "+os.path.join(PATH_TOOL, "WeChatApis.dll")
# print(mCmd)

GM["player"] = QtMultimedia.QMediaPlayer()

GM["qy"] = "@qy_g"

GM["gfWxid"] = {
	"gh_25d9ac85a4bc": "微信游戏",
	"fmessage": "朋友推荐消息",
	"medianote": "语音记事本",
	"floatbottle": "漂流瓶",
	"gh_3dfda90e39d6": "微信支付",
	"filehelper": "文件传输助手",
}

if True:
	dic = {}
	for key in GM["gfWxid"]:
		val = GM["gfWxid"][key]
		dic[val] = key
	GM["gfName"] = dic


# 读取网页配置用来更新掉的部分
GM["webConfig"] = {
	"ndUpdate": True,    # 是否进行动态更新
	"maxVersion": 1001,  # 目前的最高版本 最好我要更新到
	"keepDay": 125,
	"checkMcTime": 1200,

	"isJieChi": False,
	"dailyTipTitle": "",
	"dailyTipStr": "",
}

# lv_level 0-不能多开群 1-所有权限
GM["lv_level"] = 0
GM["oneDay"] = 86400

if "deepWeChat" in CUR_DIR and "dist" not in CUR_DIR:
	GM["hasMusic"] = False
else:
	GM["hasMusic"] = True

GM["mdImgs"] = {}  # TxtImg缓存
GM["mdIds"] = {}

# GM["needLogin"] = True
GM["needLogin"] = True
if GM["debug"]:
	GM["needLogin"] = False


