import requests
import re
from collections import defaultdict
import subprocess
import warnings
import time
import chardet  # 确保导入 chardet

# 禁用未验证的HTTPS请求警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def download_txt_file(url, filename):
    """从URL下载TXT文件并保存在本地。"""
    retries = 3
    for attempt in range(retries):
        try:
            print(f"正在尝试下载文件: {url} (尝试次数: {attempt + 1})")
            response = requests.get(url, verify=False)  # 绕过 SSL 验证
            response.raise_for_status()
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"成功下载文件: {url}")
            return
        except requests.exceptions.SSLError as e:
            print(f"SSL 错误：{e}")
        except requests.exceptions.RequestException as e:
            print(f"请求错误：{e}")
        if attempt < retries - 1:
            print("等待3秒后重试...")
            time.sleep(3)
    print(f"无法下载文件：{url}")

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        print(f"检测到的编码: {encoding}, 置信度: {confidence}")
        return encoding

def merge_txt_files(file_list, output_filename, max_channels_per_name):
    """将多个TXT文件合并成一个文件，并过滤掉IPv6地址及按指定数量保留每个频道名称的项。"""
    group_dict = defaultdict(lambda: defaultdict(list))
    ipv6_pattern = re.compile(r'([a-f0-9:]+:+)+[a-f0-9]+')

    for filename, groups in file_list:
        print(f"正在处理文件: {filename}")
        encoding = detect_encoding(filename)
        with open(filename, 'r', encoding=encoding, errors='ignore') as infile:
            current_group = None
            for line in infile:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split(',')
                if len(parts) == 2 and parts[1].startswith('#genre#'):
                    current_group = parts[0].strip()
                    print(f"找到分组: {current_group}")  # 添加调试打印
                elif current_group and len(parts) == 2:
                    channel_name, link = parts[0].strip(), parts[1].strip()
                    if not ipv6_pattern.search(link) and (groups is None or current_group.lower() in [g.lower() for g in groups]):  # 过滤掉IPv6链接和非指定分组
                        group_dict[current_group][channel_name].append(link)
                        print(f"添加频道: {channel_name} 链接: {link} 到分组: {current_group}")  # 添加调试打印

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for group, channels in group_dict.items():
            outfile.write(f"{group},#genre#\n")
            for channel_name, links in channels.items():
                for link in links[:max_channels_per_name]:
                    outfile.write(f"{channel_name},{link}\n")

def git_add_files(files, user_name, user_email):
    """将文件添加到Git版本控制中。"""
    # 设置用户信息
    subprocess.run(["git", "config", "user.name", user_name])
    subprocess.run(["git", "config", "user.email", user_email])
    
    for file in files:
        subprocess.run(["git", "add", file])
    subprocess.run(["git", "commit", "-m", "Add new downloaded files"])
    subprocess.run(["git", "push"])

def main():
    txt_urls_with_groups = [
        # ("https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt", ["央视频道", "卫视频道","影视频道"]),
        # 出处 月光宝盒抓取直播
        ("https://ygbh.site/bh.txt", ["💝中国移动ITV👉移动","💝汕头央卫👉广东"]),  # 保留所有分组
        # 小苹果，蜗牛线路[测试2]
        # ("http://wp.wadg.pro/down.php/d7b52d125998d00e2d2339bac6abd2b5.txt", ["央视频道①", "💞央视频道", "卫视频道①", "📡卫视频道","韩国频道"]),      
        # ("https://raw.githubusercontent.com/zht298/IPTVlist/main/dalian.txt", None),  # 保留所有分组  大连台
        # 出处 小鹦鹉等多处获取 
        # ("https://raw.githubusercontent.com/zht298/IPTVlist/main/JJdoudizhu.txt", None),  # 保留所有分组  JJ斗地主
        # 出处 https://adultiptv.net/→http://adultiptv.net/chs.m3u
        # ("https://raw.githubusercontent.com/zht298/IPTVlist/main/chs.txt",None),  # 保留所有分组
        # 添加更多的链接和对应的分组
    ]
    local_filenames_with_groups = []

    # 步骤1：下载TXT文件
    for i, (url, groups) in enumerate(txt_urls_with_groups, start=1):
        local_filename = f"file{i}.txt"
        download_txt_file(url, local_filename)
        local_filenames_with_groups.append((local_filename, groups))

    # 步骤2：合并TXT文件并过滤
    output_filename = "merged_output.txt"
    max_channels_per_name = 10  # 设置每个频道名称最多保留的项数量
    merge_txt_files(local_filenames_with_groups, output_filename, max_channels_per_name)

    # 步骤3：添加文件到Git版本控制中
    user_name = "zht298"
    user_email = "zht19886@gmail.com"
    git_add_files([f"file{i}.txt" for i in range(1, len(txt_urls_with_groups) + 1)] + ["merged_output.txt"], user_name, user_email)

if __name__ == "__main__":
    main()
