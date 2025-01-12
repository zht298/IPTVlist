# m3u格式转txt，按m3u文件名写出txt，可处理多个链接，并在每个链接中添加组名、更改组名、更改频道名称
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def download_m3u_file(url):
    """从URL下载M3U文件内容。"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_m3u_content(m3u_content, default_group_name, rename_groups=None, rename_channel=None):
    """解析M3U文件内容，并返回包含频道信息的播放列表。"""
    lines = [line for line in m3u_content.splitlines() if line.strip()]  # 删除所有空行
    playlist = []
    current_group = default_group_name

    for line in lines:
        if line.startswith("#EXTINF"):
            try:
                if 'group-title="' in line:
                    parts = line.split('group-title="')
                    group_info = parts[1].split('"', 1)
                    group_name = group_info[0].strip()
                    channel_info = group_info[1].split(',', 1)
                    channel_name = channel_info[1].strip()
                else:
                    parts = line.split(',', 1)
                    channel_name = parts[1].strip()
                    group_name = current_group

                # 如果指定了重命名分组，则重命名分组
                if rename_groups and group_name in rename_groups:
                    group_name = rename_groups[group_name]

                # 如果指定了重命名频道，则重命名频道
                if rename_channel:
                    for old_name, new_name in rename_channel.items():
                        if old_name in channel_name:
                            channel_name = channel_name.replace(old_name, new_name)

            except IndexError:
                print(f"跳过格式错误的行: {line}")
                continue
        elif not line.startswith("#"):
            playlist.append([group_name, channel_name, line.strip()])

    return playlist

def save_playlist_to_txt(playlist, txt_filename):
    """将播放列表保存到TXT文件中。"""
    with open(txt_filename, mode='w', encoding='utf-8') as file:
        current_group = None
        for item in playlist:
            group_name, channel_name, link = item
            if group_name != current_group:
                file.write(f"{group_name},#genre#\n")
                current_group = group_name
            file.write(f"{channel_name},{link}\n")

def process_m3u_urls(m3u_urls):
    """处理一组M3U URL，下载并解析每个M3U文件，并将结果保存为TXT文件。"""
    for url_info in m3u_urls:
        url = url_info['url']
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        default_group_name = query_params.get('group', [url_info.get('default_group', 'default')])[0]

        # 如果URL中未指定分组，则添加默认分组
        if 'group' not in query_params:
            query_params['group'] = [url_info.get('default_group', 'default')]
            query_string = urlencode(query_params, doseq=True)
            parsed_url = parsed_url._replace(query=query_string)
            url = urlunparse(parsed_url)

        # 下载 M3U 文件内容（忽略 URL 中的查询参数）
        m3u_content = download_m3u_file(url.split('?')[0])
        m3u_filename = parsed_url.path.split("/")[-1]
        txt_filename = m3u_filename.replace('.m3u', '.txt')

        # 合并重命名频道的字典
        rename_channel = url_info.get('rename_channel', {})
        rename_channel.update(url_info.get('rename_channel1', {}))
        rename_channel.update(url_info.get('rename_channel2', {}))

        playlist = parse_m3u_content(
            m3u_content, 
            default_group_name, 
            rename_groups=url_info.get('rename_groups'),
            rename_channel=rename_channel
        )
        save_playlist_to_txt(playlist, txt_filename)

def main():
    """主函数，定义M3U URL并处理它们。"""
    m3u_urls = [
        {
            "url": "https://raw.githubusercontent.com/zht298/IPTVlist/main/playlist.m3u",
            # "rename_groups": {"💞央视频道": "央视"},
            # "rename_channel": {"CCTV1 综合": " 综合"},
        },
       #  {
       #      "url": "https://raw.githubusercontent.com/zht298/IPTVlist/main/playlist.m3u",
       #      "rename_groups": {"💞央视频道": "央视"},
       #      "rename_channel": {"CCTV1 综合": " 综合"},
       #  },
        {
            "url": "http://adultiptv.net/chs.m3u",
            "default_group": "成人直播_9",
            "rename_groups": {"XXX": "成人点播_9"},
            "rename_channel1": {"MyCamTV ": ""},
            "rename_channel2": {"AdultIPTV.net ": ""},
        },
        # 添加更多的链接，并在URL中指定自定义频道分组名称
    ]
    process_m3u_urls(m3u_urls)

if __name__ == "__main__":
    main()
import requests
import re
from collections import defaultdict
import subprocess
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
                    if not ipv6_pattern.search(link) and (groups is None or current_group.lower() in [g.lower() for g in groups]):  # 过滤掉IPv6链接和非指定分组
                        group_dict[current_group][channel_name].append(link)

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
        ("https://ygbh.site/bh.txt", ["💝中国移动ITV👉移动","💝汕头央卫👉广东","焦点香港"]),  # 保留所有分组
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
