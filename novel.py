# coding=utf-8
# 2.7版本 字符串有两种编码格式（Unicode、utf-8） 防止输出错误

import function 	# 加载模块

def getNum():
	try:
		num = input('enter a number:')
	except Exception as e:
		num = getNum()
	return num

if __name__ == '__main__':	
	function.init()

	print('*************************')
	print('1: update novels in menu')
	print('2: update novels libs')
	print('3: fixed missing chapter in libs')
	print('*************************')

	index = getNum()
	if index == 1:
		function.start()
	else:
		function.checkUpdateDictionaryLib(index == 3)

