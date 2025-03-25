import subprocess
import datetime
import time
import socket

def check_internet_connection(host="github.com", port=443, timeout=5):
    """检查是否能连接到指定主机和端口"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def run_command(command):
    """运行一个 shell 命令并返回结果"""
    print(f"正在执行命令: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"错误: 命令执行失败:\n{stderr.decode(errors='ignore')}")
    else:
        print(f"成功: 命令输出:\n{stdout.decode(errors='ignore')}")
    return process.returncode, stdout.decode(errors='ignore'), stderr.decode(errors='ignore')

def check_changes():
    """检查是否有未提交的更改"""
    _, stdout, _ = run_command("git status --porcelain")
    return bool(stdout.strip())  # 如果有输出，说明有未提交的更改

def generate_commit_message():
    """生成包含日期时间的提交消息"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return f"自动提交更新 - {date_str}"

def add_and_push():
    # 检查是否有需要提交的更改
    if not check_changes():
        print("没有需要提交的更改。工作区干净。")
        return True  # 没有更改也算成功

    # 添加所有更改
    if run_command("git add .")[0] != 0:
        print("添加文件失败")
        return False  # 如果命令失败，则退出

    # 提交更改，使用包含时间戳的提交消息
    commit_message = generate_commit_message()
    if run_command(f'git commit -m "{commit_message}"')[0] != 0:
        print("提交更改失败")
        return False  # 如果命令失败，则退出

    # 检查网络连接
    max_retries = 3
    retry_delay = 5  # 秒
    
    for attempt in range(max_retries):
        if not check_internet_connection():
            print(f"无法连接到GitHub。正在重试 ({attempt+1}/{max_retries})...")
            time.sleep(retry_delay)
            continue
            
        # 推送更改到远程 master 分支
        push_result = run_command("git push origin master")
        if push_result[0] != 0:
            if "Could not connect to server" in push_result[2]:
                print(f"网络连接问题，重试中 ({attempt+1}/{max_retries})...")
                time.sleep(retry_delay)
                continue
            else:
                print("推送失败，请尝试手动解决问题")
                return False  # 如果命令失败，则退出
        else:
            print("成功推送更改到远程仓库")
            return True
            
    print(f"经过 {max_retries} 次尝试后，仍无法连接到GitHub。请检查您的网络连接。")
    return False

if __name__ == "__main__":
    # 立即执行 add 和 push
    success = add_and_push()
    print(f"自动提交脚本执行{'成功' if success else '失败'}")
