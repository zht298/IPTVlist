name: M3U to TXT

on:
  schedule:
    - cron: '0 3 * * *'  # 每天北京时间上午11点运行
  workflow_dispatch:  # 允许手动触发

permissions:
  contents: write

jobs:
  m3utotxt:
    runs-on: ubuntu-24.04  # 提前更新到 ubuntu-24.04
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.x'

    - name: Install requests library
      run: |
        python -m pip install --upgrade pip
        pip install requests

    - name: Run m3utotxt script
      run: python m3utotxt.py

    - name: Commit and push if changed
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        git config --global user.name "zht298"
        git config --global user.email "zht19886@gmail.com"
        git pull origin main  # 先拉取远程更改
        git add playlist.txt  # 确保添加正确的文件名
        if ! git diff --quiet; then
          git commit -m "Update playlist with available URLs"
          git push origin main
        fi

    - name: Upload filtered playlist
      uses: actions/upload-artifact@v4
      with:
        name: filtered-playlist
        path: "*.txt"
