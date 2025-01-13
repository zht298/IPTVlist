import requests
import re
from collections import defaultdict
import warnings
import time

# 禁用未验证的HTTPS请求警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def download_txt_file(url, filename):
    """从URL下载TXT文件并保存在本地。"""
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, verify=False)  # 绕过 SSL 验证
            response.raise_for_status()
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded content from {url} to {filename}")  # 打印下载成功信息
            return
        except requests.exceptions.SSLError as e:
            print(f"SSL Error while downloading {url}: {e}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Request Error while downloading {url}: {e}")
            continue
        if attempt < retries - 1:
            time.sleep(3)

def merge_txt_files(file_list, output_filename, max_channels_per_name):
    """将多个TXT文件合并成一个文件，并过滤掉IPv6地址及按指定数量保留每个频道名称的项。"""
    group_dict = defaultdict(lambda: defaultdict(list))
    ipv6_pattern = re.compile(r'([a-f0-9:]+:+)+[a-f0-9]+')

    for filename, groups in file_list:
        print(f"Processing file: {filename}")  # 打印正在处理的文件名
        with open(filename, 'r', encoding='utf-8', errors='ignore') as infile:
            content = infile.read()
            print(f"Content of {filename}:\n{content}\n")  # 打印文件内容
            infile.seek(0)  # 重置文件指针到开头
            current_group = None
            for line in infile:
                print(f"Processing line: {line.strip()}")  # 打印每一行内容
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split(',')
                print(f"Split parts: {parts}")  # 打印分割后的部分
                if len(parts) == 2 and parts[1].startswith('#genre#'):
                    current_group = parts[0].strip()
                    print(f"Current group set to: {current_group}")  # 打印current_group
                elif current_group and len(parts) == 2:
                    channel_name, link = parts[0].strip(), parts[1].strip()
                    print(f"Found channel: {channel_name}, link: {link}")  # 打印频道和链接
                    if not ipv6_pattern.search(link):
                        if groups is None or current_group in groups:
                            group_dict[current_group][channel_name].append(link)
                            print(f"Added {channel_name}: {link} to group {current_group}")  # 打印已添加信息

    print(f"Group dictionary: {group_dict}")  # 打印合并后的字典
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for group, channels in group_dict.items():
            outfile.write(f"{group},#genre#\n")
            for channel_name, links in channels.items():
                for link in links[:max_channels_per_name]:
                    outfile.write(f"{channel_name},{link}\n")
    print(f"Merged output written to {output_filename}")  # 打印合并成功信息

def main():
    txt_urls_with_groups = [
        # ("https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt", ["央视频道", "卫视频道","影视频道"]),
        # 出处 月光宝盒抓取直播
        # ("https://ygbh.site/bh.txt", ["💝中国移动ITV👉移动","💝汕头央卫👉广东"]),  # 保留所有分组
        ("https://raw.githubusercontent.com/zht298/IPTVlist/refs/heads/main/ygbh.txt", None), 
        # 小苹果，蜗牛线路[测试2]
        # ("http://wp.wadg.pro/down.php/d7b52d125998d00e2d2339bac6abd2b5.txt",
        #  ["央视频道①", "💞央视频道", "卫视频道①", "📡卫视频道","韩国频道"]),      
        ("https://raw.githubusercontent.com/zht298/IPTVlist/main/dalian.txt", None),  # 保留所有分组  大连台
        # 出处 小鹦鹉等多处获取 
        ("https://raw.githubusercontent.com/zht298/IPTVlist/main/JJdoudizhu.txt", None),  # 保留所有分组  JJ斗地主
        # 出处 https://adultiptv.net/→http://adultiptv.net/chs.m3u
        ("https://raw.githubusercontent.com/zht298/IPTVlist/main/chs.txt", None),  # 保留所有分组
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

if __name__ == "__main__":
    main()
