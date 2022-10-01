import os
import platform
from System_judgment.file_format_cleaning import mkdir_folder

# 判断当前运行平台
def isWondowsorLinux():
    ''' 判断当前运行平台 :return: '''
    sysstr = platform.system()
    if (sysstr == "Windows"):
        return True
    elif (sysstr == "Linux"):
        return False
    else:
        print("Other System ")
    return False

# 根据系统环境分配文件保存路径
def File_dir(file_dir: str, json_name: str):
    mkdir_folder(file_dir)

    # 判断当前系统环境
    if isWondowsorLinux() == True:
        windows_dir = os.path.join(file_dir, json_name)
        return windows_dir
    else:
        linux_dir = os.path.join(file_dir, json_name)
        return linux_dir