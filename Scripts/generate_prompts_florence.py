import os
import sys
import torch
from PIL import Image
from tqdm.auto import tqdm
import logging
import importlib.util
import importlib.machinery
import types

# 设置日志
logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)

# 模型和图片路径
MODEL_PATH = r"D:\BaiduSyncdisk\DyVault\Finetune\Models\florence-2-large"
IMAGE_DIR = r"D:\BaiduSyncdisk\DyVault\Finetune\Datasets\Custom_Images_Keai\Modified"

# 修改sys.path以便能够正确导入模型文件
sys.path.append(MODEL_PATH)

# 首先加载配置模块
config_path = os.path.join(MODEL_PATH, "configuration_florence2.py")
with open(config_path, 'r', encoding='utf-8') as f:
    config_code = f.read()

# 将配置模块加载到sys.modules中
config_module = types.ModuleType('configuration_florence2')
exec(config_code, config_module.__dict__)
sys.modules['configuration_florence2'] = config_module

# 从配置模块中获取需要的类
Florence2Config = config_module.Florence2Config
Florence2VisionConfig = config_module.Florence2VisionConfig
Florence2LanguageConfig = config_module.Florence2LanguageConfig

# 加载模型模块，但需要修改其中的相对导入
model_path = os.path.join(MODEL_PATH, "modeling_florence2.py")
with open(model_path, 'r', encoding='utf-8') as f:
    model_code = f.read()

# 替换相对导入为绝对导入
model_code = model_code.replace('from .configuration_florence2', 'from configuration_florence2')

# 创建模型模块
model_module = types.ModuleType('modeling_florence2')
exec(model_code, model_module.__dict__)
sys.modules['modeling_florence2'] = model_module

# 获取模型类
Florence2ForConditionalGeneration = model_module.Florence2ForConditionalGeneration

from transformers import AutoProcessor

class FlorenceModel:
    def __init__(self, model_path=MODEL_PATH):
        self.processor = None
        self.model = None
        self.model_path = model_path
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.load_model()

    def load_model(self):
        if not os.path.exists(self.model_path):
            logging.error(f"本地模型路径不存在: {self.model_path}")
            sys.exit(1)

        try:
            logging.info(f"正在加载本地模型: {self.model_path}")
            self.processor = AutoProcessor.from_pretrained(
                self.model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            model_file = os.path.join(self.model_path, "pytorch_model.bin")
            if os.path.exists(model_file):
                model_size = os.path.getsize(model_file) / (1024 * 1024)
                logging.info(f"模型文件大小: {model_size:.2f} MB")
            
            with tqdm(total=100, desc="加载模型中", leave=False) as pbar:
                config = Florence2Config.from_pretrained(self.model_path, local_files_only=True)
                self.model = Florence2ForConditionalGeneration.from_pretrained(
                    self.model_path,
                    config=config,
                    torch_dtype=self.torch_dtype,
                    trust_remote_code=True,
                    local_files_only=True
                ).to(self.device)
                pbar.update(100)
            
            logging.info("模型加载成功")
        except Exception as e:
            logging.error(f"加载模型失败: {str(e)}")
            sys.exit(1)

    def generate_description(self, image_path):
        try:
            image = Image.open(image_path).convert('RGB')
            prompt = "<CAPTION>"
            inputs = self.processor(text=prompt, images=image, return_tensors="pt").to(self.device, self.torch_dtype)
            
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=50,
                    num_beams=3,
                    do_sample=False
                )
                generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return generated_text
        except Exception as e:
            logging.error(f"处理图像 {image_path} 时出错: {str(e)}")
            return None

def process_images_in_directory(model, directory):
    if not os.path.exists(directory):
        logging.error(f"图片文件夹不存在: {directory}")
        sys.exit(1)
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(image_extensions)]
    
    if not image_files:
        logging.warning(f"文件夹 {directory} 中没有找到图片文件")
        return
    
    logging.info(f"找到 {len(image_files)} 张图片，开始处理...")
    
    for image_file in tqdm(image_files, desc="处理图片", unit="张"):
        image_path = os.path.join(directory, image_file)
        logging.info(f"正在处理: {image_path}")
        description = model.generate_description(image_path)
        
        if description:
            # 保存描述到与图片同名的txt文件中
            file_name, _ = os.path.splitext(image_file)
            txt_file = os.path.join(directory, f"{file_name}.txt")
            
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(description)
            
            logging.info(f"{image_file} 的描述已保存到: {txt_file}")
            logging.info(f"描述内容: {description}")
        else:
            logging.warning(f"无法生成 {image_file} 的描述")

if __name__ == "__main__":
    try:
        logging.info("初始化模型...")
        model = FlorenceModel()
        process_images_in_directory(model, IMAGE_DIR)
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        raise