import requests

def download_txt_file(url, filename):
    """从URL下载TXT文件并保存在本地。"""
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(response.text)

def merge_txt_files(file_list, output_filename):
    """将多个TXT文件合并成一个文件。"""
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for filename in file_list:
            with open(filename, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write('\n')  # 确保每个文件的内容之间有一个新行

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

    # 步骤2：合并TXT文件
    output_filename = "merged_output.txt"
    merge_txt_files(local_filenames, output_filename)
    print(f"已合并文件到：{output_filename}")

if __name__ == "__main__":
    main()
