# coding=utf-8
# 2.7版本 字符串有两种编码格式（Unicode、utf-8） 防止输出错误

# content.decode('utf-8') 把字符串按照特定编码格式变成 unicode
# content.encode('utf-8') 把 unicode 变成 对应格式的字符串

import ssl 			# 证书
import requests		# 发送网络请求
import urllib 		# 用于urldecode
import threading 	# 线程
import time 		# 时间
import math 		# 数学
import random 		# 随机
import json			# 解析
import os 			# 系统
import platform 	# 设备
import re 			# 正则匹配
import sys 			# 系统
reload(sys)
sys.setdefaultencoding('utf8')

from Stack import Stack # 栈

# 关闭证书验证
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SESSION = requests.session()
HOME_PATH = os.path.dirname((sys.argv[0])) + os.sep
DICTIONARY_PATH = HOME_PATH + 'Libs' + os.sep
REQUEST_MAX_TIMES = 15
NOVEL_INDEX_MAX = 70000
MAX_ERROR_TIMES = 10

User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

NOVEL_URLS = {
	'booktxt'	:'https://www.booktxt.net/',
	'biquke'	:'https://www.biquke.com/',
}

URL_NAMES = {
	'booktxt'	:'顶点小说网',
	'biquke' 	:'笔趣阁'
}

def init():
	novels = open(HOME_PATH + 'readme.txt','a+')
	novels.close()

	novels = open(HOME_PATH + 'readme.txt','r')
	content = novels.readline()
	novels.close()

	content = re.sub('\n','',content)

	global Names
	global NameIndex
	global RepeatTimes
	Names = content.split('=')
	NameIndex = 0
	RepeatTimes = 0

	global StackFunc
	global StackUrls
	StackFunc = Stack()
	StackUrls = Stack()

	global Name_hanzi
	global Path_dir
	global Path_chapter
	global Path_content
	global ChaptersNum
	global Ower

def getNextNovelName():
	global Names
	global NameIndex
	global Name_hanzi

	if NameIndex == len(Names):
		print(' update done')
		exit()
	else:
		Name_hanzi = Names[NameIndex]
		NameIndex = NameIndex + 1

		print(' check <%s> update '%Name_hanzi)
		initCheckOrder()

def initHadChapters():
	global Path_dir
	global Path_chapter
	global Path_content
	global ChaptersNum

	Path_dir = HOME_PATH + os.sep + 'novels' + os.sep + Ower
	Path_chapter = Path_dir + os.sep + Name_hanzi.decode('utf-8') + '_' + 'menu.txt'
	Path_content = Path_dir + os.sep + Name_hanzi.decode('utf-8') + '.txt'

	if not os.path.exists(Path_dir):
		os.makedirs(Path_dir)
	content = open(Path_chapter,'a+')
	content.close()
	chapter = open(Path_content,'a+')
	chapter.close()

	chapter = open(Path_chapter,'r')
	lines = chapter.readlines()
	ChaptersNum = len(lines)
	chapter.close()

def initCheckOrder():
	global StackFunc
	global StackUrls

	for key_value in NOVEL_URLS.items():
		func = key_value[0]
		url = key_value[1]

		StackFunc.push(func)
		StackUrls.push(url)

	checkUpdate()

def checkUpdate():
	if StackFunc.is_empty():
		getNextNovelName()
	else:
		global Ower
		global RepeatTimes

		Ower = StackFunc.pop()
		func = globals().get(Ower)
		url = StackUrls.pop()
		RepeatTimes = 0
		
		initLib(Ower)
		initHadChapters()
		func(url)

def booktxt(URL):
	print(' check novel in booktxt')

	BaseUrl = ""

	index_url = checkLibName(Name_hanzi)
	if index_url:
		index = int(index_url)
		BaseUrl = URL + '%d_%d/'%(math.floor(index / 1000),index)
		Referer = ''
	else:
		checkUpdate()
		return

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate, br',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.booktxt.net',
		'TE':'Trailers',
		'Referer':Referer,
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	try:
		html = SESSION.get(BaseUrl, headers = headers, params = {}, verify = False)
	except Exception as e:
		booktxt(URL)
		return
	result = decodeHtml(html)
	content = re.search("正文</dt>((.|\n)*?)</dl>",result).group()
	group = re.findall("<dd><a href=\"(.*?)</a></dd>",content)
	
	chapter = open(Path_chapter,'a+')
	content = open(Path_content,'a+')
	curLines = len(group)
	headers['Referer'] = BaseUrl

	def sendRequest():
		global ChaptersNum
		if ChaptersNum < curLines:
			try:
				url_name = group[ChaptersNum].split('">')
				print(' >>> %s %s'%(Name_hanzi,url_name[1]))
				html = SESSION.get(BaseUrl + url_name[0], headers = headers, params = {}, verify = False)
				result = decodeHtml(html)
				result = re.sub('&nbsp;',' ',result)
				result = re.sub('<br />','\n',result)
				goal = re.search("content\">((.|\n)*?)</div>",result).group()

				goal = re.sub('content">','',goal)
				goal = re.sub('</div>','',goal)

				goal = url_name[1] + '\n' + goal + '\n'

				content.write(goal)
				chapter.write(url_name[1] + '\n')

				ChaptersNum = ChaptersNum + 1

				timer = threading.Timer(random.uniform(0.1,0.3),sendRequest)
				timer.start()
			except Exception as e:
				global RepeatTimes
				RepeatTimes = RepeatTimes + 1
				if RepeatTimes > REQUEST_MAX_TIMES:
					checkUpdate()
				else:
					print('Error,request again')
					timer = threading.Timer(0.2,sendRequest)
					timer.start()
		else:
			content.close()
			chapter.close()
			checkUpdate()

	timer = threading.Timer(0.1,sendRequest)
	timer.start()

def biquke(URL):
	print(' check novel in biquke')

	BaseUrl = ""

	index_url = checkLibName(Name_hanzi)
	if index_url:
		index = int(index_url)
		BaseUrl = URL + 'bq/%d/%d/'%(math.floor(index / 1000),index)
	else:
		checkUpdate()
		return

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate, br',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.biquke.com',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	try:
		html = SESSION.get(BaseUrl, headers = headers, params = {}, verify = False)
	except Exception as e:
		biquke(URL)
		return

	result = decodeHtml(html)
	group = re.findall("<dd><a href=\"(.*?)\">",result)
	
	chapter = open(Path_chapter,'a+')
	content = open(Path_content,'a+')
	curLines = len(group)
	headers['Referer'] = BaseUrl

	def sendRequest():
		global ChaptersNum
		if ChaptersNum < curLines:
			try:
				url_name = group[ChaptersNum].split('" title="')
				print(' >>> %s %s'%(Name_hanzi,url_name[1]))
				html = SESSION.get(BaseUrl + url_name[0], headers = headers, params = {}, verify = False)
				result = decodeHtml(html)
				result = re.sub('&nbsp;',' ',result)
				result = re.sub('<br/>','\n',result)
				goal = re.search("content\">((.|\n)*?)</div>",result).group()

				goal = re.sub('content">','',goal)
				goal = re.sub('</div>','',goal)

				goal = url_name[1] + '\n' + goal + '\n'

				content.write(goal)
				chapter.write(url_name[1] + '\n')

				ChaptersNum = ChaptersNum + 1

				timer = threading.Timer(random.uniform(0.1,0.3),sendRequest)
				timer.start()
			except Exception as e:
				global RepeatTimes
				RepeatTimes = RepeatTimes + 1
				if RepeatTimes > REQUEST_MAX_TIMES:
					checkUpdate()
				else:
					print('Error,request again')
					timer = threading.Timer(0.2,sendRequest)
					timer.start()
		else:
			content.close()
			chapter.close()
			checkUpdate()

	timer = threading.Timer(0.1,sendRequest)
	timer.start()

def start():
	getNextNovelName()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 更新小说库

def checkUpdateDictionaryLib(bFix):
	global StackLibFunc
	StackLibFunc = Stack()

	if not os.path.exists(DICTIONARY_PATH):
		os.makedirs(DICTIONARY_PATH)
	for key in URL_NAMES:
		index = open(DICTIONARY_PATH + key + '.txt','a+')
		index.close()


	for key_value in NOVEL_URLS.items():
		func = key_value[0]
		StackLibFunc.push(func)

	checkUpdateLib(bFix)

def checkUpdateLib(bFix):
	if StackLibFunc.is_empty():
		print('update novels lib done')
	else:
		name = StackLibFunc.pop()
		func = globals().get(name + 'Lib')
		initLib(name)
		func(bFix)

def initLib(key):
	global Lib_index_name
	global Lib_name_index
	Lib_index_name = {}
	Lib_name_index = {}

	if not os.path.isfile(DICTIONARY_PATH + key + '.txt'):
		return

	txt = open(DICTIONARY_PATH + key + '.txt','r')
	lines = txt.readlines()

	for string in lines:
		string = re.sub('\n','',string)
		key_value = string.split('=')
		if len(key_value) == 2:
			Lib_index_name[key_value[1]] = key_value[0]
			Lib_name_index[key_value[0]] = key_value[1]

	txt.close()

def checkLibIndex(key):
	try:
		return Lib_index_name[key]
	except Exception as e:
		return False

def checkLibName(name):
	try:
		return Lib_name_index[name]
	except Exception as e:
		return False

def booktxtLib(bFix):
	print('update booktxt lib')

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Connection':'keep-alive',
		'Host':'www.booktxt.net',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	Lib = open(DICTIONARY_PATH + 'booktxt.txt','a+')

	global start_index
	global error_times
	if bFix:
		start_index = 1
	else:
		start_index = len(Lib_index_name)
	error_times = 0

	def requests():
		global start_index
		global error_times
		if start_index <= NOVEL_INDEX_MAX:
			try:
				novel_index = '%d_%d/'%(math.floor(start_index / 1000),start_index)
				if not checkLibIndex(str(start_index)):
					html = SESSION.get("https://www.booktxt.net/" + novel_index, headers = headers, params = {}, verify = False)
					result = decodeHtml(html)
					global Name_hanzi
					Name_hanzi = re.findall("booktitle = \"(.*?)\"",result)[0]
					if Name_hanzi != '':
						Lib.write(Name_hanzi + '=' + str(start_index) + '\n')
						print(' booktxt lib added  %s %s'%(Name_hanzi,novel_index))
						error_times = 0
			except Exception as e:
				error_times = error_times + 1
				print('Error! update chapter %s'%start_index)
				if error_times > MAX_ERROR_TIMES:
					start_index = NOVEL_INDEX_MAX + 1

			start_index = start_index + 1
			timer = threading.Timer(0,requests)
			timer.start()
		else:
			Lib.close()
			checkUpdateLib(bFix)

	timer = threading.Timer(0,requests)
	timer.start()

def biqukeLib(bFix):
	print('update biquke lib')

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Connection':'keep-alive',
		'Host':'www.biquke.com',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	Lib = open(DICTIONARY_PATH + 'biquke.txt','a+')

	global start_index
	global error_times
	if bFix:
		start_index = 1
	else:
		start_index = len(Lib_index_name)
	error_times = 0

	def requests():
		global start_index
		global error_times
		if start_index <= NOVEL_INDEX_MAX:
			try:
				novel_index = 'bq/%d/%d/'%(math.floor(start_index / 1000),start_index)
				if not checkLibIndex(str(start_index)):
					html = SESSION.get("https://www.biquke.com/" + novel_index, headers = headers, params = {}, verify = False)
					result = decodeHtml(html)
					global Name_hanzi
					Name_hanzi = re.findall("book_name\" content=\"(.*?)\"",result)[0]
					if Name_hanzi != '':
						Lib.write(Name_hanzi + '=' + str(start_index) + '\n')
						print(' biquke lib added  %s %s'%(Name_hanzi,novel_index))
						error_times = 0
			except Exception as e:
				error_times = error_times + 1
				print('Error! update chapter %s'%start_index)
				if error_times > MAX_ERROR_TIMES:
					start_index = NOVEL_INDEX_MAX + 1

			start_index = start_index + 1
			timer = threading.Timer(0,requests)
			timer.start()
		else:
			Lib.close()
			checkUpdateLib(bFix)

	timer = threading.Timer(0,requests)
	timer.start()

def decodeHtml(html):
	string = re.findall("charset=(.*?)\"",html.content)[0]
	if not string:
		string = 'gbk'

	return html.content.decode(string).encode('utf-8')