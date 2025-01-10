import requests
import re

def fetch_playlist(url):
    response = requests.get(url)
    return response.text

def clean_group_name(group_name):
    # 去掉分组名称的特殊字符
    return re.sub(r'[^\w\s]', '', group_name)

def filter_groups(playlist, target_groups):
    filtered_lines = []
    current_group = None
    lines = playlist.splitlines()

    for line in lines:
        if '#genre#' in line:
            current_group = clean_group_name(line.split(',')[0].strip())
        elif current_group in target_groups:
            filtered_lines.append(line)

    return filtered_lines

def save_to_file(filtered_lines, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for line in filtered_lines:
            file.write(line + '\n')

def main():
    url = "http://wp.wadg.pro/down.php/d7b52d125998d00e2d2339bac6abd2b5.txt"
    target_groups = ['分组2', '分组3']

    playlist = fetch_playlist(url)
    filtered_lines = filter_groups(playlist, target_groups)
    save_to_file(filtered_lines, 'filtered_playlist.txt')

if __name__ == "__main__":
    main()
