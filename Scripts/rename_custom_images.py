import os
import argparse

# 在这里设置图片目录路径
IMAGE_DIRECTORY = "D:\BaiduSyncdisk\DyVault\Finetune\Datasets\Custom_Images_Keai"  # 请修改为您的图片目录路径

def rename_images(directory_path=None):
    """
    重命名指定目录中的所有图片文件，格式为 image_001.jpg, image_002.jpg 等
    
    Args:
        directory_path: 包含图片的目录路径
    """
    # 如果没有提供目录路径，使用默认路径
    if directory_path is None:
        directory_path = IMAGE_DIRECTORY
        
    # 确保目录存在
    if not os.path.isdir(directory_path):
        print(f"错误：目录 '{directory_path}' 不存在")
        return
    
    # 获取目录中的所有文件
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    # 过滤出图片文件（简单检查常见图片扩展名）
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    image_files = [f for f in files if os.path.splitext(f.lower())[1] in image_extensions]
    
    if not image_files:
        print(f"在目录 '{directory_path}' 中没有找到图片文件")
        return
    
    # 对文件进行排序
    image_files.sort()
    
    # 重命名文件
    for i, filename in enumerate(image_files, 1):
        old_path = os.path.join(directory_path, filename)
        extension = os.path.splitext(filename)[1]
        new_filename = f"image_{i:03d}{extension}"
        new_path = os.path.join(directory_path, new_filename)
        
        # 如果新文件名已存在，跳过
        if os.path.exists(new_path) and old_path != new_path:
            print(f"跳过 '{filename}'，因为 '{new_filename}' 已存在")
            continue
        
        os.rename(old_path, new_path)
        print(f"已重命名: '{filename}' -> '{new_filename}'")
    
    print(f"完成！已重命名 {len(image_files)} 个文件")

if __name__ == "__main__":
    # 您可以直接修改上面的 IMAGE_DIRECTORY 变量，或者使用命令行参数
    parser = argparse.ArgumentParser(description='重命名指定目录中的图片文件')
    parser.add_argument('directory', type=str, nargs='?', help='包含图片的目录路径')
    
    args = parser.parse_args()
    rename_images(args.directory) 