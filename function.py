
# -- coding: utf-8 --
# 2.7版本 字符串有两种编码格式（Unicode、utf-8） 防止输出错误

# \xb6\xfe\xb6\xfe\xd5\xc2 gbk编码
# 内容解码 content.decode('gbk').encode('utf-8')

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
NOVEL_INDEX_MAX = 50000
MAX_ERROR_TIMES = 50

url_hanzi_2_pinying_1 = 'http://www.qqxiuzi.cn/zh/pinyin/'
url_hanzi_2_pinying_2 = 'http://www.qqxiuzi.cn/zh/pinyin/show.php'

User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

NOVEL_URLS = {
	'cangqionglongqi'	:'http://www.cangqionglongqi.com/',
	'biquge'			:'https://www.biqugezw.com/',
	'booktxt'			:'http://www.booktxt.net/',
	'bxwx3'				:'http://www.bxwx3.org/',
	# 'xuehong'			:'http://www.xuehong.cc/',
}

URL_NAMES = {
	'cangqionglongqi'	:'苍穹龙骑网',
	'booktxt'			:'顶点小说网',
	'biquge'			:'笔趣阁',
	'bxwx3'				:'笔下文学',
	# 'xuehong'			:'血红小说网',
}

def init():
	novels = open(HOME_PATH + '信息表.txt','a+')
	novels.close()

	novels = open(HOME_PATH + '信息表.txt','r')
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
	global Name_pinyi
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
		print u'更新完毕'
		exit()
	else:
		Name_hanzi = Names[NameIndex]
		NameIndex = NameIndex + 1

		print u'******** 检查 《%s》 更新 ********'%Name_hanzi

		getHanzi2Pinyi(False)

def getHanzi2Pinyi(only):
	global Name_pinyi

	SECRETCODE = ''
	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Connection':'keep-alive',
		'Host':'www.qqxiuzi.cn',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0',
	}

	try:
		response = SESSION.get(url_hanzi_2_pinying_1, headers = headers, params = {}, verify = False)
		SECRETCODE = re.search("token=(.*?)'",response.content).group(1)
	except Exception as e:
		pass

	if SECRETCODE == '':
		getHanzi2Pinyi(only)
		return

	headers = {
		'Accept':'*/*',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Connection':'keep-alive',
		'Content-type':'application/x-www-form-urlencoded',
		'Host':'www.qqxiuzi.cn',
		'Referer':'http://www.qqxiuzi.cn/zh/pinyin/',
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0'
	}

	data = {
		'b':'null','d':'1','h':'null','k':'1','s':'null','t':Name_hanzi,'token':SECRETCODE,'u':'null','v':'null','y':'null','z':'null',
	}
	
	response = SESSION.post(url = url_hanzi_2_pinying_2, data = data, headers = headers, verify = False)
	result = re.sub(' ','',response.content)
	Name_pinyi = re.sub('<(.*?)>','',result)
	
	if not only:
		initCheckOrder()

def initHadChapters():
	global Path_dir
	global Path_chapter
	global Path_content
	global ChaptersNum

	Path_dir = HOME_PATH + os.sep + 'novels' + os.sep + URL_NAMES[Ower]
	Path_chapter = Path_dir + os.sep + Name_hanzi + '_' + '目录.txt'
	Path_content = Path_dir + os.sep + Name_hanzi + '.txt'

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
	
def cangqionglongqi(URL):
	print u'开始检查 苍穹龙骑小说网'

	BaseUrl = URL + Name_pinyi + '/'

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.9',
		'Connection':'keep-alive',
		'Host':'www.cangqionglongqi.com',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	try:
		html = SESSION.get(BaseUrl, headers = headers, params = {}, verify = False)
	except Exception as e:
		cangqionglongqi(URL)
		return
	result = html.content.decode('gbk').encode('utf-8')
	group = re.findall("<dd><a href=\"(.*?)</a></dd>", result)

	chapter = open(Path_chapter,'a+')
	content = open(Path_content,'a+')
	curLines = len(group)
	headers['Referer'] = BaseUrl

	def sendRequest():
		global ChaptersNum
		if ChaptersNum < curLines:
			try:
				url_name = group[ChaptersNum].split('">')
				print u'正在抓取 《%s》 %s'%(Name_hanzi,url_name[1])

				html = SESSION.get(BaseUrl + url_name[0], headers = headers, params = {}, verify = False)
				result = unicode(html.content,'gbk').encode('utf8')
				result = re.sub('&nbsp;',' ',result)
				result = re.sub('<br />','\n',result)
				goal = re.search('''content">((.|\n)*?)<''',result).group()

				goal = re.sub('content">','',goal)
				goal = re.sub('<','',goal)
				goal = url_name[1] + '\n' + goal

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
					print u'请求本章发生错误，重新请求'
					timer = threading.Timer(0.2,sendRequest)
					timer.start()
		else:
			content.close()
			chapter.close()
			checkUpdate()

	timer = threading.Timer(0.1,sendRequest)
	timer.start()

def booktxt(URL):
	print u'开始检查 顶点小说网'

	BaseUrl = ""
	SearchUrl = 'http://zhannei.baidu.com/cse/search'
	Referer = SearchUrl + '?s=5334330359795686106&q=' + urllib.unquote(Name_hanzi)

	index_url = checkLibName(Name_pinyi)
	if index_url:
		index = int(index_url)
		BaseUrl = URL + '%d_%d/'%(math.floor(index / 1000),index)
		Referer = ''
	else:
		headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate',
			'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
			'Cache-Control':'max-age=0',
			'Connection':'keep-alive',
			'Host':'zhannei.baidu.com',
			'Referer':'http://www.booktxt.net/',
			'Upgrade-Insecure-Requests':'1',
			'User-Agent':User_Agent,
		}

		data = {
			'q':urllib.unquote(Name_hanzi),
			's':'5334330359795686106'
		}

		html = SESSION.get(SearchUrl, headers = headers, params = data, verify = False)
		result = html.content.encode('utf-8')
		group = re.findall("<a cpos=\"title\" (.*?) class",result)
		
		for line in group:
			url = re.findall("href=\"(.*?)\"",line)[0]
			name = re.findall("title=\"(.*?)\"",line)[0]
			if name == Name_hanzi:
				BaseUrl = url
				break

		if BaseUrl == "":
			checkUpdate()
			return

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.9',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.booktxt.net',
		'Referer':Referer,
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	try:
		html = SESSION.get(BaseUrl, headers = headers, params = {}, verify = False)
	except Exception as e:
		booktxt(URL)
		return
	result = html.content.decode('gbk').encode('utf-8')

	content = re.search("正文</dt>((.|\n)*?)</dl>",result).group()
	group = re.findall("<dd><a href=\"/(.*?)</a></dd>",content)

	chapter = open(Path_chapter,'a+')
	content = open(Path_content,'a+')
	curLines = len(group)
	headers['Referer'] = BaseUrl

	def sendRequest():
		global ChaptersNum
		if ChaptersNum < curLines:
			try:
				url_name = group[ChaptersNum].split('">')
				print u'正在抓取 《%s》 %s'%(Name_hanzi,url_name[1])
				html = SESSION.get(URL + url_name[0], headers = headers, params = {}, verify = False)
				result = unicode(html.content,'gbk').encode('utf8')
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
					print u'请求本章发生错误，重新请求'
					timer = threading.Timer(0.2,sendRequest)
					timer.start()
		else:
			content.close()
			chapter.close()
			checkUpdate()

	timer = threading.Timer(0.1,sendRequest)
	timer.start()

def bxwx3(URL):
	print u'开始检查 笔下文学网'

	SearchUrl = 'http://www.bxwx3.org/search.aspx'

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.bxwx3.org',
		'Referer':'http://www.bxwx3.org/',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}
	data = {
		'bookname':urllib.unquote(Name_hanzi.encode('gb2312')),
	}
	BaseUrl = ''
	try:
		html = SESSION.get(SearchUrl, headers = headers, params = data, verify = False)
	except Exception as e:
		bxwx3(URL)
		return
	group = re.findall("<a href=\"(.*?)</span>",html.text)

	for string in group:
		match = re.findall("_blank\">(.*?)</a>",string)
		if len(match) > 0 and match[0] == Name_hanzi:
			BaseUrl = re.findall("(.*?)\"",string)[0]
			break

	if BaseUrl == '' :
		checkUpdate()
		return

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.bxwx3.org',
		'Referer':SearchUrl + '?bookname=' + urllib.unquote(Name_hanzi.encode('gb2312')),
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	html = SESSION.get(BaseUrl, headers = headers, params = {}, verify = False)
	group = re.findall("<dd><a href=\"(.*?)</a></dd>",html.text)

	chapter = open(Path_chapter,'a+')
	content = open(Path_content,'a+')
	headers['Referer'] = BaseUrl
	curLines = len(group)

	def sendRequest():
		global ChaptersNum
		if ChaptersNum < curLines:
			try:
				url_name = group[ChaptersNum].split('">')
				print u'正在抓取 《%s》 %s'%(Name_hanzi,url_name[1])
				html = SESSION.get(url_name[0], headers = headers, params = {}, verify = False)
				result = re.sub('&nbsp;',' ',html.text)
				result = re.sub('<br />|<br/>|</p>|<p>','\n',result)
				goal = re.search("zjneirong\">((.|\n)*?)<div>",result).group()

				goal = re.sub('zjneirong">','',goal)
				goal = re.sub('<div>','',goal)

				goal = url_name[1] + goal + '\n'

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
					print u'请求本章发生错误，重新请求'
					timer = threading.Timer(0.1,sendRequest)
					timer.start()
		else:
			content.close()
			chapter.close()
			checkUpdate()

	timer = threading.Timer(0.1,sendRequest)
	timer.start()

def biquge(URL):
	print u'开始检查 笔趣阁'

	index_url = checkLibName(Name_pinyi)
	if not index_url:
		print u'本地笔趣阁库未收录，请更新库'
		checkUpdate()
		return

	index = int(index_url)
	headers = {
		'Accept':'text/html,application/xhtml+xm…plication/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.biqugezw.com',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	try:
		html = SESSION.get(URL + '%d_%d/'%(math.floor(index / 1000),index), headers = headers, data = {}, verify = False)
	except Exception as e:
		biquge(URL)
	result = html.content.decode('gbk').encode('utf-8')
	group = re.findall("<dd><a href=\"/(.*?)</a></dd>",result)

	chapter = open(Path_chapter,'a+')
	content = open(Path_content,'a+')
	headers['Referer'] = URL + index_url
	curLines = len(group)

	def sendRequest():
		global ChaptersNum
		if ChaptersNum < curLines:
			try:
				url_name = group[ChaptersNum].split('">')
				print u'正在抓取 《%s》 %s'%(Name_hanzi,url_name[1])
				html = SESSION.get(URL + url_name[0], headers = headers, params = {}, verify = False)
				result = unicode(html.content,'gbk').encode('utf8')
				result = re.sub('&nbsp;',' ',result)
				result = re.sub('<br />','\n',result)
				goal = re.search("content\">((.|\n)*?)</div>",result).group()

				goal = re.sub('content">','',goal)
				goal = re.sub('</div>','',goal)
				goal = re.sub("一秒记住【笔趣阁中文网<a href=\"http://www.biqugezw.com\" target=\"_blank\">www.biqugezw.com</a>】，为您提供精彩小说阅读。",'',goal)
				goal = re.sub("手机用户请浏览m.biqugezw.com阅读，更优质的阅读体验。",'',goal)
				
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
					print u'请求本章发生错误，重新请求'
					timer = threading.Timer(0.1,sendRequest)
					timer.start()
		else:
			content.close()
			chapter.close()
			checkUpdate()

	timer = threading.Timer(0.1,sendRequest)
	timer.start()

def xuehong(URL):
	print u'开始检查 血红小说网'

	SearchUrl = 'http://zhannei.baidu.com/cse/search'
	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'zhannei.baidu.com',
		'Referer':URL,
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	data = {
		'q':urllib.unquote(Name_hanzi),
		's':'4163767760398267886'
	}

	html = SESSION.get(SearchUrl, headers = headers, params = data, verify = False)
	result = html.content.encode('utf-8')
	# print result
	group = re.findall("<a cpos=\"title\" (.*?) class",result)
	
	BaseUrl = ""
	for line in group:
		url = re.findall("href=\"(.*?)\"",line)[0]
		name = re.findall("title=\"(.*?)\"",line)[0]
		if name == Name_hanzi:
			BaseUrl = url
			break

	if BaseUrl == "":
		checkUpdate()
		return

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.xuehong.cc',
		'Referer':SearchUrl + '?s=4163767760398267886&q=' + urllib.unquote(Name_hanzi),
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	html = SESSION.get(BaseUrl, headers = headers, params = {}, verify = False)
	result = html.content.decode('gbk').encode('utf-8')

	# <li><a href="/book/35609/18524538.html" title="新书感言">
	group = re.findall("<li><a href=\"/(.*?)\">",result)

	chapter = open(Path_chapter,'a+')
	content = open(Path_content,'a+')
	headers['Referer'] = BaseUrl
	curLines = len(group)

	def sendRequest():
		global ChaptersNum
		if ChaptersNum < curLines:
			# try:
				url_name = group[ChaptersNum].split('" title="')
				print u'正在抓取 《%s》 %s'%(Name_hanzi,url_name[1])
				print URL + url_name[0]
				html = SESSION.get(URL + url_name[0], headers = headers, params = {}, verify = False)
				result = html.content
				print html.content
				result = re.sub('&nbsp;',' ',result)
				result = re.sub('<br />','\n',result)

				goal = re.search("readx()((.|\n)*?)</div>",result).group()
				goal = re.sub("readx\(\);</script>",'',goal)
				goal = re.sub('</div>','',goal)

				goal = groupName[ChaptersNum] + '\n' + goal + '\n'
				content.write(goal)
				chapter.write(groupName[ChaptersNum] + '\n')

				ChaptersNum = ChaptersNum + 1
				timer = threading.Timer(random.uniform(0.1,0.3),sendRequest)
				timer.start()
			# except Exception as e:
			# 	global RepeatTimes
			# 	RepeatTimes = RepeatTimes + 1
			# 	if RepeatTimes > REQUEST_MAX_TIMES:
			# 		checkUpdate()
			# 	else:
			# 		print u'请求本章发生错误，重新请求'
			# 		timer = threading.Timer(0,sendRequest)
			# 		timer.start()
		else:
			content.close()
			chapter.close()
			checkUpdate()

	timer = threading.Timer(0,sendRequest)
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
		print '小说库更新完毕'
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
		if len(key_value) == 3:
			Lib_index_name[key_value[2]] = key_value[1]
			Lib_name_index[key_value[1]] = key_value[2]

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

def cangqionglongqiLib(bFix):
	checkUpdateLib(bFix)

def booktxtLib(bFix):
	print u'更新顶点小说库'

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
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
					html = SESSION.get("http://www.booktxt.net/" + novel_index, headers = headers, params = {}, verify = False)
					result = html.content.decode('gbk').encode('utf-8')
					global Name_hanzi
					Name_hanzi = re.findall("var booktitle = \"(.*?)\"",result)[0]
					if Name_hanzi != '':
						getHanzi2Pinyi(True)
						Lib.write(Name_hanzi + '=' + Name_pinyi + '=' + str(start_index) + '\n')
						print u'顶点小说库已收录 %s %s'%(Name_hanzi,novel_index)
						error_times = 0
			except Exception as e:
				error_times = error_times + 1
				print '未更新到索引 %s'%start_index
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

def bxwx3Lib(bFix):
	checkUpdateLib(bFix)

def xuehongLib(bFix):
	checkUpdateLib(bFix)

def biqugeLib(bFix):
	print u'更新笔趣阁小说库'

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'Host':'www.biqugezw.com',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	Lib = open(DICTIONARY_PATH + 'biquge.txt','a+')
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
					html = SESSION.get("https://www.biqugezw.com/" + novel_index, headers = headers, params = {}, verify = False)
					result = html.content.decode('gbk').encode('utf-8')

					global Name_hanzi
					Name_hanzi = re.findall("og:title\" content=\"(.*?)\" />",result)[0]
					if Name_hanzi != '':
						getHanzi2Pinyi(True)
						Lib.write(Name_hanzi + '=' + Name_pinyi + '=' + str(start_index) + '\n')
						print u'笔趣阁库已收录 %s %s'%(Name_hanzi,novel_index)
						error_times = 0
			except Exception as e:
				error_times = error_times + 1
				print '未更新到索引 %s'%novel_index
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

