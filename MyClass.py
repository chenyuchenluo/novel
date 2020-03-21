# -- coding: utf-8 --

import math
import re
import random

COMMON_DEFINE_1 = {
    '零':0,'一':1,'二':2,'三':3,'四':4,
    '五':5,'六':6,'七':7,'八':8,'九':9,
    '十':10,'百':100,'千':1000,'万':10000
}

COMMON_DEFINE_2 = {
    '0':'零','1':'一','2':'二','3':'三','4':'四',
    '5':'五','6':'六','7':'七','8':'八','9':'九',
    '10':'十','100':'百','1000':'千','10000':'万'
}

# Helper方法不用过类实例调用，所有自定义方法时不用传self
class Helper():

    # 输出错误信息
    def printError(string = "try it again!"):
        print(' ERROR! {}'.format(string))

    # 输出一条横线
    def printLine(string = "*", count = 30, sub = ""):
        array = []
        for x in range(1,count):
            array.append(string)
        print(sub.join(array))

    # 输出内容
    def print(string = ""):
        print(' {}'.format(string))

    # 获取用户输入的值
    def getNum(min = 0, max = 100):
        try:
            num = int(input('input a number:'))
            if num < min or num > max:
                return -1
        except Exception as e:
            return -1
        return num

    # 获取一个随机小数
    def randomFloat(minValue = 0.1, maxValue = 0.3):
        return random.uniform(minValue, maxValue)

    # 数字转换成大写
    def numToId(num):
        if not num:
            return COMMON_DEFINE_2.get('0','0')

        array = []
        while num > 0:
            left = num % 10
            num = math.floor(num / 10)
            array.insert(0,left)

        result = []
        for idx in range(0,len(array)):
            value = array[idx]
            if value == 0 :
                if array[idx - 1] != 0:
                    result.append(COMMON_DEFINE_2.get('0',''))
            else:
                result.append(COMMON_DEFINE_2.get(str(value),''))
                temp = 1
                for x in range(1,len(array) - idx):
                    temp = temp * 10
                if temp > 1:
                    result.append(COMMON_DEFINE_2.get(str(temp),''))
        
        return "".join(result)

    # 大写转换成数字
    def idToNum(string):
        if not string:
            return 0

        num = 0
        temp = 0
        for x in string:
            if x == ' ':
                return num + temp

            value = COMMON_DEFINE_1.get(x,0)
            if value < 10:
                temp = value
            else:
                num = num + temp * value
                temp = 0

        return num + temp

    # 判断章节名字格式  第xxx章 xxxx
    def formatChapterName(name):
        string = re.findall("第(.*?)",name)
        if not string:
            return "第" + name
        else:
            return name

    # 网页内容解码
    def decodeHtml(html):
        try:
            string = re.findall("charset=(.*?)\"",html.text)[0]
            if not string:
                string = 'gbk'

            return html.content.decode(string)
        except Exception as e:
            return ""
            raise e

# 网页解析
class HTML():

    # 方便扩展获取小说名字的方法
    def getBookName(self, html):
        for idx in range(1,2):
            name = eval('self.getBookName' + str(idx) + '(html)')
            if name and name != "":
                return name
        return

    # 获取网页内第一个《》中的内容
    def getBookName1(self, html):
        try:
            name = re.findall("《(.*?)》",html)
            if len(name) < 1:
                return
            return name[0]
        except Exception as e:
            raise e
        return

    # 获取网页第一个。。。
    def getBookName2(self, html):
        return

    # 获取所有的章节url ["第一章，ref=98233.html",...]
    def getChapterUrls(self, html):
        urls = []
        group = []

        for idx in range(2):
            group = eval('self.getChapterUrls' + str(idx) + '(html)')
            if len(group) > 10:
                break

        for line in group:
            url = re.search("(\d{1}|\d{2}|\d{3}|\d{4}|\d{5}|\d{6}|\d{7}|\d{8}|).html",line).group()
            content = re.findall(">(.*?)<",line)[0]
            urls.append("{}={}".format(url,content))

        return urls

    # 获取所有章节url 方法0
    def getChapterUrls0(self, html):
        # <dd><a href='/biquge_1/3850105.html'>番外九 相守</a></dd>
        # <dd><a href="38272.html" title="我的第四本书，欢迎大家。">我的第四本书，欢迎大家。</a></dd>
        temp = re.sub("head((.|\n)*?)正文","",html)
        group = re.findall("<dd><a href(.*?)/a></dd>",temp)

        return group

    # 获取所有章节url 方法1
    def getChapterUrls1(self, html):
        # <dd> <a style="" href="/0_11/4981880.html">第四千六百三十五章 大衍域</a></dd>
        temp = re.sub("<body>((.|\n)*?)正文","",html)
        group = re.findall("<dd> <a style(.*?)/a></dd>",temp)

        return group

    # 获取章节内容
    def getChapterContent(self, html):
        for idx in range(2):
            content = eval('self.getChapterContent' + str(idx) + '(html)')
            if content and content != "" :
                return content
        return "无法解析章节内容"

    # 获取章节内容，解析方法0
    def getChapterContent0(self, html):
        # <div id="content">CONTENT</div>
        html = re.sub(r"\r\n","",html)
        html = re.sub("<!(.*?)>","",html)

        content = re.findall("<div id=\"content\">(.*?)</div>",html)

        if len(content) > 0:
            text = re.sub("&nbsp;"," ",content[0])
            text = re.sub("<br/>|<br>","\n",text)
            text = re.sub("\w{3}\.(.*?)\.\w{3}","",text)
            return text

        return ""

    # 获取章节内容，解析方法1
    def getChapterContent1(self, html):
        return ""























