@echo off
call D:\BaiduSyncdisk\DyVault\Finetune\venv\Scripts\activate.bat
accelerate launch d:/BaiduSyncdisk/DyVault/Finetune/sd-scripts/train_db.py --config_file D:/BaiduSyncdisk/DyVault/Finetune/Models_Output/config_dreambooth-20250324-205926.toml
pause 