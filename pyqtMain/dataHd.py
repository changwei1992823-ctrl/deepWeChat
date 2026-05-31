# -*- coding:utf-8 -*-
from PyQt5 import QtSql

from common_init import *
from config import *
import utils

# 数据处理 

class dataHandle(object):
	"""docstring for dataHandle"""
	def __init__(self):
		super(dataHandle, self).__init__()
		# self.arg = arg
		self.mInit()

	def mInit(self):
		self.connect_db()

		self.initTabConfig()
		self.initTabApp()


		self.initTabRole()
		self.initTabRizhi()

		self.findAllApp()
		self.findAllRole()
		self.findAllBack()
		
		self.findAllRizhi()

		for key in config["setRead"]:
			self.readConfig(key)


	def getAppById (self, app_id):
		# {"app_id": app_id, "nick_name": nick_name, "golds": golds}
		if app_id in GM["AppDic"]:
			return GM["AppDic"][app_id]
		else:
			# 数据库去查询
			role = self.findAppWithAppid(app_id)
			return role


	"""
	创建or连接数据库
	"""
	def connect_db(self):
		try:
			self.db_name = "db"
			# 添加一个sqlite数据库连接并打开
			db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
			db.setDatabaseName('{}.sqlite'.format(self.db_name))
			db.open()
			# print("connect_db_success")
		except Exception as e:
			print("connect_db_fail", e)
			pass

		self.query = QtSql.QSqlQuery()
		
	"""
	单机调试的主函数
	"""
	def main(self):
		pass

	def readConfig(self, key):
		data = self.getConfigByKey(key)
		if data:
			try:
			# if True:
				data = json.loads(data["value"])
				if GM["typeDic"] == type(data):
					dataBef = config[key]
					for x in data:
						if x in dataBef:
							if type(dataBef[x]) == type(data[x]):
								dataBef[x] = data[x]
							else:
								if (type(dataBef[x]) == GM["typeInt"] or type(dataBef[x]) == GM["typeFlo"]) and (type(data[x]) == GM["typeInt"] or type(data[x]) == GM["typeFlo"]):
									dataBef[x] = data[x]
								else:
									print("类型不一致", dataBef[x], data[x], type(dataBef[x]), type(data[x]))
						else:
							dataBef[x] = data[x]
				else:
					config[key] = data
			except Exception as e:
				print("err.readConfig", key)
		else:
			dataStr = json.dumps(config[key])
			# if key in config["version_1"]:
			# 	pass
			# else:
			# 	dataStr = dataStr.replace(" ", "")
			self.saveConfig(key, dataStr)


	def updateConfigBef(self, key, value):
		if config[key] != value:
			self.updateConfig(key, value)

	def updateConfig(self, key, value):
		query = QtSql.QSqlQuery()
		# 字典或者数组
		if type(value) == int:
			value = str(value)
		elif type(value) != str:
			# dataStr = json.dumps(config[key])
			dataStr = json.dumps(value)
			value = dataStr.replace(" ", "")
		mStr = f"UPDATE love_config SET value = '{value}' WHERE key = '{key}' "
		print("updateConfig.mStr", mStr)
		# utils.info("updateConfig:\n", mStr)
		query.exec_(mStr)
		if key in self.needSaveDic:
			key_what = self.needSaveDic[key]
			value2 = value
			if "'" in value2:
				value2 = value2.replace("'", "").replace("'", "")
			if '"' in value2:
				value2 = value2.replace('"', "").replace('"', "")
			try:
				value2 = value2.encode().decode('unicode_escape')
				dic = {"m_type": 5, "do_what": "修改:"+key_what+"=>"+value2}
				self.addRizhi(dic)
			except Exception as e:
				pass
			

	def saveConfig(self, key, value):
		mStr = f"INSERT INTO love_config (key, value) VALUES ('{key}','{value}')"
		# mStr INSERT INTO love_wager (app_id, qq_time, golds, left_golds) VALUES ('10086','2020-08-20 19:59:23',100,9998)
		print("saveConfig.mStr", mStr)
		self.query.exec_(mStr)

	def getConfigByKey(self, key):
		query = QtSql.QSqlQuery()
		mStr = f"SELECT * FROM love_config WHERE key = '{key}' "
		# print("getConfigByKey.mStr", mStr)
		result = None
		if query.exec_(mStr):
			while query.next():
				key = query.value(0)
				value = query.value(1)
				result = {"key": key, "value": value}
		
		return result

	"""
	初始化-用户信息表-App
	"""
	def initTabConfig(self):
		try:
			# 创建一个数据库表
			self.query.exec_("""CREATE TABLE "love_config" (
				"key" varchar(32) NOT NULL PRIMARY KEY,
				"value" varchar(4096) NOT NULL)
			""")
		except Exception as e:
			print(e)

	# 被删除的人 qq 昵称 可以一开始全部读取 被继承后 消失
	def initTabRole(self):
		try:
			# 创建一个数据库表
			self.query.exec_("""CREATE TABLE "love_role" (
				"app_id" varchar(32) NOT NULL PRIMARY KEY,
				"nick_name" varchar(64) NOT NULL,
				"wxcount" varchar(64) DEFAULT NULL)
			""")
		except Exception as e:
			print(e)

	# 人物 信息
	def addRole(self, dic):
		mStr = f"INSERT INTO love_role (app_id, nick_name, wxcount) VALUES ('{dic['app_id']}','{dic['nick_name']}','{dic['wxcount']}')"
		print("addRole.mStr", mStr)
		self.query.exec_(mStr)
		if dic['app_id'] not in GM["RoleDic"]:
			# del GM["RoleDic"][app_id] 
			GM["RoleDic"][ dic['app_id'] ] = dic

	def deleteRole(self, app_id):
		mStr = f"DELETE FROM love_role WHERE app_id = '{app_id}' "
		self.query.exec_(mStr)

		if app_id in GM["RoleDic"]:
			del GM["RoleDic"][app_id]  

	# 列出所有被删除的人
	def findAllRole(self):
		query = QtSql.QSqlQuery()
		mStr = f"SELECT * FROM love_role"
		print("findAllRole.mStr", mStr)
		# tab = []
		if query.exec_(mStr):
			while query.next():
				app_id = query.value(0)
				nick_name = query.value(1)
				wxcount = query.value(2)
				role = {"app_id": app_id, "nick_name": nick_name, "wxcount": wxcount}
				# tab.append(role)
				GM["RoleDic"][app_id] = role

	# 修改昵称
	def updateRoleName(self, app_id, nick_name):
		# UPDATE Person SET Address = 'Zhongshan 23', City = 'Nanjing'
		# WHERE LastName = 'Wilson'
		query = QtSql.QSqlQuery()
		mStr = f"UPDATE love_role SET nick_name = '{nick_name}' WHERE app_id = '{app_id}' "
		print("mStr", mStr)
		query.exec_(mStr)

		if app_id in GM["RoleDic"]:
			GM["RoleDic"][app_id]["nick_name"] = nick_name

	def updateRoleWxcount(self, app_id, wxcount):
		query = QtSql.QSqlQuery()
		mStr = f"UPDATE love_role SET wxcount = '{wxcount}' WHERE app_id = '{app_id}' "
		print("mStr", mStr)
		query.exec_(mStr)

		if app_id in GM["RoleDic"]:
			GM["RoleDic"][app_id]["wxcount"] = wxcount

	# 被删除的人 qq 昵称 可以一开始全部读取 被继承后 消失
	def initTabBack(self):
		try:
			# 创建一个数据库表
			self.query.exec_("""CREATE TABLE "love_back" (
				"app_id" varchar(32) NOT NULL PRIMARY KEY,
				"nick_name" varchar(64) NOT NULL)
			""")
		except Exception as e:
			print(e)

	# 人物 信息
	def addBack(self, dic):
		mStr = f"INSERT INTO love_back (app_id, nick_name) VALUES ('{dic['app_id']}','{dic['nick_name']}')"
		print("addBack.mStr", mStr)
		self.query.exec_(mStr)
		if dic['app_id'] not in GM["BackDic"]:
			# del GM["BackDic"][app_id] 
			GM["BackDic"][ dic['app_id'] ] = dic

	def deleteBack(self, app_id):
		mStr = f"DELETE FROM love_back WHERE app_id = '{app_id}' "
		self.query.exec_(mStr)

		if app_id in GM["BackDic"]:
			del GM["BackDic"][app_id]

	# 修改昵称
	def updateBackName(self, app_id, nick_name):
		query = QtSql.QSqlQuery()
		mStr = f"UPDATE love_back SET nick_name = '{nick_name}' WHERE app_id = '{app_id}' "
		print("mStr", mStr)
		query.exec_(mStr)

		if app_id in GM["BackDic"]:
			GM["BackDic"][app_id]["nick_name"] = nick_name


	# 列出所有被删除的人
	def findAllBack(self):
		query = QtSql.QSqlQuery()
		mStr = f"SELECT * FROM love_back"
		print("findAllBack.mStr", mStr)
		# tab = []
		if query.exec_(mStr):
			while query.next():
				app_id = query.value(0)
				nick_name = query.value(1)
				if "|" in nick_name:
					nick_name = nick_name.replace("|", "或").replace("|", "或")
				if "'" in nick_name:
					nick_name = nick_name.replace("'", "点").replace("'", "点")
				if '"' in nick_name:
					nick_name = nick_name.replace('"', "点").replace('"', "点")
				if "[" in nick_name:
					nick_name = nick_name.replace("[", "k").replace("[", "k")
				if "]" in nick_name:
					nick_name = nick_name.replace("]", "k").replace("]", "k")
				if "@" in nick_name:
					nick_name = nick_name.replace("@", "a").replace("@", "a")
				role = {"app_id": app_id, "nick_name": nick_name}
				# tab.append(role)
				GM["BackDic"][app_id] = role

	"""
	初始化-用户信息表-App
	"""
	def initTabApp(self):
		try:
			# 创建一个数据库表
			self.query.exec_("""CREATE TABLE "love_app" (
				"app_id" varchar(32) NOT NULL PRIMARY KEY,
				"nick_name" varchar(64) NOT NULL,
				"golds" integer NOT NULL)
			""")

			# 插入数据
			"""
			self.addApp({
				"app_id": "10086", 
				"nick_name": "简易昵称",
				"golds": 900
			})
			# self.deleteApp("10086")
			
			"""

		except Exception as e:
			print(e)

	# 人物 信息
	def addApp(self, dic):
		print("addApp", dic)
		mStr = f"INSERT INTO love_app (app_id, nick_name, golds) VALUES ('{dic['app_id']}','{dic['nick_name']}',{dic['golds']})"
		print("addApp.mStr", mStr)
		self.query.exec_(mStr)

		if dic["app_id"] not in GM["AppDic"]:
			GM["AppDic"][dic["app_id"]] = dic

		if dic["app_id"] not in GM["BackDic"]:
			self.addBack(dic)

		# if dic['app_id'] not in GM["AppDic"]:
		# 	GM["AppDic"][ dic['app_id'] ] = dic


	def deleteApp(self, app_id):
		mStr = f"DELETE FROM love_app WHERE app_id = '{app_id}' "
		self.query.exec_(mStr)

		if app_id in GM["AppDic"]:
			if app_id in GM["BackDic"]:
				if GM["BackDic"][app_id]["nick_name"] != GM["AppDic"][app_id]["nick_name"]:
					self.updateBackName(app_id, GM["AppDic"][app_id]["nick_name"])
			else:
				self.addBack(GM["AppDic"][app_id])

			del GM["AppDic"][app_id]

	# 列出所有人
	def findAllApp(self):
		query = QtSql.QSqlQuery()
		mStr = f"SELECT * FROM love_app"
		print("findAllApp.mStr", mStr)
		# tab = []
		if query.exec_(mStr):
			while query.next():
				app_id = query.value(0)
				nick_name = query.value(1)
				if "|" in nick_name:
					nick_name = nick_name.replace("|", "或").replace("|", "或")
				if "'" in nick_name:
					nick_name = nick_name.replace("'", "点").replace("'", "点")
				if '"' in nick_name:
					nick_name = nick_name.replace('"', "点").replace('"', "点")
				if "[" in nick_name:
					nick_name = nick_name.replace("[", "k").replace("[", "k")
				if "]" in nick_name:
					nick_name = nick_name.replace("]", "k").replace("]", "k")
				if "@" in nick_name:
					nick_name = nick_name.replace("@", "a").replace("@", "a")
				golds = query.value(2)
				role = {"app_id": app_id, "nick_name": nick_name, "golds": golds}
				# tab.append(role)
				GM["AppDic"][app_id] = role
		# return tab

	# app需求扩展-查询一个人是否存在
	def findAppWithAppid(self, app_id):
		if app_id in GM["AppDic"]:
			return GM["AppDic"][app_id]

		query = QtSql.QSqlQuery()
		mStr = f"SELECT * FROM love_app WHERE app_id = '{app_id}' "
		print("findAppWithAppid.mStr", mStr)
		role = None
		if query.exec_(mStr):
			while query.next():
				app_id = query.value(0)
				nick_name = query.value(1)
				golds = query.value(2)
				role = {"app_id": app_id, "nick_name": nick_name, "golds": golds}

		print("role", role)
		if role == None:
			role = self.createAppDefault(app_id)
			return role
		else:
			GM["AppDic"][app_id] = role
			return role

	def hasAppAppid(self, app_id):
		# 只说 yes or no 有没有这个app_id
		if app_id in GM["AppDic"]:
			return True
		else:
			return False

		query = QtSql.QSqlQuery()
		mStr = f"SELECT * FROM love_app WHERE app_id = '{app_id}' "
		# print("hasAppAppid.mStr", mStr)
		role = None
		if query.exec_(mStr):
			while query.next():
				app_id = query.value(0)
				nick_name = query.value(1)
				golds = query.value(2)
				role = {"app_id": app_id, "nick_name": nick_name, "golds": golds}
		if role == None:
			return False
		else:
			GM["AppDic"][app_id] = role
			return True

	def findAppAppid(self, app_id):
		if app_id in GM["AppDic"]:
			return GM["AppDic"][app_id]

		query = QtSql.QSqlQuery()
		mStr = f"SELECT * FROM love_app WHERE app_id = '{app_id}' "
		print("findAppAppid.mStr", mStr)
		role = None
		if query.exec_(mStr):
			while query.next():
				app_id = query.value(0)
				nick_name = query.value(1)
				golds = query.value(2)
				role = {"app_id": app_id, "nick_name": nick_name, "golds": golds}

		if role == None:
			# 没有就说没有
			return role
		else:
			if app_id not in GM["AppDic"]:
				GM["AppDic"][app_id] = role
			return role

	# 创建 一个人的默认值
	def createAppDefault(self, app_id, nick_name = "默认"):
		# print()
		if nick_name == "默认" and "tmpMsg" in GM and GM["tmpMsg"]:
			# and "name" in GM["tmpMsg"]
			if "name" in GM["tmpMsg"]:
				nick_name = GM["tmpMsg"]["name"][0:2]
			elif "nick_name" in GM["tmpMsg"]:
				nick_name = GM["tmpMsg"]["nick_name"][0:2]
			if "|" in nick_name:
				nick_name = nick_name.replace("|", "或").replace("|", "或")
			if "'" in nick_name:
				nick_name = nick_name.replace("'", "点").replace("'", "点")
			if '"' in nick_name:
				nick_name = nick_name.replace('"', "点").replace('"', "点")
			if "[" in nick_name:
				nick_name = nick_name.replace("[", "k").replace("[", "k")
			if "]" in nick_name:
				nick_name = nick_name.replace("]", "k").replace("]", "k")
			if "@" in nick_name:
				nick_name = nick_name.replace("@", "a").replace("@", "a")

			if "'" in nick_name:
				nick_name = nick_name.replace("'", "点").replace("'", "点")
			if '"' in nick_name:
				nick_name = nick_name.replace('"', "点").replace('"', "点")
			if "[" in nick_name:
				nick_name = nick_name.replace("[", "k").replace("[", "k")
			if "]" in nick_name:
				nick_name = nick_name.replace("]", "k").replace("]", "k")
			if "@" in nick_name:
				nick_name = nick_name.replace("@", "a").replace("@", "a")

		# if nick_name
		dic = {
			"app_id": app_id, 
			"nick_name": nick_name,
			"golds": config["baseGolds"]
		}

		self.addApp(dic)
		return dic

	# 修改剩余金币
	def updateAppGolds(self, app_id, golds):
		# UPDATE Person SET Address = 'Zhongshan 23', City = 'Nanjing'
		# WHERE LastName = 'Wilson'
		query = QtSql.QSqlQuery()
		mStr = f"UPDATE love_app SET golds = {golds} WHERE app_id = '{app_id}' "
		print("mStr", mStr)
		query.exec_(mStr)

		if app_id in GM["AppDic"]:
			# 做记录 0-不做处理 1-上分 2-下分 3-手动修改即管控 4-回水
			if GM["goldMgType"]:
				dic = {
					"app_id": app_id,
					"bef_golds": GM["AppDic"][app_id]["golds"],
					"golds": golds
				}
				self.addGoldMg(dic)

			GM["AppDic"][app_id]["golds"] = golds



	# 修改昵称
	def updateAppName(self, app_id, nick_name):
		# UPDATE Person SET Address = 'Zhongshan 23', City = 'Nanjing'
		# WHERE LastName = 'Wilson'
		if "|" in nick_name:
			nick_name = nick_name.replace("|", "或").replace("|", "或")
		if "'" in nick_name:
			nick_name = nick_name.replace("'", "点").replace("'", "点")
		if '"' in nick_name:
			nick_name = nick_name.replace('"', "点").replace('"', "点")
		if "[" in nick_name:
			nick_name = nick_name.replace("[", "k").replace("[", "k")
		if "]" in nick_name:
			nick_name = nick_name.replace("]", "k").replace("]", "k")
		if "@" in nick_name:
			nick_name = nick_name.replace("@", "a").replace("@", "a")

		if "'" in nick_name:
			nick_name = nick_name.replace("'", "点").replace("'", "点")
		if '"' in nick_name:
			nick_name = nick_name.replace('"', "点").replace('"', "点")
		if "[" in nick_name:
			nick_name = nick_name.replace("[", "k").replace("[", "k")
		if "]" in nick_name:
			nick_name = nick_name.replace("]", "k").replace("]", "k")
		if "@" in nick_name:
			nick_name = nick_name.replace("@", "a").replace("@", "a")
		query = QtSql.QSqlQuery()
		mStr = f"UPDATE love_app SET nick_name = '{nick_name}' WHERE app_id = '{app_id}' "
		print("mStr", mStr)
		query.exec_(mStr)

		if app_id in GM["AppDic"]:
			GM["AppDic"][app_id]["nick_name"] = nick_name

		if app_id in GM["BackDic"]:
			if GM["BackDic"][app_id]["nick_name"] != nick_name:
				self.updateBackName(app_id, nick_name)
		else:
			self.addBack(dic)

	

	"""
	初始化-Rizhi
	"""
	def initTabRizhi(self):
		try:
			self.query.exec_("""CREATE TABLE "love_rizhi" (
				"m_type" integer NOT NULL,
				"do_what" varchar(256) NOT NULL,
				"fw_time" datetime NOT NULL)
			""")
		except Exception as e:
			print(e)

	def deleteUnUseRizhi(self):
		# 删除没用的数据
		nowTime = datetime.now().timestamp() + GM["dfTime"] - GM["webConfig"]["keepDay"]/2*GM["oneDay"]
		useDay = datetime.fromtimestamp(nowTime).strftime('%Y-%m-%d %H:%M:%S')
		mStr = f"DELETE FROM love_rizhi WHERE fw_time < '{useDay}'"
		self.query.exec_(mStr)

	def addRizhi(self, dic):
		now = utils.getNowTime()
		# print("addRizhi", now)
		dic["fw_time"] = now
		mStr = f"INSERT INTO love_rizhi (m_type, do_what, fw_time) VALUES ({dic['m_type']},'{dic['do_what']}','{now}')"
		# print("mStr", mStr)
		self.query.exec_(mStr)
		GM["rizhiTab"].append(dic)


	def findAllRizhi(self):
		self.deleteUnUseRizhi()
		query = QtSql.QSqlQuery()
		mStr = f"SELECT * FROM love_rizhi"
		if query.exec_(mStr):
			while query.next():
				m_type = query.value(0)
				do_what = query.value(1)
				fw_time = query.value(2)
				dic = {"m_type": m_type, "do_what": do_what, "fw_time": fw_time}
				GM["rizhiTab"].append(dic)


dataHandleObj = dataHandle();

if __name__ == '__main__':
	# dataHandleObj.main()
	pass