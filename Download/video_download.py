import time
import json
import re
import os
import requests
import subprocess
from tqdm import tqdm
from datetime import datetime
from System_judgment.Platform import File_dir
from System_judgment.conf_collection import config_collection
from System_judgment.file_format_cleaning import mkdir_folder, rm_folder

# 请求的url地址
def get_response(html_url):
    """
    Args: 发送请求，以及获取数据函数
        html_url: 请求的url地址 
    Returns: 返回请求服务器返回的响应数据
    """
    # 请求代码，在发送请求前，需要进行伪装 headers 请求头
    # user-agent 浏览器基本标识 用户代理 基本伪装 反爬手段
    # <Response [200]> 对象response响应对象 200 状态码 表示请求成功
    # 404 网址可能出错
    # 403 网址没有权限，出现 403 加防盗链 referer ,是为了告诉服务器，我们发送请求的url地址，是从哪里跳转过来的

    headers = {
        "referer": "https://search.www.bilibili.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }

    response = requests.get(url=html_url, headers=headers, stream=True)  # 请求代码
    # stream 字节流 (可选，开启后可用于判断大小以及做进度条使用)
    # 一般选取小而快的内容时，将stream设置为false或者不加也许，可以快速的读取response.content内容
    # 当stream开启后，后面需要自己执行response.close()操作进行关闭接收，否则只有所有的响应体数据被读取完毕连接才会被释放，如果用with可以不用close()

    return response

# 视频的详情页
def get_video_info(html_url):
    """
    获取视频标题 /音频 url地址 / 视频画面url地址
    Args:
        html_url: 视频的详情页

    Returns: 视频标题 /音频 url地址 / 视频画面url地址

    """

    response = get_response(html_url=html_url)
    # response.text 获取响应体的文本数据
    # print(response.text)
    # 解析数据 提取视频标题 re正则表达式 css选择器 xpath bs4 parsel lxml (解析模块) jsonpath 主要提取json数据

    # 正则表达式提取的数据内容 返回都是列表数据类型[0] 列表 所返回的索引取值（ 0或者-1都行，0是从左往右，-1是从右往左）
    title = re.findall('<h1 title="(.*?)" class="video-title tit">', response.text)[0] # 标题

    # 去除格式和特殊符号
    re_exp = u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\’!\"#$%&\'()*+,-./:;<=>?@，。?、…【】《》？“”‘’！["u"\\]^_`{|}~\s])"
    video_title = str(title).strip(re_exp)

    video_name = "".join(video_title.split())
    video_name = (((video_name.replace("/", "-")).replace("】", "-")).replace("[", "-")).replace("【", "-")
    video_name = (((video_name.replace("；", "-")).replace("\n", "")).replace("]", "-")).replace("r&b", "")
    video_name = (((video_name.replace("（", "-")).replace("）", "")).replace(" ", "")).replace("＆", "与")
    video_name = (((video_name.replace("--", "-")).replace("(", "")).replace(")", "")).replace("&", "")
    video_name = (((video_name.replace("amp;", "")).replace("|", "-")).replace("《", "")).replace("》", "")


    html_data = re.findall('<script>window.__playinfo__=(.*?)</script>',response.text)[0]
    # html_data 是<class 'str'>数据类型
    # 为了更加方便提取数据，可以字符串数据 转换成 字典数据类型
    json_data = json.loads(html_data)
    # 根据键值对取值
    audio_url = json_data['data']['dash']['audio'][0]['base_url']
    video_url = json_data['data']['dash']['video'][0]['base_url']
    video_info = [video_name, audio_url, video_url]

    return video_info

# 保存数据函数
def save(title, audio_url, video_url, tmp_dir):
    """

    Args: 保存数据函数
        title: 视频标题
        audio_url: 音频url
        video_url: 视频画面url
    Returns:

    """

    au_response = get_response(html_url=audio_url)
    audio_content = au_response.iter_content(chunk_size=1024)
    au_total = int(au_response.headers.get('content-length', 0))

    vi_response = get_response(html_url=video_url)
    video_content = vi_response.iter_content(chunk_size=1024)
    vi_total = int(vi_response.headers.get('content-length', 0))

    with open(tmp_dir + '/' + title + '.mp3', mode='wb') as f, tqdm(
            desc="音频下载进度",
            total=au_total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024
    ) as bar:
        for data in audio_content:
            size = f.write(data)
            bar.update(size)
        f.close()

    with open(tmp_dir + '/' + title + '.mp4', mode='wb') as f, tqdm(
            desc="视频下载进度",
            total=vi_total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024
    ) as bar:
        for data in video_content:
            size = f.write(data)
            bar.update(size)
        f.close()

    print(title, "已下载保存至临时目录：" + tmp_dir + '/' + title)

# 数据合并 - 视频合并
def merge_data(video_name, tmp_dir, Download_videos):
    """ 数据合并 - 视频合并 """

    print('视频合并开始：', video_name)
    cmd = f"ffmpeg -i {tmp_dir}/{video_name}.mp4 -i {tmp_dir}/{video_name}.mp3 -c:v copy -c:a aac -strict experimental {Download_videos}/{video_name}.mp4"
    subprocess.run(cmd, shell=True)
    print(f'视频合成结束,已将视频保存至路径： {Download_videos}/{video_name}.mp4')

# 下载主函数
def Download_main(bv_id, tmp_dir, Download_videos):
    """

    Args: 下载主函数
        bv_id: bv号
        tmp_dir：临时目录
        Download_videos：实际保存目录
    Returns:

    """
    url = f'https://www.bilibili.com/video/{bv_id}'
    video_info = get_video_info(url)  # [title, audio_url, video_url]

    save(video_info[0], video_info[1], video_info[2], tmp_dir)
    merge_data(video_info[0], tmp_dir, Download_videos)

# 下载前校验文件夹是否存在
def bili_download_main(folder_dir, Download_videos, bv_id):
    # url = 'https://www.bilibili.com/video/BV1xL411M7yg/'
    # video_info = get_video_info(url)
    # print(video_info)

    # 键盘输入
    # keyword = input("输入要下载的bv号：")
    # main(keyword)
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = datetime.strptime(start_time, r"%Y-%m-%d %H:%M:%S")

    try:
        mkdir_folder(folder_dir)
        print("临时文件夹——创建成功")

        mkdir_folder(Download_videos)
        print("视频实际存储文件夹——创建成功")

        Download_main(bv_id, folder_dir, Download_videos)
        print("视频下载成功")

        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, r"%Y-%m-%d %H:%M:%S")
        diff = end_time - start_time

        rm_folder(folder_dir)
        print("临时文件夹——已删除")
        print(f"总计运行{diff.total_seconds()}秒")
    except Exception as err:
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, r"%Y-%m-%d %H:%M:%S")
        diff = end_time - start_time
        print("临时文件夹——已删除")
        print(f"总计运行{diff.total_seconds()}秒")

# 读取json文件，执行脚本，修改下载状态
def bili_json(folder_dir, Download_videos, json_file_path_name):
    """

    Args: 读取json文件，执行脚本，修改下载状态
        folder_dir:
        Download_videos:

    Returns:

    """
    # 休眠10s
    sleepTime = 10

    json_flag = json_file_path_name.strip()
    # 判断路径是否存在 存在 True 不存在   False
    isExists = os.path.exists(json_flag)

    # 判断结果
    if not isExists:
        print(json_file_path_name + "不存在,已为您跳过!")
    else:
        with open(json_file_path_name, 'r', encoding='utf-8') as jsonFile:

            data = json.load(jsonFile)
            for aa in data:
                bv_id = aa['bv_id']
                is_Download = aa['is_Download']
                title = aa['title']

                # print(type(is_Download))
                if is_Download == 0:

                    bb = str(aa['is_Download']).replace('0', '1')
                    print(f"\n检测到新收藏,标题为：{title},正在下载,请稍后")
                    bili_download_main(folder_dir, Download_videos, bv_id)
                    aa['is_Download'] = int(bb)
                    # print("下载脚本执行完毕！,休眠30s后，继续执行！ \n ------------------------------------------------")
                    with open(json_file_path_name, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                        f.close()
                    # jsonFile.close()
                    print(f"休眠10s后，将执行下载命令！ \n ------------------------------------------------")
                    time.sleep(sleepTime)

                else:
                    jsonFile.close()
                    print(title + "\n检测到已存在下载历史，已为你跳过下载~ \n ------------------------------------------------")

if __name__ == '__main__':
    conf = config_collection()
    # 获取当前目录路径
    file_dir = os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), ".")))
    # file_dir = os.path.dirname(os.path.abspath(__file__))
    # 实际文件路径
    CONF_FILE = os.path.join(file_dir, 'config.ini')
    # 实例化语言格式
    conf.read(CONF_FILE, encoding="utf-8")
    # 获取配置文件的参数信息
    tmp_file_name = conf.get("video_dir", "Temporary_folder")
    download_file_name = conf.get("video_dir", "Download_videos_folder")
    # linux_dir = conf.get("video_dir", "linux_dir")
    windows_dir = conf.get("video_dir", "windows_dir")

    # 临时文件夹路径
    folder_dir_path = File_dir(windows_dir, tmp_file_name)
    # 视频下载实际保存路径
    Download_videos_path = File_dir(windows_dir, download_file_name)
    # 收藏夹视频json文件路径
    Subscribe = os.path.join(file_dir, 'Subscribe_json')
    # print(Subscribe)
    json_file_path_name1 = File_dir(Subscribe, (conf.get("bili_collection", "fid_1_name"))+".json")
    bili_json(folder_dir_path, Download_videos_path, json_file_path_name1)