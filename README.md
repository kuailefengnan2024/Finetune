# 载入Florence模型出问题根本原因：原始代码试图直接将模型目录添加到 sys.path 并导入 modeling_florence2，但是该文件内部使用了相对导入语法 from .configuration_florence2 import Florence2Config，
# 这在非包环境中是不允许的。


# Datasets文件夹用来存放训练数据集
可以挑选不同风格 修改后的图片和prompt 放在一起 

# Models文件夹用来存放模型

# 下载模型 运行download_model.py 下载模型


* Model Output 存放训练完的模型和其他数据
* Scripts内脚本处理图片和prompt 
