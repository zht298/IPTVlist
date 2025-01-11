import requests
from urllib.parse import urlparse, parse_qs

def download_m3u_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_m3u_content(m3u_content, default_group_name):
    lines = m3u_content.splitlines()
    playlist = []
    current_group = default_group_name

    for line in lines:
        if line.startswith("#EXTINF"):
            try:
                if 'group-title="' in line:
                    parts = line.split('group-title="')
                    group_info = parts[1].split('"', 1)
                    group_name = group_info[0]
                    channel_info = group_info[1].split(',', 1)
                    channel_name = channel_info[1]
                else:
                    parts = line.split(',', 1)
                    channel_name = parts[1]
                    group_name = current_group
            except IndexError:
                print(f"Skipping malformed line: {line}")
                continue
        elif not line.startswith("#"):
            playlist.append([group_name, channel_name, line])
    
    return playlist

def save_playlist_to_txt(playlist, txt_filename):
    with open(txt_filename, mode='w', encoding='utf-8') as file:
        current_group = None
        for item in playlist:
            group_name, channel_name, link = item
            if group_name != current_group:
                file.write(f"{group_name},#genre#\n")
                current_group = group_name
            file.write(f"{channel_name},{link}\n")

def process_m3u_urls(m3u_urls):
    for url in m3u_urls:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        default_group_name = query_params.get('group', ['default'])[0]

        # 下载 M3U 文件内容（忽略 URL 中的查询参数）
        m3u_content = download_m3u_file(url.split('?')[0])
        m3u_filename = parsed_url.path.split("/")[-1]
        txt_filename = m3u_filename.replace('.m3u', '.txt')
        
        playlist = parse_m3u_content(m3u_content, default_group_name)
        save_playlist_to_txt(playlist, txt_filename)

def main():
    m3u_urls = [
        "https://raw.githubusercontent.com/zht298/IPTVlist/main/playlist.m3u",
        "http://adultiptv.net/chs.m3u?group=直播",  # 没有 group 参数
        # 添加更多的链接，并在URL中指定自定义频道分组名称
    ]
    process_m3u_urls(m3u_urls)

if __name__ == "__main__":
    main()
