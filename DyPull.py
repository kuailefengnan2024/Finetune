import subprocess
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

def git_pull():
    """从远程仓库拉取更新"""
    print("正在从远程仓库拉取更新...")
    
    # 检查网络连接
    max_retries = 3
    retry_delay = 5  # 秒
    
    for attempt in range(max_retries):
        if not check_internet_connection():
            print(f"无法连接到GitHub。正在重试 ({attempt+1}/{max_retries})...")
            time.sleep(retry_delay)
            continue
    
        # 先尝试获取远程更新信息
        fetch_result = run_command("git fetch --all")
        if fetch_result[0] != 0:
            if "Could not connect to server" in fetch_result[2]:
                print(f"网络连接问题，重试中 ({attempt+1}/{max_retries})...")
                time.sleep(retry_delay)
                continue
            else:
                print("警告: 无法获取远程仓库信息")
                return False
            
        # 执行拉取操作
        pull_result = run_command("git pull origin master")
        if pull_result[0] != 0:
            if "Could not connect to server" in pull_result[2]:
                print(f"网络连接问题，重试中 ({attempt+1}/{max_retries})...")
                time.sleep(retry_delay)
                continue
            else:
                print("拉取失败，可能需要手动解决冲突")
                return False
        else:
            print("成功从远程仓库拉取更新")
            return True
            
    print(f"经过 {max_retries} 次尝试后，仍无法连接到GitHub。请检查您的网络连接。")
    return False

if __name__ == "__main__":
    git_pull()

