# -*- coding: utf-8 -*-
import csv
import datetime
import os
import sys

sys.path[0] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from utilTools.getConfig import CommonConfig

def getCSVObject(file):
    dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if dir.endswith('/'):
        dir = dir.split('/')[0]
    dataSource = CommonConfig.get_cf("config", "env", "dataSource")
    reader = csv.reader(open(dir + '/data/'+ dataSource + '_' + file + '.csv', 'r'))
    return reader


def timeStrfMin():
    # 获取当前时间
    now = datetime.datetime.now()

    # 将当前时间按照指定格式进行格式化
    return now.strftime("%Y-%m-%d %H:%M")


def findFilesList(path, fileType):
    dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 获取特定路径下某些格式的文件（绝对路径），并list回传
    pyList = []
    count = 0
    for root, dirs, files in os.walk(sys.path[0] + path):
        for f in files:
            if f.endswith(fileType):
                pyList.append(os.path.join(root, f).replace('\\','/'))
                count += 1
    return pyList


if __name__ == '__main__':
    print(findFilesList('/prepare', '.py'))