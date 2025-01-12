import requests
import re
import unicodedata
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

def normalize_text(text):
    """标准化文本以进行比较。"""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()

def merge_txt_files(file_list, output_filename, max_channels_per_name):
    """将多个TXT文件合并成一个文件，并过滤掉IPv6地址及按指定数量保留每个频道名称的项。"""
    group_dict = defaultdict(lambda: defaultdict(list))
    ipv6_pattern = re.compile(r'([a-f0-9:]+:+)+[a-f0-9]+')

    for filename, groups in file_list:
        print(f"正在处理文件: {filename}")
        with open(filename, 'r', encoding='utf-8', errors='ignore') as infile:
            current_group = None
            for line in infile:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split(',')
                if len(parts) == 2 and parts[1].startswith('#genre#'):
                    current_group = parts[0].strip()
                    print(f"找到分组: {current_group}")
                elif current_group and len(parts) == 2:
                    channel_name, link = parts[0].strip(), parts[1].strip()
                    normalized_group = normalize_text(current_group)
                    if not ipv6_pattern.search(link) and (groups is None or any(normalize_text(g) == normalized_group for g in groups)):  # 过滤掉IPv6链接和非指定分组
                        group_dict[current_group][channel_name].append(link)
                        print(f"添加频道: {channel_name} 链接: {link} 到分组: {current_group}")

    print("合并后的分组名称：")
    for group in group_dict.keys():
        print(f"合并分组: {group}")

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for group, channels in group_dict.items():
            outfile.write(f"{group},#genre#\n")
            print(f"写入分组: {group}")  # 打印写入到文件中的分组名称
            for channel_name, links in channels.items():
                for link in links[:max_channels_per_name]:
                    outfile.write(f"{channel_name},{link}\n")
                    print(f"写入频道: {channel_name}, 链接: {link}")

def main():
    txt_urls_with_groups = [
        ("https://ygbh.site/bh.txt", ["💝中国移动ITV👉移动","💝汕头央卫👉广东","焦点香港"]),  # 保留所有分组
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
