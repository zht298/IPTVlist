import requests
import re

def download_txt_file(url, filename):
    """从URL下载TXT文件并保存在本地。"""
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(response.text)

def merge_txt_files(file_list, output_filename, max_channels_per_group):
    """将多个TXT文件合并成一个文件，并过滤掉IPv6地址及按指定数量保留频道。"""
    group_dict = {}
    ipv6_pattern = re.compile(r'([a-f0-9:]+:+)+[a-f0-9]+')

    for filename in file_list:
        with open(filename, 'r', encoding='utf-8') as infile:
            current_group = None
            for line in infile:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split(',')
                if len(parts) == 2 and parts[1].startswith('#genre#'):
                    current_group = parts[0]
                    if current_group not in group_dict:
                        group_dict[current_group] = []
                elif current_group and len(parts) == 2:
                    channel_name, link = parts[0], parts[1].strip()
                    if not ipv6_pattern.search(link):  # 过滤掉IPv6链接
                        group_dict[current_group].append((channel_name, link))

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for group, channels in group_dict.items():
            outfile.write(f"{group},#genre#\n")
            for channel_name, link in channels[:max_channels_per_group]:
                outfile.write(f"{channel_name},{link}\n")

def main():
    txt_urls = [
        "https://raw.githubusercontent.com/zht298/IPTVlist/refs/heads/main/playlist.txt",
        "https://raw.githubusercontent.com/zht298/IPTVlist/refs/heads/main/chs.txt",
        # 添加更多的链接
    ]
    local_filenames = []

    # 步骤1：下载TXT文件
    for i, url in enumerate(txt_urls, start=1):
        local_filename = f"file{i}.txt"
        download_txt_file(url, local_filename)
        local_filenames.append(local_filename)
        print(f"已下载：{local_filename}")

    # 步骤2：合并TXT文件并过滤
    output_filename = "merged_output.txt"
    max_channels_per_group = 10  # 设置每个分组内最多保留的频道数量
    merge_txt_files(local_filenames, output_filename, max_channels_per_group)
    print(f"已合并文件到：{output_filename}")

if __name__ == "__main__":
    main()
