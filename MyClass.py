# -- coding: utf-8 --

import math
import re
import random

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
        desc = {
            '0':'零','1':'一','2':'二','3':'三','4':'四',
            '5':'五','6':'六','7':'七','8':'八','9':'九',
            '10':'十','100':'百','1000':'千','10000':'万'
        }

        if not num:
            return desc.get('0','0')

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
                    result.append(desc.get('0',''))
            else:
                result.append(desc.get(str(value),''))
                temp = 1
                for x in range(1,len(array) - idx):
                    temp = temp * 10
                if temp > 1:
                    result.append(desc.get(str(temp),''))
        
        return "".join(result)

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
        for idx in range(1,2):
            urls = eval('self.getChapterUrls' + str(idx) + '(html)')
            if len(urls) > 10:
                return urls
        return []

    # 获取所有章节url 方法1
    def getChapterUrls1(self, html):
        # <dd><a href='/biquge_1/3850105.html'>番外九 相守</a></dd>
        # <dd><a href="38272.html" title="我的第四本书，欢迎大家。">我的第四本书，欢迎大家。</a></dd>
        temp = re.sub("head((.|\n)*?)正文","",html)
        group = re.findall("<dd><a href(.*?)/a></dd>",temp)

        urls = []
        for line in group:
            url = re.search("(\d{1}|\d{2}|\d{3}|\d{4}|\d{5}|\d{6}|\d{7}|\d{8}|).html",line).group()
            content = re.findall(">(.*?)<",line)[0]
            urls.append("{}={}".format(url,content))
        return urls

    # 获取所有章节url 方法2
    def getChapterUrls2(self, html):
        urls = []
        return urls

    # 获取章节内容
    def getChapterContent(self, html):
        for idx in range(1,2):
            content = eval('self.getChapterContent' + str(idx) + '(html)')
            if content and content != "" :
                return content
        return ""

    # 获取章节内容，解析方法1
    def getChapterContent1(self, html):
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

    # 获取章节内容，解析方法2
    def getChapterContent2(self, html):
        return ""






















