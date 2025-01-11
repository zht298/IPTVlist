import requests

def download_m3u_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_m3u_content(m3u_content):
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
    
    return playlist

def save_playlist_to_txt(playlist, txt_filename):
    with open(txt_filename, mode='w', encoding='utf-8') as file:
        for item in playlist:
            file.write(f"{item[0]},{item[1]}\n")

def process_m3u_urls(m3u_urls):
    for url in m3u_urls:
        m3u_content = download_m3u_file(url)
        m3u_filename = url.split("/")[-1]
        txt_filename = m3u_filename.replace('.m3u', '.txt')
        playlist = parse_m3u_content(m3u_content)
        save_playlist_to_txt(playlist, txt_filename)

def main():
    m3u_urls = [
        "https://raw.githubusercontent.com/zht298/IPTVlist/main/playlist1.m3u",
        "https://raw.githubusercontent.com/zht298/IPTVlist/main/playlist2.m3u",
        # 添加更多的链接
    ]
    process_m3u_urls(m3u_urls)

if __name__ == "__main__":
    main()
