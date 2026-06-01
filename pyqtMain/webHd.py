
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


def _str_field(obj, default=""):
	if obj is None:
		return default
	if isinstance(obj, dict):
		return (obj.get("String") or obj.get("string") or default).strip()
	return str(obj).strip()


def _normalize_hook_message(raw):
	"""将各 Hook 回调格式统一为 handleWxMsg 可用的字段。"""
	if not raw or not isinstance(raw, dict):
		return None

	hook_md = int(config["set_1"].get("hookMd", 1))

	if "bsMsg" in raw:
		out = dict(raw)
		out["msgtype"] = out.get("msgtype", 1)
		return out

	if hook_md == 1:
		if "data" in raw and isinstance(raw["data"], dict):
			zero = raw["data"]
			out = {
				"msgtype": zero.get("type", 1),
				"wxid": zero.get("session", ""),
				"content": zero.get("content", ""),
				"sendorrecv": str(raw.get("sendorrecv", "2")),
			}
			qy = GM.get("qy", "")
			if qy and qy in out["wxid"]:
				out["bizchat_id"] = out["wxid"]
			return out

		if "content" in raw:
			out = dict(raw)
			out.setdefault("msgtype", 1)
			room = (raw.get("RoomName") or raw.get("room_wxid") or "").strip()
			if room:
				out["room_wxid"] = room
			wxid = (raw.get("wxid") or "").strip()
			if "@chatroom" in wxid and not out.get("room_wxid"):
				out["room_wxid"] = wxid
			return out

		if "signature" in raw:
			out = dict(raw)
			out.setdefault("msgtype", 1)
			if "bizchat_id" in raw["signature"]:
				match = re.search(r"<bizchat_id>(.*?)</bizchat_id>", raw["signature"])
				if match:
					out["bizchat_id"] = match.group(1)
					return out
			return None

		return None

	if hook_md == 2:
		# 模式2 常见三种回调：msglist / 微信协议字段 / 扁平 JSON(RoomName+content)
		if "msglist" in raw and raw.get("msglist"):
			zero = raw["msglist"][0]
			if not ("msgtype" in zero and "fromid" in zero and "msg" in zero):
				return None
			msgtype = int(zero.get("msgtype", 1))
			if msgtype not in (1, 37):
				return None
			out = {
				"msgtype": msgtype,
				"wxid": zero.get("fromid", ""),
				"content": zero.get("msg", ""),
				"sendorrecv": str(raw.get("sendorrecv", "2")),
			}
			msgsource = zero.get("msgsource") or ""
			if "bizchat_id" in msgsource:
				match = re.search(r"<bizchat_id>(.*?)</bizchat_id>", msgsource)
				if match:
					out["bizchat_id"] = match.group(1)
			room = (
				raw.get("RoomName") or raw.get("room_wxid")
				or zero.get("toid") or ""
			).strip()
			if room:
				out["room_wxid"] = room
			elif "@chatroom" in out["wxid"]:
				out["room_wxid"] = out["wxid"]
			return out

		if "MsgType" in raw or "FromUserName" in raw:
			msgtype = int(raw.get("MsgType", raw.get("msgtype", 1)))
			if msgtype not in (1, 37):
				return None
			out = {
				"msgtype": msgtype,
				"wxid": _str_field(raw.get("FromUserName")),
				"content": _str_field(raw.get("Content")),
				"sendorrecv": str(raw.get("sendorrecv", "2")),
			}
			room = (raw.get("RoomName") or raw.get("room_wxid") or "").strip()
			if room:
				out["room_wxid"] = room
			elif "@chatroom" in out["wxid"]:
				out["room_wxid"] = out["wxid"]
			msg_source = _str_field(raw.get("MsgSource"))
			if "bizchat_id" in msg_source:
				match = re.search(r"<bizchat_id>(.*?)</bizchat_id>", msg_source)
				if match:
					out["bizchat_id"] = match.group(1)
			return out

		if "content" in raw:
			out = dict(raw)
			out.setdefault("msgtype", 1)
			room = (raw.get("RoomName") or raw.get("room_wxid") or "").strip()
			if room:
				out["room_wxid"] = room
			wxid = (raw.get("wxid") or "").strip()
			if "@chatroom" in wxid and not out.get("room_wxid"):
				out["room_wxid"] = wxid
			return out

		return None

	return None


def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'application/json')])
	print("wocao.application")
	if environ["REQUEST_METHOD"] == "GET":
		return [b'{"state":"wxno.get"}', ]

	# if GM["mainScene"].hasLogin == False:
	# 	return [b'{"state":"wxno.noLogin"}', ]
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
		# if GM["debug"]:
		print("json_str", json_str)
		json_dict = json.loads(json_str) #（注意：key值必须双引号）
		# print("json_dict", json_dict)
		# return [b'rtn.welcome', ]
		json_dict = _normalize_hook_message(json_dict)
		if json_dict is None:
			return [b'welcome', ]

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
		print("webHd.application.err", e)
		import traceback
		traceback.print_exc()
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
		if config["set_1"]["hookMd"] == 2:
			self.openServer4()
		elif config["set_1"]["hookMd"] == 1:
			self.openServer3()

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

