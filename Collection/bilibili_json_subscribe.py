import math
import requests
import json
import logging
import os
import sys
import time
from pathlib import Path
from System_judgment.Platform import File_dir
from System_judgment.file_format_cleaning import mkdir_folder, bili_create_json, bili_json_format_eliminate, bili_tihuan, select_json

# 获取收藏夹一页内容
def generate_fav_content_url(fid: int, page_number: int) -> str:
    """
        获取收藏夹一页内容
        https://api.bilibili.com/x/v3/fav/resource/list?
            keyword=&order=mtime&type=0&tid=0&platform=web&jsonp=jsonp&ps=20&
            media_id={fid}&pn={page_number}
        :param fid: 收藏夹id
        :param page_number: 收藏夹中页码
        :return: 获取收藏夹一页内容url
    """

    return f'https://api.bilibili.com/x/v3/fav/resource/list?ps=20&media_id={fid}&pn={page_number}'

# 获取收藏夹信息
def generate_fav_url(fid: int) -> str:
    """
    获取收藏夹信息
    https://api.bilibili.com/x/v3/fav/resource/list?
        pn=1&ps=20&keyword=&order=mtime&type=0&tid=0&platform=web&jsonp=jsonp&
        media_id={fid}
    :param fid: 收藏夹id
    :return: 获取收藏夹信息url 
    """
    return f'https://api.bilibili.com/x/v3/fav/resource/list?ps=1&media_id={fid}'

# 查询页码
def page_numbe(fid):
    """
    fid: 视频收藏夹id
    Returns: 分页统计
    """
    # page_number = 0
    resp = request_retry_json(generate_fav_url(fid))
    # print(resp)
    media_count = resp['data']['info']['media_count']
    # medias = []
    page_count = math.ceil(media_count / 20)

    return page_count

def request_retry(url: str, headers: dict = None, retry: int = 3) -> requests.Response:
    if headers is None:
        headers = {'Connection': 'close'}
    headers['Connection'] = 'close'
    while retry > 0:
        try:
            resp = requests.get(url, headers=headers)
            return resp
        except:
            logging.error('request %s error: %s' % (url, sys.exc_info()[0]))
            time.sleep(5 - retry)
        retry -= 1
    raise requests.RequestException

def request_retry_json(url: str, headers=None, retry: int = 3) -> dict:
    return json.loads(request_retry(url, headers, retry).text)

# 读取resp信息
def request_info(resp):

    bili_json1 = []
    # bili_json1 = {}
    for a in resp['data']['medias']:
        # 视频搜索id
        av_id = a['id']
        # 视频搜索av_id链接
        av_id_link = a['link']
        # 播放时长
        n = int(a['duration'])
        m = int(n / 60)
        s = n - m * 60
        # print(f"可以换算成 {m}分钟 {s}秒。")
        duration = f"时长：{m}分钟{s}秒"

        # 类型
        type = a['type']
        # 标题
        title = a['title']

        # 去除格式和特殊符号
        re_exp = u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\’!\"#$%&\'()*+,-./:;<=>?@，。?、…【】《》？“”‘’！["u"\\]^_`{|}~\s])"
        video_title = str(title).strip(re_exp)
        # print(video_title)
        video_name = "".join(video_title.split())
        video_name = (((video_name.replace("/", "-")).replace("】", "-")).replace("[", "-")).replace("【", "-")
        video_name = (((video_name.replace("；", "-")).replace("\n", "")).replace("]", "-")).replace("r&b", "")
        video_name = (((video_name.replace("（", "-")).replace("）", "")).replace(" ", "")).replace("＆", "与")
        video_name = (((video_name.replace("--", "-")).replace("(", "")).replace(")", "")).replace("&","")
        video_name = (((video_name.replace("amp;", "")).replace("|", "-")).replace("《", "")).replace("》", "")
        # 图片链接
        cover = a['cover']
        # 摘要
        intro = a['intro']
        # 页数
        page = a['page']
        # up主个人id
        up_mid = a['upper']['mid']
        # up主昵称
        up_name = a['upper']['name']
        # up主头像
        up_face = a['upper']['face']
        # 视频id
        bv_id = a['bv_id']
        # 视频链接
        bv_link = "https://www.bilibili.com/video/" + a['bv_id']
        # 该视频收藏人数
        bv_collect = a['cnt_info']['collect']
        # 该视频播放次数
        bv_play = a['cnt_info']['play']
        # 当前观看人数
        bv_danmaku = a['cnt_info']['danmaku']

        bili_json = {
            'title': video_name,
            'intro': intro,
            'cover': cover,
            'bv_id': bv_id,
            'bv_link': bv_link,
            'page': page,
            'av_id': av_id,
            'av_id_link': av_id_link,
            'type': type,
            'duration': duration,
            'bv_collect': bv_collect,
            'bv_play': bv_play,
            'bv_danmaku': bv_danmaku,
            'up_mid': up_mid,
            'up_name': up_name,
            'up_face': up_face,
            'is_Download': 0
        }
        bili_json1.append(bili_json)

    return bili_json1

# json调用格式清理
def write_json(resp, json_file_path_name):

    bili_create_json(json_file_path_name)
    try:
        bili_json_format_eliminate(json_file_path_name)
    except Exception as err:
        pass
    with open(json_file_path_name, 'a', encoding='utf-8') as fw:
        fw.write(',')
        json.dump(resp, fw, indent=4, ensure_ascii=False)
        fw.write('\n')
    # print("写入完毕")
    fw.close()
    bili_create_json(json_file_path_name)
    bili_tihuan(json_file_path_name)

# 读写json
def read_write_json(resp, json_file_path_name):
    """
        文件操作中的 r, r+, a, a+, w, w+ 几种方式的区别:
        r只读，r+ 可读可写，若文件不存在，报错；
        w只写，w+ 可读可写，二者都会将文件内容清零,若文件不存在，创建；
        a附加写方式打开，不可读，a+ 附加读写方式打开，二者都是若文件不存在，创建；
    """
    my_file = Path(json_file_path_name)
    resp1 = request_info(resp)
    a = 0
    b = 0

    if my_file.is_file():
        for rss in resp1:
            tt1 = rss['bv_id']
            title_ysx = str(rss['title'].strip())
            flag = select_json(tt1, json_file_path_name)
            # print(flag)
            if flag == 1:
                # print("检测到已存在json文件中")
                a = a + 1
                # pass
            else:
                if title_ysx in "已失效视频":
                    print("该视频已被up主删除，已失效，为您跳过该条新增记录！")
                    # b = b + 1
                else:
                    write_json(rss, json_file_path_name)
                    b = b + 1
                    print(f'新增了第{b}条收藏记录，标题：' + rss['title'])
        print(f'已检测到已存在收藏记录{a}条,新增了{b}条收藏记录')
    else:
        print("检测到文件不存在，已为您新建json文件")
        for rss in resp1:
            title_ysx = str(rss['title'].strip())
            if title_ysx in "已失效视频":
                print("该视频已被up主删除，已失效，为您跳过该条新增记录！")
            else:
                write_json(rss, json_file_path_name)
                b = b + 1
                print(f'新增了第{b}条收藏记录，标题：' + rss['title'])
        print(f'已检测到已存在收藏记录{a}条,新增了{b}条收藏记录')

# 创建并添加json内容
def ins_json(fid: int, json_name: str, file_dir):
    # fid: 收藏夹id
    fid = fid
    # page_number: 收藏夹中页码
    page_number = page_numbe(fid)
    # 文件名称
    json_name = json_name + '.json'

    Subscribe = os.path.join(file_dir, 'Subscribe_json')
    mkdir_folder(Subscribe)
    # json文件路径名称
    json_file_path_name = File_dir(Subscribe, json_name)
    # total 负责做累加和
    total = 1

    while total <= page_number:
        url = generate_fav_content_url(fid, total)
        resp = request_retry_json(url)
        read_write_json(resp, json_file_path_name)
        print(f'第{total}页收藏夹已记录~~\n')
        total += 1

    print("执行完毕")
