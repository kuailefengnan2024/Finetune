import os
import argparse
from PIL import Image, ImageFilter
import numpy as np
from scipy.ndimage import distance_transform_edt

# 在这里设置图片目录路径 - 修复反斜杠问题
IMAGE_DIRECTORY = r"D:\BaiduSyncdisk\DyVault\Finetune\Datasets\Custom_Images_Keai"  # 请修改为您的图片目录路径

def resize_images(directory_path=None, target_size=(512, 512)):
    """
    调整指定目录中所有图片的大小，并将结果保存到同一目录下的Modified文件夹中
    
    Args:
        directory_path: 包含图片的目录路径
        target_size: 目标尺寸，默认为(512, 512)
    """
    # 如果没有提供目录路径，使用默认路径
    if directory_path is None:
        directory_path = IMAGE_DIRECTORY
        
    # 确保目录存在
    if not os.path.isdir(directory_path):
        print(f"错误：目录 '{directory_path}' 不存在")
        return
    
    # 创建输出目录
    output_dir = os.path.join(directory_path, "Modified")
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取目录中的所有文件
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    # 过滤出图片文件（简单检查常见图片扩展名）
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    image_files = [f for f in files if os.path.splitext(f.lower())[1] in image_extensions]
    
    if not image_files:
        print(f"在目录 '{directory_path}' 中没有找到图片文件")
        return
    
    # 调整图片大小并保存
    for filename in image_files:
        input_path = os.path.join(directory_path, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            with Image.open(input_path) as img:
                # 检查图像是否有透明通道
                has_transparency = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
                
                # 如果有透明通道，先处理透明背景
                if has_transparency:
                    # 转换为RGBA模式以确保有alpha通道
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # 调整原图大小，保持纵横比
                    img_resized = img.copy()
                    img_resized.thumbnail(target_size, Image.LANCZOS)
                    
                    # 检测边缘类型
                    is_straight_edge = detect_straight_edges(img_resized)
                    
                    if is_straight_edge:
                        # 如果是直线边缘，使用边缘扩展填充
                        print(f"检测到直线边缘，使用边缘扩展填充: '{filename}'")
                        background = extend_edges_scipy(img_resized, target_size)
                    else:
                        # 如果是不规则边缘，使用黑色背景
                        print(f"检测到不规则边缘，使用黑色背景: '{filename}'")
                        background = Image.new("RGB", target_size, (0, 0, 0))
                    
                    # 将调整大小后的图像粘贴到背景上
                    paste_x = (target_size[0] - img_resized.width) // 2
                    paste_y = (target_size[1] - img_resized.height) // 2
                    background.paste(img_resized, (paste_x, paste_y), img_resized)
                    
                    # 保存结果
                    background.save(output_path)
                else:
                    # 对于没有透明通道的图像，使用原来的处理方式
                    # 调整大小，保持纵横比
                    img_resized = img.copy()
                    img_resized.thumbnail(target_size, Image.LANCZOS)
                    
                    # 创建一个新的背景图像
                    background = Image.new("RGB", target_size, (255, 255, 255))
                    
                    # 将调整大小后的图像粘贴到中心
                    paste_x = (target_size[0] - img_resized.width) // 2
                    paste_y = (target_size[1] - img_resized.height) // 2
                    background.paste(img_resized, (paste_x, paste_y))
                    
                    # 保存结果
                    background.save(output_path)
                
                print(f"已调整大小: '{filename}' -> '{output_path}'")
        except Exception as e:
            print(f"处理 '{filename}' 时出错: {e}")
    
    print(f"完成！已处理 {len(image_files)} 个文件，结果保存在 '{output_dir}'")

def detect_straight_edges(img):
    """
    检测图像是否具有直线边缘
    
    Args:
        img: 原始图像（带透明通道）
        
    Returns:
        布尔值，表示是否具有直线边缘
    """
    # 将图像转换为numpy数组以便处理
    img_array = np.array(img)
    
    # 获取alpha通道
    alpha = img_array[:, :, 3]
    
    # 创建一个掩码，标记所有非完全透明的像素
    mask = alpha > 128  # 使用阈值128来确定是否透明
    
    # 如果图像完全透明或完全不透明，返回True
    if np.all(mask) or not np.any(mask):
        return True
    
    # 找到边缘像素
    edge_pixels = []
    height, width = mask.shape
    
    # 检查每个像素的四个相邻像素，如果有透明/不透明的过渡，则认为是边缘
    for i in range(1, height-1):
        for j in range(1, width-1):
            if mask[i, j]:
                if (not mask[i-1, j] or not mask[i+1, j] or 
                    not mask[i, j-1] or not mask[i, j+1]):
                    edge_pixels.append((i, j))
    
    if not edge_pixels:
        return True
    
    # 计算边缘像素的方向变化
    direction_changes = 0
    prev_direction = None
    
    # 对边缘像素进行排序，以便沿着边缘遍历
    # 这里使用一个简单的方法：按照x坐标排序，然后按照y坐标排序
    edge_pixels.sort()
    
    # 计算相邻边缘像素之间的方向变化
    for i in range(1, len(edge_pixels)):
        curr_y, curr_x = edge_pixels[i]
        prev_y, prev_x = edge_pixels[i-1]
        
        # 计算方向（简化为8个方向）
        dy = curr_y - prev_y
        dx = curr_x - prev_x
        
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
        
        curr_direction = (dy, dx)
        
        # 如果方向发生变化，增加计数
        if prev_direction is not None and curr_direction != prev_direction:
            direction_changes += 1
        
        prev_direction = curr_direction
    
    # 计算边缘的复杂度：方向变化次数与边缘像素数量的比率
    complexity = direction_changes / len(edge_pixels) if edge_pixels else 0
    
    # 如果复杂度低于阈值，认为是直线边缘
    # 这个阈值可以根据需要调整
    return complexity < 0.1

def extend_edges_scipy(img, target_size):
    """
    使用scipy的距离变换创建一个基于边缘扩展的背景，保持边缘的渐变效果
    
    Args:
        img: 原始图像（带透明通道）
        target_size: 目标尺寸
        
    Returns:
        填充了边缘扩展的背景图像
    """
    # 计算粘贴位置
    paste_x = (target_size[0] - img.width) // 2
    paste_y = (target_size[1] - img.height) // 2
    
    # 将图像转换为numpy数组以便处理
    img_array = np.array(img)
    
    # 获取alpha通道
    alpha = img_array[:, :, 3]
    
    # 创建一个掩码，标记所有非完全透明的像素
    mask = alpha > 0
    
    # 如果图像完全透明，返回白色背景
    if not np.any(mask):
        return Image.new("RGB", target_size, (255, 255, 255))
    
    # 获取RGB通道
    rgb = img_array[:, :, :3].astype(np.float32)
    
    # 创建目标尺寸的背景数组
    background = np.zeros((target_size[1], target_size[0], 3), dtype=np.float32)
    
    # 创建一个与目标尺寸相同的掩码，标记原始图像的位置
    full_mask = np.zeros((target_size[1], target_size[0]), dtype=bool)
    full_mask[paste_y:paste_y+img.height, paste_x:paste_x+img.width] = mask
    
    # 将原始图像的RGB值复制到背景中
    background[paste_y:paste_y+img.height, paste_x:paste_x+img.width][mask] = rgb[mask]
    
    # 使用scipy的距离变换计算每个背景像素到最近非透明像素的距离和索引
    dist, indices = distance_transform_edt(~full_mask, return_indices=True)
    
    # 对于每个背景像素，使用最近的非透明像素的颜色
    for i in range(target_size[1]):
        for j in range(target_size[0]):
            if not full_mask[i, j]:
                # 获取最近非透明像素的索引
                ii, jj = indices[:, i, j]
                
                # 如果索引指向原始图像区域内的非透明像素
                if (paste_y <= ii < paste_y+img.height and 
                    paste_x <= jj < paste_x+img.width and 
                    mask[ii-paste_y, jj-paste_x]):
                    # 使用该像素的颜色
                    background[i, j] = rgb[ii-paste_y, jj-paste_x]
                else:
                    # 否则使用白色
                    background[i, j] = [255, 255, 255]
    
    # 将背景转换为PIL图像
    background = np.clip(background, 0, 255).astype(np.uint8)
    background_img = Image.fromarray(background, 'RGB')
    
    return background_img

if __name__ == "__main__":
    # 您可以直接修改上面的 IMAGE_DIRECTORY 变量，或者使用命令行参数
    parser = argparse.ArgumentParser(description='调整指定目录中图片的大小')
    parser.add_argument('directory', type=str, nargs='?', help='包含图片的目录路径')
    parser.add_argument('--width', type=int, default=512, help='目标宽度（默认：512）')
    parser.add_argument('--height', type=int, default=512, help='目标高度（默认：512）')
    
    args = parser.parse_args()
    resize_images(args.directory, target_size=(args.width, args.height)) 