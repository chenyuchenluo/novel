
# -- coding: utf-8 --
# 2.7版本 字符串有两种编码格式（Unicode、utf-8） 防止输出错误

import function 	# 加载模块

def getNum():
	try:
		num = int(input(u'请输入一个数：'))
	except Exception as e:
		num = getNum()
	return num

if __name__ == '__main__':	
	function.init()

	print u'*************************'
	print u'1:更新信息表中的小说'
	print u'2:更新本地小说库'
	print u'3:修复小说库中的遗漏编号'
	print u'*************************'

	index = getNum()
	if index == 1:
		function.start()
	else:
		function.checkUpdateDictionaryLib(index == 3)

