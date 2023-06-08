import datetime
import time
import os

def clear_file_contents(file_path):
    with open(file_path, 'w') as file:
        file.write('')

def schedule_task():
    while True:
        current_time = datetime.datetime.now().time()
        if current_time.hour == 0 and current_time.minute == 0:
            file_path = 'path/to/your/file.txt'  # 替换为你的文件路径
            clear_file_contents(file_path)
            break
        time.sleep(60)  # 每隔一分钟检查一次时间

schedule_task()