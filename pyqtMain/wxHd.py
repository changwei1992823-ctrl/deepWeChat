
# 微信界面 测试

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from common_init import *

from PyQt5 import QtNetwork

from Ui_main import Ui_MainWindow
import win32gui, win32api, win32con
import requests

from config import *
from dataHd import dataHandleObj


web = requests.session()
web.headers['Content-Type'] = 'application/x-www-form-urlencoded'

GM["black"] = QColor(0, 0, 0, 220)
GM["blackHalf"] = QColor(0, 0, 0, 160)
GM["blueHalf"] = QColor(13, 80, 209, 160)
GM["heWidth"] = 28

class wxHandle(Ui_MainWindow):
	def __init__(self):
		super(wxHandle, self).__init__()
		# print("wxHandle")
		self.tryTime = 0

		# self.mInit()
		# self.wocao = None
		# if "wocao" in self:
		# 	print(self.wocao)
		# print(hasattr(self, "wocao"))
		# self.createResult()
	

	def apply_hook_mode_urls(self, hook_md=None):
		"""按 hookMd 设置微信 API 地址（与 webHd.openServer 端口对应）。"""
		if hook_md is None:
			hook_md = int(config["set_1"].get("hookMd", 1))
		if hook_md == 2:
			GM["sureUrl"] = GM["sureUrl4"]
			GM["baseApi"] = GM["baseApi4"]
		else:
			GM["sureUrl"] = GM["sureUrl3"]
			GM["baseApi"] = GM["baseApi3"]

	def initHookModeUi(self):
		"""启动时从 config 同步 groupBox_2 单选状态。"""
		if not hasattr(self, "rdbt_2_1"):
			return
		hook_md = int(config["set_1"].get("hookMd", 1))
		if hook_md not in (1, 2):
			hook_md = 1
			config["set_1"]["hookMd"] = hook_md
		self._hook_mode_block = True
		self.rdbt_2_1.setChecked(hook_md == 1)
		self.rdbt_2_2.setChecked(hook_md == 2)
		self._hook_mode_block = False
		if not getattr(self, "_hook_mode_inited", False):
			self.rdbt_2_1.toggled.connect(self.on_hook_mode_changed)
			self.rdbt_2_2.toggled.connect(self.on_hook_mode_changed)
			self._hook_mode_inited = True

	def on_hook_mode_changed(self, _checked=False):
		if getattr(self, "_hook_mode_block", False):
			return
		hook_md = 2 if self.rdbt_2_2.isChecked() else 1
		bef = int(config["set_1"].get("hookMd", 1))
		if hook_md == bef:
			return
		reply = QMessageBox.information(
			self,
			"切换控制模式",
			"更换控制模式需要重启软件！现在更换？",
			QMessageBox.Yes,
			QMessageBox.Yes,
		)
		if reply != QMessageBox.Yes:
			self._hook_mode_block = True
			self.rdbt_2_1.setChecked(bef == 1)
			self.rdbt_2_2.setChecked(bef == 2)
			self._hook_mode_block = False
			return
		config["set_1"]["hookMd"] = hook_md
		dataHandleObj.updateConfig("set_1", config["set_1"])
		self.inQieHuan = True
		self.close()

	# 这个要等到界面出现才能执行
	def wxHdInit(self):
		print("hookMd", config["set_1"]["hookMd"])
		self.apply_hook_mode_urls()
		# self.replayClean()
		self.withWarn = False
		# self.lb_9_1.setReadOnly(True)
		# self.rcdQun = "什么|25365139502@chatroom"
		self.failTime = 0  # 短时间内 连续几次发送事件失败 那么可能是微信断开连接了
		self.replayWxHd()
		self.withWarn = True

	def replayWxHd(self):
		if config["set_1"]["noWx"]:
			self.inHandleWx = False
			self.canUseWx = True
			return
		else:
			# 是否可以使用微信
			self.inHandleWx = True
			self.canUseWx = False
		
		self.tryTime = 0
		# self.isCanUseWx()
		self.pushDelay(0.5, self.isCanUseWx)
		pass

	def isCanUseWx(self):
		# 去判断是否登录了 是否有端口
		# 先判断微信打开了没有
		# url = 'http://123.176.96.188/api/recv.html?&format=json&code=cakeno&rows=3'
		self.tryTime += 1
		url = GM["sureUrl"]
		# url = "http://127.0.0.1:9999/"
		req = QtNetwork.QNetworkRequest(QUrl(url))
		self.nam = QtNetwork.QNetworkAccessManager()
		self.nam.finished.connect(self.handleIsCanUseWx)
		self.nam.get(req)
		print("isCanUseWx")
		
		pass

	def handleIsCanUseWx(self, reply):
		print("handleIsCanUseWx", reply)
		er = reply.error()
		if er == QtNetwork.QNetworkReply.NoError:
			print("可以正常的控制微信")
			self.sureCanUseWx()
			self.inHandleWx = False
			self.updateTime = 100
		else:
			if config["set_1"]["hookMd"] == 1:
				if self.tryTime < 2:
					print("发生了错误.3,估计是服务器没有开")
					self.startMyShou()
				else:
					self.warnCantUseWx()
					self.inHandleWx = False
			elif config["set_1"]["hookMd"] == 2:
				if self.tryTime < 2:
					print("发生了错误.4,估计是服务器没有开")
					self.startMyShou("ConsoleApp4.exe")
				else:
					self.warnCantUseWx()
					self.inHandleWx = False
			else:
				web.headers['Content-Type'] = 'application/json'
				# if self.tryTime < 2:
				# 	print("发生了错误,估计是服务器没有开")
				# 	self.startGuiShou()
				# else:
				# 	self.warnCantUseWx()
				# 	self.inHandleWx = False
				self.warnCantUseWx()

	def warnCantUseWx(self):
		A = QMessageBox.warning(self, "找不到服务", "未能控制微信,请确保登录微信\n或者浏览器打开\n"+GM["sureUrl"]+"\n可以访问", QMessageBox.Yes, QMessageBox.Yes)
		if A == QMessageBox.Yes:
			pyperclip.copy(GM["sureUrl"])
		pass

	# 打开微信
	def openWx(self):
		pathBaseTab = [
			r"C:\Program Files (x86)\Tencent\WeChat",
			r"C:\Program Files\Tencent\WeChat",
			r"D:\Program Files (x86)\Tencent\WeChat",
			r"D:\Program Files\Tencent\WeChat",
			r"E:\Program Files (x86)\Tencent\WeChat",
			r"E:\Program Files\Tencent\WeChat",
		]
		hasFond = False
		# Tencent\WeChat\improve.xml  2.9.0.123
		for wPath in pathBaseTab:
			if os.path.exists(wPath):
				improve = os.path.join(wPath, "improve.xml")
				with open(improve, "r") as tmp_file:
					content = tmp_file.read()
					# print(content)
					if GM["wxVersion"] in content:
						print("版本正确")
					else:
						hasFond = True
						QMessageBox.warning(self, "版本不对", "微信版本不对\n"+GM["wxVersion"], QMessageBox.Yes, QMessageBox.Yes)
						break
				mCmd = "WeChat.exe"
				utils.exec_2(mCmd,wPath)
				hasFond = True
				break
		if hasFond == False:
			QMessageBox.warning(self, "未能找到", "没有找到微信的启动路径", QMessageBox.Yes, QMessageBox.Yes)

	# 刷新群列表
	def updateGroupList(self, chekTime = False):
		if chekTime:
			diffTime = GM["updateAllTime"] - self.updateGroupListTime
			if diffTime < 4:
				return
		self.updateGroupListTime = GM["updateAllTime"]
		if self.canUseWx:
			self.cbx_2_1_curText = self.cbx_2_1.currentText()
			self.cbx_2_2_curText = self.cbx_2_2.currentText()
			self.getChatList()
		else:
			self.replayWxHd()

	# 开启鬼手的handle微信
	def startGuiShou(self):
		# mCmd = r"D:\quick\wxMcTools\guishou\CInjectTool.exe D:\quick\wxMcTools\guishou\WeChatApis.dll"
		if not os.path.exists(PATH_TOOL):
			return QMessageBox.warning(self, "警告", "tool文件夹不存在\n检查下media文件夹是不是没有拷贝", QMessageBox.Yes, QMessageBox.Yes)

		CInjectTool = os.path.join(PATH_TOOL, "CInjectTool.exe")
		if not os.path.exists(CInjectTool):
			return QMessageBox.warning(self, "警告", "tool文件夹CInjectTool.exe不存在\n检查下media文件夹是不是没有拷贝", QMessageBox.Yes, QMessageBox.Yes)

		WeChatApis = os.path.join(PATH_TOOL, "WeChatApis.dll")
		if not os.path.exists(WeChatApis):
			return QMessageBox.warning(self, "警告", "tool文件夹WeChatApis.dll不存在\n检查下media文件夹是不是没有拷贝", QMessageBox.Yes, QMessageBox.Yes)

		# 	return
		mCmd = CInjectTool+" "+WeChatApis
		out,err = utils.exec_(mCmd,PATH_TOOL)
		if self.withWarn == False:
			return
		# out = str(out, encoding='utf-8')
		self.exeOut = str(out, encoding = "gb18030")
		# print(self.exeOut == "注入成功")
		if self.exeOut == "注入成功":
			# 改requests吧  不然莫名其妙闪退
			time.sleep(0.7)
			try:
				response = requests.get(GM["sureUrl"])
				if response.status_code == 200:
					print("鬼手打开了")
					self.sureCanUseWx()
					return
			except Exception as e:
				pass

			self.warnCantUseWx()
		else:
			QMessageBox.warning(self, "警告", "微信尚未启动或者版本不对:"+self.exeOut, QMessageBox.Yes, QMessageBox.Yes)

	# 开启我的handle微信
	def startMyShou(self, exeName="ConsoleApp2.exe"):
		# mCmd = r"D:\quick\wxMcTools\guishou\CInjectTool.exe D:\quick\wxMcTools\guishou\WeChatApis.dll"
		if not os.path.exists(PATH_TOOL):
			return QMessageBox.warning(self, "警告", "tool文件夹不存在\n检查下media文件夹是不是没有拷贝", QMessageBox.Yes, QMessageBox.Yes)

		CInjectTool = os.path.join(PATH_TOOL, exeName)
		if not os.path.exists(CInjectTool):
			return QMessageBox.warning(self, "警告", "tool文件夹"+exeName+"不存在\n检查下media文件夹是不是没有拷贝", QMessageBox.Yes, QMessageBox.Yes)

		# 	return
		mCmd = CInjectTool
		out,err = utils.exec_(mCmd,PATH_TOOL)
		if self.withWarn == False:
			return
		# out = str(out, encoding='utf-8')
		self.exeOut = str(out, encoding = "gb18030")
		# print(self.exeOut == "注入成功")
		# if self.exeOut == "注入成功":
		if "DLL注入完成" in self.exeOut:
			# 改requests吧  不然莫名其妙闪退
			time.sleep(0.7)
			try:
				response = requests.get(GM["sureUrl"])
				if response.status_code == 200:
					print("我的handle微信打开了")
					self.sureCanUseWx()
					return
			except Exception as e:
				pass

			self.warnCantUseWx()
		else:
			scStr = "Dll1"
			if exeName =="ConsoleApp4.exe":
				scStr = "Dll4"
			if scStr in self.exeOut:
				time.sleep(0.7)
				try:
					response = requests.get(GM["sureUrl"])
					if response.status_code == 200:
						print("我的handle微信打开了")
						self.sureCanUseWx()
						return
				except Exception as e:
					pass

				self.warnCantUseWx()
			else:
				QMessageBox.warning(self, "警告", "微信尚未启动或者版本不对:"+self.exeOut+"\n"+scStr, QMessageBox.Yes, QMessageBox.Yes)
		

	# 对的 我就是可以控制微信
	def sureCanUseWx(self):
		self.canUseWx = True
		# 有缓存要读取缓存 waiting
		self.getMyMessage()
		self.getChatList()
		pass

	# 获得我这个微信的基本信息
	"""
{
  "bigheader": "http://wx.qlogo.cn/mmhead/ver_1/xr2TczsdJLTl0EJcxNdlsu46PbvQn2UMpGIYvuyaxs6uMJYk8xufe8600UDLw6hALLqmdjErXfQUVonwczGuRYDnSLKm1QwDPbF5rIdiasIE/132",
  "cachedir": "D:\\Documents\\WeChat Files\\fengchaojiujie\\config\\AccInfo.dat",
  "device": "android",
  "nation": "CN",
  "nickname": "风风火火闯九州",
  "phonenumber": "15372126884",
  "province": "Fujian",
  "smallheader": "(null)",
  "wxcount": "fengchaojiujie",
  "wxid": "wxid_gr4n465thmv222",
  "wxsex": "男"
}

wxid nickname phonenumber wxcount nation
	"""
	def getMyMessage(self):
		url = GM["baseApi"]
		json2 = {"type": 47}
		if config["set_1"]["hookMd"] == 1:
			json2 = None
			url = GM["baseApi"] + "GetSelfInfo"
		elif config["set_1"]["hookMd"] == 2:
			json2 = None
			url = GM["baseApi"] + "get_profile_cache"
		try:
			data = web.post(url, [], json2)
			if data.status_code == 200:
				mJson = json.loads(data.text)
				# print("mJson", mJson)
				if config["set_1"]["hookMd"] == 2:
					if "UserInfo" in mJson:
						mJson["nickname"] = mJson["UserInfo"]["NickName"]["String"]
						mJson["wxid"] = mJson["UserInfo"]["UserName"]["String"]
						mJson["phonenumber"] = mJson["UserInfo"]["BindMobile"]["String"]
						mJson["wxcount"] = mJson["UserInfo"]["Alias"]
						mJson["nation"] = "CN"
						if "UserInfoExt" in mJson:
							if "RegCountry" in mJson["UserInfoExt"]:
								mJson["nation"] = mJson["UserInfoExt"]["RegCountry"]
				if "wxid" in mJson:
					pass
				elif "data" in mJson and "wxid" in mJson["data"]:
					mJson = mJson["data"]
				if "wxid" in mJson:
					self.myWxMsg = mJson
					self.tryTime = 0
				else:
					self.myWxMsg = None
					return QMessageBox.warning(self,"警告","获取自身信息接口失败！",QMessageBox.Yes,QMessageBox.Yes)
			else:
				self.myWxMsg = None
		except Exception as e:
			self.myWxMsg = None
		pass

	# 同意好友请求
	def agreeFriend(self, dic):
		url = GM["baseApi"]
		# v1=encryptusername v2=ticket
		json2 = {
			"type": 11,
			"v1": dic["encryptusername"],
			"v2": dic["ticket"],
		}
		print("agreeFriend", json2)
		if config["set_1"]["hookMd"] == 1:
			return
		elif config["set_1"]["hookMd"] == 2:
			url = GM["baseApi"] + "accept_friend"
			json2 = {
			    "v3": dic["encryptusername"],
			    "v4": dic["ticket"],
			    "scence": "好友来源",
  				"role": "朋友权限"
			    # "role": "8"
			}
		try:
			data = web.post(url, [], json2)
			if data.status_code == 200:
				mJson = json.loads(data.text)
				print("agreeFriend.mJson", mJson)
				if config["set_2"]["zdAgree"] == 1:
					wxid = dic["fromusername"]
					dic = {
						"wxid": wxid,
						"wxcount": dic["alias"],
						"nickname": dic["fromnickname"]
					}
					self.wxMsgDic[wxid] = dic
					self.autoDic = dic
					self.sendTextMsg(config["set_2"]["zdMsg"], wxid)
		except Exception as e:
			pass

	# 添加好友
	def addFriend(self, wxid, msg):
		url = GM["baseApi"]
		# v1=encryptusername v2=ticket
		json2 = {
			"type": 9,
			"source": 6,
			"wxid": wxid,
			"msg": msg
		}
		if config["set_1"]["hookMd"] == 2:
			url = GM["baseApi"] + "add_friend"
			json2 = {
				"wxid": wxid,
				"greet": msg,
				"scence": "30",
				"role": "0"
			}
		print("addFriend", json2)
		try:
			data = web.post(url, [], json2)
			if data.status_code == 200:
				GM["mainScene"].ledt_2_wxid_2.setText("")
				mJson = json.loads(data.text)
				print("addFriend.mJson", mJson)
		except Exception as e:
			pass

	# 获取好友列表和群列表
	"""
{
  'result': [{
    'nickname': '什么',
    'wxcount': '',
    'wxid': '25365139502@chatroom'
  }, {
    'nickname': '相亲相爱一家人',
    'wxcount': '',
    'wxid': '25039063002@chatroom'
  }]
}
	"""
	def getChatList(self):
		url = GM["baseApi"]
		json2 = {"type": 14}
		if config["set_1"]["hookMd"] == 1:
			json2 = None
			url = GM["baseApi"] + "GetContacts"
			# print("url", url)
		elif config["set_1"]["hookMd"] == 2:
			json2 = None
			url = GM["baseApi"] + "get_frien_lists"
		# try:
		if True:
			# if True:
			# print("url", url)
			self.inHandleWx = False
			data = web.post(url, [], json2)
			# print("data.text", data.status_code, data.text)
			if data.status_code == 200:
				mJson = json.loads(data.text)
				wxQunTab = []
				if config["set_1"]["hookMd"] == 2:
					if "data" in mJson:
						data = mJson["data"]
						for dic in data:
							if "wxh" in dic:
								dic["wxcount"] = dic["wxh"]
							else:
								dic["wxcount"] = ""
						mJson["result"] = data

				self.lb_1_7.setText("状态:微信已登录")
				result = mJson["result"]
				# print("getChatMsg", mJson)
				for dic in result:
					if dic["wxcount"] == "":
						self.wxAllDic[dic["wxid"]] = dic
						# print("dic", dic)
						if "chatroom" in dic["wxid"]:
							wxQunTab.append(dic)
					else:
						if (dic["nickname"] == "微信游戏" and dic["wxcount"] == "game") or (dic["nickname"] == "微信支付" and dic["wxcount"] == "wxzhifu"):
							pass
						else:
							self.wxRoleDic[dic["wxid"]] = dic
							self.wxAllDic[dic["wxid"]] = dic

					if dic["wxid"] != "" and dic["wxid"] not in self.wxMsgDic:
						self.wxMsgDic[ dic["wxid"] ] = dic

				# print(wxQunTab)
				self.wxQunTab = wxQunTab
				
				self.cbx_2_1.clear()
				self.cbx_2_2.clear()

				self.inHandleWx = False
				cs1 = ""
				cs2 = ""
				if len(wxQunTab) > 0:
					# print("wxQunTab", wxQunTab)
					for dic in wxQunTab:
						mStr = dic["nickname"]+"|"+dic["wxid"]
						# print("mStr", mStr)
						self.cbx_2_1.addItem(mStr)
						self.cbx_2_2.addItem(mStr)

						if cs1 == "":
							if "接单" in mStr:
								cs1 = mStr

						if cs2 == "":
							if "飞单" in mStr:
								cs2 = mStr

						# if mStr == config["set_1"]["jdQun"]:
						# 	self.cbx_2_1.setCurrentText(mStr)

				if hasattr(self, "cbx_2_1_curText") and self.cbx_2_1_curText != "":
					self.cbx_2_1.setCurrentText(self.cbx_2_1_curText)
				elif config["set_1"]["jdQun"] != "":
					self.cbx_2_1.setCurrentText(config["set_1"]["jdQun"])
				elif cs1 != "":
					self.cbx_2_1.setCurrentText(cs1)

				if hasattr(self, "cbx_2_2_curText") and self.cbx_2_2_curText != "":
					self.cbx_2_2.setCurrentText(self.cbx_2_2_curText)
				elif config["set_1"]["fdQun"] != "":
					self.cbx_2_2.setCurrentText(config["set_1"]["fdQun"])
				elif cs2 != "":
					self.cbx_2_2.setCurrentText(cs2)
		# except Exception as e:
		# 	print("getChatList.error", e)
		# 	if self.tryTime < 4:
		# 		self.tryTime += 1
		# 		if config["set_1"]["hookMd"] == 1:
		# 			time.sleep(0.4)
		# 			self.startMyShou()
		# 		elif config["set_1"]["hookMd"] == 2:
		# 			time.sleep(0.4)
		# 			self.startMyShou("ConsoleApp4.exe")

	def sendTextMsg0Aft(self):
		if len(GM["waitMsgTab"]) > 0:
			tab = GM["waitMsgTab"][0]
			GM["waitMsgTab"].pop(0)
			self.sendTextMsg0(tab[0], tab[1], False)


	# 发送 文本消息
	def sendTextMsg0(self, msg, wxid = "", needWait=True):
		if wxid == "":
			# 接单群
			if self.cbx_2_1.currentIndex() > -1:
				wxid = self.getJieDanQun1()

		if wxid != "" and msg != "":
			# if GM["debug"]:
			# 	utils.info("sendTextMsg", wxid, msg)
				
			if needWait and config["more"]["waitSd"]:
				diffTime = GM["updateAllTime"] - self.lastSendTime
				print("diffTime", diffTime)
				if diffTime < config["more"]["lsTime"]:
					GM["waitMsgTab"].append([msg, wxid])
					self.pushDelay( (len(GM["waitMsgTab"])+len(GM["waitImgTab"]))*config["more"]["wTime"]/100, self.sendTextMsg0Aft)
					return
			self.lastSendTime = GM["updateAllTime"]
			url = GM["baseApi"]
			json2 = {
				"type": 1,
				"wxid": wxid,
				"msg": msg
			}
			if config["set_1"]["noWx"]:
				return
			# 走到了这里就是肯定有发
			if config["set_1"]["hookMd"] == 1:
				url = GM["baseApi"] + "SendTextMsg"
			elif config["set_1"]["hookMd"] == 2:
				url = GM["baseApi"] + "send_text_msg"
			try:
				data = web.post(url, [], json2)
				if data.status_code == 200:
					mJson = json.loads(data.text)
					print("sendTextMsg", mJson)
					# mJson-{'result': '请求已经被成功处理'}

				msg2 = msg.replace("\n", "~")
				name = ""
				if wxid in self.wxAllDic:
					name = self.wxAllDic[wxid]["nickname"]
				if wxid in GM["AppDic"]:
					name = GM["AppDic"][wxid]["nick_name"]
				elif wxid in GM["BackDic"]:
					name = GM["BackDic"][wxid]["nick_name"]
				msg3 = ""
				if "@chatroom" in wxid:
					# 群聊
					msg3 = "To群聊:["+name+"]("+wxid+")"
				if GM["qy"] in wxid:
					# 企业群
					msg3 = "To企业群:["+name+"]("+wxid+")"
				else:
					msg3 = "To个人:["+name+"]("+wxid+")"
				utils.info4TongXun(msg3+msg2)
			except Exception as e:
				pass

	# GM["mdImgs"] GM["mdIds"]
	def createTxtImg(self, msg, wxid):
		if msg in GM["mdImgs"]:
			return GM["mdImgs"][msg]

		tab = msg.split("\n")
		if len(tab) > 10:
			self.sendTextMsg0(msg, wxid)
			return False

		rand = random.randint(100000,900000)
		if rand in GM["mdIds"]:
			rand = random.randint(100000,900000)
			if rand in GM["mdIds"]:
				rand = random.randint(100000,900000)
		rand = str(rand)
		if not os.path.exists(PATH_TEMP):
			os.makedirs(PATH_TEMP)
		path = os.path.join(PATH_TEMP, rand+".jpg")

		qp = QPainter(self)
		width = 510+random.randint(-10,10)
		height = 250+random.randint(-10,10)
		length = len(tab)
		if length > 7:
			height += (length-7)*33

		mMap = QPixmap(width, height)
		mMap.fill(Qt.white)
		qp.begin(mMap)

		if config["vs_cfg"]["vMoHu"]:
			if "imgZao" not in GM:
				sureImg()
			if "imgZao" in GM:
				rect = QRect(-1*random.randint(0,800),-1*random.randint(0,1200),GM["imgZao"].width()*1.8,GM["imgZao"].height()*1.8) 
				qp.drawImage(rect,GM["imgZao"])

		qp.setPen(QColor(Qt.darkRed))
		qp.setFont(QFont('Microsoft YaHei', 19))
		# qp.drawText(64,40,msg)
		for x in range(0,len(tab)):
			qp.drawText(20,30+x*32,tab[x])
			if config["vs_cfg"]["duoCai"]:
				yu = x%3
				if yu == 0:
					qp.setPen(QColor(Qt.black))
				elif yu == 1:
					rand2 = random.randint(1,3)
					if rand2 == 1:
						qp.setPen(QColor(Qt.red))
					elif rand2 == 2:
						qp.setPen(QColor(Qt.darkGreen))
					else:
						qp.setPen(QColor(Qt.darkBlue))
				else:
					qp.setPen(QColor(Qt.darkRed))

		qp.end()
		mMap.save(path, "JPG")

		GM["mdIds"][rand] = True
		GM["mdImgs"][msg] = path

		return path

	def sendTextMsg(self, msg, wxid = "", pKey = ""):
		if wxid == "":
			# 接单群
			if self.cbx_2_1.currentIndex() > -1:
				wxid = self.getJieDanQun1()

		if wxid != "" and msg != "":
			if pKey == "":
				self.sendTextMsg0(msg, wxid)
			elif config["vs_cfg"]["tuState"] == 1:
				self.sendTextMsg0(msg, wxid)
			elif config["vs_cfg"]["tuState"] == 2:
				if pKey != "" and pKey in config["direct"]:
					self.sendTextMsg0(msg, wxid)
				else:
					path = self.createTxtImg(msg, wxid)
					if path:
						self.sendImageMsg(path, wxid)
			else:
				path = self.createTxtImg(msg, wxid)
				if path:
					self.sendImageMsg(path, wxid)

	def sendImageMsgAft(self):
		if len(GM["waitImgTab"]) > 0:
			tab = GM["waitImgTab"][0]
			GM["waitImgTab"].pop(0)
			self.sendImageMsg(tab[0], tab[1], False)

	# 发送 图片
	def sendImageMsg(self, path, wxid = "", needWait=True):
		# if self.cbx_2_1.currentIndex() > -1:
		if self.canUseWx:
			print("sendImageMsg", path)
			# 说明wxQunTab 存在
			if wxid == "":
				wxid = self.getJieDanQun1()

			if self.sendWxId != "":
				wxid = self.sendWxId
				self.sendWxId = ""

			if needWait and config["more"]["waitSd"]:
				diffTime = GM["updateAllTime"] - self.lastSendTime
				print("diffTime", diffTime)
				if diffTime < config["more"]["lsTime"]:
					GM["waitImgTab"].append([path, wxid])
					self.pushDelay( (len(GM["waitMsgTab"])+len(GM["waitImgTab"]))*config["more"]["wTime"]/100, self.sendImageMsgAft)
					return
			
			self.lastSendTime = GM["updateAllTime"]
			url = GM["baseApi"]
			json2 = {
				"type": 2,
				"wxid": wxid,
				"imagepath": path
			}
			if config["set_1"]["noWx"]:
				return
			if config["set_1"]["hookMd"] == 1:
				url = GM["baseApi"] + "SendImageMsg"
				json2 = {
				    "wxid": wxid,
				    "path": path
				}
			elif config["set_1"]["hookMd"] == 2:
				url = GM["baseApi"] + "send_image_msg"
				json2 = {
				    "wxid": wxid,
				    "image_path": path
				}
			try:
				data = web.post(url, [], json2)
				if data.status_code == 200:
					mJson = json.loads(data.text)
					# print("sendImageMsg", mJson)
					# mJson-{'result': '请求已经被成功处理'}
			except Exception as e:
				pass


	# 发送结算图片
	def sendResultImage(self, maxPnum = 0):
		if maxPnum != 0:
			self.maxPnum = maxPnum
		if config["set_1"]["buJd"]:
			return
		path = self.createResult()
		if path:
			self.sendImageMsg(path)
		self.maxPnum = 0
		return path

	def _wxid_from_combo(self, combo):
		if combo is None or combo.currentIndex() < 0:
			return ""
		text = combo.currentText().strip()
		if "|" in text:
			return text.split("|", 1)[1].strip()
		idx = combo.currentIndex()
		if hasattr(self, "wxQunTab") and 0 <= idx < len(self.wxQunTab):
			return self.wxQunTab[idx].get("wxid", "") or ""
		return ""

	def getJieDanQun1(self):
		return self._wxid_from_combo(self.cbx_2_1)

	def getFdQun1(self):
		return self._wxid_from_combo(self.cbx_2_2)

	def sendResultImagePerson(self):
		path = self.createResult()
		if path:
			self.sendImageMsg(path)

		





if __name__ == '__main__':
    from main import main
    main()




