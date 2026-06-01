
from common_init import *
import utils

config = {}
config["softName"] = "ai微信直接聊"

config["baseSize"] = 21

# 给的初始金币
config["baseGolds"] = 0; 
# 开奖是第几期
config["prizeNum"] = 100000;

# scrollArea 状态
config["scStates"] = {
	"clean": 0,   # 清除状态 就是无状态
	"input": 1,   # 录入状态 包括上分 下注 下分
	"kaijiang": 2,# 开奖状态-其实就是结束状态
	# "zhangdan": 3,# 导入账单
}

config["dengl"] = {
	"rmb": 0,   # 记住用户
	"name": "", # 用户名
	"pass": "", # 密码
}

# 数据初始化 
def configInit():

	GM["configCopy"] = {}
	for key in config:
		GM["configCopy"][key] = utils.copyObj(config[key])

	GM["config"] = config
	# print("configCopy", GM["configCopy"]["main"])
	# print(GM["configCopy"])
	# print("哈", config["matchTab"])  # , config["matchDic"]

# 额外增加项
config["more"] = {
	"autoQl": 0, # pg1 自动清零
	"lsCha": 1,  # 拉手查询
	"fixDh": 0,  # fix dataHd
	"cha1": 1,
	"cha2": 1,
	"chaP": 1,
	"chaRp": "请稍候！",
	"waitSd": 1,
	"wTime": 17,  # 就是0.1
	"lsTime": 25, # 就是0.2
}

### 主页面部分
config["main"] = {
	"height": 530, # 高度
	"machine": "mckeyCreater"+str(random.randint(1000000,90000000)),
	"rcday": 1108483200, # 上一次做统计的日期 2005-2-16 每隔一天统计一次
	"chaX": "", # 上一次查询 得到的信息
}

config["control"] = {
	"ckFront": 1,  # 上下分窗口 本窗口始终在最前面
	"autoHide": 0, # 自动隐藏本窗口(上下分自动提示)
}

### 第四页 广告
config["ads"] = {
	"fpTime": "60",  # 封盘时间
	"fpImg": "fpImg.png",     # 封盘图片
	"ad1Time": "90",
	"ad1Img": "ad1Img.png",
	"ad2Time": "0",
	"ad2Img": "ad2Img.png",
	"tuTitle": "",   # 图片标题文字
	"zdAd": "", # 账单下面的广告
	"ckMp": 0,  # 改为推送名片

	"tid": "", # 推送id
	"ttx": "",       # 推送文字
}

### 第二页 设置
config["set_1"] = {
	"jiekou": 1,  # 接口选择
	"hookMd": 1,  # hook模式
	"jdQun": "",  # 接单群
	"fdQun": "",  # 飞单群
	"jdQy": 0,
	"fdQy": 0,
	"jdQyq": "",  # 接单企业群
	"fdQyq": "",  # 飞单企业群
	"buJd": 0,
	"buFd": 0,

	"noWx": 0,
}

config["set_2"] = {
	"zdAgree": 1,   # 自动同意好友 
	"zdMsg": "你好！财神科技欢迎您！",# 发送xxx
	"msg": "添加好友携带描述！",
}


### 设置页面 赔率部分
config["qy_qun"] = []

config["setRead"] = [
	# "pl_1314", "pl_fei1314", "pl_wanfa", "pl_ck", "xian_e", "set_ot", "pl_dl", "sz_fw", "machine",
	"qy_qun",
]



config["vs_cfg"] = {
	"choose": "2",
	"ziDing": 0,  # 使用自定义版本
	"tuState": 1, # 纯文字 半文字 全图
	"vMoHu": 1,   # 图片模糊处理
	"duoCai": 0,  # 图片多彩文字
	"faSan": 1,   # 玩家发送3查今日输赢明细
}



configInit();


# if __name__ == '__main__':
# 	# main()
# 	print("wocao")


# print(config)
