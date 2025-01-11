import requests
import os

# 下载m3u文件
url = "https://raw.githubusercontent.com/zht298/IPTVlist/main/playlist.m3u"
response = requests.get(url)
m3u_content = response.text

# 获取文件名
m3u_filename = url.split("/")[-1]
txt_filename = m3u_filename.replace('.m3u', '.txt')

# 解析m3u文件内容
lines = m3u_content.splitlines()
playlist = []
current_group = None

for line in lines:
    if line.startswith("#EXTINF"):
        parts = line.split('group-title="')
        group_info = parts[1].split('"', 1)
        group_name = group_info[0]
        channel_info = group_info[1].split(',', 1)
        channel_name = channel_info[1]
    elif not line.startswith("#"):
        if current_group != group_name:
            playlist.append([group_name, "#genre#"])
            current_group = group_name
        playlist.append([channel_name, line])

# 保存为txt文件，文件名取自m3u文件名
try:
    with open(txt_filename, mode='w', encoding='utf-8') as file:
        for item in playlist:
            file.write(f"{item[0]},{item[1]}\n")
    print(f"文件 {txt_filename} 已成功创建并写入内容。")
except Exception as e:
    print(f"写入文件时出错: {e}")

# 验证文件是否成功写入
if os.path.exists(txt_filename):
    print(f"文件 {txt_filename} 存在。")
else:
    print(f"文件 {txt_filename} 不存在。")
