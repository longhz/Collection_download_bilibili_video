# Collection_download_bilibili_video
> This is a download script source code, 
> used to automatically download bilibili favorite video, of course, 
> before using you need to get to your favorite_id: fid,
> and then modify the config.ini, the attachment has a packaged zip file,
> well ... It is a bit big, because it contains ffmpeg and python3.7, 
> you can first install these yourself in the system to set the environment variables, 
> and then use my script. 
> I will continue to improve it later 

## 1.Modify config.ini 

After getting the fid, you need to change the configuration information in config.ini

```
[bili_collection]
fid_1: 1781782216
fid_1_name: 测试收藏

;Of course, you can also have more favorites
;fid_2: #
;fid_2_name: #

;fid_3: #
;fid_3_name: #
;...

[video_dir]
;临时文件夹名称
Temporary_folder: tmp
;视频文件夹名称
Download_videos_folder: Download_videos
;具体保存路径
windows_dir: D:/Downloads/video/
```

## 2.Modify main.py
If you add some information to the bili_collection, then main.py also needs to be adjusted


```
# 同步收藏夹，第一处修改
def tb_sc():
    # ---如果有多个收藏夹，可以仿照下面复制，要记得修改数字---
    fid_2 = conf.get("bili_collection", "fid_2")
    fid_2_name = conf.get("bili_collection", "fid_2_name")
    ins_json(fid_2, fid_2_name, file_dir)
    
    # fid_3 = conf.get("bili_collection", "fid_3")
    # fid_3_name = conf.get("bili_collection", "fid_3_name")
    # ins_json(fid_2, fid_2_name, file_dir)
    
# 下载收藏夹视频，第二处修改
def download_video():

    # ---如果有多个收藏夹，可以仿照下面复制，要记得修改数字---
    json_file_path_name2 = File_dir((os.path.join(file_dir, 'Subscribe_json')), (conf.get("bili_collection", "fid_2_name")) + ".json")
    bili_json(folder_dir_path, Download_videos_path, json_file_path_name2)
    
    --------------------------------------------------
    
    #json_file_path_name3 = File_dir((os.path.join(file_dir, 'Subscribe_json')), (conf.get("bili_collection", "fid_3_name")) + ".json")
    #bili_json(folder_dir_path, Download_videos_path, json_file_path_name3)
```

### Sample image of script execution
![](https://cdn.jsdelivr.net/gh/longhz/cdn/images/blog1/202210011139740.png)
![](https://cdn.jsdelivr.net/gh/longhz/cdn/images/blog1/202210011140513.png)
