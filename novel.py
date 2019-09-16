# coding=utf-8

from MyClass import Helper
import Function

def UpdateNovelChapter():
	Function.updateChapters()

def UpdateNovelLib():
	Function.updateLib()

def ResetNovelLib():
	Function.resetLib()

def Quit():
	quit()

def defalt():
	Helper.printError(string = "can't find funcName")

def init():
	funcData = {
		"1" : {"idx" : 1, "funcName" : "UpdateNovelChapter"},
		"2" : {"idx" : 2, "funcName" : "UpdateNovelLib"},
		"3" : {"idx" : 3, "funcName" : "ResetNovelLib"},
		"0" : {"idx" : 0, "funcName" : "Quit"},
	}

	Helper.printLine()
	for data in funcData.values():
		Helper.print(string = '{}: {}'.format(data.get("idx"),data.get("funcName")))
	Helper.printLine()


	checkDone = False
	while not checkDone:
		try:
			data = funcData.get(str(Helper.getNum()),{})
			if data:
				checkDone = True
				funcName = data.get('funcName','defalt')
				func = globals().get(funcName)
				func()
		except Exception as e:
			Helper.printError()
			raise e
	

if __name__ == '__main__':
	# 初始化lib novel name txt文件
	Function.init()
	# init()
	# 死循环
	while True:
		init()




