import os
import logging
import time
import traceback
from datetime import datetime
from Collection.bilibili_json_subscribe import ins_json
from Download.video_download import bili_json
from System_judgment.Platform import File_dir
from System_judgment.conf_collection import config_collection

# 日期获取 
def getDate():
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return "当前时间："+date


conf = config_collection()
# 获取当前目录路径
file_dir = os.path.dirname(os.path.abspath(__file__))
# 实际文件路径
CONF_FILE = os.path.join(file_dir, 'config.ini')
# 实例化语言格式
conf.read(CONF_FILE, encoding="utf-8")

# 同步收藏夹
def tb_sc():
    # 获取配置文件的参数信息
    fid_1 = conf.get("bili_collection", "fid_1")
    fid_1_name = conf.get("bili_collection", "fid_1_name")
    ins_json(fid_1, fid_1_name, file_dir)

    # ---如果有多个收藏夹，可以仿照下面复制，要记得修改数字---
    # fid_2 = conf.get("bili_collection", "fid_2")
    # fid_2_name = conf.get("bili_collection", "fid_2_name")
    # ins_json(fid_2, fid_2_name, file_dir)

# 下载收藏夹视频
def download_video():
    # 获取配置文件的参数信息
    tmp_file_name = conf.get("video_dir", "Temporary_folder")
    download_file_name = conf.get("video_dir", "Download_videos_folder")
    # 根据系统来使用linux还是windows
    # linux_dir = conf.get("video_dir", "linux_dir")
    windows_dir = conf.get("video_dir", "windows_dir")

    # 临时文件夹路径
    folder_dir_path = File_dir(windows_dir, tmp_file_name)
    # 视频下载实际保存路径
    Download_videos_path = File_dir(windows_dir, download_file_name)
    # 收藏夹视频json文件路径
    json_file_path_name1 = File_dir((os.path.join(file_dir, 'Subscribe_json')), (conf.get("bili_collection", "fid_1_name")) + ".json")
    # 调用下载
    bili_json(folder_dir_path, Download_videos_path, json_file_path_name1)

    # ---如果有多个收藏夹，可以仿照下面复制，要记得修改数字---
    # json_file_path_name2 = File_dir((os.path.join(file_dir, 'Subscribe_json')), (conf.get("bili_collection", "fid_2_name")) + ".json")
    # bili_json(folder_dir_path, Download_videos_path, json_file_path_name2)

if __name__ == '__main__':
    # 1分=60s,休眠10分钟
    sleepTime = 600
    # 添加err_log日志文件
    logging.basicConfig(filename='err.log')

    while True:
        try:
            # 执行收藏同步
            tb_sc()
            print(getDate() + " 收藏记录执行完毕！")

            try:
                # 执行视频下载
                download_video()
                print(getDate() + " 视频下载执行完毕！")
            except Exception as e:
                s = traceback.format_exc()
                print(getDate() + " 视频下载执行失败！")
                logging.error(s)

        except Exception as e:
            s = traceback.format_exc()
            print(getDate() + " 收藏记录执行失败！")
            logging.error(s)

        print("脚本执行完毕！" + getDate() + " ,休眠10分钟后，继续执行！")
        # 休眠10分钟
        time.sleep(sleepTime)
        continue
