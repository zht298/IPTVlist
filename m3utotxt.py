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
