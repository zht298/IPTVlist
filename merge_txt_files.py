import requests

def download_txt_file(url, filename):
    """Download a TXT file from a URL and save it locally."""
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(response.text)

def merge_txt_files(file_list, output_filename):
    """Merge multiple TXT files into a single file."""
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for filename in file_list:
            with open(filename, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write('\n')  # Ensure each file's content is separated by a new line

def main():
    txt_urls = [
        "https://example.com/file1.txt",
        "https://example.com/file2.txt",
        # 添加更多的链接
    ]
    local_filenames = []

    # Step 1: Download TXT files
    for i, url in enumerate(txt_urls, start=1):
        local_filename = f"file{i}.txt"
        download_txt_file(url, local_filename)
        local_filenames.append(local_filename)
        print(f"Downloaded: {local_filename}")

    # Step 2: Merge TXT files
    output_filename = "merged_output.txt"
    merge_txt_files(local_filenames, output_filename)
    print(f"Merged files into: {output_filename}")

if __name__ == "__main__":
    main()
