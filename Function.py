# -- coding: utf-8 --

import requests		# 发送网络请求
import threading 	# 线程
import time 		# 时间
import math 		# 数学
import json			# 解析
import re 			# 正则匹配
import sys 			# 系统
import os 			# 系统

from Stack import Stack # 栈
from MyClass import Helper
from MyClass import HTML

# 关闭证书验证
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SESSION = requests.session()
Html = HTML()
HOME_PATH = os.path.dirname((sys.argv[0])) + os.sep
NOVEL_PATH = HOME_PATH + 'novel' + os.sep
NOVEL_LIB_PATH = HOME_PATH + 'Libs' + os.sep

User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'

URLS = {
	'1':{'name':'biquke', 'url':'https://www.biquke.com/bq/{}/{}/'},
	'2':{'name':'gebiqu', 'url':'https://www.gebiqu.com/biquge_{}/'},
}

URL_LIMIT = {
	# count url中参数个数
	'biquke' : {'count':2},
	'gebiqu' : {'count':1},
}

Lib_Max_Count = 80000
Repeat_Max_Count = 10

def init():
	novels = open(HOME_PATH + 'name.txt','a+', encoding = 'utf-8')
	novels.close()

	global SearchNovels
	global StackFunc
	global StackUrls

	SearchNovels = []
	StackFunc = Stack()
	StackUrls = Stack()

	with open(HOME_PATH + 'name.txt','r', encoding = 'utf-8') as namesFile:
		for bookName in namesFile:
			if bookName != "\n" and bookName != "":
				SearchNovels.append(re.sub('\n','',bookName))

	if not os.path.exists(NOVEL_LIB_PATH):
		os.makedirs(NOVEL_LIB_PATH)
	for data in URLS.values():
		if not os.path.exists(NOVEL_PATH + data['name']):
			os.makedirs(NOVEL_PATH + data['name'])
		if not os.path.isfile(NOVEL_LIB_PATH + data['name'] + '.txt'):
			lib = open(NOVEL_LIB_PATH + data['name'] + '.txt','a+')
			lib.close()
		for name in SearchNovels:
			if not os.path.isfile(NOVEL_PATH + data['name'] + os.sep + name + '.txt'):
				book = open(NOVEL_PATH + data['name'] + os.sep + name + '.txt','a+')
				book.close()
				mulu = open(NOVEL_PATH + data['name'] + os.sep + name + '_目录.txt','a+')
				mulu.close()

# 初始化检查网站顺序
def initCheckUrlOrder():
	global StackFunc
	global StackUrls

	for data in URLS.values():
		func = data['name']
		url = data['url']

		StackFunc.push(func)
		StackUrls.push(url)


# 按初始顺序依次检查各网站
def checkNextUrl():
	global StackFunc
	global StackUrls
	global funcIndex

	if StackUrls.is_empty():
		Helper.print('Check WebUrl Done')
	else:
		name = StackFunc.pop()
		url = StackUrls.pop()

		if funcIndex == 1:
			checkBooks(name, url)
		elif funcIndex == 2:
			checkLib(name, url)
		else:
			pass


# 获取某本小说的所有章节的网页
def getBookChapterHtml(libIndex,libName,libUrl):
	baseUrl = re.search("www(.*?)/",libUrl).group()
	baseUrl = re.sub("/","",baseUrl)

	limitData = URL_LIMIT[libName]
	if limitData['count'] == 2:
		url = libUrl.format(math.floor(libIndex/1000),libIndex)
	if limitData['count'] == 1:
		url = libUrl.format(libIndex)

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		'Accept-Encoding':'gzip, deflate, br',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':baseUrl,
		'Referer': 'https://' + baseUrl,
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	questTimes = 0
	while questTimes < 2:
		try:
			html = SESSION.get(url, headers = headers, params = {}, verify = False, timeout = 3)
			return Helper.decodeHtml(html)
		except Exception as e:
			questTimes = questTimes + 1
			time.sleep(Helper.randomFloat())

	return ""


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# 更新小说章节
def updateChapters():
	global funcIndex
	funcIndex = 1

	initCheckUrlOrder()
	checkNextUrl()


def checkBooks(libName, libUrl):
	Helper.print("Check " + libName + " chapter")

	# 把lib里面的书按照 name=index 存到字典里
	Novel_Book = {}
	Lib = open(NOVEL_LIB_PATH + libName + '.txt','r+', encoding = 'utf-8')
	for line in Lib.readlines():
		line = re.sub('\n','',line)
		values = line.split('=')
		Novel_Book[values[0]] = values[1]
	Lib.close()

	# 判断库里有没有存这本书的索引
	bookSelect = 0
	while bookSelect < len(SearchNovels):
		bookName = SearchNovels[bookSelect]
		Helper.print("Update {} chapters".format(bookName))
		libIndex = int(Novel_Book.get(str(bookName),"0"))
		if libIndex != 0:
			checkChapters(libName, libUrl, libIndex, bookName)
		else:
			Helper.print("Can't find {} in {} lib".format(bookName,libName))

		bookSelect = bookSelect + 1
		time.sleep(Helper.randomFloat())

	checkNextUrl()


def checkChapters(libName, libUrl, libIndex, bookName):
	fileContent = open(NOVEL_PATH + libName + os.sep + bookName + '.txt','a+', encoding = 'utf-8')
	fileMulu = open(NOVEL_PATH + libName + os.sep + bookName + '_目录.txt','r+', encoding = 'utf-8')

	curIdx = -1
	allIdx = -1
	chapterUrls = []
	try:
		html = getBookChapterHtml(libIndex, libName, libUrl)
		novelName = Html.getBookName(html)
		if bookName == novelName:
			mulu = fileMulu.readlines()
			curIdx = len(mulu)
			chapterUrls = Html.getChapterUrls(html)
			allIdx = len(chapterUrls)
		else:
			Helper.printError("{} lib {} index {} need update".format(libName,bookName,libIndex))
	except Exception as e:
		Helper.printError()

	if curIdx < allIdx:
		while curIdx <= (allIdx - 1):
			errorTimes = 0
			while errorTimes < 3:
				try:
					url_name = chapterUrls[curIdx]
					values = re.split("=",url_name)
					chapter = values[1]
					html = getChapterHtml(libName,libUrl,libIndex,values[0])
					content = Html.getChapterContent(html)

					if content == "":
						content = chapter
					fileContent.write(chapter + "\n" + content + "\n")
					fileMulu.write(chapter + "\n")
					Helper.print("{} {}".format(bookName,chapter))
					errorTimes = 3
				except Exception as e:
					errorTimes = errorTimes + 1
					Helper.printError()
			curIdx = curIdx + 1

	fileContent.close()
	fileMulu.close()


def getChapterHtml(libName, libUrl, libIndex, chapterIdx):
	baseUrl = re.search("www(.*?)/",libUrl).group()
	baseUrl = re.sub("/","",baseUrl)

	limitData = URL_LIMIT[libName]
	if limitData['count'] == 2:
		url = libUrl.format(math.floor(libIndex/1000),libIndex)
	if limitData['count'] == 1:
		url = libUrl.format(libIndex)

	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
		'Connection': 'keep-alive',
		'Host': baseUrl,
		# 'Referer': url,
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': User_Agent,
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'none',
	}

	questTimes = 0
	while questTimes < 3:
		try:
			html = SESSION.get(url + chapterIdx, headers = headers, params = {}, verify = False, timeout = 3)
			questTimes = 5
		except Exception as e:
			questTimes = questTimes + 1
			time.sleep(Helper.randomFloat())

	if questTimes < 5:
		return

	return Helper.decodeHtml(html)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# 更新lib文本
def updateLib():
	global funcIndex
	funcIndex = 2
	initCheckUrlOrder()
	checkNextUrl()


def checkLib(libName,libUrl):
	Helper.print("check " + libName + " lib")
	Novel_Lib = {}

	Lib = open(NOVEL_LIB_PATH + libName + '.txt','r+', encoding = 'utf-8')
	for line in Lib.readlines():
		line = re.sub('\n','',line)
		values = line.split('=')
		Novel_Lib[values[1]] = values[0]

	curIndex = len(Novel_Lib) + 1
	ErrorCount = 0

	while curIndex <= Lib_Max_Count :
		try:
			html = getBookChapterHtml(curIndex, libName, libUrl)
			novelName = Html.getBookName(html)
			if novelName and Novel_Lib.get(str(curIndex),"") != novelName:
				ErrorCount = 0
				Novel_Lib[str(curIndex)] = novelName
				Lib.write(novelName + "=" + str(curIndex) + "\n")
				Helper.print("{} add {} {}".format(libName,curIndex,novelName))
			else:
				ErrorCount = ErrorCount + 1
				if ErrorCount > Repeat_Max_Count:
					curIndex = Lib_Max_Count + 1
					ErrorCount = 0

			curIndex = curIndex + 1
		except Exception as e:
			Helper.printError()
	
		time.sleep(Helper.randomFloat())

	Lib.close()
	checkNextUrl()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# 清空lib文本
def resetLib():
	for data in URLS.values():
		lib = open(NOVEL_LIB_PATH + data['name'] + '.txt','w')
		lib.close()
	Helper.print("reset lib done")

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

























































































































