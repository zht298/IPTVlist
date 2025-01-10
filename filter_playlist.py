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

    print("Starting filtering process...")

    for line in lines:
        if '#genre#' in line:
            current_group = clean_group_name(line.split(',')[0].strip())
            print(f"Found group: {current_group}")
            if current_group in target_groups:
                print(f"Adding group: {current_group}")
                filtered_lines.append(line)
        elif current_group in target_groups:
            filtered_lines.append(line)

    print("Filtering process completed.")
    return filtered_lines

def save_to_file(filtered_lines, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for line in filtered_lines:
            file.write(line + '\n')

def main():
    urls = [
        "http://wp.wadg.pro/down.php/d7b52d125998d00e2d2339bac6abd2b5.txt",
        # 这里可以继续添加更多链接
        # "http://example.com/another_playlist.txt"
    ]
    target_groups = ['分组2', '分组3']
    all_filtered_lines = []

    for url in urls:
        playlist = fetch_playlist(url)
        filtered_lines = filter_groups(playlist, target_groups)
        all_filtered_lines.extend(filtered_lines)

    save_to_file(all_filtered_lines, 'filtered_playlist.txt')

if __name__ == "__main__":
    main()
