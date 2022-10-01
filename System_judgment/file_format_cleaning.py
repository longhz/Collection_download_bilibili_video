#!/usr/bin/python
# encoding:utf-8
import json
import os
import re

"""

       文件操作中的 r, r+, a, a+, w, w+ 几种方式的区别:
       r只读，r+ 可读可写，若文件不存在，报错；
       w只写，w+ 可读可写，二者都会将文件内容清零,若文件不存在，创建；
       a附加写方式打开，不可读，a+ 附加读写方式打开，二者都是若文件不存在，创建； 

"""
# 创建文件
def mkdir_folder(path):
    """
    Args:
        path: 创建临时文件
    Returns:
    """
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在 存在 True 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        # print(path+' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        # print(path+' 目录已存在')
        return False

def rm_folder(dir):
    """

    Args:
        dir: 遍历删除文件夹和文件

    Returns:

    """
    # 引入模块
    import os
    # 判断是否是文件夹，如果是，递归调用rmdir()函数
    if (os.path.isdir(dir)):
        # 遍历地址下的所有文件
        for file in os.listdir(dir):
            # 删除文件
            oo = dir + r'/' + file
            os.remove(oo)
            # print("文件已删除")
            # 继续删除文件夹
            rm_folder(dir)
        # 如果是空文件夹，直接删除
        if (os.path.exists(dir)):
            os.rmdir(dir)
            # print(dir, "文件夹删除成功")
    # 如果是文件，直接删除
    else:
        if (os.path.exists(dir)):
            os.remove(dir)
            print(dir, "文件删除成功")

# True/False
def bili_create_json(json_file_path_name):
    ffe = os.path.exists(json_file_path_name)

    if ffe == True:

        with open(json_file_path_name, 'a', encoding='utf-8') as fw:
            fw.write(']\n')
        # print("写入完毕")
        fw.close()
    else:
        with open(json_file_path_name, 'w+', encoding='utf-8') as fw:
            fw.write('[')
        # print("创建写入完毕")
        fw.close()

def bili_red(json_file_path_name):
    with open(json_file_path_name, 'r', encoding='utf-8') as jsonFile:
        data = json.load(jsonFile)
        # print(data[1]['title'])
        print(data)

    jsonFile.close()

def bili_json_format_eliminate(json_file_path_name):
    matchPattern = re.compile(r']')

    file = open(json_file_path_name, 'r', encoding='UTF-8')
    lineList = []
    while 1:
        line = file.readline()
        if not line:
            # print("指定格式已清理")
            break
        elif matchPattern.search(line):
            pass
        else:
            lineList.append(line)
    file.close()
    file = open(json_file_path_name, 'w', encoding='UTF-8')
    for i in lineList:
        file.write(i)
    file.close()

def bili_tihuan(json_file_path_name):
    # 创建一个变量并存储我们要搜索的文本
    search_text = "[,"

    # 创建一个变量并存储我们要添加的文本
    replace_text = "["

    # 使用 open() 函数以只读模式打开我们的文本文件
    with open(json_file_path_name, 'r', encoding='UTF-8') as file:
        # 使用 read() 函数读取文件内容并将它们存储在一个新变量中
        data = file.read()

        # 使用 replace() 函数搜索和替换文本
        data = data.replace(search_text, replace_text)

    # 以只写模式打开我们的文本文件以写入替换的内容
    with open(json_file_path_name, 'w', encoding='UTF-8') as file:
        # 在我们的文本文件中写入替换的数据
        file.write(data)

    # 打印文本已替换
    # print("文本已替换")

def select_json(bv_id, json_file_path_name):
    # title = "[干货向]智能家居装修指南 EP1.布线篇"
    with open(json_file_path_name, 'r', encoding='utf-8') as jsonFile:
        data = json.load(jsonFile)
        aa = 0
        for data_a in data:
            if bv_id == data_a['bv_id']:
                # print("存在")
                aa = aa+1
                jsonFile.close()
                return aa
            else:
                pass
        # print(aa)
        jsonFile.close()
        return aa