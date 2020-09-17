# -- coding: utf-8 --

import requests		# 发送网络请求
import time 		# 时间
import math 		# 数学
import random 		# 随机
import re 			# 正则匹配
import sys 			# 系统
import os 			# 系统

# 关闭证书验证
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SESSION = requests.session()
HOME_PATH = os.path.dirname((sys.argv[0])) + os.sep
NOVEL_PATH = HOME_PATH + 'novel' + os.sep

User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'

ArgusData = {
	'1':{'name':'万族之劫','url':'https://www.boquge.com/book/120030/'},
	'2':{'name':'大奉打更人','url':'http://www.biquge.info/62_62245/'},
	'3':{'name':'大梦主','url':'http://www.biquge.info/53_53752/'},
	'4':{'name':'全球高武','url':'https://www.xsbiquge.com/81_81336/'},
	'5':{'name':'牧龙师','url':'http://www.biquge.info/10_10876/'},
	'6':{'name':'太初','url':'https://www.xsbiquge.com/22_22634/'},
	'7':{'name':'三寸人间','url':'https://www.xsbiquge.com/34_34822/'},
	'8':{'name':'临渊行','url':'http://www.biquge.info/11_11301/'},
}

def updateBook(data):
	dirUrl = data.get('url')
	novelName = data.get('name')
	log("Check Update《{}》".format(novelName),1)

	index = 0
	searchHead = "/"
	for line in dirUrl.split('/'):
		index = index + 1
		if index == 3:
			baseUrl = line
		if index > 3 and line != "":
			searchHead = searchHead + line + "/"

	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Encoding':'gzip, deflate, br',
		'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Cache-Control':'max-age=0',
		'Connection':'keep-alive',
		'sec-fetch-dest': 'document',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-site': 'none',
		'Upgrade-Insecure-Requests':'1',
		'User-Agent':User_Agent,
	}

	questTimes = 0
	html = ""
	# respons = SESSION.get(dirUrl, headers = headers, params = {}, verify = False, timeout = 3)
	# print(respons.text)
	while questTimes < 3:
		try:
			respons = SESSION.get(dirUrl, headers = headers, params = {}, verify = False, timeout = 3)
			html = decodeHtml(respons)
			questTimes = 5
		except Exception as e:
			pass

		questTimes = questTimes + 1
		time.sleep(randomFloat())

	if not html or html == "":
		log("Request Url Faild. {}".format(dirUrl),2)
		return

	# novelName = getBookName(html)
	# if not novelName:
	# 	log("Get Bookname Faild. {}".format(dirUrl),2)
	# 	return

	# 处理章节排序
	group = getChapterUrls(html,searchHead)
	if not group or len(group) < 10:
		log("Get Chapters Faild. {}".format(dirUrl),2)
		return

	if not os.path.exists(NOVEL_PATH):
		os.makedirs(NOVEL_PATH)

	BookPath = "{}{}.txt".format(NOVEL_PATH,novelName)
	MenuPath = "{}{}_目录.txt".format(NOVEL_PATH,novelName)

	if not os.path.isfile(MenuPath):
		book = open(BookPath,'a+')
		book.close()
		mulu = open(MenuPath,'a+')
		mulu.close()

	updateChapter(novelName,BookPath,MenuPath,group,dirUrl)

def updateChapter(BookName,BookPath,MenuPath,group,url):
	fileContent = open(BookPath,'a+', encoding = 'utf-8')
	fileMulu = open(MenuPath,'r+', encoding = 'utf-8')

	mulu = fileMulu.readlines()
	cur = len(mulu)

	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': User_Agent,
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'none',
	}

	faildTimes = 0
	minV = 0.3
	maxV = 0.5
	for x in range(cur,len(group)):
		index = str(x)
		chapterUrl = url + group[index].get('url')
		chapterName = group[index].get('name')

		# 调试
		# html = SESSION.get(chapterUrl, headers = headers, params = {}, verify = False, timeout = 5)
		# html = decodeHtml(html)
		# content = getChapterContent(html)
		# break

		questTimes = 0
		content = ""
		while questTimes < 5:
			try:
				html = SESSION.get(chapterUrl, headers = headers, params = {}, verify = False, timeout = 5)
				html = decodeHtml(html)
				content = getChapterContent(html)
				if not content:
					content = "解析 <{}> 内容失败".format(chapterName)
					log(content,2)
				else:
					fileContent.write(chapterName + "\n" + content + "\n")
					fileMulu.write(chapterName + "\n")
					log("Book《{}》add <{}>".format(BookName,chapterName),1)
					questTimes = 5
			except Exception as e:
				faildTimes = faildTimes + 1
				if faildTimes%5 == 0:
					minV = minV + 0.5
					maxV = maxV + 0.5
					faildTimes = 0
				log("Request Faild {}".format(chapterUrl),2)
			
			questTimes = questTimes + 1
			sleepTime = random.uniform(minV, maxV)
			time.sleep(sleepTime)

	fileContent.close()
	fileMulu.close()

# 获取章节内容
def getChapterContent(html):
    for idx in range(1,2):
        content = eval('getChapterContent' + str(idx) + '(html)')
        if content:
            return content
    return

# 获取章节内容，解析方法1
def getChapterContent1(html):
    # <div id="txtContent">xxxxxxxxx</div>
    # <div id="content">xxxxxxxxx</div>
    html = re.sub(r"\r\n","",html)
    html = re.sub(r'<!--([a-z]+)-->','',html)

    content = re.findall(r'<div id="content">(.*?)</div>',html)
    if not content:
        content = re.findall(r'<div id=\"txtContent\">(.*?)</div>',html)

    if len(content) > 0:
        text = re.sub(r'&nbsp;'," ",content[0])
        text = re.sub(r'<br/><div class(.*?)</script></div>',"",text)
        text = re.sub("<br/>|<br>","\n",text)
        # text = re.sub("\w{3}\.(.*?)\.\w{3}","",text)
        return text

    return

def getChapterUrls(html,argv):
	urls = {}

	for idx in range(1,3):
	    group = eval('getChapterUrls' + str(idx) + '(html,argv)')
	    if len(group) > 10:
	        break

	# 章节去重
	last = group[len(group) - 1]
	repeatIdx = -1
	for index in range(10):
		if last == group[index]:
			repeatIdx = index

	if repeatIdx >= 0:
		while repeatIdx >= 0:
			del group[0]
			repeatIdx = repeatIdx - 1

	repeatIdx = 0
	for line in group:
		line = re.sub(r'"(.*?)>','">',line)
		kv = line.split('">')
		url = kv[0]
		name = kv[1]
		urls[str(repeatIdx)] = {'url':url, 'name':name}
		repeatIdx = repeatIdx + 1

	return urls

def getChapterUrls1(html,argv):
	# href="/book/120030/169481945.html">第1章 父子</a></li><li ><a
	searchStr = "href=\"{}([0-9].*?)</a>".format(argv)
	group = re.findall(searchStr,html)
	return group

def getChapterUrls2(html,argv):
	# <dd><a href="10262913.html" title="第一章 牢狱之灾">第一章 牢狱之灾</a></dd>
	html = re.sub(r' title="(.*?)"','',html)
	group = re.findall(r'<dd><a href="([0-9].*?)</a>',html)
	return group

# 解码网页
def decodeHtml(html):
    try:
        string = re.findall(r'charset=(.*?)"',html.text)[0]
        if not string:
            string = 'gbk'
        return html.content.decode(string)
    except Exception as e:
        return

def randomFloat(minValue = 0.1, maxValue = 0.3):
    return random.uniform(minValue, maxValue)

def log(str,mType):
	if mType == 1:
		print(">>> {}".format(str))
	elif mType == 2:
		print(">>> Error, {}".format(str))
	else:
		print(">>> Unkown Error")

if __name__ == '__main__':
	if not os.path.exists(NOVEL_PATH):
		os.makedirs(NOVEL_PATH)

	for data in ArgusData.values():
		updateBook(data)

	log('Books Update Done!',1)





