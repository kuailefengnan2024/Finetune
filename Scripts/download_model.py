#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型下载脚本
用于从Hugging Face下载模型到本地
"""

import os
import sys
import argparse
import logging
from tqdm.auto import tqdm
import shutil
import time
from pathlib import Path
from huggingface_hub import hf_hub_download, snapshot_download, HfApi
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 可修改：默认模型地址，如果命令行没有提供，则使用此地址
DEFAULT_MODEL_REPO = "@https://huggingface.co/black-forest-labs/FLUX.1-dev"
#DEFAULT_MODEL_REPO = "@https://huggingface.co/XLabs-AI/flux-dev-fp8"  # 在这里修改默认模型地址

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 模型保存的默认位置
MODELS_DIR = os.path.join(ROOT_DIR, "Models")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="从Hugging Face下载模型到本地")
    parser.add_argument(
        "--repo_id", 
        type=str, 
        default=DEFAULT_MODEL_REPO.lstrip("@"),
        help="Hugging Face模型仓库ID，例如：'black-forest-labs/FLUX.1-dev'"
    )
    parser.add_argument(
        "--save_dir", 
        type=str, 
        default=None,
        help="模型保存的目录，默认为Models/<repo_name>"
    )
    parser.add_argument(
        "--allow_patterns", 
        type=str, 
        default=None, 
        nargs="+",
        help="指定要下载的文件模式，例如：'*.json' '*.py' 'pytorch_model.bin'"
    )
    parser.add_argument(
        "--ignore_patterns", 
        type=str, 
        default=None, 
        nargs="+",
        help="指定要忽略的文件模式，例如：'.*' '*.safetensors'"
    )
    parser.add_argument(
        "--local_dir_use_symlinks", 
        type=str, 
        default="auto",
        choices=["auto", "true", "false"],
        help="是否使用符号链接下载大文件"
    )
    parser.add_argument(
        "--revision", 
        type=str, 
        default="main",
        help="模型的分支或标签，默认为'main'"
    )
    parser.add_argument(
        "--token", 
        type=str, 
        default=None,
        help="Hugging Face的访问令牌，用于下载私有模型"
    )
    parser.add_argument(
        "--list_files", 
        action="store_true",
        help="仅列出模型仓库中的文件，不下载"
    )
    
    return parser.parse_args()

def parse_repo_id(repo_id):
    """
    解析仓库ID，处理可能的URL格式
    
    参数:
    - repo_id: 可能是简单的ID "namespace/name" 或完整的URL "https://huggingface.co/namespace/name"
    
    返回:
    - 规范化的repo_id格式 "namespace/name"
    """
    # 移除可能的@前缀
    if repo_id.startswith("@"):
        repo_id = repo_id[1:]
    
    # 如果是URL格式，提取实际的repo_id部分
    url_pattern = r"https?://huggingface\.co/([^/]+/[^/]+)/?.*"
    match = re.match(url_pattern, repo_id)
    if match:
        return match.group(1)
    
    return repo_id

def list_repository_files(repo_id, token=None, revision="main"):
    """列出Hugging Face仓库中的文件"""
    repo_id = parse_repo_id(repo_id)
    logging.info(f"正在获取仓库 {repo_id} 的文件列表...")
    api = HfApi()
    try:
        files = api.list_repo_files(repo_id=repo_id, revision=revision, token=token)
        return files
    except Exception as e:
        logging.error(f"获取文件列表失败: {e}")
        return []

def download_model(repo_id, save_dir=None, allow_patterns=None, ignore_patterns=None, 
                  local_dir_use_symlinks="auto", revision="main", token=None):
    """下载模型到本地"""
    # 解析仓库ID
    repo_id = parse_repo_id(repo_id)
    logging.info(f"解析仓库ID: {repo_id}")
    
    # 如果没有指定保存目录，使用默认的Models/<repo_name>
    if not save_dir:
        repo_name = repo_id.split("/")[-1]
        save_dir = os.path.join(MODELS_DIR, repo_name)
    
    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)
    
    logging.info(f"开始下载模型 {repo_id} 到 {save_dir}")
    
    try:
        # 将symlinks参数转换为布尔值
        if local_dir_use_symlinks.lower() == "true":
            use_symlinks = True
        elif local_dir_use_symlinks.lower() == "false":
            use_symlinks = False
        else:  # "auto"
            use_symlinks = "auto"
            
        # 使用snapshot_download下载整个仓库
        start_time = time.time()
        snapshot_download(
            repo_id=repo_id,
            local_dir=save_dir,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            local_dir_use_symlinks=use_symlinks,
            revision=revision,
            token=token
        )
        end_time = time.time()
        
        logging.info(f"模型下载完成！耗时: {end_time - start_time:.2f}秒")
        logging.info(f"模型保存在: {save_dir}")
        return save_dir
        
    except Exception as e:
        logging.error(f"下载模型失败: {e}")
        return None

def main():
    """主函数"""
    args = parse_args()
    
    # 从命令行或从DEFAULT_MODEL_REPO获取repo_id
    repo_id = args.repo_id
    
    # 如果只是列出文件
    if args.list_files:
        files = list_repository_files(repo_id, token=args.token, revision=args.revision)
        if files:
            logging.info(f"仓库 {repo_id} 中的文件:")
            for file in files:
                print(f"  {file}")
        return
        
    # 下载模型
    download_model(
        repo_id=repo_id,
        save_dir=args.save_dir,
        allow_patterns=args.allow_patterns,
        ignore_patterns=args.ignore_patterns,
        local_dir_use_symlinks=args.local_dir_use_symlinks,
        revision=args.revision,
        token=args.token
    )

if __name__ == "__main__":
    main() 