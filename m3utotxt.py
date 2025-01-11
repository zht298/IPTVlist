import requests

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
with open(txt_filename, mode='w', encoding='utf-8') as file:
    for item in playlist:
        file.write(f"{item[0]},{item[1]}\n")
