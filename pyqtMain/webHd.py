
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from common_init import *
from config import *
import utils

from wsgiref.simple_server import make_server
import urllib.parse
import re
import stopThreading

# 接收post请求处理 发送请求之类的

"""
{
	'ServerPort': '30001',
	'selfwxid': 'wxid_63f2olu8w7q922',
	'sendorrecv': '2',
	'msgnumber': '1',
	'msglist': [{
		'index': '1',
		'time': '2024-05-09 01:01:25',
		'msgtype': '1',
		'msgsvrid': '9597616806269721424',
		'msg': '1',
		'fromtype': '1',
		'fromid': 'woaizhengyouru',
		'toid': ''
	}]
}

{
    "msgtype":1,
    "wxid":"filehelper",
    "RoomName":"xxx",
    "content":"xxxxx",
    "filepath":"xxxxx",
    "sender":"xxxxxx",
    "SendNickName":"xxxxxx",
    "source":"xxxxxxx",
    "isphonemsg":"xxxxxxx",
    "selfwxid":"xxxxxxx",
    "timestamp":"xxxxx",
    "port":"xxxxx",
    "atuserlist": "[{'nickname': 'xxxx', 'wxid': 'xxxx'}]"
}
"""

def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'application/json')])
	# print("wocao.application")
	if environ["REQUEST_METHOD"] == "GET":
		return [b'{"state":"wxno.get"}', ]

	if GM["mainScene"].hasLogin == False:
		return [b'{"state":"wxno.noLogin"}', ]
	try:
	# if True:
		# 定义文件请求的类型和当前请求成功的code
		# start_response('200 OK', [('Content-Type', 'application/json')])
		# environ是当前请求的所有数据，包括Header和URL，body
		request_body = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH", 0)))
		# print("request_body", request_body)
		json_str = request_body.decode('utf-8') # byte 转 str
		json_str = json_str.replace("amsg=", "")
		json_str = re.sub('\'','\"', json_str) # 单引号转双引号, json.loads 必须使用双引号
		if "xml" in json_str or "<msg>" in json_str:
			print("不能解析字符串", json_str)
			return [b'welcome', ]
		if GM["debug"]:
			print("json_str", json_str)
		json_dict = json.loads(json_str) #（注意：key值必须双引号）
		# print("json_dict", json_dict)
		# return [b'rtn.welcome', ]
		if "bsMsg" in json_dict:
			bsMsg = json_dict["bsMsg"]
			json_dict["msgtype"] = 1
			# json2["wxid"] = zero
			# json2["content"] = zero["Content"]["String"]
		else:
			# 消息
			if config["set_1"]["hookMd"] == 1:
				json2 = {}
				zero = json_dict["data"]
				json2["msgtype"] = zero["type"]
				if "@qy_u" in zero["session"]:
					# print("来自企业.个人")
					return [b'{"state":"ok"}', ]
				json2["wxid"] = zero["session"]
				# json2["wxid"] = zero["to"]
				if GM["qy"] in zero["session"]:
					json2["bizchat_id"] = json2["wxid"]
				json2["content"] = zero["content"]
				# json2["msgsource"] = zero["MsgSource"]
				json_dict = json2
			elif config["set_1"]["hookMd"] == 2:
				json2 = {}
				# print("-1", len(json_dict["msglist"]), len(json_dict["msglist"]) < 1)
				if len(json_dict["msglist"]) < 1:
					return [b'welcome', ]
				# print("0000")
				zero = json_dict["msglist"][0]
				if "msgtype" in zero and "fromid" in zero and "msg" in zero:
					json2["msgtype"] = int(zero["msgtype"])
					json2["wxid"] = zero["fromid"]
					json2["content"] = zero["msg"]
					if "msgsource" in zero:
						if "bizchat_id" in zero["msgsource"]:
							match = re.search(r'<bizchat_id>(.*?)</bizchat_id>', zero["msgsource"])
							if match:
								bizchat_id_content = match.group(1)
								json2["bizchat_id"] = bizchat_id_content
							else:
								return [b'welcome', ]
					# print("111", json2)
					if json2["msgtype"] == 1 or json2["msgtype"] == 37:
						json_dict = json2
					else:
						return [b'welcome', ]
					# print("2222", json_dict)
				else:
					return [b'welcome', ]
			elif config["set_1"]["hookMd"] == 3:
				if "signature" in json_dict:
					if "bizchat_id" in json_dict["signature"]:
						match = re.search(r'<bizchat_id>(.*?)</bizchat_id>', json_dict["signature"])
						if match:
							bizchat_id_content = match.group(1)
							json_dict["bizchat_id"] = bizchat_id_content
						else:
							return [b'welcome', ]
			elif config["set_1"]["hookMd"] == 4:
				json2 = {}
				zero = json_dict
				json2["msgtype"] = zero["MsgType"]
				json2["wxid"] = zero["FromUserName"]["String"]
				json2["content"] = zero["Content"]["String"]
				# json2["msgsource"] = zero["MsgSource"]
				if "bizchat_id" in zero["MsgSource"]:
					match = re.search(r'<bizchat_id>(.*?)</bizchat_id>', zero["MsgSource"])
					if match:
						bizchat_id_content = match.group(1)
						json2["bizchat_id"] = bizchat_id_content
					else:
						return [b'welcome', ]

				json_dict = json2

		if "content" not in json_dict:
			return [b'welcome', ]
		content = json_dict["content"].strip()
		if len(content) < 1:
			return [b'welcome', ]

		# return [b'welcome', ]
		this = GM["mainScene"]
		if this.json_dict1 == None:
			this.json_dict1 = json_dict
		elif this.json_dict2 == None:
			this.json_dict2 = json_dict
		elif this.json_dict3 == None:
			this.json_dict3 = json_dict
		else:
			this.json_dict4 = json_dict

		this.finish.emit()
		
	except Exception as e:
		pass
	return [b'{"state":"ok"}', ]

class webHandle(object):
	def __init__(self):
		super(webHandle, self).__init__()
		# self.mInit()
		self.sever_th = None

	def main(self):
		pass

	def mInit(self):
		# print("webHandle.mInit")
		pass

	def openServer(self):
		if config["set_1"]["hookMd"] == 4:
			self.openServer4()
		elif config["set_1"]["hookMd"] == 3:
			self.openServer3()
		elif config["set_1"]["hookMd"] == 2:
			self.openServer2()
		else:
			port = 8888
			httpd = make_server("0.0.0.0", port , application)
			print("serving http on port {0}...".format(str(port)))
			httpd.serve_forever()

	def openServer2(self):
		port = 8898
		httpd = make_server("0.0.0.0", port , application)
		print("serving http on port {0}...".format(str(port)))
		httpd.serve_forever()

	def openServer3(self):
		print("openServer3------")
		port = 8888
		httpd = make_server("0.0.0.0", port , application)
		print("serving http on port {0}...".format(str(port)))
		httpd.serve_forever()

	def openServer4(self):
		print("openServer4------")
		port = 8850
		httpd = make_server("0.0.0.0", port , application)
		print("serving http on port {0}...".format(str(port)))
		httpd.serve_forever()


	def startThread(self):
		print("webHandle.startThread")
		self.sever_th = threading.Thread(target=self.openServer)
		self.sever_th.start()
		pass

	def closeThread(self):
		try:
			if self.sever_th:
				stopThreading.stop_thread(self.sever_th)
				self.sever_th = None
		except Exception as e:
			pass


webHandleObj = webHandle();

if __name__ == "__main__":
	# dataHandleObj.main()
	pass

