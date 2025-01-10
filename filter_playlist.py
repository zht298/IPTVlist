import requests

def fetch_playlist(url):
    response = requests.get(url)
    return response.text

def filter_groups(playlist, target_groups):
    filtered_lines = []
    current_group = None
    lines = playlist.splitlines()

    for line in lines:
        if '#genre#' in line:
            current_group = line.split(',')[0].strip()
        if current_group in target_groups:
            filtered_lines.append(line)

    return filtered_lines

def save_to_file(filtered_lines, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for line in filtered_lines:
            file.write(line + '\n')

def convert_to_m3u(filtered_lines, m3u_filename):
    with open(m3u_filename, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        current_group = None
        for line in filtered_lines:
            if '#genre#' in line:
                current_group = line.split(',')[0].strip()
            else:
                parts = line.split(',')
                if len(parts) == 2:
                    channel_name, url = parts
                    file.write(f"#EXTINF:-1 group-title=\"{current_group}\",{channel_name}\n{url}\n")
        print(f"Written {m3u_filename} successfully.")

def main():
    urls = [
        "http://wp.wadg.pro/down.php/d7b52d125998d00e2d2339bac6abd2b5.txt",
        # 这里可以继续添加更多链接
        # "http://example.com/another_playlist.txt"
    ]
    target_groups = ['央视频道①', '💞央视频道', '卫视频道①', '📡卫视频道','韩国频道']
    all_filtered_lines = []

    for url in urls:
        playlist = fetch_playlist(url)
        filtered_lines = filter_groups(playlist, target_groups)
        all_filtered_lines.extend(filtered_lines)

    save_to_file(all_filtered_lines, 'filtered_playlist.txt')
    convert_to_m3u(all_filtered_lines, 'filtered_playlist.m3u')

if __name__ == "__main__":
    main()
